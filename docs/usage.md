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

## Subagents and Composability

Codebase-analyzer is designed to work with Claude's subagent system for parallel processing, plan-based workflows, and integration with other tools.

### Trigger Phrases for Automatic Activation

These phrases match the skill description and activate it automatically:

| Intent | Trigger Phrases |
|--------|-----------------|
| **Trace dependencies** | "trace imports from", "trace the dependency graph", "follow the import chain" |
| **Verify implementation** | "verify code does what", "confirm the implementation", "validate the code matches" |
| **Audit code** | "audit untrusted code", "analyze without executing", "check what this actually does" |
| **Document exhaustively** | "document how code works from", "trace down from entry point", "exhaustively analyze" |
| **Compare implementations** | "compare against reference", "diff the implementations", "what's different between" |
| **Find entry points** | "find all entry points", "where does execution start", "find CLI commands" |

---

### Subagent Patterns

#### Parallel Analysis

Spawn multiple subagents to analyze different parts of the codebase simultaneously:

> "Spawn subagents to analyze each entry point in parallel"

> "Use parallel subagents to document every module in the dependency tree"

> "Fork analysis across all CLI commands and summarize findings"

> "Trace each of the 5 entry points concurrently and report shared dependencies"

#### Fan-Out / Fan-In

Distribute work across subagents, then consolidate results:

> "Find all entry points, spawn a subagent for each to trace imports, then summarize which modules are shared vs unique"

> "Trace from main.py, identify the 10 core modules, spawn subagents to document each, then compile into architecture doc"

#### Pipeline Composition

Chain analysis steps where output of one feeds the next:

> "Trace imports -> identify external dependencies -> check each for security advisories"

> "Find entry points -> trace each -> compare traces -> identify dead code"

> "Analyze structure -> find all classes -> document inheritance hierarchy"

---

### Integration with Implementation Workflows

#### During Planning

Use codebase-analyzer to inform implementation plans:

```markdown
## Planning Phase
- Trace imports from existing entry points to understand current architecture
- Find all entry points to identify integration points for new feature
- Analyze structure to find existing patterns to follow
```

#### During Implementation

Validate as you build:

```markdown
## Implementation with Continuous Validation
1. Implement feature in `src/new_feature.py`
2. Trace imports from new file to verify it integrates correctly
3. Compare trace against planned architecture - flag deviations
4. Spawn subagent to document the new module
```

#### Post-Implementation

Verify completeness and correctness:

```markdown
## Post-Implementation Validation
- Trace from entry point to confirm new code is reachable
- Compare before/after traces to verify no regressions
- Verify documentation matches actual code paths
- Audit implementation against spec
```

---

### Plan Templates

Copy these into your implementation plans to include codebase-analyzer validation.

#### Template: Feature Implementation with Validation

```markdown
## Implementation Plan: [Feature Name]

### Phase 1: Understand Existing Code
- Trace imports from [related_entry_point] to map current architecture
- Find entry points to identify where new feature integrates
- Document existing patterns to follow

### Phase 2: Implement Feature
- Create [new_files]
- Modify [existing_files]
- Add tests

### Phase 3: Validate Implementation
- Trace imports from [new_entry_point] to verify dependency tree
- Compare against planned architecture - flag unexpected dependencies
- Spawn subagents to document each new module
- Verify code does what documentation says

### Phase 4: Final Verification
- Run full trace comparison (before vs after)
- Confirm no circular dependencies introduced
- Audit implementation matches original spec
```

#### Template: Refactoring with Safety Checks

```markdown
## Refactoring Plan: [Component]

### Pre-Refactor Baseline
- Trace imports from all entry points that touch [component]
- Save traces as baseline for comparison
- Document current dependency graph

### Refactoring Steps
- [Your refactoring steps here]

### Post-Refactor Validation
- Trace same entry points after changes
- Compare new traces against baseline
- Flag any broken dependencies or unexpected changes
- Verify all previous functionality still reachable
```

#### Template: Documentation Generation

```markdown
## Documentation Plan: [Codebase/Module]

### Discovery
- Find all entry points in [scope]
- Trace each entry point to build complete dependency map

### Parallel Documentation
- Spawn subagents to document each major module:
  - Module purpose and responsibility
  - Public API surface
  - Dependencies (internal and external)
  - Usage patterns

### Synthesis
- Compile module docs into architecture overview
- Generate dependency diagram
- Identify and document shared utilities
```

#### Template: Code Audit

```markdown
## Security/Quality Audit: [Codebase]

### Mapping Phase
- Find all entry points (main blocks, CLI, web endpoints)
- Trace each to build complete execution map
- Identify external dependencies

### Analysis Phase (Parallel Subagents)
- Subagent 1: Audit external dependencies for known vulnerabilities
- Subagent 2: Analyze code structure for anti-patterns
- Subagent 3: Verify code does what comments/docs claim
- Subagent 4: Check for dead code or unused imports

### Report
- Compile findings from all subagents
- Prioritize issues by severity
- Generate remediation recommendations
```

---

### Composing with Other Tools and Agents

Codebase-analyzer outputs JSON designed for other tools to consume. Combine with:

#### With Test Runners

> "Trace from main.py, identify all modules, then spawn subagents to verify each has test coverage"

> "Find entry points, trace their dependencies, compare against test files to find untested modules"

#### With Documentation Generators

> "Trace the dependency tree, then for each module spawn a subagent to generate docstrings"

> "Analyze structure to extract all public APIs, then generate API documentation"

#### With Code Review Agents

> "Trace imports from the changed files, spawn review subagents for each affected module"

> "Compare PR branch trace against main branch trace, review all modules that differ"

#### With Security Scanners

> "Trace external dependencies, spawn subagents to check each against vulnerability databases"

> "Audit code paths that handle user input - trace from API endpoints to data stores"

#### With Refactoring Agents

> "Analyze structure to find duplicate code patterns, spawn subagents to propose consolidations"

> "Trace imports to find circular dependencies, propose refactoring to break cycles"

---

### Multi-Agent Coordination Patterns

#### Leader-Worker Pattern

One agent coordinates, workers execute in parallel:

```
Leader: Find all entry points and categorize by type
Workers (parallel): Each worker traces one category of entry points
Leader: Synthesize findings into unified architecture doc
```

#### Verification Chain

Each agent validates the previous agent's work:

```
Agent 1: Implement feature
Agent 2: Trace imports to verify implementation
Agent 3: Compare trace against spec to verify correctness
Agent 4: Generate documentation from verified code
```

#### Competitive Analysis

Multiple agents analyze independently, compare results:

```
Agent 1: Trace from main.py with default filters
Agent 2: Trace from main.py with --all flag
Compare: Identify what the smart filter excluded and why
```

---

### Example: Full Workflow with Multiple Subagents

Here's a complete example combining planning, implementation, and validation:

```markdown
## Feature: Add User Authentication

### Phase 1: Discovery (Codebase Analyzer)
- Find all entry points to identify where auth checks should go
- Trace from `api/routes.py` to understand current request flow
- Analyze structure to find existing middleware patterns

### Phase 2: Planning
Based on analysis:
- Auth middleware goes in `middleware/auth.py` (follows existing pattern)
- Session handling in `services/session.py`
- Integration points: all route handlers in `api/`

### Phase 3: Implementation
- Implement `middleware/auth.py`
- Implement `services/session.py`
- Add auth decorators to routes

### Phase 4: Validation (Parallel Subagents)
- Subagent A: Trace from each API endpoint to verify auth middleware in path
- Subagent B: Compare new trace against Phase 1 baseline
- Subagent C: Verify session handling matches security spec
- Subagent D: Document new auth flow

### Phase 5: Final Verification
- All routes now include auth in their trace
- No unexpected dependencies introduced
- Documentation accurately reflects implementation
- Code does what it claims to do
```

---

## Real-World Scenario: Documenting a Complex ML Pipeline

This example demonstrates using codebase-analyzer to validate documentation scope before writing technical documentation for a complex codebase with multiple entry points and a central coordinator pattern.

### The Situation

You're documenting a Diffusion Transformer (DiT) video generation pipeline with:
- **Multiple entry points**: `text_to_video.py` (basic) and `text_to_video_hq.py` (high-quality with upsampling)
- **Central coordinator**: `model_registry.py` that wires together transformers, VAEs, text encoders, and optional components
- **Deep dependency tree**: The registry imports from 8+ submodules, each with their own dependencies

You've drafted a documentation outline with 8 sections, but before writing thousands of words, you need to verify your outline actually covers what the code does.

### The Challenge

The coordinator pattern is deceptively complex:

```python
# model_registry.py imports
from core.loader.weight_manager import WeightManager as Manager
from core.models.transformer import DiTModel, DiTConfigurator
from core.models.video_vae import VideoEncoder, VideoDecoder
from core.models.audio_vae import AudioDecoder, Vocoder
from core.text_encoders.llm_encoder import LLMTextEncoder
from core.models.upsampler import LatentUpsampler  # HQ pipeline only?
from core.loader.lora_utils import LoRAConfig
```

Questions before documenting:
- Does the HQ pipeline use all the same components plus upsampler, or is the flow different?
- Are there modules the registry imports that aren't used by either entry point?
- Does your 8-section outline cover every module in the actual execution path?

### The Validation Workflow

#### Step 1: Trace Both Entry Points

```markdown
## Pre-Documentation Validation

### Trace Entry Points
Trace both pipelines to understand the full dependency trees:

- Trace from `text_to_video.py` with `--all` flag to capture complete dependency tree
- Trace from `text_to_video_hq.py` with `--all` flag
- Compare the two traces to identify shared core vs. HQ-specific modules
```

**Prompt to Claude:**
> "Trace imports from `pipelines/text_to_video.py` and `pipelines/text_to_video_hq.py`. Compare the traces and tell me which modules are shared between both (the core) versus which are unique to the HQ pipeline."

#### Step 2: Verify the Coordinator Path

The registry is the heart of the system. Verify the import chain exists:

```markdown
### Verify Critical Paths

Confirm these paths appear in traces:

| Path | Expected |
|------|----------|
| Entry → Registry | Both pipelines import `model_registry.py` |
| Registry → WeightManager | `model_registry.py` → `weight_manager.py` |
| Registry → Transformer | imports from `core.models.transformer` |
| Registry → Video VAE | imports from `core.models.video_vae` |
| Registry → Audio VAE | imports from `core.models.audio_vae` |
| Registry → Text Encoder | imports from `core.text_encoders` |
| Registry → Upsampler | imports from `core.models.upsampler` (HQ only?) |
| Registry → LoRA | imports from `core.loader.lora_utils` |
```

**Prompt to Claude:**
> "Verify the traced path from `text_to_video_hq.py` includes: entry point → `model_registry.py` → `weight_manager.py`. List every module that `model_registry.py` imports and confirm each appears in the trace."

#### Step 3: Map Traces to Documentation Sections

Create a mapping table between traced modules and planned documentation:

```markdown
### Module-to-Section Mapping

| Traced Module | Documentation Section | Status |
|---------------|----------------------|--------|
| `model_registry.py` | 5. Model Loading | Covered |
| `weight_manager.py` | 5.1 Weight Loading | Covered |
| `transformer.py` | 2. DiT Architecture | Covered |
| `video_vae.py` | 3. VAE Architecture | Covered |
| `audio_vae.py` | 3. VAE Architecture | Covered |
| `llm_encoder.py` | 4. Text Conditioning | Covered |
| `upsampler.py` | ??? | GAP - needs section |
| `lora_utils.py` | 5.2 LoRA Integration | Covered |
| `scheduler.py` | ??? | GAP - not in outline |
```

**Prompt to Claude:**
> "Map every file in the trace to my documentation outline. Flag any traced modules that don't have a corresponding section, and any outline sections that don't correspond to traced code."

#### Step 4: Gap Analysis

Before writing documentation, address all gaps:

```markdown
### Gap Report

**Traced modules missing from documentation:**
- `core/models/upsampler.py` - Add Section 3.3: Latent Upsampling
- `core/inference/scheduler.py` - Add Section 6.2: Scheduler
- `core/loader/quantization.py` - Add to Section 5: FP8 handling

**Documentation sections with no traced code:**
- Section 7.3: "Multi-GPU Support" - Not found in traces, verify or remove

**Registry factory methods needing documentation:**
- `registry.transformer()` - Covered in 2.1
- `registry.video_encoder()` - Covered in 3.1
- `registry.upsampler()` - NOT COVERED - add section
```

**Prompt to Claude:**
> "Based on the gap analysis, which modules appear in the HQ trace but aren't covered by my outline? For each gap, suggest where it should be documented and what the section should cover."

### Complete Validation Prompt

Here's a single comprehensive prompt for this workflow:

> "I'm about to write technical documentation for a DiT video generation pipeline. Before I start, validate my documentation scope:
>
> 1. **Trace both entry points** at `pipelines/text_to_video.py` and `pipelines/text_to_video_hq.py` with full dependency trees
>
> 2. **Compare traces** to identify:
>    - Shared modules (core documentation everyone needs)
>    - HQ-only modules (advanced features section)
>
> 3. **Verify the coordinator path**: Both entry points → `model_registry.py` → `weight_manager.py` → all component modules
>
> 4. **Map every traced module to my documentation outline** (8 sections covering architecture, text conditioning, inference, model loading, memory optimization)
>
> 5. **Output a gap report**:
>    - Traced modules missing from my outline (need new sections)
>    - Outline sections with no traced code (verify path or remove)
>    - Registry factory methods that need explicit documentation
>
> **Gate**: Don't let me proceed with writing until gaps are resolved."

### Why This Matters

Without validation, you might:
- Write 5000 words about the transformer, miss the scheduler entirely
- Document the upsampler that only HQ uses, confuse basic pipeline users
- Claim the registry loads models a certain way when the trace shows different paths
- Miss the quantization module that's critical for memory optimization

The 30 minutes spent on trace validation saves hours of documentation rewrites.

### Outcome

After validation, your documentation structure reflects reality:

```markdown
## Documentation Structure (Validated)

### Core (Both Pipelines)
- 1. Overview
- 2. DiT Transformer Architecture
- 3. VAE Architecture (Video + Audio)
- 4. Text Conditioning Pipeline
- 5. Model Registry & Loading
- 6. Inference Pipeline
- 7. Memory Optimization

### HQ Pipeline Additions
- 8. Two-Stage Generation
- 8.1 Latent Upsampler (HQ only)
- 8.2 Refinement LoRA (HQ only)

### Removed (Not in traces)
- ~~Multi-GPU Support~~ (not implemented yet)
```

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
