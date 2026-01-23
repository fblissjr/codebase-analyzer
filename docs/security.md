# Security

## Context

codebase-analyzer scripts are typically invoked by an LLM (like Claude Code) that may have access to shell commands, file operations, and other tools. This document describes what the scripts themselves do - the LLM orchestrating them has broader capabilities.

## What the Scripts Do

| Property | Script Behavior |
|----------|-----------------|
| Code analysis | AST parsing (no execution of analyzed code) |
| Network access | None from scripts |
| File reads | Paths you specify |
| File writes | Only with explicit `--log` flag |
| Subprocess calls | `llmfiles` (also AST-based) |

## How Analysis Works

The scripts use Python's `ast.parse()` function, which converts source code into a syntax tree data structure. This is the same technique used by linters, formatters, and IDEs.

## Dependencies

The main external dependency is `llmfiles`, which uses a similar AST-based approach.

## What This Doesn't Cover

This documentation describes the scripts in isolation. When used as a Claude Code plugin:

- The LLM can run arbitrary shell commands
- The LLM can read/write files beyond what the scripts access
- The LLM may use other plugins or tools
- The LLM interprets the script output and decides what to do next

Review what permissions you've granted to the LLM tool invoking these scripts.
