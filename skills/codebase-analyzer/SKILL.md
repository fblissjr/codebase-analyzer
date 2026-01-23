# Codebase Analyzer

AST-based import tracing and codebase analysis using llmfiles.

## When to Use

Use this skill when you need to:
- Trace Python imports from an entry point
- Find entry points in a codebase (main blocks, CLI commands, web apps)
- Analyze codebase structure (classes, functions)
- Compare two import traces for debugging

## Quick Reference

### Trace Imports
```bash
# Smart filtered trace (recommended)
uv run scripts/trace.py main.py

# Full trace (all imports)
uv run scripts/trace.py main.py --all

# With logging
uv run scripts/trace.py main.py --log
```

### Find Entry Points
```bash
# Find all entry points
uv run scripts/find_entries.py /path/to/project

# Filter by type
uv run scripts/find_entries.py . --types main_block,click_command

# Available types: main_block, click_command, fastapi, flask, typer, argparse
```

### Analyze Structure
```bash
# Extract classes and functions
uv run scripts/analyze.py /path/to/project --structure

# Search for pattern
uv run scripts/analyze.py . --pattern "Config"

# Parallel processing
uv run scripts/analyze.py . --structure --parallel 4
```

### Compare Traces
```bash
# Compare two trace files
uv run scripts/compare.py trace1.json trace2.json

# Trace and compare two entry points
uv run scripts/compare.py --entry ref/main.py --entry impl/main.py
```

## Output Format

All scripts output JSON to stdout with this structure:

### Success
```json
{
  "status": "success",
  "duration_ms": 234,
  ...
}
```

### Error
```json
{
  "status": "error",
  "error_type": "file_not_found",
  "message": "Entry file not found: main.py"
}
```

## Subagent Patterns

### Parallel Tracing
```bash
# Trace multiple entry points in parallel
entries=("main.py" "cli.py" "api/app.py")
for entry in "${entries[@]}"; do
  uv run scripts/trace.py "$entry" &
done
wait
```

### Composable Pipeline
```bash
# Find entries -> trace each
uv run scripts/find_entries.py . | \
  jq -r '.entry_points[].file' | \
  xargs -I{} uv run scripts/trace.py {}
```

## See Also

- `workflows.md` - Detailed workflow guides
- `reference.md` - Complete llmfiles flag reference
