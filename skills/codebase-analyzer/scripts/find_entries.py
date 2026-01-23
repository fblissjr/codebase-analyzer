#!/usr/bin/env python3
"""Discover entry points in a Python codebase.

Usage:
    uv run scripts/find_entries.py .
    uv run scripts/find_entries.py . --types main,click,fastapi
    uv run scripts/find_entries.py /path/to/project --json
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# Add parent directory to path for internal imports
sys.path.insert(0, str(Path(__file__).parent))

from internal.output import Timer, emit, error_response, success_response


# Entry point detection patterns
ENTRY_TYPES = {
    "main_block": "if __name__ == '__main__'",
    "click_command": "@click.command or @click.group",
    "fastapi": "FastAPI() app instance",
    "flask": "Flask() app instance",
    "typer": "typer.Typer() app",
    "argparse": "argparse.ArgumentParser usage",
    "setuptools_entry": "entry_points in setup.py/pyproject.toml",
}


def find_main_block(tree: ast.AST) -> int | None:
    """Find 'if __name__ == "__main__"' block."""
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            # Check for: if __name__ == "__main__"
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                if isinstance(left, ast.Name) and left.id == "__name__":
                    for comparator in node.test.comparators:
                        if isinstance(comparator, ast.Constant):
                            if comparator.value == "__main__":
                                return node.lineno
    return None


def find_click_commands(tree: ast.AST) -> list[int]:
    """Find @click.command() or @click.group() decorators."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ("command", "group"):
                            if isinstance(decorator.func.value, ast.Name):
                                if decorator.func.value.id == "click":
                                    lines.append(node.lineno)
                elif isinstance(decorator, ast.Attribute):
                    if decorator.attr in ("command", "group"):
                        if isinstance(decorator.value, ast.Name):
                            if decorator.value.id == "click":
                                lines.append(node.lineno)
    return lines


def find_fastapi_app(tree: ast.AST) -> int | None:
    """Find FastAPI() app instantiation."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "FastAPI":
                    return node.lineno
                if isinstance(func, ast.Attribute) and func.attr == "FastAPI":
                    return node.lineno
    return None


def find_flask_app(tree: ast.AST) -> int | None:
    """Find Flask() app instantiation."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "Flask":
                    return node.lineno
                if isinstance(func, ast.Attribute) and func.attr == "Flask":
                    return node.lineno
    return None


def find_typer_app(tree: ast.AST) -> int | None:
    """Find typer.Typer() app instantiation."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute):
                    if func.attr == "Typer":
                        return node.lineno
    return None


def find_argparse_usage(tree: ast.AST) -> int | None:
    """Find argparse.ArgumentParser() usage."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr == "ArgumentParser":
                    return node.lineno
            if isinstance(func, ast.Name):
                if func.id == "ArgumentParser":
                    return node.lineno
    return None


def analyze_file(filepath: Path, types_filter: set[str] | None = None) -> list[dict]:
    """Analyze a single file for entry points.

    Args:
        filepath: Path to the Python file
        types_filter: Set of entry types to look for (None = all)

    Returns:
        List of entry point dictionaries
    """
    entries = []

    try:
        content = filepath.read_text()
        tree = ast.parse(content)
    except (SyntaxError, FileNotFoundError, PermissionError, UnicodeDecodeError):
        return []

    # Check each entry type
    if types_filter is None or "main_block" in types_filter:
        line = find_main_block(tree)
        if line:
            entries.append({
                "file": str(filepath),
                "type": "main_block",
                "line": line,
            })

    if types_filter is None or "click_command" in types_filter:
        lines = find_click_commands(tree)
        for line in lines:
            entries.append({
                "file": str(filepath),
                "type": "click_command",
                "line": line,
            })

    if types_filter is None or "fastapi" in types_filter:
        line = find_fastapi_app(tree)
        if line:
            entries.append({
                "file": str(filepath),
                "type": "fastapi",
                "line": line,
            })

    if types_filter is None or "flask" in types_filter:
        line = find_flask_app(tree)
        if line:
            entries.append({
                "file": str(filepath),
                "type": "flask",
                "line": line,
            })

    if types_filter is None or "typer" in types_filter:
        line = find_typer_app(tree)
        if line:
            entries.append({
                "file": str(filepath),
                "type": "typer",
                "line": line,
            })

    if types_filter is None or "argparse" in types_filter:
        line = find_argparse_usage(tree)
        if line:
            entries.append({
                "file": str(filepath),
                "type": "argparse",
                "line": line,
            })

    return entries


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in directory, excluding common non-source directories."""
    excluded_dirs = {
        ".venv", "venv", ".git", "__pycache__", "node_modules",
        ".tox", ".pytest_cache", ".mypy_cache", "dist", "build",
        ".eggs", "*.egg-info",
    }

    python_files = []
    for filepath in directory.rglob("*.py"):
        # Skip excluded directories
        parts = filepath.parts
        if any(excluded in parts for excluded in excluded_dirs):
            continue
        if any(part.endswith(".egg-info") for part in parts):
            continue
        python_files.append(filepath)

    return sorted(python_files)


def run_find_entries(directory: str, types: str | None = None) -> dict:
    """Find entry points in a directory.

    Args:
        directory: Path to search
        types: Comma-separated list of entry types to find

    Returns:
        Structured result dictionary
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists():
        return error_response(
            f"Directory not found: {directory}",
            error_type="directory_not_found",
            details={"path": str(dir_path)},
        )

    if not dir_path.is_dir():
        return error_response(
            f"Path is not a directory: {directory}",
            error_type="not_a_directory",
            details={"path": str(dir_path)},
        )

    # Parse types filter
    types_filter = None
    if types:
        types_filter = set(t.strip() for t in types.split(","))
        invalid_types = types_filter - set(ENTRY_TYPES.keys())
        if invalid_types:
            return error_response(
                f"Invalid entry types: {', '.join(invalid_types)}",
                error_type="invalid_types",
                details={
                    "invalid": list(invalid_types),
                    "valid": list(ENTRY_TYPES.keys()),
                },
            )

    # Find all Python files
    python_files = find_python_files(dir_path)

    # Analyze each file
    all_entries = []
    for filepath in python_files:
        entries = analyze_file(filepath, types_filter)
        all_entries.extend(entries)

    # Make paths relative to the search directory
    for entry in all_entries:
        try:
            entry["file"] = str(Path(entry["file"]).relative_to(dir_path))
        except ValueError:
            pass  # Keep absolute if not relative

    return {
        "entry_points": all_entries,
        "files_scanned": len(python_files),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Discover entry points in a Python codebase"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search (default: current directory)",
    )
    parser.add_argument(
        "--types",
        help=f"Comma-separated entry types: {', '.join(ENTRY_TYPES.keys())}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Output as JSON (default)",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Also write output to internal/log/",
    )

    args = parser.parse_args()

    with Timer() as timer:
        result = run_find_entries(args.directory, types=args.types)

    if result.get("status") == "error":
        emit(result, log=args.log, log_name="find_entries")
        sys.exit(1)

    response = success_response(result, duration_ms=timer.elapsed_ms)
    emit(response, log=args.log, log_name="find_entries")


if __name__ == "__main__":
    main()
