# Usage Guide

This is a Claude Code plugin. You use it by asking Claude to analyze Python codebases in natural language.

## Installation

### Quick Start (per-session)

```bash
git clone https://github.com/fblissjr/codebase-analyzer.git ~/claude-plugins/codebase-analyzer
cd ~/claude-plugins/codebase-analyzer
uv sync

# Launch Claude Code with the plugin
claude --plugin-dir ~/claude-plugins/codebase-analyzer
```

### Persistent Installation

Use the marketplace for persistent installation:

```bash
# Inside Claude Code - add repo as marketplace (one-time)
/plugin marketplace add fblissjr/codebase-analyzer

# Install to your preferred scope
/plugin install codebase-analyzer@fblissjr-codebase-analyzer --scope user
```

### Installation Scopes

| Scope | Command | Effect |
|-------|---------|--------|
| Per-session | `claude --plugin-dir ./path` | Only for current session |
| User | `--scope user` | Available in all your projects |
| Project | `--scope project` | Shared with team (committed to repo) |
| Local | `--scope local` | Your project only (gitignored) |

## How Claude Knows to Use This

Understanding the mechanism helps you get better results.

### The Registration Chain

```
.claude-plugin/plugin.json    # Registers the plugin with Claude Code
    |
    v
skills/codebase-analyzer/SKILL.md    # Defines WHEN to use and HOW to use
    |
    +-- "When to Use" section    # Triggers - Claude reads these to decide relevance
    +-- "Quick Reference"        # Commands - what Claude can actually run
```

### What This Means for You

**You don't need magic keywords.** The "When to Use" section contains intent-based triggers like:
- "Understand how a Python codebase works"
- "Verify code is doing what they think"
- "Audit untrusted Python code"

So when you say "I don't trust this code - what does it actually do?", Claude recognizes this matches the verification triggers and activates the analyzer.

**Claude interprets the results.** The scripts output JSON, but Claude:
- Reads and explains the dependency graph
- Identifies architectural patterns
- Points out potential issues
- Suggests next steps

The JSON output is designed for Claude to consume and reason about, not for you to parse manually.

## How to Use It

Just ask Claude. Here are real-world examples:

### Understanding Code You Didn't Write

> "I just cloned this repo. Can you tell me where the code starts and what it does?"

> "What are all the entry points in this project?"

> "Trace the imports from `main.py` - I want to understand the dependency structure."

### Deep Documentation from an Entry Point

> "Document every granular detail of how this code works starting from `pipeline.py`"

> "Trace down from `app/main.py` and exhaustively analyze every module it touches"

> "I need to understand every nuanced detail of this codebase - start at `cli.py` and work your way through all dependencies"

> "Deep dive into the code structure starting at `src/core/engine.py` - I want to know exactly what runs and how"

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

## User Journeys

These show how analysis unfolds as a conversation, with branches based on what you find.

---

### Journey 1: "I don't trust this code - help me verify it's doing what we think"

**Starting point:** You wrote (or inherited) code and want to verify it works as intended.

**Step 1: Trace what actually runs**
> "Trace from main.py and show me what files are actually in the execution path"

Claude traces, shows the dependency graph.

**Step 2: Branch based on findings**

*If the trace looks reasonable:*
> "Compare this trace to what I expected - here's my mental model: [describe]"

Claude compares actual vs expected, highlights discrepancies.

*If there are unexpected files:*
> "Why is `utils/legacy_handler.py` in the trace? I didn't think we used that anymore"

Claude analyzes the import chain to show how it got pulled in.

*If you want deeper verification:*
> "Analyze the structure of the core modules and summarize what each one does"

Claude uses subagents to document each module's purpose.

*If you find something suspicious:*
> "That circular dependency looks wrong. Show me the exact import chain"

Claude traces the cycle and explains the problem.

**Possible endpoints:**
- Confidence report: "Yes, this does what you think"
- Issue list: "Found 3 problems - here's what to fix"
- Architecture doc: Generated documentation of what the code actually does
- Refactoring plan: "Here's how to remove that dead code path"

---

### Journey 2: "The README says run generate.py but there's 100 files in core/"

**Starting point:** New codebase, you want to understand how it actually works.

**Step 1: Find the entry point and trace it**
> "The readme says `generate.py` is the main entry point. Trace it and tell me which of the 100 files in core/ actually get used"

Claude traces, identifies the "hot path" - maybe only 23 of 100 files are actually imported.

**Step 2: Branch based on findings**

*If you want the architecture:*
> "Draw me an architecture diagram of how these 23 files relate to each other"

Claude analyzes the graph and explains the layers/modules.

*If you want to understand a specific module:*
> "What does `core/pipeline.py` do? It seems central"

Claude reads the file, analyzes its structure, explains its role.

*If you're wondering about the other 77 files:*
> "What about the other files in core/ that aren't in this trace? Are they dead code or used elsewhere?"

Claude finds other entry points, traces them, identifies which files are truly unused.

*If you want the full picture:*
> "Find all entry points in this repo, trace each one, and tell me which modules are shared vs unique to each entry point"

Claude runs parallel traces, compares graphs, shows the shared core vs specialized modules.

**Possible endpoints:**
- Architecture overview: "Here's how the codebase is organized"
- Hot path documentation: "These 23 files are what matters for generate.py"
- Dead code report: "These 15 files appear unused by any entry point"
- Module deep-dives: Detailed docs for specific modules you care about

---

### Journey 3: "Compare my implementation to the reference"

**Starting point:** You're implementing something to match a reference and want to verify completeness.

**Step 1: Compare the traces**
> "Compare my implementation in `src/` to the reference in `reference/` - what am I missing?"

Claude traces both, diffs them, shows files only in reference.

**Step 2: Branch based on findings**

*If you're missing files:*
> "I'm missing 5 files. What do those files do in the reference?"

Claude reads them, summarizes their purpose.

*If the structure differs:*
> "The import structure is different. Is mine wrong or just organized differently?"

Claude analyzes both graphs, explains the architectural differences.

*If you want to generate the missing pieces:*
> "Generate stubs for the 5 missing files based on the reference"

Claude reads reference files, generates implementation stubs.

**Possible endpoints:**
- Gap analysis: "You're missing X, Y, Z"
- Equivalence confirmation: "Your implementation covers the same functionality"
- Generated stubs: Starting points for missing implementations

---

## The Four Modes

| Mode | Description | Example |
|------|-------------|---------|
| **One-and-done** | Simple query, direct answer | "What are the entry points?" |
| **With Claude** | Analysis + interpretation | "Trace and explain the architecture" |
| **With subagents** | Parallel processing | "Document each CLI command" |
| **Composable** | Chained analysis | "Trace, find core modules, then analyze each" |

**Key insight:** The JSON output is designed for Claude to consume and act on. Each field (files, graph, classes) maps to something Claude can reason about, explain, or delegate to a subagent.

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
