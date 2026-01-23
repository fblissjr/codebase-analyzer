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

## Usage

Just ask Claude. Examples:

> "I just cloned this repo. Can you tell me where the code starts and what it does?"

> "I'm not sure the code we wrote yesterday is doing what we think. Can you trace through it and verify?"

> "Compare my implementation against the reference - am I missing anything?"

> "Find all the CLI commands, trace their imports, and summarize what each one does."

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
