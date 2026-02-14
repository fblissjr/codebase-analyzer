last updated: 2026-02-14

# Anthropic Skills Best Practices Guide - Full Analysis Report

> Source: "The Complete Guide to Building Skills for Claude" (30-page PDF)
> Applied to: codebase-analyzer plugin

---

## Navigation

- [Part 1: Guide Summary](#part-1-guide-summary) -- Distilled best practices from the official PDF
  - [1.1 Fundamentals](#11-fundamentals)
  - [1.2 Planning and Design](#12-planning-and-design)
  - [1.3 Technical Requirements](#13-technical-requirements)
  - [1.4 Writing Effective Skills](#14-writing-effective-skills)
  - [1.5 Testing and Iteration](#15-testing-and-iteration)
  - [1.6 Distribution and Sharing](#16-distribution-and-sharing)
  - [1.7 Patterns and Troubleshooting](#17-patterns-and-troubleshooting)
  - [1.8 Quick Checklist](#18-quick-checklist-reference-a)
- [Part 2: Codebase Analyzer Audit](#part-2-codebase-analyzer-audit) -- Findings from applying the guide
  - [2.1 Frontmatter Quality](#21-frontmatter-quality)
  - [2.2 Progressive Disclosure](#22-progressive-disclosure)
  - [2.3 Secondary Skills Analysis](#23-secondary-skills-analysis)
  - [2.4 Instruction Quality](#24-instruction-quality)
  - [2.5 Triggering Risk Assessment](#25-triggering-risk-assessment)
  - [2.6 Structural Issues](#26-structural-issues)
  - [2.7 Script Architecture](#27-script-architecture)
  - [2.8 Content Architecture](#28-content-architecture)
  - [2.9 Token Economy](#29-token-economy)
  - [2.10 Test Coverage](#210-test-coverage)
- [Part 3: Scorecard](#part-3-scorecard) -- Compliance scores per best practice
- [Part 4: What Is Working Well](#part-4-what-is-working-well)
- [Part 5: Issues by Severity](#part-5-issues-by-severity)
  - [5.1 Critical Issues](#51-critical-issues)
  - [5.2 Major Issues](#52-major-issues)
  - [5.3 Minor Issues](#53-minor-issues)
- [Part 6: Implementation Plan](#part-6-implementation-plan-with-resolution-status)
- [Part 7: Post-Implementation Review](#part-7-post-implementation-review-2026-02-14)

---

## Part 1: Guide Summary

### 1.1 Fundamentals

**What is a skill?**

A skill is a folder containing instructions that teach Claude how to handle specific tasks or workflows. It is packaged as a simple folder with:

- `SKILL.md` (required) -- Instructions in Markdown with YAML frontmatter
- `scripts/` (optional) -- Executable code (Python, Bash, etc.)
- `references/` (optional) -- Documentation loaded as needed
- `assets/` (optional) -- Templates, fonts, icons used in output

**Core design principles:**

1. **Progressive Disclosure** -- Skills use a three-level system:
   - **First level (YAML frontmatter)**: Always loaded into Claude's system prompt. Provides just enough information for Claude to know WHEN each skill should be used. Must be minimal to conserve tokens.
   - **Second level (SKILL.md body)**: Loaded only when Claude thinks the skill is relevant to the current task. Contains the full instructions and guidance.
   - **Third level (Linked files)**: Additional files bundled within the skill directory that Claude can choose to navigate and discover only as needed (references/, scripts/, etc.).

2. **Composability** -- Claude can load multiple skills simultaneously. Your skill should work well alongside others, not assume it is the only capability available.

3. **Portability** -- Skills work identically across Claude.ai, Claude Code, and API. Create a skill once and it works across all surfaces without modification, provided the environment supports any dependencies the skill requires.

**For MCP Builders: Skills + Connectors**

- MCP provides the professional kitchen (connectivity): Connects Claude to your service, provides real-time data access and tool invocation, defines what Claude can do
- Skills provide the recipes (knowledge): Teaches Claude how to use your service effectively, captures workflows and best practices, defines how Claude should do it

### 1.2 Planning and Design

**Start with use cases.** Before writing any code, identify 2-3 concrete use cases your skill should enable.

**Good use case definition format:**
```
Use Case: [Name]
Trigger: User says "[phrase]" or "[phrase]"
Steps:
1. [First action]
2. [Second action]
Result: [Expected outcome]
```

**Ask yourself:**
- What does a user want to accomplish?
- What multi-step workflows does this require?
- Which tools are needed (built-in or MCP)?
- What domain knowledge or best practices should be embedded?

**Common skill use case categories:**

| Category | Used For | Key Techniques |
|----------|----------|----------------|
| **Document & Asset Creation** | Creating consistent, high-quality output (documents, presentations, apps, designs, code) | Embedded style guides, template structures, quality checklists, no external tools needed |
| **Workflow Automation** | Multi-step processes benefiting from consistent methodology, including multi-MCP coordination | Step-by-step workflow with validation gates, templates for common structures, built-in review suggestions, iterative refinement loops |
| **MCP Enhancement** | Workflow guidance to enhance tool access an MCP server provides | Coordinates multiple MCP calls in sequence, embeds domain expertise, provides context users would otherwise need to specify, error handling for common MCP issues |

**Define success criteria:**

Quantitative metrics:
- Skill triggers on 90% of relevant queries (measure: run 10-20 test queries, track auto vs explicit invocation)
- Completes workflow in X tool calls (measure: compare with/without skill, count tool calls and tokens)
- 0 failed API calls per workflow (measure: monitor MCP server logs during test runs)

Qualitative metrics:
- Users don't need to prompt Claude about next steps
- Workflows complete without user correction
- Consistent results across sessions
- New users can accomplish tasks on first try with minimal guidance

### 1.3 Technical Requirements

**File structure:**
```
your-skill-name/
  SKILL.md                  # Required - main skill file
  scripts/                  # Optional - executable code
  references/               # Optional - documentation
  assets/                   # Optional - templates, etc.
```

**Critical rules:**

- **SKILL.md naming**: Must be exactly `SKILL.md` (case-sensitive). No variations (SKILL.MD, skill.md, etc.)
- **Skill folder naming**: Use kebab-case only (`notion-project-setup`). No spaces, no underscores, no capitals.
- **No README.md inside your skill folder**: All documentation goes in SKILL.md or references/. (Note: when distributing via GitHub, you'll still want a repo-level README for human users -- this is separate from the skill folder.)

**YAML frontmatter -- The most important part:**

The YAML frontmatter is how Claude decides whether to load your skill. Get this right.

Minimal required format:
```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

**Field requirements:**

`name` (required):
- kebab-case only
- No spaces or capitals
- Should match folder name

`description` (required):
- MUST include BOTH: What the skill does AND When to use it (trigger conditions)
- Under 1024 characters
- No XML tags (< or >)
- Include specific tasks users might say
- Mention file types if relevant

`allowed-tools` (optional):
- Restricts which tools the skill can use (e.g., `Bash(uv:*)`)

`license` (optional):
- Use if making skill open source (MIT, Apache-2.0)

`compatibility` (optional):
- 1-500 characters
- Indicates environment requirements (intended product, required system packages, network access needs)

`metadata` (optional):
- Any custom key-value pairs
- Suggested: author, version, mcp-server

**Security restrictions -- Forbidden in frontmatter:**
- XML angle brackets (< >)
- Skills with "claude" or "anthropic" in name (reserved)
- Why: Frontmatter appears in Claude's system prompt. Malicious content could inject instructions.

### 1.4 Writing Effective Skills

**The description field:**

Formula: `[What it does] + [When to use it] + [Key capabilities]`

Good examples:
```yaml
# Good - specific and actionable
description: Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for "design specs", "component documentation", or "design-to-code handoff".

# Good - includes trigger phrases
description: Manages Linear project workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".

# Good - clear value proposition
description: End-to-end customer onboarding workflow for PayFlow. Handles account creation, payment setup, and subscription management. Use when user says "onboard new customer", "set up subscription", or "create PayFlow account".
```

Bad examples:
```yaml
# Too vague
description: Helps with projects.

# Missing triggers
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

**Writing the main instructions (SKILL.md body):**

Recommended structure:
```markdown
---
name: your-skill
description: [...]
---

# Your Skill Name

## Instructions

### Step 1: [First Major Step]
Clear explanation of what happens.

Example:
  ```bash
  python scripts/fetch_data.py --project-id PROJECT_ID
  Expected output: [describe what success looks like]
  ```

### Step 2: [Next Step]
...

## Examples

### Example 1: [common scenario]
User says: "..."
Actions:
1. ...
2. ...
Result: ...

## Troubleshooting

### Error: [Common error message]
Cause: [Why it happens]
Solution: [How to fix]


**Best practices for instructions:**

1. **Be specific and actionable**
   - Good: `Run python scripts/validate.py --input {filename} to check data format. If validation fails, common issues include: Missing required fields (add them to the CSV), Invalid date formats (use YYYY-MM-DD)`
   - Bad: `Validate the data before proceeding.`

2. **Include error handling** -- Provide specific recovery steps for common errors

3. **Reference bundled resources clearly**:
   ```
   Before building queries, consult `references/api-patterns.md` for:
   - Rate limiting guidance
   - Pagination patterns
   - Error codes and handling
   ```

4. **Use progressive disclosure** -- Keep SKILL.md focused on core instructions. Move detailed documentation to `references/` and link to it. Keep SKILL.md under 5,000 words.

### 1.5 Testing and Iteration

**Three testing approaches:**
1. **Manual testing in Claude.ai** -- Run queries directly and observe behavior. Fast iteration, no setup required.
2. **Scripted testing in Claude Code** -- Automate test cases for repeatable validation across changes.
3. **Programmatic testing via skills API** -- Build evaluation suites that run systematically against defined test sets.

**Pro Tip:** Iterate on a single task before expanding. The most effective skill creators iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill.

**Recommended testing covers three areas:**

**1. Triggering tests** -- Goal: Ensure your skill loads at the right times.
- Should trigger on obvious tasks
- Should trigger on paraphrased requests
- Should NOT trigger on unrelated topics

**2. Functional tests** -- Goal: Verify the skill produces correct outputs.
- Valid outputs generated
- API calls succeed
- Error handling works
- Edge cases covered

**3. Performance comparison** -- Goal: Prove the skill improves results vs. baseline.
- Compare token usage, tool calls, user corrections with vs without skill

**Using the skill-creator skill:**
- Built into Claude.ai and available for Claude Code
- Generate skills from natural language descriptions
- Produces properly formatted SKILL.md with frontmatter
- Suggests trigger phrases and structure
- Reviews skills: flags vague descriptions, missing triggers, structural problems
- Suggests test cases based on skill's stated purpose

**Iteration based on feedback:**

Undertriggering signals:
- Skill doesn't load when it should
- Users manually enabling it
- Support questions about when to use it
- Solution: Add more detail and nuance to the description, include keywords for technical terms

Overtriggering signals:
- Skill loads for irrelevant queries
- Users disabling it
- Confusion about purpose
- Solution: Add negative triggers, be more specific

### 1.6 Distribution and Sharing

**Current distribution model (January 2026):**

Individual users:
1. Download the skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory

Organization-level:
- Admins can deploy skills workspace-wide (shipped December 18, 2025)
- Automatic updates
- Centralized management

**Using skills via API:**
- `/v1/skills` endpoint for listing and managing skills
- Add skills to Messages API requests via `container.skills` parameter
- Version control through the Claude Console
- Works with the Claude Agent SDK for building custom agents

**Recommended approach today:**
1. Host on GitHub with public repo
2. Document in your MCP repo (link to skills from MCP docs)
3. Create an installation guide

**Positioning your skill -- Focus on outcomes, not features:**

Good: "The ProjectHub skill enables teams to set up complete project workspaces in seconds -- including pages, databases, and templates -- instead of spending 30 minutes on manual setup."

Bad: "The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."

### 1.7 Patterns and Troubleshooting

**Choosing your approach: Problem-first vs. tool-first**

- **Problem-first**: "I need to set up a project workspace" -> Skill orchestrates the right MCP calls in the right sequence. Users describe outcomes; the skill handles the tools.
- **Tool-first**: "I have Notion MCP connected" -> Skill teaches Claude the optimal workflows and best practices. Users have access; the skill provides expertise.

**Pattern 1: Sequential workflow orchestration**
Use when: Multi-step processes in specific order.
Key techniques: Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

**Pattern 2: Multi-MCP coordination**
Use when: Workflows span multiple services.
Key techniques: Clear phase separation, data passing between MCPs, validation before moving to next phase, centralized error handling.

**Pattern 3: Iterative refinement**
Use when: Output quality improves with iteration.
Key techniques: Explicit quality criteria, iterative improvement, validation scripts, know when to stop iterating.

**Pattern 4: Context-aware tool selection**
Use when: Same outcome, different tools depending on context.
Key techniques: Clear decision criteria, fallback options, transparency about choices.

**Pattern 5: Domain-specific intelligence**
Use when: Skill adds specialized knowledge beyond tool access.
Key techniques: Domain expertise embedded in logic, compliance before action, comprehensive documentation, clear governance.

**Troubleshooting guide:**

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Skill won't upload | SKILL.md not named correctly / invalid YAML | Rename to exactly SKILL.md; use --- delimiters; fix YAML syntax |
| Skill never loads automatically | Description too generic or missing triggers | Rewrite description with specific user phrases; include [What]+[When] |
| Skill triggers too often | Description too broad | Add negative triggers; be more specific about scope |
| Skill loads but doesn't follow instructions | Instructions too verbose, buried, or ambiguous | Keep concise; use bullet points; put critical instructions at top; use ## Important headers; be specific not vague |
| Skill seems slow or degraded | Content too large; too many skills enabled | Move docs to references/; keep SKILL.md under 5,000 words; reduce enabled skills |

**Model "laziness" workaround:** Add explicit encouragement:
```markdown
## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```
Note: Adding this to user prompts is more effective than in SKILL.md.

### 1.8 Quick Checklist (Reference A)

**Before you start:**
- [ ] Identified 2-3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Reviewed this guide and example skills
- [ ] Planned folder structure

**During development:**
- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling)
- [ ] YAML frontmatter has --- delimiters
- [ ] name field: kebab-case, no spaces, no capitals
- [ ] description includes WHAT and WHEN
- [ ] No XML tags (< >) anywhere
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked

**Before upload:**
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)
- [ ] Compressed as .zip file

**After upload:**
- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions
- [ ] Update version in metadata

---

## Part 2: Codebase Analyzer Audit

### 2.1 Frontmatter Quality

**Current frontmatter (`skills/codebase-analyzer/SKILL.md`):**
```yaml
---
name: codebase-analyzer
description: AST-based Python codebase analysis. Use when the user wants to trace imports from a file, find entry points, understand codebase architecture, verify code does what they expect, audit untrusted code without executing it, document how code works from an entry point, or compare implementations.
allowed-tools: Bash(uv:*)
---
```

| Criterion | Status | Notes |
|-----------|--------|-------|
| Name is kebab-case | PASS | `codebase-analyzer` is correct |
| Name matches folder | PASS | Folder is `skills/codebase-analyzer/` |
| No XML tags | PASS | Clean YAML |
| Under 1024 chars | PASS | ~297 characters |
| [What]+[When]+[Capabilities] formula | PARTIAL | Has "what" and "when" but as a single run-on sentence, not structured blocks |
| Natural-language trigger phrases | WEAK | Uses formal phrasing ("trace imports"). Missing: "what does this code do", "I just cloned this", "is this safe" |
| `allowed-tools` | GOOD | Properly scoped to `uv` commands only |

**Key problem:** The description uses technical phrasing that matches how developers describe tools, not how users ask questions. Users say "what does this code do" not "trace imports from a file". The excellent natural-language triggers in the body's "When to Use" section only load at Level 2 -- AFTER Claude has already decided whether the skill is relevant. Level 1 (description) is where triggering actually happens.

**Recommended rewrite:**
```yaml
description: AST-based Python codebase analysis that traces imports, finds entry points, and extracts code structure without executing any code. Use when the user asks to understand how a codebase works, trace what code runs from an entry point, audit or verify untrusted code, find where code starts, compare implementations, document code architecture, or deep dive into a Python project. Handles questions like "what does this code actually do", "I just cloned this repo", "trace down from main.py", "I don't trust this code", or "compare my implementation to the reference".
```
(~525 chars, well under 1024 limit)

### 2.2 Progressive Disclosure

**Level 1 (Frontmatter -- always loaded):**
- Present and functional
- 297 characters -- well within limits
- Needs natural-language trigger phrases (see above)

**Level 2 (SKILL.md body -- loaded when relevant):**
- ~750 words, well under 5,000 word ceiling
- Organized: When to Use, Quick Reference, Output Format, Subagent Patterns, See Also
- Writing style is mostly imperative/reference-card -- correct per guide

**Level 3 (Linked files -- loaded on demand):**
- `workflows.md` (150 lines, ~950 words): Detailed workflow guides
- `reference.md` (139 lines, ~750 words): llmfiles flag reference
- `scripts/`: 4 Python scripts + 2 internal modules

**Assessment:** Progressive disclosure is well-implemented for the main skill. SKILL.md is lean, workflows and reference docs are properly separated. This is one of the strongest aspects of the plugin.

**Gap:** 759-line `docs/usage.md` contains excellent content (user journeys, conversation patterns, plan templates) that Claude never sees because docs/ is not linked from the skill's references. This is the single largest missed opportunity.

### 2.3 Secondary Skills Analysis

Five additional skill folders exist but are NOT registered in plugin.json:

| Folder | Lines | Has `name`? | Has `triggers:`? | Uses plugin scripts? |
|--------|-------|-------------|------------------|---------------------|
| code-exploration/ | 143 | No | Yes | No (uses llmfiles directly) |
| debugging/ | 162 | No | Yes | No (uses llmfiles directly) |
| documentation/ | 187 | No | Yes | No (uses llmfiles directly) |
| import-tracing/ | 137 | No | Yes | No (uses llmfiles directly) |
| reference-matching/ | 162 | No | Yes | No (uses llmfiles directly) |

**Critical problems:**
1. **Not registered** -- plugin.json only points to `./skills/codebase-analyzer`. These folders are dead code.
2. **Missing `name` field** -- Required per the guide. None have it.
3. **`triggers:` is not a standard field** -- The guide specifies only `name` and `description` as frontmatter fields. `triggers:` is likely silently ignored.
4. **Reference `llmfiles` directly** -- Not the plugin's scripts with `${CLAUDE_PLUGIN_ROOT}`. Different invocation model.
5. **Each has "Prerequisites" section** requiring manual `llmfiles` install -- contradicts the main skill's managed dependency model.
6. **Heavy overlap** with main skill's "When to Use" section.

**Recommendation:** Delete all 5 and merge any unique workflow content into the main skill's references.

### 2.4 Instruction Quality

| Criterion | Assessment | Notes |
|-----------|-----------|-------|
| Specific and actionable | STRONG | Concrete bash commands with exact flags |
| Error handling guidance | WEAK | Shows error JSON format but no "what to do when X fails" |
| Bundled resources referenced | STRONG | Consistent `${CLAUDE_PLUGIN_ROOT}` paths |
| Progressive disclosure | STRONG | Body lean, details in linked files |
| Writing style (imperative) | STRONG | "Trace imports", "Find entry points" |
| Examples present | STRONG | Every command has a code block |

**Missing from instructions:**
1. No prerequisite/dependency verification step (what if llmfiles isn't installed?)
2. No guidance on interpreting output (what should Claude DO with the JSON?)
3. No guidance on when NOT to use this skill (non-Python codebases, single-file scripts)
4. No error recovery guidance (how to handle each error_type)

### 2.5 Triggering Risk Assessment

**Over-triggering risk: LOW-MODERATE**
- Main skill description is fairly specific to Python analysis
- Would not fire on unrelated tasks
- If secondary skills were registered, debugging skill's triggers ("debug", "not working", "broken") would fire on virtually every debugging request

**Under-triggering risk: MODERATE**
- Description is clinical/technical
- Missing natural-language phrases users commonly use
- Key missing triggers: "what does this code do", "how does this project work", "I just cloned this", "is this safe", "walk me through the codebase", "deep dive", "what files matter"

### 2.6 Structural Issues

**Folder naming:** All PASS (kebab-case)

**Missing `references/` directory in main skill:** Guide convention is `references/` subfolder. Currently uses flat files alongside SKILL.md. The `import-tracing` skill actually follows convention with `references/llmfiles-flags.md`.

**Commands:** `plugin.json` references `"commands": "./commands"`. Only 2 of 4 scripts have command definitions:
- `commands/trace.md` -- exists
- `commands/analyze.md` -- exists
- `commands/find-entries.md` -- MISSING
- `commands/compare.md` -- MISSING

**Orphaned files:**
- 5 secondary skill folders (not registered)
- `skills/import-tracing/references/llmfiles-flags.md` (skill not registered; overlaps with main skill's reference.md)

**Duplicate `find_python_files()`:** Both `find_entries.py` and `analyze.py` define their own with slightly different exclude sets.

### 2.7 Script Architecture

**Four scripts with consistent design:**

| Script | Lines | Purpose | External Deps | Quality |
|--------|-------|---------|---------------|---------|
| trace.py | 317 | Import tracing | llmfiles CLI | 4/5 |
| find_entries.py | 323 | Entry point detection | None | 5/5 |
| analyze.py | 335 | Structure extraction | None | 5/5 |
| compare.py | 295 | Trace comparison | trace.py subprocess | 4/5 |

**Shared infrastructure (`internal/output.py`):**
```python
def emit(data, log, log_name) -> None     # JSON to stdout + optional log
def error_response(message, error_type, details) -> dict
def success_response(data, duration_ms) -> dict
class Timer                                 # Context manager for timing
```
Consistent JSON structure across all scripts -- excellent for LLM consumption.

**llmfiles_wrapper.py -- dead code:**
- Clean wrapper exists (74 lines) with `LlmfilesError` exception class
- But `trace.py` calls `subprocess.run` directly (lines 236-244)
- Duplicated error handling, wrapper never used

**Code quality issues:**
1. Hardcoded stdlib set (50+ modules manually listed, should use `sys.stdlib_module_names`)
2. Cycle detection limited to first 10 files (`files[:10]`)
3. Uses `json` not `orjson` (violates project CLAUDE.md convention)
4. Fragile regex parsing of llmfiles output
5. `--json` flag is always-on default (can never be False)

**Excellent design patterns:**
- Consistent CLI via argparse
- Pure functions separated from I/O (testable)
- AST-only analysis (no eval/exec -- security win)
- JSON stdout for machine consumption
- Parallel processing support (analyze.py --parallel)
- Relative path output for cleaner results

### 2.8 Content Architecture

**Content duplication found:**

llmfiles flags documented 3 times:
1. `skills/codebase-analyzer/reference.md` (139 lines)
2. `skills/import-tracing/SKILL.md` (orphaned)
3. `skills/import-tracing/references/llmfiles-flags.md` (orphaned)

Installation instructions documented 3 times:
1. README.md
2. docs/usage.md
3. Referenced in CHANGELOG.md

**docs/usage.md (759 lines) -- misplaced content:**

| Lines | Content | Should Be In |
|-------|---------|-------------|
| 1-38 | Installation | docs/usage.md (keep) |
| 40-64 | "How Claude Knows to Use This" | SKILL.md body |
| 74-120 | Usage examples | references/workflows.md |
| 122-250 | User journeys with branching | references/user-journeys.md |
| 262-448 | Plan templates & subagent patterns | references/plan-templates.md |
| 450-700 | Advanced coordination patterns | references/plan-templates.md |
| 700-759 | What Claude can tell you | SKILL.md body |

### 2.9 Token Economy

**What gets loaded on skill activation:**
```
SKILL.md body: ~850 words = ~1,133 tokens
```

**When Claude follows links:**
```
workflows.md: ~900 words = ~1,200 tokens
reference.md: ~800 words = ~1,067 tokens
Total reachable: ~3,400 tokens (excellent, under 5,000)
```

**Content Claude NEVER sees (wasted):**
```
5 orphaned skills: ~6,500 tokens
docs/usage.md:    ~6,000 tokens
Total waste:     ~12,500 tokens of excellent content
```

### 2.10 Test Coverage

**What exists:** Integration tests running scripts as subprocesses
- test_trace.py: Basic execution, flags, output structure, error cases
- test_find_entries.py: Entry point detection
- test_analyze.py: Structure extraction, pattern search
- test_compare.py: Trace comparison

**What is missing:**
- Unit tests for core functions (parse_llmfiles_output, build_dependency_graph, extract_structure, compare_traces)
- Edge case tests (circular deps, unicode filenames, large files)
- Tests for llmfiles_wrapper.py (completely untested -- it's unused)
- Tests for parallel processing in analyze.py
- Estimated coverage gap: ~40%

---

## Part 3: Scorecard

| Best Practice | Score | Notes |
|---------------|-------|-------|
| Progressive disclosure | 3/5 | Main skill good; orphans and misplaced content hurt |
| Description formula ([What]+[When]+[Capabilities]) | 3/5 | Has elements but lacks natural-language triggers |
| Actionable instructions | 5/5 | Clear, specific commands |
| SKILL.md under 5,000 words | 5/5 | ~850 words |
| Workflow automation pattern | 5/5 | Clear sequential and pipeline patterns |
| Folder naming (kebab-case) | 5/5 | All correct |
| plugin.json registers skills | 1/5 | Only 1 of 6 skill folders registered |
| No README in skill folders | 5/5 | Correct |
| Composability | 5/5 | Works alongside other skills |
| Error handling in instructions | 2/5 | Scripts handle errors but SKILL.md doesn't guide recovery |
| Examples provided | 4/5 | Good command examples; missing user-journey examples in SKILL.md |
| References clearly linked | 3/5 | Links exist but not in references/ subfolder; best content in docs/ not linked |

**Overall: 46/60 (77%) -- "Good foundation, needs organizational polish"**

---

## Part 4: What Is Working Well

1. **Security-first design** -- All scripts use `ast.parse()` only (no code execution). `allowed-tools: Bash(uv:*)` restricts Claude to uv commands only. Documented transparently in security.md and what-runs-on-your-machine.md.

2. **Excellent JSON output design** -- Consistent `success_response`/`error_response` pattern via shared `output.py`. Standardized `error_type` field allows Claude to take appropriate recovery action. Duration tracking for performance monitoring.

3. **Intent-based triggers in "When to Use"** -- Organized by user intent (Understand code, Verify code, Debug, Analyze structure) rather than by tool features. This is exactly what the guide recommends.

4. **Lean SKILL.md body** -- ~850 words, well under 5,000 word ceiling. Focused on reference-card style instructions. Details properly separated into linked files.

5. **Portable script paths** -- Consistent use of `${CLAUDE_PLUGIN_ROOT}` in all commands ensures the skill works across all installation scopes (per-session, user, project).

6. **Solid command definitions** -- `commands/trace.md` and `commands/analyze.md` provide parameterized Jinja-style templates with argument definitions.

7. **README is separate from SKILL.md** -- Per guide requirements. README serves human users; SKILL.md serves Claude.

8. **Comprehensive docs** -- security.md, what-runs-on-your-machine.md, and the user journeys in usage.md are thorough and well-written. The content quality is high -- it's just in the wrong locations per progressive disclosure.

---

## Part 5: Issues by Severity

### 5.1 Critical Issues

**CRITICAL-1: Description under-triggers on natural language**

- Location: `skills/codebase-analyzer/SKILL.md` line 3
- Impact: Skill fails to activate when users ask naturally ("what does this code do", "I just cloned this")
- Root cause: Technical phrasing in Level 1 description; natural-language triggers only in Level 2 body
- Fix: Rewrite description per recommended version in section 2.1

**CRITICAL-2: Five orphaned skill folders**

- Location: `skills/code-exploration/`, `skills/debugging/`, `skills/documentation/`, `skills/import-tracing/`, `skills/reference-matching/`
- Impact: Dead code confusion, invalid frontmatter, content duplication, maintenance burden
- Root cause: plugin.json only registers `./skills/codebase-analyzer`
- Fix: Delete all 5 folders, merge unique content into main skill's references/

**CRITICAL-3: Best content in wrong location (docs/usage.md)**

- Location: `docs/usage.md` (759 lines)
- Impact: ~6,000 tokens of user journeys, plan templates, and coordination patterns invisible to Claude
- Root cause: Content in docs/ rather than skill's references/
- Fix: Redistribute to `references/user-journeys.md`, `references/plan-templates.md`, and SKILL.md body

### 5.2 Major Issues

**MAJOR-1: No output interpretation guidance**

- Location: `skills/codebase-analyzer/SKILL.md`
- Impact: Claude gets JSON but no guidance on how to synthesize and present results
- Fix: Add "Interpreting Results" section (~10 lines)

**MAJOR-2: No "when NOT to use" guidance**

- Location: `skills/codebase-analyzer/SKILL.md`
- Impact: Risk of over-triggering on non-Python codebases or trivially simple scripts
- Fix: Add "Limitations" section

**MAJOR-3: Missing command definitions**

- Location: `commands/`
- Impact: `find_entries.py` and `compare.py` are less discoverable
- Fix: Create `commands/find-entries.md` and `commands/compare.md`

**MAJOR-4: No error recovery guidance in SKILL.md**

- Location: `skills/codebase-analyzer/SKILL.md`
- Impact: Claude doesn't know what to tell users when scripts fail
- Fix: Add error recovery table mapping error_type to user-facing instructions

**MAJOR-5: llmfiles_wrapper.py is dead code**

- Location: `scripts/internal/llmfiles_wrapper.py` (74 lines, never imported)
- Impact: Duplicated error handling in trace.py, inconsistent patterns
- Fix: Refactor trace.py to use the wrapper

### 5.3 Minor Issues

**MINOR-1: workflows.md and reference.md not in references/ subfolder**

- Convention: Guide recommends `references/` subdirectory for Level 3 files
- Fix: Move to `references/workflows.md` and `references/llmfiles-reference.md`

**MINOR-2: Duplicate find_python_files() implementations**

- Location: `find_entries.py` line 198 and `analyze.py` line 113 (slightly different exclude sets)
- Fix: Extract to `internal/file_utils.py`

**MINOR-3: Uses json not orjson**

- Per project CLAUDE.md convention: "Use orjson for all Python JSON serialization"
- Fix: Add orjson dependency, replace json calls (judgment call for distributable plugin)

**MINOR-4: Hardcoded stdlib module set**

- Location: `trace.py` lines 129-140 (50+ modules manually listed)
- Fix: Use `sys.stdlib_module_names` (available Python 3.10+, project requires 3.11+)

**MINOR-5: Cycle detection artificially limited**

- Location: `trace.py` line 192 (`files[:10]`)
- Fix: Remove limit or make configurable

**MINOR-6: "Subagent Patterns" naming in SKILL.md**

- "Subagent" is internal jargon
- Fix: Rename to "Advanced Patterns" or "Pipeline Patterns"

**MINOR-7: No-op --json flag**

- All scripts: `--json` is `default=True` and `store_true`, can never be False
- Fix: Remove flag or implement alternative output mode

---

## Part 6: Implementation Plan (with resolution status)

### Phase 1: Critical Fixes -- DONE (v1.2.0)

1. ~~Rewrite main skill description with natural-language trigger phrases~~ -- DONE
2. ~~Delete 5 orphaned skill folders (audit for unique content first)~~ -- DONE
3. ~~Create `references/` directory and redistribute content from docs/usage.md~~ -- DONE
4. ~~Wire up llmfiles_wrapper.py in trace.py~~ -- SUPERSEDED: v2.0.0 rewrote trace.py to import llmfiles CallTracer directly as library. Wrapper kept as subprocess fallback only. This is objectively better than the original recommendation.

### Phase 2: Major Improvements -- DONE (v2.0.0)

5. ~~Add "Interpreting Results" section to SKILL.md~~ -- DONE (8 bullet points, lines 121-131)
6. ~~Add "Limitations" section to SKILL.md~~ -- DONE (4 items, lines 166-171)
7. ~~Create missing command definitions (find-entries.md, compare.md)~~ -- DONE (67 and 89 lines respectively)
8. ~~Add error recovery guidance to SKILL.md~~ -- DONE (5 error_type mappings, lines 173-178)

### Phase 3: Code Quality -- DONE (v1.2.0 + v2.0.0)

9. ~~Replace hardcoded stdlib with sys.stdlib_module_names~~ -- DONE (trace.py line 217)
10. ~~Extract shared find_python_files to internal/file_utils.py~~ -- DONE (both analyze.py and find_entries.py import from it)
11. ~~Switch from json to orjson (per CLAUDE.md)~~ -- DONE (output.py, compare.py)
12. ~~Remove cycle detection limit~~ -- PARTIALLY DONE: analysis is unlimited, but output capped at 10 cycles via `cycles[:10]`. Defensible as output limit.
13. ~~Clean up --json flag~~ -- DONE (removed entirely; JSON is always the output format)

### Phase 4: Testing -- DONE (v2.0.0)

14. ~~Add unit tests for core functions~~ -- DONE (test_core_functions.py, 548 lines, covers find_python_files, output utilities, hub scores, cycles, trace, entries, structure extraction)
15. ~~Update CHANGELOG.md~~ -- DONE (through v2.0.1)

**Final status: 15/16 items DONE, 1 PARTIALLY DONE (defensible)**

---

## Part 7: Post-Implementation Review (2026-02-14)

### Updated Scorecard

| Best Practice | Original Score | Updated Score | Change |
|---|---|---|---|
| Progressive disclosure | 3/5 | 5/5 | +2 (orphans deleted, references/ structured, 4 linked files) |
| Description formula | 3/5 | 5/5 | +2 (natural-language triggers, example questions) |
| Actionable instructions | 5/5 | 5/5 | -- |
| SKILL.md under 5,000 words | 5/5 | 5/5 | -- |
| Workflow automation pattern | 5/5 | 5/5 | -- (now even stronger with 8 workflows) |
| Folder naming | 5/5 | 5/5 | -- |
| plugin.json registers skills | 1/5 | 5/5 | +4 (only 1 skill folder exists, registered) |
| No README in skill folders | 5/5 | 5/5 | -- |
| Composability | 5/5 | 5/5 | -- (LSP integration guidance added) |
| Error handling in instructions | 2/5 | 4/5 | +2 (5 error_type mappings; still lacks guidance for long-running traces and fallback scenarios) |
| Examples provided | 4/5 | 5/5 | +1 (user journeys, plan templates in references/) |
| References clearly linked | 3/5 | 5/5 | +2 (all in references/, all linked from See Also) |

**Updated Overall: 59/60 (98%) -- up from 46/60 (77%)**

### What Went Beyond the Audit

The v2.0.0 overhaul delivered improvements the audit didn't anticipate:

1. **Direct CallTracer library integration** -- trace.py no longer shells out to llmfiles CLI. Instead imports `CallTracer` from `llmfiles.core.import_tracer`, providing richer data (per-edge line numbers, symbol filtering, hub module scoring). Subprocess wrapper kept as fallback.

2. **Combined AST+LSP workflow guidance** -- SKILL.md lines 133-164 provide three concrete workflows combining codebase-analyzer with pyright LSP. The "When to Use Which Tool" decision table is particularly strong for helping Claude choose the right approach.

3. **analyze.py enrichment** -- Docstrings, decorators, base classes, type annotations, async detection, and return types. All properly tested. Meaningfully increases analysis depth.

4. **New trace.py flags** -- `--grep PATTERN` (content-based discovery) and `--since DATE` (recent changes). These enable new workflows documented in references/workflows.md.

5. **"How Claude Knows to Use This" section** -- SKILL.md lines 200-216 explain the plugin registration chain. Good for transparency and debugging triggering issues.

6. **Comprehensive unit tests** -- 93 tests across 5 files (1190 total test lines). Coverage gap estimated at ~40% in audit has been substantially closed.

### Remaining Items for Future Consideration

**Low effort, high polish (consider doing):**
- ~~Rename "Subagent Patterns" to "Pipeline Patterns" (MINOR-6)~~ -- DONE (2026-02-14)
- ~~Sync plugin.json version to 2.0.1~~ -- DONE (2026-02-14)

**Cleanup decisions needed:**
- ~~`agents/codebase-explorer.md` (169 lines) uses outdated `llmfiles` CLI invocation patterns and is not registered in plugin.json. Either delete or rewrite to use `${CLAUDE_PLUGIN_ROOT}` paths.~~ -- DONE: deleted. Used outdated llmfiles CLI invocations, duplicated SKILL.md triggers. Directory removed.
- ~~`AGENTS.md` was deleted (git status: `D AGENTS.md`). CLAUDE.md at project root now serves this purpose. Confirm intentional.~~ -- DONE: confirmed intentional. CLAUDE.md serves this purpose. No stale forward references found (CHANGELOG entries are historical).

**Optional polish:**
- ~~Move `pyright` from runtime dependencies to dev dependencies in pyproject.toml (it is a dev tool, not needed by the plugin scripts at runtime)~~ -- DONE: moved to `[dependency-groups.dev]`. No script imports pyright; pyright-lsp plugin installs it independently.
- Add `"cycles_truncated": true` field to trace output when cycles exceed the 10-cycle output cap
- Add tests for `llmfiles_wrapper.py` functions and `analyze_file_worker` parallel processing
- Add error guidance for long-running traces and subprocess fallback scenarios (would bring error handling to 5/5)
