#!/usr/bin/env python3
"""Compare two import traces for debugging and reference matching.

Usage:
    uv run scripts/compare.py trace1.json trace2.json
    uv run scripts/compare.py --entry ref/main.py --entry my/main.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for internal imports
sys.path.insert(0, str(Path(__file__).parent))

from internal.output import Timer, emit, error_response, success_response


def load_trace(filepath: Path) -> dict | None:
    """Load a trace JSON file.

    Args:
        filepath: Path to the trace JSON file

    Returns:
        Parsed trace data or None on error
    """
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None


def run_trace_for_entry(entry_path: Path) -> dict | None:
    """Run trace.py for an entry point and return the result.

    Args:
        entry_path: Path to the entry file

    Returns:
        Trace result or None on error
    """
    script_dir = Path(__file__).parent
    trace_script = script_dir / "trace.py"

    try:
        result = subprocess.run(
            [sys.executable, str(trace_script), str(entry_path)],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def compare_traces(trace1: dict, trace2: dict) -> dict:
    """Compare two trace results.

    Args:
        trace1: First trace result
        trace2: Second trace result

    Returns:
        Comparison result dictionary
    """
    # Extract file lists
    files1 = set(trace1.get("files", []))
    files2 = set(trace2.get("files", []))

    # Normalize file names for comparison (just basenames)
    def normalize(files):
        return {Path(f).name: f for f in files}

    norm1 = normalize(files1)
    norm2 = normalize(files2)

    names1 = set(norm1.keys())
    names2 = set(norm2.keys())

    only_in_first = sorted(names1 - names2)
    only_in_second = sorted(names2 - names1)
    common = sorted(names1 & names2)

    # Compare graphs
    graph1 = trace1.get("graph", {})
    graph2 = trace2.get("graph", {})

    # Normalize graph edges by basename
    def normalize_graph(graph):
        normalized = {}
        for src, deps in graph.items():
            src_name = Path(src).name
            dep_names = [Path(d).name for d in deps]
            normalized[src_name] = set(dep_names)
        return normalized

    norm_graph1 = normalize_graph(graph1)
    norm_graph2 = normalize_graph(graph2)

    # Find edge differences
    all_edges1 = set()
    for src, deps in norm_graph1.items():
        for dep in deps:
            all_edges1.add((src, dep))

    all_edges2 = set()
    for src, deps in norm_graph2.items():
        for dep in deps:
            all_edges2.add((src, dep))

    added_edges = [list(e) for e in sorted(all_edges2 - all_edges1)]
    removed_edges = [list(e) for e in sorted(all_edges1 - all_edges2)]

    # Compare external dependencies
    ext1 = set(trace1.get("external", []))
    ext2 = set(trace2.get("external", []))

    ext_only_first = sorted(ext1 - ext2)
    ext_only_second = sorted(ext2 - ext1)
    ext_common = sorted(ext1 & ext2)

    # Build summary
    file_diff = len(only_in_first) + len(only_in_second)
    summary = f"{file_diff} files differ, {len(common)} common"

    return {
        "only_in_first": only_in_first,
        "only_in_second": only_in_second,
        "common": common,
        "graph_diff": {
            "added_edges": added_edges,
            "removed_edges": removed_edges,
        },
        "external_diff": {
            "only_in_first": ext_only_first,
            "only_in_second": ext_only_second,
            "common": ext_common,
        },
        "summary": summary,
        "stats": {
            "files_in_first": len(files1),
            "files_in_second": len(files2),
            "common_files": len(common),
            "unique_to_first": len(only_in_first),
            "unique_to_second": len(only_in_second),
        },
    }


def run_compare(
    trace_files: list[str] | None = None,
    entry_files: list[str] | None = None,
) -> dict:
    """Run trace comparison.

    Args:
        trace_files: Two JSON trace files to compare
        entry_files: Two entry files to trace and compare

    Returns:
        Structured result dictionary
    """
    traces = []

    if trace_files:
        if len(trace_files) != 2:
            return error_response(
                "Exactly two trace files required",
                error_type="invalid_args",
            )

        for tf in trace_files:
            path = Path(tf)
            if not path.exists():
                return error_response(
                    f"Trace file not found: {tf}",
                    error_type="file_not_found",
                    details={"path": str(path)},
                )
            trace = load_trace(path)
            if trace is None:
                return error_response(
                    f"Failed to load trace file: {tf}",
                    error_type="parse_error",
                    details={"path": str(path)},
                )
            traces.append(trace)

    elif entry_files:
        if len(entry_files) != 2:
            return error_response(
                "Exactly two entry files required",
                error_type="invalid_args",
            )

        for ef in entry_files:
            path = Path(ef).resolve()
            if not path.exists():
                return error_response(
                    f"Entry file not found: {ef}",
                    error_type="file_not_found",
                    details={"path": str(path)},
                )
            trace = run_trace_for_entry(path)
            if trace is None:
                return error_response(
                    f"Failed to trace entry file: {ef}",
                    error_type="trace_error",
                    details={"path": str(path)},
                )
            traces.append(trace)

    else:
        return error_response(
            "Provide either two trace files or two entry files",
            error_type="invalid_args",
        )

    # Compare the traces
    comparison = compare_traces(traces[0], traces[1])

    first_name = trace_files[0] if trace_files else (entry_files[0] if entry_files else "unknown")
    second_name = trace_files[1] if trace_files else (entry_files[1] if entry_files else "unknown")

    return {
        "first": first_name,
        "second": second_name,
        **comparison,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compare two import traces"
    )
    parser.add_argument(
        "trace_files",
        nargs="*",
        help="Two trace JSON files to compare",
    )
    parser.add_argument(
        "--entry",
        action="append",
        dest="entry_files",
        help="Entry files to trace and compare (use twice)",
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

    # Validate inputs
    if args.trace_files and args.entry_files:
        emit(error_response(
            "Provide either trace files or --entry flags, not both",
            error_type="invalid_args",
        ))
        sys.exit(1)

    with Timer() as timer:
        result = run_compare(
            trace_files=args.trace_files if args.trace_files else None,
            entry_files=args.entry_files,
        )

    if result.get("status") == "error":
        emit(result, log=args.log, log_name="compare")
        sys.exit(1)

    response = success_response(result, duration_ms=timer.elapsed_ms)
    emit(response, log=args.log, log_name="compare")


if __name__ == "__main__":
    main()
