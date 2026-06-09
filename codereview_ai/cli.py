"""
Command Line Interface Module
命令行接口模块

Main entry point for the CodeReview-AI-CLI application.
Provides argument parsing and command dispatch.
"""

import argparse
import json
import os
import sys
from typing import Optional

from .analyzer import CodeAnalyzer
from .git_diff import GitDiffAnalyzer
from .reviewer import AIReviewEngine
from .tui import TUI


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="codereview-ai",
        description="🦞 CodeReview-AI-CLI - Lightweight Terminal Code Review & Quality Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codereview-ai analyze src/                    Analyze a directory
  codereview-ai analyze main.py                 Analyze a single file
  codereview-ai diff                            Analyze unstaged changes
  codereview-ai diff --base main                Compare with main branch
  codereview-ai commit HEAD~1                   Analyze previous commit
  codereview-ai report src/ -o report.json      Generate JSON report
  codereview-ai compare main develop            Compare two branches
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze code files or directories",
        description="Analyze code quality, security, and style issues"
    )
    analyze_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to analyze (default: current directory)"
    )
    analyze_parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    analyze_parser.add_argument(
        "--severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
        default="INFO",
        help="Minimum severity level to report"
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="Analyze Git diff",
        description="Analyze changes in Git working directory or between commits"
    )
    diff_parser.add_argument(
        "--base",
        default=None,
        help="Base commit/branch for comparison"
    )
    diff_parser.add_argument(
        "--target",
        default="HEAD",
        help="Target commit/branch (default: HEAD)"
    )
    diff_parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    diff_parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )

    # Commit command
    commit_parser = subparsers.add_parser(
        "commit",
        help="Analyze a specific commit",
        description="Analyze all changes in a specific Git commit"
    )
    commit_parser.add_argument(
        "hash",
        nargs="?",
        default="HEAD",
        help="Commit hash to analyze (default: HEAD)"
    )
    commit_parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )

    # Compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two branches",
        description="Compare code quality between two Git branches"
    )
    compare_parser.add_argument(
        "branch1",
        help="Base branch"
    )
    compare_parser.add_argument(
        "branch2",
        nargs="?",
        default="HEAD",
        help="Compare branch (default: HEAD)"
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate comprehensive report",
        description="Generate a comprehensive code quality report"
    )
    report_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)"
    )
    report_parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path"
    )
    report_parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "html"],
        default="json",
        help="Report format"
    )

    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        aliases=["i"],
        help="Launch interactive TUI mode",
        description="Launch interactive terminal user interface"
    )

    return parser


class CLI:
    """命令行接口主类"""

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.git_analyzer = GitDiffAnalyzer()
        self.review_engine = AIReviewEngine()
        self.tui = TUI()
        self.severity_levels = {
            "CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4
        }

    def run(self, args: Optional[list] = None):
        """运行CLI"""
        parser = create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return 0

        try:
            if parsed_args.command == "analyze":
                return self._cmd_analyze(parsed_args)
            elif parsed_args.command == "diff":
                return self._cmd_diff(parsed_args)
            elif parsed_args.command == "commit":
                return self._cmd_commit(parsed_args)
            elif parsed_args.command == "compare":
                return self._cmd_compare(parsed_args)
            elif parsed_args.command == "report":
                return self._cmd_report(parsed_args)
            elif parsed_args.command in ("interactive", "i"):
                return self._cmd_interactive()
            else:
                parser.print_help()
                return 1
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def _cmd_analyze(self, args):
        """处理analyze命令"""
        path = args.path
        min_severity = self.severity_levels.get(args.severity, 4)

        if not os.path.exists(path):
            print(f"Error: Path not found: {path}", file=sys.stderr)
            return 1

        self.tui.print_header(
            "🦞 CodeReview-AI-CLI",
            "Code Quality Analysis Report"
        )

        if os.path.isfile(path):
            results = [self.analyzer.analyze_file(path)]
        else:
            print(f"Analyzing directory: {path}")
            results = self.analyzer.analyze_directory(path)

        # Filter by severity
        filtered_results = []
        for result in results:
            if "error" in result:
                continue
            result["issues"] = [
                issue for issue in result.get("issues", [])
                if self.severity_levels.get(issue.get("severity", "INFO"), 4) <= min_severity
            ]
            result["issue_count"] = len(result["issues"])
            filtered_results.append(result)

        # Generate reviews
        reviews = []
        for result in filtered_results:
            review = self.review_engine.generate_review(result)
            reviews.append(review)

        # Output
        if args.format == "json":
            output = json.dumps(reviews, indent=2, ensure_ascii=False)
        elif args.format == "markdown":
            output = self._format_markdown(reviews)
        else:
            self._print_text_report(reviews)
            output = None

        if output and args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nReport saved to: {args.output}")
        elif output:
            print(output)

        return 0

    def _cmd_diff(self, args):
        """处理diff命令"""
        self.tui.print_header(
            "🦞 CodeReview-AI-CLI",
            "Git Diff Analysis"
        )

        stats = self.git_analyzer.get_diff_stats(args.target, args.base)
        if "error" in stats:
            print(f"Error: {stats['error']}", file=sys.stderr)
            return 1

        files = self.git_analyzer.get_changed_files(args.target, args.base)
        risks = self.git_analyzer.detect_risky_changes(args.target, args.base)

        self.tui.print_git_stats(stats)

        if risks:
            self.tui.print_risk_alert(risks)

        # Analyze each changed file
        print(f"\nAnalyzing {len(files)} changed files...")
        analyses = []
        for i, file_info in enumerate(files):
            if "error" in file_info or file_info.get("is_deleted"):
                continue
            self.tui.print_progress(i + 1, len(files), file_info.get("filepath", ""))

            diff_analysis = self.git_analyzer.get_file_diff(
                file_info["filepath"], args.target, args.base
            )
            if "error" not in diff_analysis:
                analyses.append(diff_analysis)

        # Print results
        for analysis in analyses:
            filepath = analysis.get("filepath", "")
            issues = analysis.get("issues_in_changes", [])
            if issues:
                self.tui.print_section(f"Issues in {filepath}")
                for issue in issues:
                    self.tui.print_issue(issue)

        return 0

    def _cmd_commit(self, args):
        """处理commit命令"""
        self.tui.print_header(
            "🦞 CodeReview-AI-CLI",
            f"Commit Analysis: {args.hash}"
        )

        commit_analysis = self.git_analyzer.analyze_commit(args.hash)
        if "error" in commit_analysis:
            print(f"Error: {commit_analysis['error']}", file=sys.stderr)
            return 1

        print(f"\n  Commit: {commit_analysis.get('commit_hash', 'N/A')[:12]}")
        print(f"  Author: {commit_analysis.get('author', 'N/A')}")
        print(f"  Date: {commit_analysis.get('date', 'N/A')}")
        print(f"  Message: {commit_analysis.get('message', 'N/A')}")

        stats = commit_analysis.get("stats", {})
        self.tui.print_git_stats(stats)

        file_analyses = commit_analysis.get("file_analyses", [])
        if file_analyses:
            self.tui.print_section("File Analysis")
            for fa in file_analyses:
                filepath = fa.get("filepath", "")
                issues = fa.get("issues_in_changes", [])
                print(f"\n  📄 {filepath}")
                if issues:
                    for issue in issues[:3]:
                        self.tui.print_issue(issue)
                else:
                    print(f"    {self.tui.color('✅ No issues detected', Colors.GREEN)}")

        return 0

    def _cmd_compare(self, args):
        """处理compare命令"""
        self.tui.print_header(
            "🦞 CodeReview-AI-CLI",
            f"Branch Comparison: {args.branch1} → {args.branch2}"
        )

        comparison = self.git_analyzer.get_branch_comparison(args.branch1, args.branch2)
        if "error" in comparison:
            print(f"Error: {comparison['error']}", file=sys.stderr)
            return 1

        print(f"\n  Base: {comparison.get('base_branch', 'N/A')}")
        print(f"  Compare: {comparison.get('compare_branch', 'N/A')}")
        print(f"  Files Changed: {comparison.get('files_changed', 0)}")

        stats = comparison.get("stats", {})
        self.tui.print_git_stats(stats)

        return 0

    def _cmd_report(self, args):
        """处理report命令"""
        path = args.path

        if not os.path.exists(path):
            print(f"Error: Path not found: {path}", file=sys.stderr)
            return 1

        print(f"Generating comprehensive report for: {path}")

        if os.path.isfile(path):
            results = [self.analyzer.analyze_file(path)]
        else:
            results = self.analyzer.analyze_directory(path)

        reviews = []
        for result in results:
            if "error" not in result:
                review = self.review_engine.generate_review(result)
                reviews.append(review)

        summary = self.review_engine.generate_pr_summary(reviews)

        report = {
            "generated_at": self._get_timestamp(),
            "project_path": os.path.abspath(path),
            "summary": summary,
            "file_reviews": reviews
        }

        if args.format == "json":
            content = json.dumps(report, indent=2, ensure_ascii=False)
        elif args.format == "markdown":
            content = self._format_full_markdown(report)
        elif args.format == "html":
            content = self._format_html(report)
        else:
            content = json.dumps(report, indent=2, ensure_ascii=False)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Report saved to: {args.output}")
        return 0

    def _cmd_interactive(self):
        """处理interactive命令"""
        self.tui.print_welcome()

        while True:
            try:
                print()
                cmd = input(self.tui.color("codereview-ai> ", Colors.BRIGHT_CYAN + Colors.BOLD)).strip()
                if not cmd:
                    continue

                parts = cmd.split()
                if parts[0] == "quit" or parts[0] == "exit":
                    print(self.tui.color("Goodbye! 👋", Colors.BRIGHT_GREEN))
                    break
                elif parts[0] == "help":
                    self.tui.print_help()
                elif parts[0] == "analyze":
                    path = parts[1] if len(parts) > 1 else "."
                    self._interactive_analyze(path)
                elif parts[0] == "diff":
                    base = parts[1] if len(parts) > 1 else None
                    self._interactive_diff(base)
                else:
                    print(self.tui.color(f"Unknown command: {parts[0]}", Colors.YELLOW))
                    self.tui.print_help()

            except KeyboardInterrupt:
                print("\n")
                continue
            except EOFError:
                break

        return 0

    def _interactive_analyze(self, path: str):
        """交互式分析"""
        if not os.path.exists(path):
            print(self.tui.color(f"Path not found: {path}", Colors.RED))
            return

        if os.path.isfile(path):
            result = self.analyzer.analyze_file(path)
            review = self.review_engine.generate_review(result)
            self._print_single_review(review)
        else:
            results = self.analyzer.analyze_directory(path)
            reviews = []
            for result in results:
                if "error" not in result:
                    reviews.append(self.review_engine.generate_review(result))

            self.tui.print_section(f"Analyzed {len(reviews)} files")
            for review in reviews:
                self.tui.print_file_summary(
                    review.get("filepath", ""),
                    review.get("quality_score", 0),
                    review.get("issue_count", 0)
                )

    def _interactive_diff(self, base: str = None):
        """交互式diff分析"""
        files = self.git_analyzer.get_changed_files("HEAD", base)
        valid_files = [f for f in files if "error" not in f and not f.get("is_deleted")]

        if not valid_files:
            print(self.tui.color("No changes detected", Colors.YELLOW))
            return

        print(f"\n{len(valid_files)} files changed:")
        for i, f in enumerate(valid_files, 1):
            print(f"  {i}. {f.get('filepath')} [{f.get('status', '?')}]")

    def _print_text_report(self, reviews: list):
        """打印文本格式报告"""
        total_issues = sum(r.get("issue_count", 0) for r in reviews)
        avg_score = sum(r.get("quality_score", 0) for r in reviews) / max(len(reviews), 1)

        self.tui.print_score(int(avg_score))

        if total_issues > 0:
            self.tui.print_section(f"Issues Found: {total_issues}")
            for review in reviews:
                if review.get("issue_count", 0) > 0:
                    self.tui.print_section(f"📄 {os.path.basename(review.get('filepath', 'unknown'))}")
                    for issue in review.get("review_comments", [])[:10]:
                        print(f"  {issue}")

        for review in reviews:
            suggestions = review.get("general_suggestions", [])
            if suggestions:
                self.tui.print_section("Suggestions")
                for suggestion in suggestions:
                    print(f"  {suggestion}")
                break

    def _print_single_review(self, review: dict):
        """打印单个文件审查"""
        self.tui.print_section(os.path.basename(review.get("filepath", "unknown")))
        self.tui.print_score(review.get("quality_score", 0))

        for issue in review.get("review_comments", []):
            print(f"  {issue}")

    def _format_markdown(self, reviews: list) -> str:
        """格式化为Markdown"""
        lines = ["# Code Review Report\n"]
        for review in reviews:
            lines.append(f"## {review.get('filepath', 'unknown')}\n")
            lines.append(f"**Quality Score:** {review.get('quality_score', 0)}/100\n")
            lines.append(f"**Assessment:** {review.get('assessment', '')}\n")

            if review.get("review_comments"):
                lines.append("### Issues\n")
                for comment in review["review_comments"]:
                    lines.append(f"- {comment}\n")

            lines.append("\n---\n")
        return "\n".join(lines)

    def _format_full_markdown(self, report: dict) -> str:
        """格式化完整Markdown报告"""
        lines = [
            "# 📊 Code Quality Report",
            "",
            f"**Generated:** {report.get('generated_at', 'N/A')}",
            f"**Project:** {report.get('project_path', 'N/A')}",
            "",
            "## Summary",
            "",
        ]

        summary = report.get("summary", {})
        lines.append(f"- **Total Files:** {summary.get('total_files', 0)}")
        lines.append(f"- **Total Issues:** {summary.get('total_issues', 0)}")
        lines.append(f"- **Average Quality Score:** {summary.get('average_quality_score', 0)}/100")
        lines.append(f"- **Overall Assessment:** {summary.get('overall_assessment', 'N/A')}")
        lines.append("")

        severity = summary.get("severity_breakdown", {})
        if any(severity.values()):
            lines.append("### Severity Breakdown")
            lines.append("")
            for sev, count in severity.items():
                if count > 0:
                    lines.append(f"- **{sev}:** {count}")
            lines.append("")

        lines.append("## File Details")
        lines.append("")

        for review in report.get("file_reviews", []):
            lines.append(f"### {review.get('filepath', 'unknown')}")
            lines.append("")
            lines.append(f"- **Score:** {review.get('quality_score', 0)}/100")
            lines.append(f"- **Issues:** {review.get('issue_count', 0)}")
            lines.append("")

            if review.get("review_comments"):
                lines.append("#### Issues")
                lines.append("")
                for comment in review["review_comments"]:
                    lines.append(f"- {comment}")
                lines.append("")

        return "\n".join(lines)

    def _format_html(self, report: dict) -> str:
        """格式化为HTML报告"""
        summary = report.get("summary", {})
        score = summary.get("average_quality_score", 0)

        if score >= 75:
            score_color = "#28a745"
        elif score >= 50:
            score_color = "#ffc107"
        else:
            score_color = "#dc3545"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Quality Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .issue {{ padding: 10px; margin: 5px 0; border-left: 4px solid #ddd; background: #f9f9f9; }}
        .CRITICAL {{ border-left-color: #dc3545; }}
        .HIGH {{ border-left-color: #fd7e14; }}
        .MEDIUM {{ border-left-color: #ffc107; }}
        .LOW {{ border-left-color: #17a2b8; }}
        .INFO {{ border-left-color: #6c757d; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 Code Quality Report</h1>
        <p>{report.get('project_path', 'N/A')}</p>
        <p>Generated: {report.get('generated_at', 'N/A')}</p>
    </div>

    <div class="card">
        <div class="score">{score}/100</div>
        <p>{summary.get('overall_assessment', 'N/A')}</p>
        <div class="metric">
            <div class="metric-value">{summary.get('total_files', 0)}</div>
            <div class="metric-label">Files</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary.get('total_issues', 0)}</div>
            <div class="metric-label">Issues</div>
        </div>
    </div>
"""

        for review in report.get("file_reviews", []):
            html += f"""
    <div class="card">
        <h3>{review.get('filepath', 'unknown')}</h3>
        <p>Score: {review.get('quality_score', 0)}/100 | Issues: {review.get('issue_count', 0)}</p>
"""
            for comment in review.get("review_comments", [])[:5]:
                html += f"        <div class='issue'>{comment}</div>\n"
            html += "    </div>\n"

        html += """
</body>
</html>
"""
        return html

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """主入口函数"""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
