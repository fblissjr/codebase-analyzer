# Usage Guide

last updated: 2026-02-14

This is a Claude Code plugin. You use it by asking Claude to analyze Python codebases in natural language.

## Installation

### Per-Session (Development/Testing)

```bash
git clone https://github.com/fblissjr/codebase-analyzer.git ~/claude-plugins/codebase-analyzer
cd ~/claude-plugins/codebase-analyzer
uv sync

claude --plugin-dir ~/claude-plugins/codebase-analyzer
```

### Persistent (User-Wide)

Add to `~/.claude/settings.json`:

```json
{
  "pluginDirs": ["~/claude-plugins/codebase-analyzer"]
}
```

### Persistent (Per-Project)

Add to your project's `.claude/settings.json`:

```json
{
  "pluginDirs": ["~/claude-plugins/codebase-analyzer"]
}
```

### Installation Scopes

| Scope | Config Location | Effect |
|-------|-----------------|--------|
| Per-session | CLI flag | Only for current session |
| User | `~/.claude/settings.json` | Available in all your projects |
| Project | `.claude/settings.json` | Shared with team (committed to repo) |

## How to Use It

Just talk to Claude. The plugin activates automatically when your request matches analysis intents.

### Understanding Code

> "I just cloned this repo. Where does the code start and what does it do?"

> "Trace the imports from main.py -- I want to understand the dependency structure."

> "Document every granular detail of how this code works starting from pipeline.py."

> "Deep dive into the code structure starting at src/core/engine.py."

### Verifying and Auditing Code

> "I don't trust this code. Can you analyze what it actually does without running it?"

> "Compare my implementation against the reference -- am I missing anything?"

> "We refactored the import structure. Can you confirm we didn't break any dependencies?"

### Debugging Import Issues

> "Something's wrong with my imports. Can you trace from app.py and show me the full dependency graph?"

> "Why isn't my module being found? Can you analyze what's actually being imported?"

### Finding Things

> "Find all the CLI commands in this project."

> "Where are all the FastAPI route handlers?"

> "Search for anything with 'Config' in the name across the codebase."

### Composing Analysis

> "Find all the entry points, then trace each one and tell me which files are shared across multiple entry points."

> "Analyze the structure of src/, then compare it to tests/ -- are there any modules without test coverage?"

> "Trace from main.py, identify the external dependencies, and check if any of them have known security issues."

## What Claude Can Tell You

When you ask Claude to analyze a Python codebase, it can report:

- **Entry points** -- Where code execution starts (main blocks, CLI commands, web apps)
- **Import dependencies** -- What files import what, with per-edge line numbers and call graph
- **Hub modules** -- Which files are most connected (highest in-degree + out-degree)
- **Code structure** -- Classes (with inheritance, decorators, docstrings), functions (with type annotations, return types), async functions
- **Comparisons** -- Differences between two codebases or traces
- **Patterns** -- Finding specific named elements across the codebase
- **Content search** -- Finding files by content pattern and tracing their dependencies
- **Circular dependencies** -- Import cycles that may indicate design issues
- **External dependencies** -- Third-party packages grouped by which files import them
- **Recent changes** -- Files modified within a git time window

## Advanced Workflows

### Content-Based Discovery
> "Find all code related to 'generate' and trace its dependencies."

Uses `--grep` to find files by content pattern, then traces their full dependency graph.

### Recent Changes Analysis
> "What changed in the last week? Trace the recently modified files."

Uses `--since` to focus on git-modified files within a time window.

### Combined AST + LSP Analysis
> "Show me the full architecture starting from main.py, then drill into the most important modules."

Claude uses codebase-analyzer to get the structural map (entry points, import graph, hub modules), then uses pyright LSP for semantic details on specific symbols (find references, call hierarchies, type information). This combination provides both breadth (full codebase structure) and depth (precise semantic queries).

## What to Expect

When you ask for analysis, Claude:

1. Runs the appropriate script(s) -- you'll see the `uv run` commands
2. Receives JSON output with structured analysis data
3. Interprets the results -- explaining the dependency graph, identifying patterns, flagging issues
4. Suggests next steps based on what it found

The JSON output is designed for Claude to consume and reason about, not for you to parse manually.

## Troubleshooting

### "llmfiles not found"

The plugin depends on `llmfiles` for import tracing. Install it:

```bash
cd ~/claude-plugins/codebase-analyzer
uv sync
```

### "Entry file not found"

Check the file path. The trace script needs an absolute path or a path relative to the current working directory.

### "No Python files found"

The directory you specified doesn't contain `.py` files, or they're all in excluded directories (`.venv`, `node_modules`, `__pycache__`, etc.).

### Plugin Not Activating

Verify the plugin is loaded by checking that the `--plugin-dir` flag points to the correct directory, or that your `settings.json` has the right path in `pluginDirs`.
