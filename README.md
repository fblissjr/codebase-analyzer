# Codebase Analyzer

A Claude Code plugin for analyzing Python codebases. Ask Claude to trace imports, find entry points, and understand code structure - all without executing the code.

## Installation

```bash
git clone https://github.com/fblissjr/codebase-analyzer.git
cd codebase-analyzer
uv sync
```

Then add it to Claude Code:

```bash
claude mcp add /path/to/codebase-analyzer
```

## How It Works

This plugin extends Claude's capabilities through Claude Code's skill system:

1. **Registration**: The `.claude-plugin/plugin.json` file registers this as a Claude Code plugin
2. **Skill Loading**: Claude reads `skills/codebase-analyzer/SKILL.md` which contains:
   - **When to Use**: Triggers that tell Claude when this skill is relevant
   - **Quick Reference**: Commands Claude can run to analyze your code
3. **Automatic Activation**: When your prompt matches the triggers (like "understand this codebase" or "trace imports"), Claude knows to use these tools

This means you don't need magic keywords - phrases like "I don't trust this code" or "what does this actually do" will trigger the analyzer because they match the intent-based triggers.

See [How Claude Knows to Use This](docs/usage.md#how-claude-knows-to-use-this) for the full explanation.

## Usage

Just ask Claude. Examples:

> "I just cloned this repo. Can you tell me where the code starts and what it does?"

> "Document every granular detail of how this code works starting from `main.py`"

> "I'm not sure the code we wrote yesterday is doing what we think. Can you trace through it and verify?"

> "Compare my implementation against the reference - am I missing anything?"

> "Trace down from `pipeline.py` and exhaustively analyze every module it touches"

See the [Usage Guide](docs/usage.md) for more examples.

## What It Can Do

- **Trace imports** - Follow the dependency graph from any entry point
- **Find entry points** - Discover main blocks, CLI commands, web apps
- **Analyze structure** - Extract classes and functions across files
- **Compare codebases** - Diff two implementations or traces
- **Search patterns** - Find specific named elements

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

## Documentation

- [Usage Guide](docs/usage.md) - How to use it with Claude
- [What Runs on Your Machine](docs/what-runs-on-your-machine.md) - Transparency
- [Security](docs/security.md) - Security properties

## Testing

```bash
uv run pytest
```

## License

MIT
