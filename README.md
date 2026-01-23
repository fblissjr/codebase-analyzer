# Codebase Analyzer

AST-based Python import tracing and codebase analysis. See [what runs on your machine](docs/what-runs-on-your-machine.md).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI (for plugin features)

## Installation

```bash
git clone https://github.com/fblissjr/codebase-analyzer.git
cd codebase-analyzer
uv sync
```

### As Claude Code Plugin

```bash
claude --plugin-dir /path/to/codebase-analyzer
```

## Scripts

| Script | Purpose |
|--------|---------|
| `trace.py` | Import tracing with dependency graph |
| `find_entries.py` | Discover entry points (main blocks, CLI commands, web apps) |
| `analyze.py` | Structure analysis and pattern search |
| `compare.py` | Compare two import traces |

All scripts output JSON to stdout. Use `--log` to also write to `internal/log/`.

```bash
cd skills/codebase-analyzer
uv run scripts/trace.py /path/to/main.py
uv run scripts/find_entries.py /path/to/project
uv run scripts/analyze.py /path/to/project --structure
```

## Testing

```bash
uv run pytest
```

## Documentation

- [What Runs on Your Machine](docs/what-runs-on-your-machine.md) - Transparency documentation
- [Security](docs/security.md) - Security properties
- `skills/codebase-analyzer/SKILL.md` - Full skill documentation

## License

MIT
