---
name: find-entries
description: Find entry points in a Python codebase
arguments:
  - name: directory
    description: Directory to search for entry points
    required: false
    default: "."
  - name: types
    description: Comma-separated entry types to find (main_block, click_command, fastapi, flask, typer, argparse)
    required: false
---

# Entry Point Discovery

Find all entry points in a Python codebase using AST analysis.

## Usage

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py {{ directory }}{% if types %} --types {{ types }}{% endif %}
```

## Output

The script outputs JSON with:
- `entry_points`: List of discovered entry points, each with `file`, `type`, and `line`
- `files_scanned`: Total number of Python files scanned
- `duration_ms`: Execution time

## Examples

### Find All Entry Points
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py /path/to/project
```

Output:
```json
{
  "status": "success",
  "entry_points": [
    {"file": "main.py", "type": "main_block", "line": 45},
    {"file": "cli.py", "type": "click_command", "line": 12},
    {"file": "api/app.py", "type": "fastapi", "line": 8}
  ],
  "files_scanned": 42,
  "duration_ms": 89
}
```

### Filter by Type
```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py . --types main_block,click_command
```

## Entry Point Types

| Type | Detects |
|------|---------|
| `main_block` | `if __name__ == "__main__"` |
| `click_command` | `@click.command()` or `@click.group()` |
| `fastapi` | `FastAPI()` app instantiation |
| `flask` | `Flask()` app instantiation |
| `typer` | `typer.Typer()` app instantiation |
| `argparse` | `argparse.ArgumentParser()` usage |
