#!/usr/bin/env python3
"""Comprehensive codebase analysis combining tracing and structure.

Usage:
    uv run scripts/analyze.py src/
    uv run scripts/analyze.py --pattern "Config"
    uv run scripts/analyze.py --structure
    uv run scripts/analyze.py --parallel 4
"""

from __future__ import annotations

import argparse
import ast
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Add parent directory to path for internal imports
sys.path.insert(0, str(Path(__file__).parent))

from internal.file_utils import find_python_files
from internal.output import Timer, emit, error_response, success_response


def _get_docstring(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Extract docstring from a function or class node."""
    if not node.body:
        return None
    first = node.body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        # Return first line only (summary)
        return first.value.value.strip().split("\n")[0]
    return None


def _get_decorators(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extract decorator names from a class or function node."""
    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            decorators.append(ast.unparse(dec))
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                decorators.append(ast.unparse(dec.func))
    return decorators


def _get_base_classes(node: ast.ClassDef) -> list[str]:
    """Extract base class names from a class definition."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(ast.unparse(base))
    return bases


def _get_type_annotation(arg: ast.arg) -> str | None:
    """Extract type annotation string from a function argument."""
    if arg.annotation is None:
        return None
    return ast.unparse(arg.annotation)


def _get_return_annotation(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Extract return type annotation from a function definition."""
    if node.returns is None:
        return None
    return ast.unparse(node.returns)


def extract_structure(filepath: Path) -> dict | None:
    """Extract classes and functions from a Python file.

    Args:
        filepath: Path to the Python file

    Returns:
        Dictionary with classes and functions, or None on error
    """
    try:
        content = filepath.read_text()
        tree = ast.parse(content)
    except (SyntaxError, FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None

    classes = []
    functions = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = {"name": item.name}
                    method_decorators = _get_decorators(item)
                    if method_decorators:
                        method_info["decorators"] = method_decorators
                    methods.append(item.name)

            class_info: dict = {
                "name": node.name,
                "line": node.lineno,
                "methods": methods,
            }

            bases = _get_base_classes(node)
            if bases:
                class_info["bases"] = bases

            decorators = _get_decorators(node)
            if decorators:
                class_info["decorators"] = decorators

            docstring = _get_docstring(node)
            if docstring:
                class_info["docstring"] = docstring

            classes.append(class_info)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = [arg.arg for arg in node.args.args]

            func_info: dict = {
                "name": node.name,
                "line": node.lineno,
                "params": params,
            }

            # Add type annotations for params (only if at least one exists)
            type_hints = {}
            for arg in node.args.args:
                ann = _get_type_annotation(arg)
                if ann:
                    type_hints[arg.arg] = ann
            if type_hints:
                func_info["type_hints"] = type_hints

            ret = _get_return_annotation(node)
            if ret:
                func_info["returns"] = ret

            decorators = _get_decorators(node)
            if decorators:
                func_info["decorators"] = decorators

            docstring = _get_docstring(node)
            if docstring:
                func_info["docstring"] = docstring

            if isinstance(node, ast.AsyncFunctionDef):
                func_info["async"] = True

            functions.append(func_info)

    if not classes and not functions:
        return None

    return {
        "classes": classes,
        "functions": functions,
    }


def search_pattern(filepath: Path, pattern: str) -> list[dict]:
    """Search for a pattern in file content and structure.

    Args:
        filepath: Path to the Python file
        pattern: Pattern to search for (case-insensitive)

    Returns:
        List of matches with context
    """
    matches = []
    pattern_lower = pattern.lower()

    try:
        content = filepath.read_text()
        tree = ast.parse(content)
    except (SyntaxError, FileNotFoundError, PermissionError, UnicodeDecodeError):
        return []

    # Search in class names
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if pattern_lower in node.name.lower():
                matches.append({
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "file": str(filepath),
                })
        elif isinstance(node, ast.FunctionDef):
            if pattern_lower in node.name.lower():
                matches.append({
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "file": str(filepath),
                })

    return matches


def analyze_file_worker(args: tuple[Path, str | None, bool]) -> dict:
    """Worker function for parallel file analysis.

    Args:
        args: Tuple of (filepath, pattern, include_structure)

    Returns:
        Analysis result for the file
    """
    filepath, pattern, include_structure = args
    result: dict = {"file": str(filepath)}

    if pattern:
        matches = search_pattern(filepath, pattern)
        if matches:
            result["pattern_matches"] = matches

    if include_structure:
        structure = extract_structure(filepath)
        if structure:
            result["structure"] = structure

    return result


def run_analyze(
    directory: str,
    pattern: str | None = None,
    structure: bool = False,
    parallel: int = 1,
) -> dict:
    """Run comprehensive analysis on a directory.

    Args:
        directory: Path to analyze
        pattern: Optional pattern to search for
        structure: Whether to extract code structure
        parallel: Number of parallel workers

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

    # Find Python files
    python_files = find_python_files(dir_path)

    if not python_files:
        return error_response(
            f"No Python files found in: {directory}",
            error_type="no_files",
            details={"path": str(dir_path)},
        )

    # Prepare work items
    work_items = [(f, pattern, structure) for f in python_files]

    # Process files
    pattern_matches: list[dict] = []
    structure_data = {}

    if parallel > 1:
        # Parallel processing
        with ProcessPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(analyze_file_worker, item): item[0]
                for item in work_items
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if "pattern_matches" in result:
                        pattern_matches.extend(result["pattern_matches"])
                    if "structure" in result:
                        rel_path = str(Path(result["file"]).relative_to(dir_path))
                        structure_data[rel_path] = result["structure"]
                except Exception:
                    pass
    else:
        # Sequential processing
        for item in work_items:
            result = analyze_file_worker(item)
            if "pattern_matches" in result:
                pattern_matches.extend(result["pattern_matches"])
            if "structure" in result:
                try:
                    rel_path = str(Path(result["file"]).relative_to(dir_path))
                except ValueError:
                    rel_path = result["file"]
                structure_data[rel_path] = result["structure"]

    # Build response
    response: dict = {
        "files_analyzed": len(python_files),
    }

    if pattern:
        # Make paths relative
        for match in pattern_matches:
            try:
                match["file"] = str(Path(match["file"]).relative_to(dir_path))
            except ValueError:
                pass
        response["pattern"] = pattern
        response["matches"] = pattern_matches
        response["match_count"] = len(pattern_matches)

    if structure:
        response["structure"] = structure_data

    # Add summary stats
    if structure_data:
        total_classes = sum(
            len(s.get("classes", [])) for s in structure_data.values()
        )
        total_functions = sum(
            len(s.get("functions", [])) for s in structure_data.values()
        )
        response["stats"] = {
            "files_with_structure": len(structure_data),
            "total_classes": total_classes,
            "total_functions": total_functions,
        }

    return response


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive codebase analysis"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to analyze (default: current directory)",
    )
    parser.add_argument(
        "--pattern",
        help="Search for pattern in class/function names",
    )
    parser.add_argument(
        "--structure",
        action="store_true",
        help="Extract code structure (classes, functions)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers (default: 1)",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Also write output to internal/log/",
    )

    args = parser.parse_args()

    # Require at least one analysis mode
    if not args.pattern and not args.structure:
        args.structure = True  # Default to structure analysis

    with Timer() as timer:
        result = run_analyze(
            args.directory,
            pattern=args.pattern,
            structure=args.structure,
            parallel=args.parallel,
        )

    if result.get("status") == "error":
        emit(result, log=args.log, log_name="analyze")
        sys.exit(1)

    response = success_response(result, duration_ms=timer.elapsed_ms)
    emit(response, log=args.log, log_name="analyze")


if __name__ == "__main__":
    main()
