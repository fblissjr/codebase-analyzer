#!/usr/bin/env python3
"""Import tracing with structured JSON output.

Uses llmfiles CallTracer library for AST-based import resolution.
Falls back to subprocess invocation if library import fails.

Usage:
    uv run scripts/trace.py main.py              # Smart filtered
    uv run scripts/trace.py main.py --all        # Full trace
    uv run scripts/trace.py main.py --grep PAT   # Find files by content, then trace
    uv run scripts/trace.py main.py --since DATE # Only recently changed files
    uv run scripts/trace.py main.py --log        # Also write to internal/log/
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for internal imports
sys.path.insert(0, str(Path(__file__).parent))

from internal.output import Timer, emit, error_response, success_response

# Try importing llmfiles library directly; track availability
_LLMFILES_AVAILABLE = False
try:
    # Suppress llmfiles structlog output (it writes to stdout and contaminates JSON)
    import logging
    import structlog
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
    )

    from llmfiles.core.import_tracer import CallTracer
    from llmfiles.core.discovery.git_utils import get_git_modified_files

    _LLMFILES_AVAILABLE = True
except ImportError:
    pass


def compute_hub_scores(call_graph: dict[Path, set[Path]]) -> list[dict]:
    """Compute hub scores for files based on in-degree + out-degree.

    Args:
        call_graph: Dict mapping file -> set of imported files

    Returns:
        Top 5 hub modules sorted by score, as list of dicts
    """
    out_degree: dict[Path, int] = {}
    in_degree: dict[Path, int] = defaultdict(int)

    for src, deps in call_graph.items():
        out_degree[src] = len(deps)
        for dep in deps:
            in_degree[dep] += 1

    all_files = set(out_degree.keys()) | set(in_degree.keys())
    scores = []
    for f in all_files:
        od = out_degree.get(f, 0)
        ind = in_degree.get(f, 0)
        scores.append({"file": f, "in_degree": ind, "out_degree": od, "score": ind + od})

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:5]


def detect_cycles(call_graph: dict[Path, set[Path]]) -> list[list[str]]:
    """Detect circular dependencies in the call graph.

    Args:
        call_graph: Dict mapping file -> set of imported files

    Returns:
        List of cycles, each cycle is a list of file path strings
    """
    cycles = []
    visited = set()

    def dfs(node: Path, path: list[Path], on_stack: set[Path]):
        if node in on_stack:
            cycle_start = path.index(node)
            cycle = [str(p) for p in path[cycle_start:]] + [str(node)]
            cycles.append(cycle)
            return
        if node in visited:
            return
        visited.add(node)
        on_stack.add(node)
        path.append(node)
        for neighbor in call_graph.get(node, set()):
            dfs(neighbor, path.copy(), on_stack.copy())

    for start in call_graph:
        if start not in visited:
            dfs(start, [], set())

    return cycles[:10]


def trace_with_library(
    entry_path: Path,
    trace_all: bool = False,
    grep_pattern: str | None = None,
    since: str | None = None,
) -> dict:
    """Trace imports using llmfiles CallTracer library directly.

    Args:
        entry_path: Resolved path to the entry file
        trace_all: If True, trace all imports without smart filtering
        grep_pattern: If set, find files containing pattern and use as seeds
        since: If set, only include files modified since this git date

    Returns:
        Structured result dictionary
    """
    project_root = entry_path.parent

    # Walk up to find the project root (look for pyproject.toml, setup.py, .git)
    candidate = entry_path.parent
    for _ in range(10):
        if any((candidate / marker).exists() for marker in ("pyproject.toml", "setup.py", "setup.cfg", ".git")):
            project_root = candidate
            break
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent

    # Initialize CallTracer
    tracer = CallTracer(
        project_root=project_root,
        filter_unused=not trace_all,
    )

    # Determine entry points
    entry_points = [entry_path]

    # If --grep is specified, find files containing pattern and use them as seeds
    if grep_pattern:
        from llmfiles.core.discovery.walker import grep_files_for_content
        from llmfiles.config.settings import PromptConfig

        config = PromptConfig(
            input_paths=[project_root],
            grep_content_pattern=grep_pattern,
            include_patterns=["*.py"],
            recursive=True,
        )
        grep_results = list(grep_files_for_content(config))
        if not grep_results:
            return error_response(
                f"No files found containing pattern: {grep_pattern}",
                error_type="no_matches",
                details={"pattern": grep_pattern, "search_root": str(project_root)},
            )
        entry_points = grep_results

    # If --since is specified, filter to recently changed files
    git_modified = None
    if since:
        git_modified = get_git_modified_files(since, project_root)
        if git_modified is None:
            return error_response(
                f"Failed to get git history (not a git repo or invalid date spec: {since})",
                error_type="git_error",
                details={"since": since, "project_root": str(project_root)},
            )
        if not git_modified:
            return error_response(
                f"No files modified since: {since}",
                error_type="no_matches",
                details={"since": since},
            )

    # Run the trace
    all_files = tracer.trace_all(entry_points)

    # Filter by --since if specified
    if git_modified is not None:
        all_files = [f for f in all_files if f in git_modified]

    # Build relative file paths
    rel_files = []
    for f in all_files:
        try:
            rel_files.append(str(f.relative_to(project_root)))
        except ValueError:
            rel_files.append(str(f))

    # Build enriched call_graph with per-edge line numbers
    call_graph_output: dict[str, list[dict]] = defaultdict(list)
    for call_info in tracer.discovered_calls:
        try:
            from_rel = str(call_info.from_file.relative_to(project_root))
        except ValueError:
            from_rel = str(call_info.from_file)
        try:
            to_rel = str(call_info.to_file.relative_to(project_root))
        except ValueError:
            to_rel = str(call_info.to_file)

        call_graph_output[from_rel].append({
            "to": to_rel,
            "module": call_info.from_name,
            "line": call_info.from_line,
        })

    # Classify external dependencies using resolve_import
    external: dict[str, list[str]] = defaultdict(list)
    stdlib_modules = sys.stdlib_module_names

    # Collect all unique top-level module names from imports that weren't resolved to project files
    seen_ext = set()
    for call_info in tracer.discovered_calls:
        top_module = call_info.from_name.split(".")[0]
        if top_module in stdlib_modules:
            continue
        # If the target file is in the project, it's internal
        if call_info.to_file in tracer.visited_files:
            continue
        key = (top_module, str(call_info.from_file))
        if key not in seen_ext:
            seen_ext.add(key)
            try:
                from_rel = str(call_info.from_file.relative_to(project_root))
            except ValueError:
                from_rel = str(call_info.from_file)
            external[top_module].append(from_rel)

    # Also check skipped imports for external deps
    for file_path, module_name, _line in tracer.skipped_imports:
        top_module = module_name.split(".")[0]
        if top_module in stdlib_modules:
            continue
        try:
            from_rel = str(file_path.relative_to(project_root))
        except ValueError:
            from_rel = str(file_path)
        key = (top_module, from_rel)
        if key not in seen_ext:
            seen_ext.add(key)
            external[top_module].append(from_rel)

    # Compute hub scores
    hubs = compute_hub_scores(tracer.call_graph)
    hub_output = []
    for h in hubs:
        try:
            hub_file = str(h["file"].relative_to(project_root))
        except (ValueError, AttributeError):
            hub_file = str(h["file"])
        hub_output.append({
            "file": hub_file,
            "in_degree": h["in_degree"],
            "out_degree": h["out_degree"],
            "score": h["score"],
        })

    # Detect circular dependencies
    circular = detect_cycles(tracer.call_graph)
    # Make paths relative in cycle output
    circular_rel = []
    for cycle in circular:
        rel_cycle = []
        for p in cycle:
            try:
                rel_cycle.append(str(Path(p).relative_to(project_root)))
            except ValueError:
                rel_cycle.append(p)
        circular_rel.append(rel_cycle)

    # Compute max depth via BFS from entry
    max_depth = 0
    if entry_path.resolve() in tracer.call_graph or entry_path in tracer.visited_files:
        bfs_visited = set()
        queue = [(entry_path.resolve(), 0)]
        while queue:
            current, depth = queue.pop(0)
            if current in bfs_visited:
                continue
            bfs_visited.add(current)
            max_depth = max(max_depth, depth)
            for dep in tracer.call_graph.get(current, set()):
                if dep not in bfs_visited:
                    queue.append((dep, depth + 1))

    # Build parse error output
    parse_errors = []
    for file_path, error_msg in tracer.parse_errors:
        try:
            pe_rel = str(file_path.relative_to(project_root))
        except ValueError:
            pe_rel = str(file_path)
        parse_errors.append({"file": pe_rel, "error": error_msg})

    result = {
        "entry": str(entry_path.relative_to(project_root)) if _is_subpath(entry_path, project_root) else str(entry_path),
        "project_root": str(project_root),
        "files": rel_files,
        "call_graph": dict(call_graph_output),
        "external": {pkg: sorted(set(files)) for pkg, files in external.items()},
        "stats": {
            "total_files": len(rel_files),
            "max_depth": max_depth,
            "circular_deps": circular_rel,
            "parse_errors": parse_errors,
            "skipped_imports": len(tracer.skipped_imports),
            "hub_modules": hub_output,
        },
    }

    if grep_pattern:
        result["grep_pattern"] = grep_pattern
        result["grep_seed_files"] = len(entry_points)

    if since:
        result["since"] = since
        result["git_modified_count"] = len(git_modified) if git_modified else 0

    return result


def _is_subpath(path: Path, parent: Path) -> bool:
    """Check if path is under parent directory."""
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def trace_with_subprocess(entry_path: Path, trace_all: bool = False) -> dict:
    """Fallback: trace imports using llmfiles CLI subprocess.

    Used when llmfiles library cannot be imported directly.

    Args:
        entry_path: Resolved path to the entry file
        trace_all: If True, trace all imports

    Returns:
        Structured result dictionary
    """
    from internal.llmfiles_wrapper import LlmfilesError, run_llmfiles

    llmfiles_args = [str(entry_path), "--deps"]
    if trace_all:
        llmfiles_args.append("--all")

    try:
        run_llmfiles(llmfiles_args, cwd=entry_path.parent)
    except LlmfilesError as e:
        return error_response(
            str(e),
            error_type="llmfiles_error" if e.returncode != 127 else "dependency_missing",
            details={"returncode": e.returncode, "stderr": e.stderr},
        )

    # Basic fallback: just report the entry file since we can't parse the output reliably
    return {
        "entry": str(entry_path),
        "files": [str(entry_path)],
        "call_graph": {},
        "external": {},
        "stats": {
            "total_files": 1,
            "max_depth": 0,
            "circular_deps": [],
            "parse_errors": [],
            "skipped_imports": 0,
            "hub_modules": [],
        },
        "_fallback": True,
        "_note": "Used subprocess fallback -- install llmfiles as library for full analysis",
    }


def run_trace(
    entry: str,
    trace_all: bool = False,
    grep_pattern: str | None = None,
    since: str | None = None,
) -> dict:
    """Run import trace on an entry file.

    Args:
        entry: Path to the entry file
        trace_all: If True, trace all imports without filtering
        grep_pattern: If set, find files containing pattern and use as seeds
        since: If set, only include files modified since this git date

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

    if _LLMFILES_AVAILABLE:
        return trace_with_library(entry_path, trace_all=trace_all, grep_pattern=grep_pattern, since=since)
    else:
        if grep_pattern or since:
            return error_response(
                "--grep and --since require llmfiles library (not just CLI). Install with: uv add llmfiles",
                error_type="dependency_missing",
                details={"feature": "grep/since", "fix": "uv sync"},
            )
        return trace_with_subprocess(entry_path, trace_all=trace_all)


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
        "--grep",
        dest="grep_pattern",
        help="Find files containing pattern, then trace their deps",
    )
    parser.add_argument(
        "--since",
        help="Only include files modified since date (e.g. '7 days ago')",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Also write output to internal/log/",
    )

    args = parser.parse_args()

    with Timer() as timer:
        result = run_trace(
            args.entry,
            trace_all=args.trace_all,
            grep_pattern=args.grep_pattern,
            since=args.since,
        )

    if result.get("status") == "error":
        emit(result, log=args.log, log_name="trace")
        sys.exit(1)

    response = success_response(result, duration_ms=timer.elapsed_ms)
    emit(response, log=args.log, log_name="trace")


if __name__ == "__main__":
    main()
