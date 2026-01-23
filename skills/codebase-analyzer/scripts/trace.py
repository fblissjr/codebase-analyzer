#!/usr/bin/env python3
"""Import tracing with structured JSON output.

Usage:
    uv run scripts/trace.py main.py              # Smart filtered
    uv run scripts/trace.py main.py --all        # Full trace
    uv run scripts/trace.py main.py --json       # JSON to stdout (default)
    uv run scripts/trace.py main.py --log        # Also write to internal/log/
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for internal imports
sys.path.insert(0, str(Path(__file__).parent))

from internal.output import Timer, emit, error_response, success_response


def parse_llmfiles_output(output: str, entry_path: Path) -> dict:
    """Parse llmfiles output to extract file list and build dependency graph.

    Args:
        output: Raw llmfiles output
        entry_path: The entry file path for reference

    Returns:
        Dict with files list and graph structure
    """
    files = []
    graph = defaultdict(list)
    external = set()

    # Extract file paths from llmfiles output
    # llmfiles outputs files in a structured format with file markers
    for line in output.split("\n"):
        # Match file path markers like "# File: path/to/file.py" or "--- path/to/file.py ---"
        file_match = re.match(r"^(?:#\s*File:\s*|---\s*)(.+\.py)(?:\s*---)?$", line)
        if file_match:
            filepath = file_match.group(1).strip()
            if filepath and filepath not in files:
                files.append(filepath)

    # If no files found from markers, try to find them from content structure
    if not files:
        # Look for file separators in llmfiles output format
        sections = re.split(r"\n={3,}\n|\n-{3,}\n", output)
        for section in sections:
            # Try to extract filename from first line of section
            first_line = section.strip().split("\n")[0] if section.strip() else ""
            if first_line.endswith(".py"):
                filepath = first_line.strip()
                if filepath and filepath not in files:
                    files.append(filepath)

    # Build basic graph by analyzing imports in each file
    # This is a simplified approach - for full accuracy, use llmfiles --deps output parsing
    entry_str = str(entry_path)
    if entry_str not in files and files:
        # Entry should be first
        files.insert(0, entry_str)

    return {
        "files": files,
        "graph": dict(graph),
        "external": sorted(external),
    }


def analyze_imports_from_file(filepath: Path) -> tuple[list[str], list[str]]:
    """Analyze imports from a Python file using AST.

    Args:
        filepath: Path to the Python file

    Returns:
        Tuple of (local_imports, external_imports)
    """
    local_imports = []
    external_imports = []

    try:
        content = filepath.read_text()
        tree = ast.parse(content)
    except (SyntaxError, FileNotFoundError, PermissionError):
        return [], []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                external_imports.append(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level > 0:  # Relative import
                    local_imports.append(node.module)
                else:
                    # Could be local or external
                    name = node.module.split(".")[0]
                    external_imports.append(name)

    return local_imports, external_imports


def build_dependency_graph(
    entry_path: Path, files: list[str], base_dir: Path
) -> tuple[dict[str, list[str]], list[str], dict]:
    """Build a dependency graph from the traced files.

    Args:
        entry_path: The entry point file
        files: List of traced file paths
        base_dir: Base directory for resolving paths

    Returns:
        Tuple of (graph, external_deps, stats)
    """
    graph = defaultdict(list)
    all_external = set()
    max_depth = 0

    # Standard library modules to exclude
    stdlib = {
        "os", "sys", "re", "json", "ast", "time", "datetime", "pathlib",
        "collections", "functools", "itertools", "typing", "dataclasses",
        "logging", "argparse", "subprocess", "shutil", "tempfile", "io",
        "math", "random", "hashlib", "base64", "urllib", "http", "socket",
        "threading", "multiprocessing", "concurrent", "asyncio", "contextlib",
        "copy", "struct", "enum", "abc", "inspect", "importlib",
        "unittest", "doctest", "pdb", "traceback", "warnings", "weakref",
        "textwrap", "difflib", "string", "codecs", "unicodedata", "locale",
        "calendar", "heapq", "bisect", "array", "queue", "types", "operator",
        "fnmatch", "glob", "linecache", "tokenize", "keyword", "builtins",
    }

    for filepath_str in files:
        filepath = Path(filepath_str)
        if not filepath.is_absolute():
            filepath = base_dir / filepath

        if filepath.exists():
            local_imports, external_imports = analyze_imports_from_file(filepath)

            # Add external dependencies (excluding stdlib)
            for ext in external_imports:
                if ext not in stdlib:
                    all_external.add(ext)

            # Build graph edges
            for local_import in local_imports:
                # Try to resolve to a file in our traced set
                for other_file in files:
                    if local_import in other_file:
                        graph[filepath_str].append(other_file)

    # Calculate max depth using BFS
    entry_str = str(entry_path)
    if entry_str in files or any(entry_str.endswith(f) for f in files):
        visited = set()
        queue = [(entry_str, 0)]
        while queue:
            current, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            max_depth = max(max_depth, depth)
            for dep in graph.get(current, []):
                if dep not in visited:
                    queue.append((dep, depth + 1))

    # Detect circular dependencies
    circular_deps = []

    def find_cycles(node, path, visited):
        if node in path:
            cycle_start = path.index(node)
            circular_deps.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            find_cycles(neighbor, path.copy(), visited)

    for start_node in files[:10]:  # Limit cycle detection to first 10 files
        find_cycles(start_node, [], set())

    stats = {
        "total_files": len(files),
        "max_depth": max_depth,
        "circular_deps": circular_deps[:5],  # Limit reported cycles
    }

    return dict(graph), sorted(all_external), stats


def run_trace(entry: str, trace_all: bool = False) -> dict:
    """Run import trace on an entry file.

    Args:
        entry: Path to the entry file
        trace_all: If True, trace all imports without filtering

    Returns:
        Structured result dictionary
    """
    entry_path = Path(entry).resolve()

    if not entry_path.exists():
        return error_response(
            f"Entry file not found: {entry}",
            error_type="file_not_found",
            details={"path": str(entry_path)},
        )

    if not entry_path.suffix == ".py":
        return error_response(
            f"Entry file must be a Python file: {entry}",
            error_type="invalid_file_type",
            details={"path": str(entry_path), "suffix": entry_path.suffix},
        )

    # Build llmfiles arguments
    args = [str(entry_path), "--deps"]
    if trace_all:
        args.append("--all")

    # Run llmfiles via subprocess
    import subprocess

    try:
        result = subprocess.run(
            ["llmfiles"] + args,
            capture_output=True,
            text=True,
            cwd=entry_path.parent,
        )
    except FileNotFoundError:
        return error_response(
            "llmfiles not found. Install with: uv add llmfiles",
            error_type="dependency_missing",
        )

    if result.returncode != 0:
        return error_response(
            f"llmfiles failed: {result.stderr}",
            error_type="llmfiles_error",
            details={"returncode": result.returncode, "stderr": result.stderr},
        )

    # Parse output
    parsed = parse_llmfiles_output(result.stdout, entry_path)
    files = parsed["files"]

    # If no files found from parsing, at minimum include the entry
    if not files:
        files = [str(entry_path)]

    # Build dependency graph
    base_dir = entry_path.parent
    graph, external, stats = build_dependency_graph(entry_path, files, base_dir)

    return {
        "entry": str(entry_path),
        "files": files,
        "graph": graph,
        "external": external,
        "stats": stats,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Import tracing with structured JSON output"
    )
    parser.add_argument("entry", help="Entry file to trace imports from")
    parser.add_argument(
        "--all",
        action="store_true",
        dest="trace_all",
        help="Trace all imports without smart filtering",
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
        result = run_trace(args.entry, trace_all=args.trace_all)

    if result.get("status") == "error":
        emit(result, log=args.log, log_name="trace")
        sys.exit(1)

    response = success_response(result, duration_ms=timer.elapsed_ms)
    emit(response, log=args.log, log_name="trace")


if __name__ == "__main__":
    main()
