"""
AI Review Engine Module
AI审查引擎模块

Generates intelligent code review comments based on analysis results:
- Context-aware suggestions
- Best practice recommendations
- Security warnings
- Performance optimization tips
"""

import re
from typing import Dict, List, Any
from .analyzer import CodeAnalyzer


class AIReviewEngine:
    """AI代码审查引擎"""

    # Review templates for different categories
    REVIEW_TEMPLATES = {
        "Security": {
            "CRITICAL": [
                "🚨 **Security Critical**: {message}\n   💡 {suggestion}",
                "⚠️ **Immediate Action Required**: {message}\n   🔧 {suggestion}"
            ],
            "HIGH": [
                "🔒 **Security Risk**: {message}\n   💡 {suggestion}",
                "🛡️ **Security Concern**: {message}\n   🔧 {suggestion}"
            ]
        },
        "Performance": {
            "MEDIUM": [
                "⚡ **Performance**: {message}\n   💡 {suggestion}",
                "🚀 **Optimization Opportunity**: {message}\n   🔧 {suggestion}"
            ]
        },
        "Style": {
            "LOW": [
                "🎨 **Style**: {message}\n   💡 {suggestion}",
                "✨ **Code Style**: {message}\n   🔧 {suggestion}"
            ],
            "INFO": [
                "📝 **Note**: {message}\n   💡 {suggestion}"
            ]
        },
        "Complexity": {
            "MEDIUM": [
                "🧩 **Complexity**: {message}\n   💡 {suggestion}",
                "📊 **Maintainability**: {message}\n   🔧 {suggestion}"
            ]
        },
        "Documentation": {
            "LOW": [
                "📚 **Documentation**: {message}\n   💡 {suggestion}",
                "🗒️ **Docs**: {message}\n   🔧 {suggestion}"
            ]
        },
        "Bug Risk": {
            "HIGH": [
                "🐛 **Bug Risk**: {message}\n   💡 {suggestion}",
                "⚠️ **Potential Bug**: {message}\n   🔧 {suggestion}"
            ]
        }
    }

    # Language-specific best practices
    BEST_PRACTICES = {
        "python": [
            "Use list comprehensions instead of map/filter with lambdas for readability",
            "Prefer 'is' over '==' for None comparisons",
            "Use context managers (with statement) for resource management",
            "Follow PEP 8 naming conventions: snake_case for functions, PascalCase for classes",
            "Use type hints for function signatures to improve code clarity",
            "Prefer pathlib over os.path for path manipulations",
            "Use f-strings for string formatting (Python 3.6+)",
            "Avoid mutable default arguments in function definitions"
        ],
        "javascript": [
            "Use const/let instead of var for variable declarations",
            "Prefer async/await over Promise chains for readability",
            "Use destructuring for cleaner code",
            "Avoid using ==, prefer === for strict equality checks"
        ],
        "typescript": [
            "Use explicit return types for public API functions",
            "Prefer interfaces over type aliases for object shapes",
            "Use readonly for immutable properties"
        ]
    }

    def __init__(self):
        self.analyzer = CodeAnalyzer()

    def generate_review(self, analysis_result: Dict[str, Any], language: str = "python") -> Dict[str, Any]:
        """生成完整的代码审查报告"""
        review_comments = []
        issues = analysis_result.get("issues", [])
        metrics = analysis_result.get("metrics", {})
        filepath = analysis_result.get("filepath", "unknown")

        # Generate comments from issues
        for issue in issues:
            comment = self._format_issue(issue)
            if comment:
                review_comments.append(comment)

        # Add general suggestions based on metrics
        general_suggestions = self._generate_general_suggestions(metrics, language)

        # Add best practice recommendations
        best_practices = self._get_best_practices(language)

        # Calculate overall assessment
        quality_score = analysis_result.get("quality_score", 50)
        assessment = self._get_quality_assessment(quality_score)

        return {
            "filepath": filepath,
            "quality_score": quality_score,
            "assessment": assessment,
            "metrics_summary": self._summarize_metrics(metrics),
            "review_comments": review_comments,
            "general_suggestions": general_suggestions,
            "best_practices": best_practices,
            "issue_count": len(issues),
            "severity_breakdown": analysis_result.get("issue_summary", {})
        }

    def _format_issue(self, issue: Dict[str, Any]) -> str:
        """格式化单个问题为审查评论"""
        category = issue.get("category", "Style")
        severity = issue.get("severity", "INFO")
        message = issue.get("message", "")
        suggestion = issue.get("suggestion", "")
        line = issue.get("line", 0)

        templates = self.REVIEW_TEMPLATES.get(category, {}).get(severity, [])
        if not templates:
            templates = ["📝 **{category}** (Line {line}): {message}\n   💡 {suggestion}"]

        import random
        template = random.choice(templates)

        return template.format(
            message=message,
            suggestion=suggestion,
            category=category,
            line=line
        )

    def _generate_general_suggestions(self, metrics: Dict[str, Any], language: str) -> List[str]:
        """基于度量指标生成一般性建议"""
        suggestions = []

        loc = metrics.get("lines_of_code", 0)
        if loc > 500:
            suggestions.append(f"📦 **File Size**: This file has {loc} lines. Consider splitting into smaller modules for better maintainability.")

        max_length = metrics.get("max_line_length", 0)
        if max_length > 120:
            suggestions.append(f"📏 **Line Length**: Maximum line length is {max_length} characters. Consider breaking long lines for readability.")

        complexity = metrics.get("complexity_score", 0)
        if complexity > 15:
            suggestions.append(f"🧩 **Complexity**: Cyclomatic complexity is {complexity}. Consider refactoring complex functions into smaller ones.")

        func_count = metrics.get("function_count", 0)
        class_count = metrics.get("class_count", 0)
        if func_count > 20:
            suggestions.append(f"🔧 **Function Count**: {func_count} functions detected. Consider grouping related functions into classes or modules.")

        comment_ratio = metrics.get("comment_lines", 0) / max(metrics.get("lines_of_code", 1), 1)
        if comment_ratio < 0.05:
            suggestions.append("📝 **Documentation**: Low comment ratio. Consider adding docstrings and inline comments for complex logic.")

        return suggestions

    def _get_best_practices(self, language: str) -> List[str]:
        """获取语言特定的最佳实践"""
        return self.BEST_PRACTICES.get(language.lower(), self.BEST_PRACTICES["python"])

    def _get_quality_assessment(self, score: int) -> str:
        """获取质量评估描述"""
        if score >= 90:
            return "Excellent 🌟 - Production-ready code with minor improvements possible"
        elif score >= 75:
            return "Good ✅ - Solid code quality, address medium/low priority issues"
        elif score >= 60:
            return "Fair ⚠️ - Acceptable but needs attention to several issues"
        elif score >= 40:
            return "Poor ❌ - Significant issues need to be addressed before merging"
        else:
            return "Critical 🚨 - Major problems detected, requires immediate attention"

    def _summarize_metrics(self, metrics: Dict[str, Any]) -> str:
        """生成度量指标摘要"""
        parts = []
        if "lines_of_code" in metrics:
            parts.append(f"{metrics['lines_of_code']} LOC")
        if "function_count" in metrics:
            parts.append(f"{metrics['function_count']} functions")
        if "class_count" in metrics:
            parts.append(f"{metrics['class_count']} classes")
        if "complexity_score" in metrics:
            parts.append(f"complexity: {metrics['complexity_score']}")
        return " | ".join(parts)

    def generate_pr_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成PR摘要报告"""
        total_files = len(analyses)
        total_issues = sum(a.get("issue_count", 0) for a in analyses)
        avg_score = sum(a.get("quality_score", 0) for a in analyses) / max(total_files, 1)

        severity_totals = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for analysis in analyses:
            breakdown = analysis.get("severity_breakdown", {})
            for sev, count in breakdown.items():
                severity_totals[sev] = severity_totals.get(sev, 0) + count

        return {
            "total_files": total_files,
            "total_issues": total_issues,
            "average_quality_score": round(avg_score, 1),
            "severity_breakdown": severity_totals,
            "overall_assessment": self._get_quality_assessment(int(avg_score)),
            "files": [{
                "filepath": a.get("filepath"),
                "quality_score": a.get("quality_score"),
                "issue_count": a.get("issue_count")
            } for a in analyses]
        }

    def generate_inline_comments(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成行内评论格式"""
        comments = []
        issues = analysis_result.get("issues", [])

        for issue in issues:
            if issue.get("severity") in ["CRITICAL", "HIGH"]:
                comments.append({
                    "line": issue.get("line", 1),
                    "severity": issue.get("severity"),
                    "message": issue.get("message", ""),
                    "suggestion": issue.get("suggestion", ""),
                    "category": issue.get("category", "General")
                })

        return comments
