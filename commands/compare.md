---
name: compare
description: Compare two import traces or trace two entry points and diff them
arguments:
  - name: trace1
    description: First trace JSON file (positional, use with trace2)
    required: false
  - name: trace2
    description: Second trace JSON file (positional, use with trace1)
    required: false
  - name: entry1
    description: First entry file to trace and compare (use --entry flag twice)
    required: false
  - name: entry2
    description: Second entry file to trace and compare (use --entry flag twice)
    required: false
---

# Trace Comparison

Compare two import traces to find differences in file coverage, dependency graphs, and external dependencies.

## Usage

### Compare Existing Trace Files
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py {{ trace1 }} {{ trace2 }}
```

### Trace and Compare Entry Points
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py --entry {{ entry1 }} --entry {{ entry2 }}
```

## Output

The script outputs JSON with:
- `first` / `second`: Names of the compared traces
- `only_in_first`: Files unique to the first trace
- `only_in_second`: Files unique to the second trace
- `common`: Files shared between both traces
- `graph_diff`: Added and removed dependency edges
- `external_diff`: Differences in external package dependencies
- `stats`: Summary statistics (file counts, unique counts)
- `summary`: Human-readable summary string
- `duration_ms`: Execution time

## Examples

### Compare Two Trace Files
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py ref_trace.json impl_trace.json
```

Output:
```json
{
  "status": "success",
  "first": "ref_trace.json",
  "second": "impl_trace.json",
  "only_in_first": ["scheduler.py", "optimizer.py"],
  "only_in_second": ["my_scheduler.py"],
  "common": ["main.py", "engine.py", "utils.py"],
  "graph_diff": {
    "added_edges": [["main.py", "my_scheduler.py"]],
    "removed_edges": [["main.py", "scheduler.py"]]
  },
  "external_diff": {
    "only_in_first": ["numpy"],
    "only_in_second": ["torch"],
    "common": ["click", "rich"]
  },
  "stats": {
    "files_in_first": 5,
    "files_in_second": 4,
    "common_files": 3,
    "unique_to_first": 2,
    "unique_to_second": 1
  },
  "summary": "3 files differ, 3 common",
  "duration_ms": 456
}
```

### Trace and Compare Two Entry Points
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py --entry reference/main.py --entry my_impl/main.py
```
