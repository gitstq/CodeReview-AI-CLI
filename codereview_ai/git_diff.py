"""
Git Diff Analyzer Module
Git差异分析模块

Analyzes Git diffs to provide intelligent code review insights:
- Changed files summary
- Addition/deletion statistics
- Potential issue detection in changes
- Change impact assessment
"""

import re
import subprocess
import os
from typing import Dict, List, Tuple, Any
from .analyzer import CodeAnalyzer, Issue


class GitDiffAnalyzer:
    """Git差异分析器"""

    def __init__(self):
        self.analyzer = CodeAnalyzer()

    def get_changed_files(self, target: str = "HEAD", base: str = None) -> List[Dict[str, Any]]:
        """获取变更文件列表"""
        try:
            if base:
                cmd = ['git', 'diff', '--name-status', f'{base}..{target}']
            else:
                cmd = ['git', 'diff', '--name-status', target]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                return [{"error": result.stderr}]

            files = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    filepath = parts[1]
                    files.append({
                        "status": status,
                        "filepath": filepath,
                        "is_new": status.startswith('A'),
                        "is_deleted": status.startswith('D'),
                        "is_modified": status.startswith('M')
                    })
            return files
        except Exception as e:
            return [{"error": str(e)}]

    def get_diff_stats(self, target: str = "HEAD", base: str = None) -> Dict[str, Any]:
        """获取差异统计信息"""
        try:
            if base:
                cmd = ['git', 'diff', '--stat', f'{base}..{target}']
            else:
                cmd = ['git', 'diff', '--stat', target]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                return {"error": result.stderr}

            lines = result.stdout.strip().split('\n')
            if not lines:
                return {"files_changed": 0, "insertions": 0, "deletions": 0}

            # Parse the summary line (last line)
            summary = lines[-1]
            files_changed = 0
            insertions = 0
            deletions = 0

            match = re.search(r'(\d+)\s+file', summary)
            if match:
                files_changed = int(match.group(1))

            match = re.search(r'(\d+)\s+insertion', summary)
            if match:
                insertions = int(match.group(1))

            match = re.search(r'(\d+)\s+deletion', summary)
            if match:
                deletions = int(match.group(1))

            return {
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
                "total_changes": insertions + deletions,
                "change_ratio": round(insertions / max(deletions, 1), 2) if deletions > 0 else insertions
            }
        except Exception as e:
            return {"error": str(e)}

    def get_file_diff(self, filepath: str, target: str = "HEAD", base: str = None) -> Dict[str, Any]:
        """获取单个文件的差异内容"""
        try:
            if base:
                cmd = ['git', 'diff', f'{base}..{target}', '--', filepath]
            else:
                cmd = ['git', 'diff', target, '--', filepath]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                return {"error": result.stderr}

            diff_content = result.stdout
            hunks = self._parse_diff_hunks(diff_content)

            # Analyze the new version of the file
            try:
                show_cmd = ['git', 'show', f'{target}:{filepath}']
                show_result = subprocess.run(show_cmd, capture_output=True, text=True, cwd=os.getcwd())
                file_content = show_result.stdout if show_result.returncode == 0 else ""
            except:
                file_content = ""

            # Run code analysis on changed content
            issues = []
            if file_content and filepath.endswith('.py'):
                analysis = self.analyzer.analyze_file(filepath, file_content)
                issues = analysis.get("issues", [])

            return {
                "filepath": filepath,
                "diff": diff_content,
                "hunks": hunks,
                "issues_in_changes": issues[:5],  # Top 5 issues
                "lines_added": diff_content.count('\n+') - diff_content.count('\n+++'),
                "lines_removed": diff_content.count('\n-') - diff_content.count('\n---')
            }
        except Exception as e:
            return {"error": str(e)}

    def _parse_diff_hunks(self, diff_content: str) -> List[Dict[str, Any]]:
        """解析diff的hunk信息"""
        hunks = []
        hunk_pattern = r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@'

        current_hunk = None
        for line in diff_content.split('\n'):
            match = re.match(hunk_pattern, line)
            if match:
                if current_hunk:
                    hunks.append(current_hunk)
                current_hunk = {
                    "old_start": int(match.group(1)),
                    "old_count": int(match.group(2)) if match.group(2) else 1,
                    "new_start": int(match.group(3)),
                    "new_count": int(match.group(4)) if match.group(4) else 1,
                    "lines": []
                }
            elif current_hunk is not None:
                current_hunk["lines"].append(line)

        if current_hunk:
            hunks.append(current_hunk)

        return hunks

    def analyze_commit(self, commit_hash: str = "HEAD") -> Dict[str, Any]:
        """分析单个提交"""
        try:
            # Get commit info
            log_cmd = ['git', 'log', '-1', '--format=%H|%an|%ae|%ad|%s', commit_hash]
            log_result = subprocess.run(log_cmd, capture_output=True, text=True, cwd=os.getcwd())

            if log_result.returncode != 0:
                return {"error": log_result.stderr}

            commit_info = log_result.stdout.strip().split('|')
            if len(commit_info) < 5:
                return {"error": "Invalid commit format"}

            # Get changed files
            files = self.get_changed_files(commit_hash, f"{commit_hash}~1")
            stats = self.get_diff_stats(commit_hash, f"{commit_hash}~1")

            # Analyze each changed file
            file_analyses = []
            for file_info in files:
                if "error" in file_info:
                    continue
                if file_info.get("is_deleted"):
                    continue
                diff_analysis = self.get_file_diff(file_info["filepath"], commit_hash, f"{commit_hash}~1")
                if "error" not in diff_analysis:
                    file_analyses.append(diff_analysis)

            return {
                "commit_hash": commit_info[0],
                "author": commit_info[1],
                "email": commit_info[2],
                "date": commit_info[3],
                "message": commit_info[4],
                "files_changed": files,
                "stats": stats,
                "file_analyses": file_analyses
            }
        except Exception as e:
            return {"error": str(e)}

    def get_branch_comparison(self, branch1: str, branch2: str = "HEAD") -> Dict[str, Any]:
        """比较两个分支"""
        try:
            files = self.get_changed_files(branch2, branch1)
            stats = self.get_diff_stats(branch2, branch1)

            return {
                "base_branch": branch1,
                "compare_branch": branch2,
                "files_changed": len([f for f in files if "error" not in f]),
                "stats": stats,
                "changed_files": files
            }
        except Exception as e:
            return {"error": str(e)}

    def detect_risky_changes(self, target: str = "HEAD", base: str = None) -> List[Dict[str, Any]]:
        """检测高风险变更"""
        risky_patterns = [
            (r'\bDROP\s+TABLE\b', "Database schema change - DROP TABLE", "CRITICAL"),
            (r'\bDELETE\s+FROM\b', "Database DELETE operation", "HIGH"),
            (r'\bALTER\s+TABLE\s+.*\bDROP\b', "Database column removal", "HIGH"),
            (r'rm\s+-rf\s+/', "Dangerous rm -rf operation", "CRITICAL"),
            (r'sudo\s+', "Sudo command usage", "MEDIUM"),
            (r'chmod\s+777', "Overly permissive file permissions", "MEDIUM"),
            (r'password\s*=\s*', "Password in code", "CRITICAL"),
            (r'secret\s*=\s*', "Secret in code", "CRITICAL"),
            (r'api_key\s*=\s*', "API key in code", "CRITICAL"),
        ]

        risks = []
        try:
            if base:
                cmd = ['git', 'diff', f'{base}..{target}']
            else:
                cmd = ['git', 'diff', target]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            diff_content = result.stdout

            for pattern, description, severity in risky_patterns:
                matches = re.finditer(pattern, diff_content, re.IGNORECASE)
                for match in matches:
                    # Find line number in diff
                    line_num = diff_content[:match.start()].count('\n') + 1
                    risks.append({
                        "line": line_num,
                        "severity": severity,
                        "description": description,
                        "pattern": pattern,
                        "context": diff_content[max(0, match.start()-50):match.end()+50]
                    })

            return risks
        except Exception as e:
            return [{"error": str(e)}]
