"""
Tests for the CodeAnalyzer module
"""

import unittest
import tempfile
import os
from codereview_ai.analyzer import CodeAnalyzer, Issue


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for CodeAnalyzer"""

    def setUp(self):
        self.analyzer = CodeAnalyzer()

    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file"""
        content = """
def hello():
    print("Hello, World!")

class MyClass:
    def method(self):
        return 42
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            filepath = f.name

        try:
            result = self.analyzer.analyze_file(filepath, content)
            self.assertIn("metrics", result)
            self.assertIn("issues", result)
            self.assertIn("quality_score", result)
            self.assertGreaterEqual(result["quality_score"], 0)
            self.assertLessEqual(result["quality_score"], 100)
        finally:
            os.unlink(filepath)

    def test_detect_security_issues(self):
        """Test detecting security issues"""
        content = """
import os

def dangerous():
    password = "secret123"
    eval("1 + 1")
    os.system("ls -la")
"""
        result = self.analyzer.analyze_file("test.py", content)
        issues = result.get("issues", [])

        security_issues = [i for i in issues if i.get("category") == "Security"]
        self.assertGreater(len(security_issues), 0)

    def test_detect_style_issues(self):
        """Test detecting style issues"""
        content = """
def very_long_function_name_that_exceeds_the_recommended_length_and_should_be_shortened():
    x = 1
    return x
"""
        result = self.analyzer.analyze_file("test.py", content)
        self.assertIn("metrics", result)

    def test_complexity_calculation(self):
        """Test complexity calculation"""
        content = """
def complex_function(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                return "small even"
            else:
                return "small odd"
        else:
            return "large"
    elif x == 0:
        return "zero"
    else:
        return "negative"
"""
        result = self.analyzer.analyze_file("test.py", content)
        metrics = result.get("metrics", {})
        self.assertGreater(metrics.get("complexity_score", 0), 0)

    def test_quality_score_range(self):
        """Test that quality score is within valid range"""
        content = "def foo():\n    pass\n"
        result = self.analyzer.analyze_file("test.py", content)
        score = result.get("quality_score", 0)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_empty_file(self):
        """Test analyzing empty file"""
        result = self.analyzer.analyze_file("test.py", "")
        self.assertIn("metrics", result)
        self.assertEqual(result["metrics"]["lines_of_code"], 1)


class TestIssue(unittest.TestCase):
    """Test cases for Issue class"""

    def test_issue_creation(self):
        """Test creating an Issue"""
        issue = Issue(10, "HIGH", "Security", "Test message", "Test suggestion")
        self.assertEqual(issue.line, 10)
        self.assertEqual(issue.severity, "HIGH")
        self.assertEqual(issue.category, "Security")
        self.assertEqual(issue.message, "Test message")
        self.assertEqual(issue.suggestion, "Test suggestion")

    def test_issue_to_dict(self):
        """Test converting Issue to dict"""
        issue = Issue(5, "MEDIUM", "Style", "Message", "Suggestion")
        d = issue.to_dict()
        self.assertEqual(d["line"], 5)
        self.assertEqual(d["severity"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()
