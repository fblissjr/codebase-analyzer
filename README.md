# Codebase Analyzer

A Claude Code skills plugin for AST-based import tracing and codebase analysis using llmfiles.

## Features

- **Import Tracing**: Trace all Python imports from an entry point with dependency graph
- **Entry Point Detection**: Find main blocks, CLI commands (Click/Typer), web apps (FastAPI/Flask)
- **Structure Analysis**: Extract classes and functions from Python files
- **Trace Comparison**: Compare two traces for debugging or reference matching
- **Parallel Processing**: Analyze large codebases efficiently
- **JSON Output**: All scripts output structured JSON for easy parsing

## Installation

```bash
cd ~/utils/codebase-analyzer
uv sync
```

## Quick Start

### Trace Imports
```bash
cd skills/codebase-analyzer
uv run scripts/trace.py /path/to/main.py
```

### Find Entry Points
```bash
uv run scripts/find_entries.py /path/to/project
```

### Analyze Structure
```bash
uv run scripts/analyze.py /path/to/project --structure
```

### Compare Traces
```bash
uv run scripts/compare.py trace1.json trace2.json
```

## Scripts

| Script | Purpose |
|--------|---------|
| `trace.py` | Import tracing with dependency graph |
| `find_entries.py` | Discover entry points in codebase |
| `analyze.py` | Structure analysis and pattern search |
| `compare.py` | Compare two import traces |

## Output Format

All scripts output JSON to stdout:

```json
{
  "status": "success",
  "duration_ms": 234,
  ...
}
```

Errors:
```json
{
  "status": "error",
  "error_type": "file_not_found",
  "message": "Entry file not found: main.py"
}
```

## Testing

```bash
uv run pytest
uv run pytest -v                    # Verbose
uv run pytest --cov=scripts         # With coverage
```

## Documentation

- `skills/codebase-analyzer/SKILL.md` - Main skill documentation
- `skills/codebase-analyzer/workflows.md` - Detailed workflow guides
- `skills/codebase-analyzer/reference.md` - llmfiles flag reference

## License

MIT
