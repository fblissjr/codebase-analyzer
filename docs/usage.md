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

### Tracing Execution Paths

> "What happens when I call the generate API in web/server.py? Trace the full path from the route handler through model loading and inference."

> "I want to understand the full execution path when the flux2 pipeline runs starting from server.py."

Claude combines codebase-analyzer (forward trace from the entry point, structure search for relevant symbols) with pyright LSP (goToDefinition on the route handler, outgoingCalls to follow the call chain through service layers).

### Reverse Lookups

> "Where is generate.py used? What calls its main functions?"

Forward tracing shows what a file depends on. For the reverse -- who calls this file's functions -- Claude uses pyright LSP's `findReferences` and `incomingCalls` operations.

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

## Using with Pyright LSP

codebase-analyzer provides bulk structural analysis (the map). For semantic precision queries, Claude uses the pyright LSP plugin. Together they cover both breadth and depth.

### Prerequisites

1. Install pyright:

```bash
npm install -g pyright
```

Or via pip/pipx:

```bash
pipx install pyright
```

2. Install the pyright-lsp plugin for Claude Code. This can be done by adding it to your `~/.claude/settings.json` or project `.claude/settings.json` `pluginDirs`, or by using the official Claude Code plugins repository.

3. Your Python project should have a `pyproject.toml` or `pyrightconfig.json` so pyright can resolve imports correctly.

### What Pyright LSP Provides

Once the pyright-lsp plugin is installed, Claude has access to these LSP operations on any `.py` or `.pyi` file:

| Operation | What It Does | When to Use |
|-----------|-------------|-------------|
| `goToDefinition` | Jump to where a symbol is defined | "Where is this class defined?" |
| `findReferences` | Find all usages of a symbol | "Who calls this function?" |
| `hover` | Get type info and docstrings for a symbol | "What type does this return?" |
| `documentSymbol` | List all symbols in a file | "What's in this module?" |
| `workspaceSymbol` | Search for symbols across the project | "Find all classes named Config" |
| `goToImplementation` | Find implementations of an interface | "What implements this protocol?" |
| `incomingCalls` | Find all callers of a function | "What calls this handler?" |
| `outgoingCalls` | Find all functions called by a function | "What does this function invoke?" |

### Combined Workflows

These workflows show how Claude uses both tools together. You don't need to specify which tool to use -- just describe what you want to know.

**Understand a codebase end-to-end:**

> "I just cloned this repo. Give me the full architecture starting from the entry points."

Claude will: (1) find entry points with `find_entries.py`, (2) trace imports with `trace.py` to get the dependency graph and hub modules, (3) use LSP `documentSymbol` on hub modules to see their contents, (4) use LSP `incomingCalls`/`outgoingCalls` on key functions to map data flow.

**Find all callers of a function:**

> "Who calls the `process_batch` function and what data do they pass?"

Claude will: (1) use `analyze.py --pattern process_batch` to find where it's defined, (2) use LSP `findReferences` to locate all call sites, (3) use LSP `hover` at each call site to see argument types.

**Trace data flow from an endpoint:**

> "When a request hits `/api/generate`, what happens step by step?"

Claude will: (1) trace from the server entry point with `trace.py` to see the module graph, (2) use LSP `goToDefinition` to find the route handler, (3) use LSP `outgoingCalls` recursively to follow the execution path from handler through service layers to data access.

**Audit a refactor:**

> "We moved the config parsing into a new module. Did we break any references?"

Claude will: (1) run `trace.py --since "3 days ago"` to see recently changed files, (2) use LSP `findReferences` on the moved symbols to verify all call sites still resolve, (3) compare the old and new traces with `compare.py` to confirm the dependency graph is intact.

### When Each Tool Wins

| Question | Best Tool |
|----------|-----------|
| "What files are in the dependency graph?" | codebase-analyzer `trace.py` |
| "Where are the entry points?" | codebase-analyzer `find_entries.py` |
| "What classes and functions exist?" | codebase-analyzer `analyze.py` |
| "Who calls this specific function?" | pyright LSP `findReferences` or `incomingCalls` |
| "What type does this return?" | pyright LSP `hover` |
| "Where is this symbol defined?" | pyright LSP `goToDefinition` |
| "Show me the full architecture" | Both: codebase-analyzer for the map, LSP for details |
| "What happens when I run this?" | Both: trace for the graph, LSP for call chains |

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
