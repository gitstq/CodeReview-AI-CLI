"""
Tests for the AIReviewEngine module
"""

import unittest
from codereview_ai.reviewer import AIReviewEngine


class TestAIReviewEngine(unittest.TestCase):
    """Test cases for AIReviewEngine"""

    def setUp(self):
        self.engine = AIReviewEngine()

    def test_generate_review(self):
        """Test generating a review"""
        analysis_result = {
            "filepath": "test.py",
            "metrics": {
                "lines_of_code": 100,
                "function_count": 5,
                "class_count": 2,
                "complexity_score": 10
            },
            "issues": [
                {"line": 10, "severity": "HIGH", "category": "Security", "message": "Test issue", "suggestion": "Fix it"}
            ],
            "quality_score": 75,
            "issue_summary": {"HIGH": 1}
        }

        review = self.engine.generate_review(analysis_result)
        self.assertIn("quality_score", review)
        self.assertIn("assessment", review)
        self.assertIn("review_comments", review)
        self.assertEqual(review["quality_score"], 75)

    def test_quality_assessment_excellent(self):
        """Test quality assessment for excellent score"""
        assessment = self.engine._get_quality_assessment(95)
        self.assertIn("Excellent", assessment)

    def test_quality_assessment_poor(self):
        """Test quality assessment for poor score"""
        assessment = self.engine._get_quality_assessment(30)
        self.assertIn("Critical", assessment)

    def test_generate_pr_summary(self):
        """Test generating PR summary"""
        analyses = [
            {"filepath": "a.py", "quality_score": 80, "issue_count": 2, "severity_breakdown": {"LOW": 2}},
            {"filepath": "b.py", "quality_score": 90, "issue_count": 0, "severity_breakdown": {}}
        ]

        summary = self.engine.generate_pr_summary(analyses)
        self.assertEqual(summary["total_files"], 2)
        self.assertEqual(summary["total_issues"], 2)
        self.assertEqual(summary["average_quality_score"], 85.0)

    def test_inline_comments(self):
        """Test generating inline comments"""
        analysis = {
            "issues": [
                {"line": 10, "severity": "CRITICAL", "category": "Security", "message": "Critical issue", "suggestion": "Fix immediately"},
                {"line": 20, "severity": "LOW", "category": "Style", "message": "Style issue", "suggestion": "Format code"}
            ]
        }

        comments = self.engine.generate_inline_comments(analysis)
        self.assertEqual(len(comments), 1)  # Only CRITICAL and HIGH
        self.assertEqual(comments[0]["line"], 10)


if __name__ == "__main__":
    unittest.main()
