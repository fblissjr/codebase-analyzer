# Usage Guide

This is a Claude Code plugin. You use it by asking Claude to analyze Python codebases in natural language.

## Installation

```bash
claude mcp add /path/to/codebase-analyzer
```

Or start Claude Code with the plugin:

```bash
claude --plugin-dir /path/to/codebase-analyzer
```

## How to Use It

Just ask Claude. Here are real-world examples:

### Understanding Code You Didn't Write

> "I just cloned this repo. Can you tell me where the code starts and what it does?"

> "What are all the entry points in this project?"

> "Trace the imports from `main.py` - I want to understand the dependency structure."

### Verifying Your Implementation

> "I'm not sure the code we wrote yesterday is doing what we think. Can you trace through it and verify it matches the original?"

> "Compare my implementation in `src/` against the reference in `reference/` - am I missing anything?"

> "We refactored the import structure. Can you confirm we didn't break any dependencies?"

### Debugging Import Issues

> "Something's wrong with my imports. Can you trace from `app.py` and show me the full dependency graph?"

> "Why isn't my module being found? Can you analyze what's actually being imported?"

### Finding Things in Large Codebases

> "Find all the CLI commands in this project."

> "Where are all the FastAPI route handlers?"

> "Search for anything with 'Config' in the name across the codebase."

### Security/Trust Verification

> "I downloaded this package but I'm not sure I trust it. Can you analyze what it actually does without running it?"

> "Trace all the imports from `setup.py` - I want to see what gets pulled in when this installs."

## Composable Prompts

The real power is chaining analysis tasks together conversationally:

> "Find all the entry points, then trace each one and tell me which files are shared across multiple entry points."

> "Analyze the structure of `src/`, then compare it to `tests/` - are there any modules without test coverage?"

> "Trace from `main.py`, identify the external dependencies, and check if any of them have known security issues."

> "Find all the Click commands, trace their imports, and summarize what each command actually does."

## What Claude Can Tell You

When you ask Claude to analyze a Python codebase, it can report:

- **Entry points**: Where code execution starts (main blocks, CLI commands, web apps)
- **Import dependencies**: What files import what, full dependency trees
- **Structure**: Classes, functions, and their signatures across files
- **Comparisons**: Differences between two codebases or traces
- **Patterns**: Finding specific named elements across the codebase

## How It Works (For the Curious)

Claude uses AST (Abstract Syntax Tree) parsing to analyze Python code *without executing it*. This means:

- Safe to analyze untrusted code
- No side effects from analysis
- Works on any valid Python syntax

See [What Runs on Your Machine](what-runs-on-your-machine.md) for full transparency on what the scripts do.
