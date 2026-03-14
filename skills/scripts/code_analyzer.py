#!/usr/bin/env python3
"""
Code quality analyzer script.

This script demonstrates best practices for analyzing Python code quality.
It can be used as a template for building code review tools.
"""

import ast
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CodeIssue:
    """Represents a code quality issue."""

    file: Path
    line: int
    severity: Severity
    message: str
    rule: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line} [{self.severity.value}] {self.rule}: {self.message}"


@dataclass
class AnalysisResult:
    """Results from code analysis."""

    files_analyzed: int = 0
    issues: list[CodeIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)

    def add_issue(self, issue: CodeIssue) -> None:
        """Add an issue to the results."""
        self.issues.append(issue)

    def print_summary(self) -> None:
        """Print analysis summary."""
        print(f"\nAnalyzed {self.files_analyzed} files")
        print(f"Found {len(self.issues)} issues:")
        print(f"  - Errors: {self.error_count}")
        print(f"  - Warnings: {self.warning_count}")


class CodeAnalyzer:
    """Analyzes Python code for quality issues."""

    MAX_FUNCTION_LENGTH = 50
    MAX_FUNCTION_PARAMS = 5

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.result = AnalysisResult()

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        if not self._is_python_file(file_path):
            return

        try:
            with open(file_path) as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self._check_file(tree, file_path)
            self.result.files_analyzed += 1

        except SyntaxError as e:
            self._add_issue(
                file_path,
                e.lineno or 0,
                Severity.ERROR,
                f"Syntax error: {e.msg}",
                "E001",
            )

    def analyze_directory(self, directory: Path) -> AnalysisResult:
        """Recursively analyze all Python files in directory."""
        for file_path in directory.rglob("*.py"):
            self.analyze_file(file_path)

        return self.result

    def _check_file(self, tree: ast.AST, file_path: Path) -> None:
        """Check various code quality metrics."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._check_class(node, file_path)

    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """Check function-level issues."""
        # Check function length
        if hasattr(node, "end_lineno") and node.end_lineno:
            length = node.end_lineno - node.lineno
            if length > self.MAX_FUNCTION_LENGTH:
                self._add_issue(
                    file_path,
                    node.lineno,
                    Severity.WARNING,
                    f"Function '{node.name}' is {length} lines (max {self.MAX_FUNCTION_LENGTH})",
                    "W001",
                )

        # Check number of parameters
        param_count = len(node.args.args)
        if param_count > self.MAX_FUNCTION_PARAMS:
            self._add_issue(
                file_path,
                node.lineno,
                Severity.WARNING,
                f"Function '{node.name}' has {param_count} parameters (max {self.MAX_FUNCTION_PARAMS})",
                "W002",
            )

        # Check for missing docstring
        if not ast.get_docstring(node) and not node.name.startswith("_"):
            severity = Severity.ERROR if self.strict else Severity.WARNING
            self._add_issue(
                file_path,
                node.lineno,
                severity,
                f"Function '{node.name}' missing docstring",
                "W003",
            )

    def _check_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check class-level issues."""
        # Check for missing docstring
        if not ast.get_docstring(node) and not node.name.startswith("_"):
            severity = Severity.ERROR if self.strict else Severity.WARNING
            self._add_issue(
                file_path,
                node.lineno,
                severity,
                f"Class '{node.name}' missing docstring",
                "W004",
            )

    def _add_issue(
        self, file_path: Path, line: int, severity: Severity, message: str, rule: str
    ) -> None:
        """Add an issue to results."""
        issue = CodeIssue(
            file=file_path, line=line, severity=severity, message=message, rule=rule
        )
        self.result.add_issue(issue)

    @staticmethod
    def _is_python_file(file_path: Path) -> bool:
        """Check if file is a Python file."""
        return file_path.suffix == ".py" and file_path.name != "__pycache__"


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python code_analyzer.py <path> [--strict]")
        return 1

    path = Path(sys.argv[1])
    strict = "--strict" in sys.argv

    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        return 1

    analyzer = CodeAnalyzer(strict=strict)

    if path.is_file():
        analyzer.analyze_file(path)
    else:
        analyzer.analyze_directory(path)

    # Print issues
    for issue in analyzer.result.issues:
        print(issue)

    # Print summary
    analyzer.result.print_summary()

    # Return non-zero if errors found
    return 1 if analyzer.result.error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
