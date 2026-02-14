# Codebase Analyzer

last updated: 2026-02-14

A Claude Code plugin that analyzes Python codebases using AST parsing -- tracing imports, finding entry points, extracting code structure, and comparing implementations. No code execution; all analysis is static and safe.

## What It Does

- **Trace imports** -- Follow the dependency graph from any Python entry point, see every file in the execution path
- **Find entry points** -- Discover main blocks, Click/Typer CLI commands, FastAPI/Flask apps, argparse usage
- **Analyze structure** -- Extract all classes and functions across a codebase with method signatures
- **Compare traces** -- Diff two implementations or trace files to find gaps, extras, and structural differences
- **Search patterns** -- Find classes and functions by name across an entire project

All analysis uses `ast.parse()` (the same technique linters and IDEs use). Your code is never executed. See [docs/security.md](docs/security.md) for details.

## Quick Start

```bash
# Clone and install dependencies
git clone https://github.com/fblissjr/codebase-analyzer.git ~/claude-plugins/codebase-analyzer
cd ~/claude-plugins/codebase-analyzer
uv sync

# Launch Claude Code with the plugin
claude --plugin-dir ~/claude-plugins/codebase-analyzer
```

Then just ask Claude:

> "I just cloned this repo. Where does the code start and what does it do?"

> "Trace the imports from main.py -- I want to understand the dependency structure."

> "I don't trust this code. Can you analyze what it actually does without running it?"

## Installation Methods

| Method | Command | Scope |
|--------|---------|-------|
| Per-session | `claude --plugin-dir ~/claude-plugins/codebase-analyzer` | Current session only |
| User-wide | Add to `~/.claude/settings.json` `pluginDirs` | All your projects |
| Per-project | Add to `.claude/settings.json` `pluginDirs` | Shared with team |

### Manual Configuration

Add to your settings.json (user-wide or per-project):

```json
{
  "pluginDirs": ["~/claude-plugins/codebase-analyzer"]
}
```

## Usage Examples

### Understanding a New Codebase
> "What are all the entry points in this project?"

> "Trace down from `pipeline.py` and exhaustively analyze every module it touches."

> "Document every granular detail of how this code works starting from `main.py`."

### Verifying Code
> "Compare my implementation against the reference -- am I missing anything?"

> "We refactored the import structure. Can you confirm we didn't break any dependencies?"

### Debugging Imports
> "Something's wrong with my imports. Can you trace from `app.py` and show me the full dependency graph?"

### Finding Things
> "Find all the CLI commands in this project."

> "Search for anything with 'Config' in the name across the codebase."

## How It Works

1. **Plugin registration**: `.claude-plugin/plugin.json` registers the plugin with Claude Code
2. **Skill loading**: Claude reads `skills/codebase-analyzer/SKILL.md` which defines when and how to use the tools
3. **Automatic activation**: When your prompt matches intent-based triggers (like "understand this codebase" or "trace imports"), Claude activates the analyzer
4. **Analysis**: Scripts parse your code using `ast.parse()`, with `llmfiles` for import resolution
5. **Interpretation**: Claude reads the JSON output, explains findings, and suggests next steps

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

Dependencies are installed automatically via `uv sync`:
- `llmfiles` -- AST-based import resolution
- `orjson` -- JSON serialization

## Documentation

- [Usage Guide](docs/usage.md) -- How to use it with Claude
- [What Runs on Your Machine](docs/what-runs-on-your-machine.md) -- Full transparency on scripts and data flow
- [Security](docs/security.md) -- Security model and permissions

## Testing

```bash
uv sync --dev
uv run python -m pytest -v
```

## License

MIT
