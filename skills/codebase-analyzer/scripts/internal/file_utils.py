"""Shared file discovery utilities."""

from __future__ import annotations

from pathlib import Path

EXCLUDED_DIRS = {
    ".venv", "venv", ".git", "__pycache__", "node_modules",
    ".tox", ".pytest_cache", ".mypy_cache", "dist", "build",
    ".eggs",
}


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in directory, excluding common non-source directories.

    Args:
        directory: Root directory to search

    Returns:
        Sorted list of Python file paths
    """
    python_files = []
    for filepath in directory.rglob("*.py"):
        parts = filepath.parts
        if any(excluded in parts for excluded in EXCLUDED_DIRS):
            continue
        if any(part.endswith(".egg-info") for part in parts):
            continue
        python_files.append(filepath)

    return sorted(python_files)
