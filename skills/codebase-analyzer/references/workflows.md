# Codebase Analyzer Workflows

Detailed guides for common analysis tasks.

## Workflow 1: Understanding a New Codebase

When you encounter a new Python project:

### Step 1: Find Entry Points
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py /path/to/project
```

This identifies:
- `main_block`: `if __name__ == "__main__"` patterns
- `click_command`: Click CLI commands
- `fastapi`: FastAPI applications
- `flask`: Flask applications
- `typer`: Typer CLI apps
- `argparse`: ArgumentParser usage

### Step 2: Trace from Entry Point
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py /path/to/project/main.py
```

This produces:
- List of all imported files
- Dependency graph
- External dependencies
- Statistics (depth, circular deps)

### Step 3: Analyze Structure
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py /path/to/project --structure
```

This extracts:
- All classes with methods
- All top-level functions
- Parameter information

## Workflow 2: Debugging Import Issues

When imports aren't resolving correctly:

### Step 1: Get Full Trace
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py --all > full_trace.json
```

### Step 2: Get Filtered Trace
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py > filtered_trace.json
```

### Step 3: Compare
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py full_trace.json filtered_trace.json
```

This shows what the smart filter is excluding.

## Workflow 3: Reference Implementation Matching

When implementing something to match a reference:

### Step 1: Trace Reference
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py reference/main.py > ref_trace.json
```

### Step 2: Trace Your Implementation
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py my_impl/main.py > impl_trace.json
```

### Step 3: Compare
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py ref_trace.json impl_trace.json
```

The comparison shows:
- Files only in reference (you might be missing)
- Files only in your impl (you might have extra)
- Graph differences (import structure differences)

## Workflow 4: Pattern Search

When looking for specific patterns:

### Find Classes by Name
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --pattern "Handler"
```

### Find Functions by Name
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --pattern "validate"
```

### Combined Search
```bash
# First find, then analyze structure of matches
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --pattern "Config" --structure
```

## Workflow 5: Large Codebase Analysis

For large codebases, use parallel processing:

### Parallel Structure Analysis
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --structure --parallel 4
```

### Parallel Entry Point Tracing
```bash
# Find all entries
entries=$(uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . | jq -r '.entry_points[].file')

# Trace each in parallel
echo "$entries" | xargs -P4 -I{} uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py {} --log
```

## JSON Output Parsing

All outputs are JSON. Use `jq` for parsing:

### Extract File List
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py | jq -r '.files[]'
```

### Get Entry Point Files
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . | jq -r '.entry_points[].file'
```

### Filter by Type
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . | jq '.entry_points[] | select(.type == "click_command")'
```

### Get Class Names
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --structure | \
  jq -r '.structure | to_entries[] | .value.classes[].name'
```
