# Codebase Analyzer

AST-based import tracing and codebase analysis using llmfiles.

## When to Use

Use this skill when the user wants to:

**Understand code**
- Understand how a Python codebase works
- Figure out what code actually runs when they execute something
- Learn the architecture of an unfamiliar project
- See which files matter vs which are dead code
- Document every granular detail of how code works starting from a file
- Trace down from an entry point to understand all dependencies
- Deep dive into a codebase starting at a specific Python file
- Exhaustively analyze code structure and flow

**Verify and trust code**
- Verify code is doing what they think it's doing
- Audit untrusted Python code without executing it
- Confirm an implementation matches a reference
- Check if a refactor broke any dependencies

**Debug issues**
- Debug import or module resolution issues
- Find why a module isn't being found
- Trace unexpected behavior to its source

**Analyze structure**
- Find all entry points in a codebase (main blocks, CLI commands, web apps)
- Identify what would be affected by a change
- Find all the ways code can be invoked
- Compare their implementation to a reference

**Technical operations**
- Trace Python imports from an entry point
- Analyze codebase structure (classes, functions)
- Compare two import traces

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
