"""
Code Quality Analyzer Module
代码质量分析器模块

Provides comprehensive code analysis including:
- Complexity metrics (cyclomatic complexity estimation)
- Code style checking
- Security vulnerability detection
- Performance anti-pattern detection
- Documentation coverage analysis
"""

import ast
import re
import os
from typing import Dict, List, Tuple, Any


class CodeMetrics:
    """代码度量指标容器"""
    def __init__(self):
        self.lines_of_code = 0
        self.logical_lines = 0
        self.comment_lines = 0
        self.blank_lines = 0
        self.max_line_length = 0
        self.avg_line_length = 0.0
        self.function_count = 0
        self.class_count = 0
        self.complexity_score = 0
        self.duplicate_lines = 0


class Issue:
    """代码问题/建议容器"""
    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_LOW = "LOW"
    SEVERITY_INFO = "INFO"

    def __init__(self, line: int, severity: str, category: str, message: str, suggestion: str = ""):
        self.line = line
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "suggestion": self.suggestion
        }


class CodeAnalyzer:
    """代码分析器核心类"""

    # Security vulnerability patterns
    SECURITY_PATTERNS = [
        (r'eval\s*\(', "eval() usage", "Avoid using eval() - major security risk"),
        (r'exec\s*\(', "exec() usage", "Avoid using exec() - major security risk"),
        (r'input\s*\(', "input() in Python 2", "Use raw_input() or input() from Python 3 carefully"),
        (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "shell=True in subprocess", "Avoid shell=True - command injection risk"),
        (r'os\.system\s*\(', "os.system() usage", "Use subprocess module instead of os.system()"),
        (r'pickle\.loads?\s*\(', "pickle deserialization", "Unpickling untrusted data is dangerous - use json instead"),
        (r'yaml\.load\s*\([^)]*\)', "yaml.load() without Loader", "Use yaml.safe_load() instead"),
        (r'\.format\s*\([^)]*\)', "str.format() with user input", "Be cautious with .format() and f-strings with untrusted input"),
        (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded password", "Never hardcode passwords in source code"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "hardcoded secret", "Never hardcode secrets in source code"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded API key", "Never hardcode API keys in source code"),
        (r'token\s*=\s*["\'][^"\']+["\']', "hardcoded token", "Never hardcode tokens in source code"),
    ]

    # Performance anti-patterns
    PERF_PATTERNS = [
        (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', "range(len()) anti-pattern", "Use enumerate() instead of range(len())"),
        (r'\+\s*\n?\s*["\']', "string concatenation in loop", "Use list.join() or f-strings for string building"),
        (r'list\s*\(\s*\)', "list() for empty list", "Use [] instead of list() for empty lists"),
        (r'dict\s*\(\s*\)', "dict() for empty dict", "Use {} instead of dict() for empty dicts"),
        (r'\[\s*\]\s*\*\s*\d+', "list multiplication", "Be careful with list multiplication - creates references, not copies"),
    ]

    # Code style patterns
    STYLE_PATTERNS = [
        (r'^\s*print\s+["\']', "Python 2 print statement", "Use print() function for Python 3 compatibility"),
        (r'except\s*:', "bare except", "Use 'except Exception:' instead of bare 'except:'"),
        (r'\bTODO\b', "TODO comment", "Address TODO items before merging"),
        (r'\bFIXME\b', "FIXME comment", "Address FIXME items before merging"),
        (r'\bXXX\b', "XXX comment", "Address XXX items before merging"),
    ]

    def __init__(self):
        self.issues: List[Issue] = []
        self.metrics = CodeMetrics()

    def analyze_file(self, filepath: str, content: str = None) -> Dict[str, Any]:
        """分析单个文件"""
        if content is None:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return {"error": str(e)}

        self.issues = []
        self.metrics = CodeMetrics()

        lines = content.split('\n')
        self._calculate_metrics(lines)
        self._check_line_length(lines)
        self._check_security_issues(lines)
        self._check_performance_issues(lines)
        self._check_style_issues(lines)
        self._check_docstring_coverage(content)
        self._check_import_order(lines)
        self._check_naming_conventions(content)

        # Try AST analysis for Python files
        if filepath.endswith('.py'):
            self._ast_analysis(content)

        return {
            "filepath": filepath,
            "metrics": {
                "lines_of_code": self.metrics.lines_of_code,
                "logical_lines": self.metrics.logical_lines,
                "comment_lines": self.metrics.comment_lines,
                "blank_lines": self.metrics.blank_lines,
                "max_line_length": self.metrics.max_line_length,
                "avg_line_length": round(self.metrics.avg_line_length, 1),
                "function_count": self.metrics.function_count,
                "class_count": self.metrics.class_count,
                "complexity_score": self.metrics.complexity_score,
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "issue_summary": self._summarize_issues(),
            "quality_score": self._calculate_quality_score()
        }

    def _calculate_metrics(self, lines: List[str]):
        """计算基础代码度量"""
        self.metrics.lines_of_code = len(lines)
        total_length = 0
        in_multiline_string = False

        for line in lines:
            stripped = line.strip()
            total_length += len(line)

            if len(line) > self.metrics.max_line_length:
                self.metrics.max_line_length = len(line)

            if not stripped:
                self.metrics.blank_lines += 1
                continue

            if stripped.startswith('#'):
                self.metrics.comment_lines += 1
                continue

            # Handle multi-line strings
            if '"""' in stripped or "'''" in stripped:
                quote_count = stripped.count('"""') + stripped.count("'''")
                if quote_count % 2 == 1:
                    in_multiline_string = not in_multiline_string
                if in_multiline_string or stripped.startswith(('"""', "'''")):
                    self.metrics.comment_lines += 1
                    continue

            if in_multiline_string:
                self.metrics.comment_lines += 1
                continue

            # Count inline comments
            if '#' in stripped:
                self.metrics.comment_lines += 1

            self.metrics.logical_lines += 1

        if self.metrics.lines_of_code > 0:
            self.metrics.avg_line_length = total_length / self.metrics.lines_of_code

    def _check_line_length(self, lines: List[str]):
        """检查行长度"""
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(Issue(
                    i, Issue.SEVERITY_LOW, "Style",
                    f"Line too long ({len(line)} > 120 chars)",
                    "Break line into multiple lines or use parentheses for implicit continuation"
                ))
            elif len(line) > 88:
                self.issues.append(Issue(
                    i, Issue.SEVERITY_INFO, "Style",
                    f"Line exceeds 88 chars ({len(line)} chars)",
                    "Consider breaking for better readability (PEP 8 recommends 79, Black uses 88)"
                ))

    def _check_security_issues(self, lines: List[str]):
        """检查安全问题"""
        for i, line in enumerate(lines, 1):
            for pattern, name, suggestion in self.SECURITY_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        i, Issue.SEVERITY_CRITICAL, "Security",
                        f"Potential security issue: {name}",
                        suggestion
                    ))

    def _check_performance_issues(self, lines: List[str]):
        """检查性能问题"""
        for i, line in enumerate(lines, 1):
            for pattern, name, suggestion in self.PERF_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(Issue(
                        i, Issue.SEVERITY_MEDIUM, "Performance",
                        f"Performance anti-pattern: {name}",
                        suggestion
                    ))

    def _check_style_issues(self, lines: List[str]):
        """检查代码风格问题"""
        for i, line in enumerate(lines, 1):
            for pattern, name, suggestion in self.STYLE_PATTERNS:
                if re.search(pattern, line):
                    severity = Issue.SEVERITY_LOW
                    if "TODO" in name or "FIXME" in name or "XXX" in name:
                        severity = Issue.SEVERITY_INFO
                    elif "bare except" in name:
                        severity = Issue.SEVERITY_HIGH
                    self.issues.append(Issue(
                        i, severity, "Style",
                        f"Style issue: {name}",
                        suggestion
                    ))

    def _check_docstring_coverage(self, content: str):
        """检查文档字符串覆盖率"""
        try:
            tree = ast.parse(content)
            functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            self.metrics.function_count = len(functions)
            self.metrics.class_count = len(classes)

            undocumented = []
            for func in functions:
                if not ast.get_docstring(func):
                    undocumented.append(func.lineno)

            for cls in classes:
                if not ast.get_docstring(cls):
                    undocumented.append(cls.lineno)

            if undocumented:
                self.issues.append(Issue(
                    undocumented[0], Issue.SEVERITY_LOW, "Documentation",
                    f"Missing docstrings in {len(undocumented)} functions/classes",
                    "Add docstrings to improve code maintainability"
                ))
        except SyntaxError:
            pass

    def _check_import_order(self, lines: List[str]):
        """检查导入顺序"""
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_lines.append((i, stripped))

        if len(import_lines) > 1:
            # Check if imports are grouped (stdlib, third-party, local)
            stdlib_modules = {'os', 'sys', 're', 'json', 'time', 'datetime', 'collections', 'itertools', 'functools', 'pathlib', 'typing', 'argparse', 'subprocess', 'hashlib', 'base64', 'urllib', 'http', 'socket', 'threading', 'multiprocessing', 'unittest', 'inspect', 'ast', 'copy', 'math', 'random', 'string', 'csv', 'io', 'warnings', 'traceback', 'types', 'enum', 'dataclasses'}

            groups = []
            for _, imp in import_lines:
                module = imp.split()[1].split('.')[0]
                if module in stdlib_modules:
                    groups.append('stdlib')
                else:
                    groups.append('third_party')

            # Simple check: stdlib should come before third-party
            seen_third_party = False
            for i, group in enumerate(groups):
                if group == 'third_party':
                    seen_third_party = True
                elif group == 'stdlib' and seen_third_party:
                    line_num = import_lines[i][0]
                    self.issues.append(Issue(
                        line_num, Issue.SEVERITY_INFO, "Style",
                        "Import order violation: stdlib import after third-party",
                        "Group imports: stdlib first, then third-party, then local"
                    ))
                    break

    def _check_naming_conventions(self, content: str):
        """检查命名规范"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('__') and node.name.endswith('__'):
                        continue  # Dunder methods are OK
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        self.issues.append(Issue(
                            node.lineno, Issue.SEVERITY_LOW, "Style",
                            f"Function name '{node.name}' doesn't follow snake_case",
                            "Use snake_case for function names (PEP 8)"
                        ))
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        self.issues.append(Issue(
                            node.lineno, Issue.SEVERITY_LOW, "Style",
                            f"Class name '{node.name}' doesn't follow PascalCase",
                            "Use PascalCase for class names (PEP 8)"
                        ))
                elif isinstance(node, ast.NameConstant) and node.value is True:
                    # Check for boolean traps
                    pass
        except SyntaxError:
            pass

    def _ast_analysis(self, content: str):
        """AST深度分析"""
        try:
            tree = ast.parse(content)
            complexity = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                   ast.With, ast.Assert, ast.comprehension)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            self.metrics.complexity_score = complexity

            # Flag high complexity
            if complexity > 20:
                self.issues.append(Issue(
                    1, Issue.SEVERITY_MEDIUM, "Complexity",
                    f"High cyclomatic complexity: {complexity}",
                    "Consider refactoring into smaller functions"
                ))

            # Check for mutable default arguments
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults + node.args.kw_defaults:
                        if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            self.issues.append(Issue(
                                node.lineno, Issue.SEVERITY_HIGH, "Bug Risk",
                                f"Mutable default argument in function '{node.name}'",
                                "Use None as default and initialize mutable object inside function"
                            ))

        except SyntaxError:
            pass

    def _summarize_issues(self) -> Dict[str, int]:
        """汇总问题统计"""
        summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for issue in self.issues:
            summary[issue.severity] = summary.get(issue.severity, 0) + 1
        return summary

    def _calculate_quality_score(self) -> int:
        """计算代码质量分数 (0-100)"""
        score = 100
        summary = self._summarize_issues()
        score -= summary["CRITICAL"] * 20
        score -= summary["HIGH"] * 10
        score -= summary["MEDIUM"] * 5
        score -= summary["LOW"] * 2
        score -= summary["INFO"] * 1

        # Complexity penalty
        if self.metrics.complexity_score > 15:
            score -= (self.metrics.complexity_score - 15) * 2

        # Documentation bonus/penalty
        if self.metrics.function_count > 0:
            doc_ratio = 1.0 - (summary.get("LOW", 0) / max(self.metrics.function_count, 1))
            score = int(score * (0.5 + 0.5 * doc_ratio))

        return max(0, min(100, score))

    def analyze_directory(self, directory: str, extensions: Tuple[str, ...] = ('.py', '.js', '.ts', '.java', '.go', '.rs')) -> List[Dict[str, Any]]:
        """分析整个目录"""
        results = []
        for root, _, files in os.walk(directory):
            # Skip common non-source directories
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', 'venv', '.venv', 'dist', 'build', '.egg-info']):
                continue
            for file in files:
                if file.endswith(extensions):
                    filepath = os.path.join(root, file)
                    result = self.analyze_file(filepath)
                    if "error" not in result:
                        results.append(result)
        return results
