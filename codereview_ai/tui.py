"""
Terminal User Interface Module
终端用户界面模块

Provides an interactive terminal dashboard for code review results:
- File browser
- Issue viewer with filtering
- Metrics dashboard
- Interactive navigation
"""

import os
import sys
from typing import Dict, List, Any, Optional


class Colors:
    """终端颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class TUI:
    """终端用户界面"""

    SEVERITY_COLORS = {
        "CRITICAL": Colors.BRIGHT_RED,
        "HIGH": Colors.RED,
        "MEDIUM": Colors.YELLOW,
        "LOW": Colors.BLUE,
        "INFO": Colors.DIM
    }

    SEVERITY_BG = {
        "CRITICAL": Colors.BG_RED,
        "HIGH": Colors.BG_RED,
        "MEDIUM": Colors.BG_YELLOW,
        "LOW": Colors.BG_BLUE,
        "INFO": Colors.DIM
    }

    def __init__(self):
        self.use_colors = self._supports_color()
        self.term_width = self._get_terminal_width()

    def _supports_color(self) -> bool:
        """检测终端是否支持颜色"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _get_terminal_width(self) -> int:
        """获取终端宽度"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except:
            return 80

    def color(self, text: str, color_code: str) -> str:
        """添加颜色代码"""
        if self.use_colors:
            return f"{color_code}{text}{Colors.RESET}"
        return text

    def bold(self, text: str) -> str:
        """加粗文本"""
        return self.color(text, Colors.BOLD)

    def print_header(self, title: str, subtitle: str = ""):
        """打印标题头"""
        width = min(self.term_width, 80)
        print()
        print(self.color("=" * width, Colors.CYAN))
        print(self.color(title.center(width), Colors.BOLD + Colors.BRIGHT_CYAN))
        if subtitle:
            print(self.color(subtitle.center(width), Colors.DIM))
        print(self.color("=" * width, Colors.CYAN))
        print()

    def print_section(self, title: str):
        """打印章节标题"""
        print()
        print(self.color(f"▶ {title}", Colors.BOLD + Colors.BRIGHT_BLUE))
        print(self.color("─" * min(len(title) + 3, self.term_width), Colors.BLUE))

    def print_metric(self, label: str, value: str, unit: str = ""):
        """打印度量指标"""
        print(f"  {self.color(label + ':', Colors.DIM):<25} {self.color(value, Colors.BRIGHT_WHITE)}{unit}")

    def print_score(self, score: int):
        """打印质量分数"""
        if score >= 90:
            color = Colors.BRIGHT_GREEN
            emoji = "🌟"
        elif score >= 75:
            color = Colors.GREEN
            emoji = "✅"
        elif score >= 60:
            color = Colors.YELLOW
            emoji = "⚠️"
        elif score >= 40:
            color = Colors.RED
            emoji = "❌"
        else:
            color = Colors.BRIGHT_RED
            emoji = "🚨"

        bar_length = 40
        filled = int(score / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\n  {self.bold('Quality Score:')} {self.color(f'{emoji} {score}/100', color + Colors.BOLD)}")
        print(f"  [{self.color(bar, color)}]")

    def print_issue(self, issue: Dict[str, Any], index: int = 0):
        """打印单个问题"""
        severity = issue.get("severity", "INFO")
        category = issue.get("category", "General")
        message = issue.get("message", "")
        suggestion = issue.get("suggestion", "")
        line = issue.get("line", 0)

        color = self.SEVERITY_COLORS.get(severity, Colors.WHITE)
        bg = self.SEVERITY_BG.get(severity, "")

        severity_tag = self.color(f"[{severity}]", color + Colors.BOLD)
        category_tag = self.color(f"[{category}]", Colors.DIM)

        print(f"\n  {severity_tag} {category_tag} {self.color(f'Line {line}', Colors.DIM)}")
        print(f"    📝 {message}")
        if suggestion:
            print(f"    💡 {self.color(suggestion, Colors.BRIGHT_GREEN)}")

    def print_file_summary(self, filepath: str, score: int, issue_count: int):
        """打印文件摘要"""
        if score >= 75:
            icon = "✅"
            color = Colors.GREEN
        elif score >= 50:
            icon = "⚠️"
            color = Colors.YELLOW
        else:
            icon = "❌"
            color = Colors.RED

        filename = os.path.basename(filepath)
        print(f"  {icon} {self.color(filename, color)} {self.color(f'({score}/100, {issue_count} issues)', Colors.DIM)}")

    def print_progress(self, current: int, total: int, filename: str = ""):
        """打印进度条"""
        width = 30
        filled = int(current / max(total, 1) * width)
        bar = "█" * filled + "░" * (width - filled)
        percent = int(current / max(total, 1) * 100)

        print(f"\r  [{self.color(bar, Colors.BRIGHT_CYAN)}] {percent}% ({current}/{total}) {self.color(filename, Colors.DIM)}", end="", flush=True)
        if current >= total:
            print()

    def print_summary_table(self, data: List[Dict[str, Any]], columns: List[str]):
        """打印摘要表格"""
        if not data:
            print(self.color("  No data to display", Colors.DIM))
            return

        # Calculate column widths
        widths = {}
        for col in columns:
            widths[col] = max(len(str(col)), max(len(str(row.get(col, ""))) for row in data))

        # Print header
        header = " | ".join(self.color(col.upper(), Colors.BOLD + Colors.BRIGHT_BLUE) for col in columns)
        print(f"\n  {header}")
        print(f"  {self.color('-' * (sum(widths.values()) + 3 * (len(columns) - 1)), Colors.DIM)}")

        # Print rows
        for row in data:
            row_str = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
            print(f"  {row_str}")

    def print_severity_breakdown(self, breakdown: Dict[str, int]):
        """打印严重级别分布"""
        print()
        for severity, count in breakdown.items():
            if count > 0:
                color = self.SEVERITY_COLORS.get(severity, Colors.WHITE)
                bar = "█" * min(count, 20)
                print(f"  {self.color(f'{severity}:', color + Colors.BOLD):<12} {self.color(bar, color)} {count}")

    def print_git_stats(self, stats: Dict[str, Any]):
        """打印Git统计信息"""
        print()
        self.print_metric("Files Changed", str(stats.get("files_changed", 0)))
        self.print_metric("Insertions", str(stats.get("insertions", 0)), f" {self.color('+', Colors.GREEN)}")
        self.print_metric("Deletions", str(stats.get("deletions", 0)), f" {self.color('-', Colors.RED)}")
        self.print_metric("Total Changes", str(stats.get("total_changes", 0)))

    def print_risk_alert(self, risks: List[Dict[str, Any]]):
        """打印风险警告"""
        if not risks:
            return

        print()
        print(self.color("  🚨 HIGH RISK CHANGES DETECTED", Colors.BRIGHT_RED + Colors.BOLD))
        print(self.color("  " + "=" * 50, Colors.RED))

        for risk in risks:
            severity = risk.get("severity", "HIGH")
            color = self.SEVERITY_COLORS.get(severity, Colors.RED)
            print(f"\n  {self.color(f'[{severity}]', color + Colors.BOLD)} {risk.get('description', '')}")
            context = risk.get("context", "")
            if context:
                print(f"    {self.color('Context:', Colors.DIM)}")
                print(f"    {self.color(context[:100] + '...' if len(context) > 100 else context, Colors.DIM)}")

    def print_best_practices(self, practices: List[str]):
        """打印最佳实践建议"""
        print()
        print(self.color("  📚 Best Practices for this project:", Colors.BRIGHT_BLUE + Colors.BOLD))
        for i, practice in enumerate(practices[:5], 1):
            print(f"    {i}. {practice}")

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_help(self):
        """打印帮助信息"""
        print()
        self.print_section("Available Commands")
        print("  analyze <path>     Analyze a file or directory")
        print("  diff [base]        Analyze Git diff (default: HEAD)")
        print("  commit [hash]      Analyze a specific commit")
        print("  compare <b1> <b2>  Compare two branches")
        print("  report <path>      Generate full report")
        print("  help               Show this help message")
        print("  quit               Exit the application")

    def interactive_file_browser(self, files: List[Dict[str, Any]]) -> Optional[str]:
        """交互式文件浏览器"""
        if not files:
            print(self.color("  No files to display", Colors.DIM))
            return None

        print()
        self.print_section("Files")
        for i, file_info in enumerate(files, 1):
            filepath = file_info.get("filepath", "unknown")
            score = file_info.get("quality_score", 0)
            issues = file_info.get("issue_count", 0)
            print(f"  {i}. ", end="")
            self.print_file_summary(filepath, score, issues)

        print()
        try:
            choice = input(self.color("  Select file number (or 0 to cancel): ", Colors.BRIGHT_CYAN))
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx].get("filepath")
        except (ValueError, IndexError):
            pass

        return None

    def print_welcome(self):
        """打印欢迎界面"""
        self.clear_screen()
        print()
        print(self.color("""
    🦞 CodeReview-AI-CLI 🦞
    """, Colors.BRIGHT_CYAN + Colors.BOLD))
        print(self.color("""
    ╔═══════════════════════════════════════╗
    ║  Lightweight Terminal Code Review     ║
    ║  & Quality Analysis Engine            ║
    ║                                       ║
    ║  Zero Dependencies · Pure Python      ║
    ║  TUI Dashboard · Git Integration      ║
    ╚═══════════════════════════════════════╝
    """, Colors.CYAN))
        print(self.color("    Version 1.0.0 | MIT License | github.com/gitstq/CodeReview-AI-CLI", Colors.DIM))
        print()
