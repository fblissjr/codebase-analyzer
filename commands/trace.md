---
name: trace
description: Trace Python imports from an entry file
arguments:
  - name: entry
    description: Entry file to trace imports from
    required: true
  - name: all
    description: Trace all imports without smart filtering
    required: false
    default: "false"
---

# Import Tracing

Trace all imports starting from an entry file using llmfiles' AST-based import tracer.

## Usage

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py {{ entry }}{% if all == "true" %} --all{% endif %}
```

## Output

The script outputs JSON with:
- `entry`: The entry file path
- `files`: List of all traced files
- `graph`: Dependency graph (file -> dependencies)
- `external`: External package dependencies
- `stats`: Statistics (total files, max depth, circular deps)
- `duration_ms`: Execution time

## Example

```bash
uv run scripts/trace.py /path/to/project/main.py
```

Output:
```json
{
  "status": "success",
  "entry": "/path/to/project/main.py",
  "files": ["main.py", "core/engine.py", "utils/helpers.py"],
  "graph": {
    "main.py": ["core/engine.py", "utils/helpers.py"]
  },
  "external": ["click", "rich"],
  "stats": {
    "total_files": 3,
    "max_depth": 2,
    "circular_deps": []
  },
  "duration_ms": 234
}
```

## Flags

- `--all`: Trace ALL imports without filtering (finds lazy imports, dynamic imports)
- `--json`: Output as JSON (default)
- `--log`: Also write output to internal/log/ for later review
