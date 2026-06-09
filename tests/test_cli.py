"""
Tests for the CLI module
"""

import unittest
import sys
from io import StringIO
from codereview_ai.cli import CLI, create_parser


class TestCLI(unittest.TestCase):
    """Test cases for CLI"""

    def setUp(self):
        self.cli = CLI()

    def test_parser_creation(self):
        """Test argument parser creation"""
        parser = create_parser()
        self.assertIsNotNone(parser)

    def test_analyze_command(self):
        """Test analyze command parsing"""
        parser = create_parser()
        args = parser.parse_args(["analyze", "test.py"])
        self.assertEqual(args.command, "analyze")
        self.assertEqual(args.path, "test.py")

    def test_diff_command(self):
        """Test diff command parsing"""
        parser = create_parser()
        args = parser.parse_args(["diff", "--base", "main"])
        self.assertEqual(args.command, "diff")
        self.assertEqual(args.base, "main")

    def test_report_command(self):
        """Test report command parsing"""
        parser = create_parser()
        args = parser.parse_args(["report", "-o", "report.json"])
        self.assertEqual(args.command, "report")
        self.assertEqual(args.output, "report.json")

    def test_help_output(self):
        """Test help output"""
        parser = create_parser()
        with self.assertRaises(SystemExit) as cm:
            parser.parse_args(["--help"])
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
