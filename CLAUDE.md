# Agent Context: codebase-analyzer

## Repository Purpose

AST-based Python codebase analysis tools for import tracing, entry point detection, and structure extraction. All analysis uses `ast.parse()` - no code execution.

## Architecture

The plugin operates as three complementary layers:

- **codebase-analyzer** = reconnaissance tool (bulk structure analysis via AST)
- **pyright LSP** = precision tool (semantic details on specific symbols -- available to Claude natively)
- **Claude** = synthesis layer (combines both into architectural narratives)
- **llmfiles** = underlying AST engine (shared dependency, used as library by trace.py)

`trace.py` imports llmfiles' `CallTracer` directly as a Python library (not subprocess). This gives access to rich call graph data, per-edge line numbers, and symbol filtering. The subprocess path (`llmfiles_wrapper.py`) exists as a fallback.

## Directory Structure

```
codebase-analyzer/
  .claude-plugin/
    plugin.json            # Plugin registration
    marketplace.json       # Marketplace config
  skills/codebase-analyzer/
    SKILL.md               # Skill documentation (with frontmatter)
    references/            # Additional context files
      workflows.md         # Workflow guides (includes LSP-combined workflows)
      llmfiles-reference.md # llmfiles flag reference
      user-journeys.md     # Conversation-style examples
      plan-templates.md    # Copy-paste plan templates
    scripts/               # Main analysis scripts
      trace.py             # Import tracing (uses llmfiles CallTracer library)
      find_entries.py      # Entry point detection
      analyze.py           # Structure analysis (classes, functions, inheritance, decorators, docstrings)
      compare.py           # Trace comparison
      internal/
        output.py          # JSON output utilities (orjson)
        llmfiles_wrapper.py # llmfiles CLI wrapper (subprocess fallback)
        file_utils.py      # Shared file discovery
  commands/                # Slash command definitions
    trace.md
    analyze.md
    find-entries.md
    compare.md
  agents/                  # Agent definitions
    codebase-explorer.md
  docs/                    # User documentation
    usage.md
    security.md
    what-runs-on-your-machine.md
  tests/                   # pytest tests
    fixtures/sample_project/
```

## Script Invocation

When used as a Claude Code plugin, scripts are invoked via `${CLAUDE_PLUGIN_ROOT}`:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py --grep "pattern"
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/trace.py main.py --since "7 days ago"
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/find_entries.py .
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/analyze.py . --structure
uv run ${CLAUDE_PLUGIN_ROOT}/skills/codebase-analyzer/scripts/compare.py --entry a.py --entry b.py
```

For local development:
```bash
uv run skills/codebase-analyzer/scripts/trace.py main.py
```

## Scripts Overview

| Script | Input | Output | Engine |
|--------|-------|--------|--------|
| `trace.py` | Python file path | JSON (files, call_graph, externals, hub_modules) | llmfiles CallTracer (library) |
| `find_entries.py` | Directory path | JSON (entry points) | Python ast module |
| `analyze.py` | Directory path | JSON (structure with inheritance, decorators, docstrings) | Python ast module |
| `compare.py` | Two traces or files | JSON (diff) | trace.py |

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
uv sync --dev
uv run python -m pytest -v
```

## Key Files for Modification

- **Add analysis features**: `scripts/analyze.py`
- **Modify import tracing**: `scripts/trace.py`
- **Add entry point types**: `scripts/find_entries.py`
- **Change output format**: `scripts/internal/output.py`
- **Shared file discovery**: `scripts/internal/file_utils.py`
- **llmfiles fallback**: `scripts/internal/llmfiles_wrapper.py`
- **Update skill docs**: `skills/codebase-analyzer/SKILL.md`

## Dependencies

- `llmfiles` - AST-based import resolution (used as library by `trace.py`, with subprocess fallback)
- `orjson` - JSON serialization
- `structlog` - Logging (transitive via llmfiles, suppressed in trace.py output)
- `pytest` - Testing (dev dependency)

## Conventions

- All scripts use `argparse` for CLI
- All scripts support `--log` flag for file output
- JSON output uses `internal/output.py` utilities (orjson)
- File discovery uses `internal/file_utils.py` (shared excluded dirs)
- trace.py imports llmfiles as library; llmfiles_wrapper.py is subprocess fallback only
- structlog is suppressed to WARNING level to keep stdout clean for JSON
