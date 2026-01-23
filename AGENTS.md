# Agent Context: codebase-analyzer

## Repository Purpose

AST-based Python codebase analysis tools for import tracing, entry point detection, and structure extraction. All analysis uses `ast.parse()` - no code execution.

## Directory Structure

```
codebase-analyzer/
  .claude-plugin/
    plugin.json            # Plugin registration
    marketplace.json       # Marketplace config
  skills/codebase-analyzer/
    SKILL.md               # Skill documentation (with frontmatter)
    workflows.md           # Workflow guides
    reference.md           # llmfiles reference
    scripts/               # Main analysis scripts
      trace.py             # Import tracing
      find_entries.py      # Entry point detection
      analyze.py           # Structure analysis
      compare.py           # Trace comparison
      internal/
        output.py          # JSON output utilities
        llmfiles_wrapper.py
  docs/                    # User documentation
  tests/                   # pytest tests
```

## Script Invocation

When used as a Claude Code plugin, scripts are invoked via `${CLAUDE_PLUGIN_ROOT}`:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py .
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --structure
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py --entry a.py --entry b.py
```

For local development:
```bash
uv run skills/codebase-analyzer/scripts/trace.py main.py
```

## Scripts Overview

| Script | Input | Output | Subprocess |
|--------|-------|--------|------------|
| `trace.py` | Python file path | JSON (files, graph, externals) | `llmfiles` |
| `find_entries.py` | Directory path | JSON (entry points) | None |
| `analyze.py` | Directory path | JSON (structure, patterns) | None |
| `compare.py` | Two traces or files | JSON (diff) | `trace.py` |

## Output Format

All scripts emit JSON to stdout:

```json
{
  "status": "success",
  "duration_ms": 234,
  ...
}
```

Errors use `"status": "error"` with `error_type` and `message` fields.

## Testing

```bash
uv run pytest
uv run pytest -v                    # Verbose
uv run pytest --cov=scripts         # Coverage
```

## Key Files for Modification

- **Add analysis features**: `scripts/analyze.py`
- **Modify import tracing**: `scripts/trace.py`
- **Add entry point types**: `scripts/find_entries.py`
- **Change output format**: `scripts/internal/output.py`
- **Update skill docs**: `skills/codebase-analyzer/SKILL.md`

## Dependencies

- `llmfiles` - AST-based import resolution (used by `trace.py`)
- `pytest` - Testing (dev dependency)

## Conventions

- All scripts use `argparse` for CLI
- All scripts support `--log` flag for file output
- JSON output uses `internal/output.py` utilities
- Excluded directories defined in each script's `find_python_files()`
