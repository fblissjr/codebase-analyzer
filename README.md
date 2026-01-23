# Codebase Analyzer

A Claude Code skills plugin for AST-based import tracing and codebase analysis using llmfiles.

## Features

- **Import Tracing**: Trace all Python imports from an entry point with dependency graph
- **Entry Point Detection**: Find main blocks, CLI commands (Click/Typer), web apps (FastAPI/Flask)
- **Structure Analysis**: Extract classes and functions from Python files
- **Trace Comparison**: Compare two traces for debugging or reference matching
- **Parallel Processing**: Analyze large codebases efficiently
- **JSON Output**: All scripts output structured JSON for easy parsing

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI (for plugin features)

## Installation

### Claude Code (CLI)

**Option 1: Install to Claude plugins directory (recommended)**
```bash
mkdir -p ~/.claude/plugins
git clone https://github.com/fblissjr/codebase-analyzer.git ~/.claude/plugins/codebase-analyzer
cd ~/.claude/plugins/codebase-analyzer
uv sync
```

Then add to `~/.claude/settings.json`:
```json
{
  "plugins": [
    "~/.claude/plugins/codebase-analyzer"
  ]
}
```

**Option 2: Install anywhere**
```bash
git clone https://github.com/fblissjr/codebase-analyzer.git /path/of/your/choice
cd /path/of/your/choice
uv sync
```

Then add the full path to `~/.claude/settings.json`:
```json
{
  "plugins": [
    "/path/of/your/choice"
  ]
}
```

**After installation**, restart Claude Code. You'll have access to:
- `/trace <file>` - Trace imports from an entry file
- `/analyze <directory>` - Analyze codebase structure and patterns

### Claude Desktop

Claude Desktop supports "skills" but they're **instruction-only** (markdown files that give Claude context). This plugin requires **code execution** (running Python scripts), which Claude Desktop skills cannot do.

**Options for Claude Desktop users:**

1. **Use MCP**: If someone builds an MCP server wrapper for these scripts, it could work with Claude Desktop
2. **Manual workflow**: Run scripts in terminal and paste the JSON output into your conversation:
   ```bash
   cd /path/to/codebase-analyzer/skills/codebase-analyzer
   uv run scripts/trace.py /path/to/your/file.py
   ```

### Scripts Only (No Plugin)

To use just the analysis scripts without Claude Code:

```bash
git clone https://github.com/fblissjr/codebase-analyzer.git
cd codebase-analyzer
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
