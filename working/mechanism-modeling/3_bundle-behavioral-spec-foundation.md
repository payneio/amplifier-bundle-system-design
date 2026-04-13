# Behavioral Specification: `foundation` Bundle

> **Generated**: 2026-04-08
> **Bundle**: `foundation` (root bundle)
> **Dependency chain**: foundation > amplifier-expert-behavior > core-expert-behavior > foundation-expert-behavior > behavior-sessions > behavior-status-context > behavior-redaction > behavior-todo-reminder > behavior-streaming-ui > behavior-agents > recipes-behavior > design-intelligence-behavior > python-dev > shadow > skills-behavior > hook-shell-behavior > mcp-behavior > behavior-apply-patch > browser-testing-behavior > superpowers-methodology-behavior > routing-matrix > behavior-logging > lsp-python > python-dev-behavior > behavior-modes > behavior-python-lsp > python-quality-behavior > behavior-lsp-core

---

## Part 1: Component Inventory

### 1.1 Bundles (Behaviors)

Behaviors are composable capability units. The `includes:` chain in the root bundle determines which behaviors are active. Later includes override earlier ones.

| # | Name | Origin Bundle | Type | Includes / Nests | Description |
|---|------|--------------|------|------------------|-------------|
| 1 | `behavior-agents` | foundation | behavior | context: delegation-instructions, multi-agent-patterns; agents: (none directly); tool: tool-delegate, tool-skills | Agent orchestration with enhanced delegate tool, two-parameter context inheritance |
| 2 | `behavior-amplifier-dev` | foundation | behavior | context: ecosystem-map, dev-workflows, testing-patterns; agents: ecosystem-expert | Amplifier multi-repo development workflows |
| 3 | `foundation-expert-behavior` | foundation | behavior | context: bundle-awareness; agents: foundation-expert | Expert consultant for bundle composition and agent authoring |
| 4 | `behavior-logging` | foundation | behavior | hooks: hooks-logging | Session logging to JSONL files |
| 5 | `behavior-progress-monitor` | foundation | behavior | hooks: hooks-progress-monitor | Detects analysis paralysis and injects corrective prompts |
| 6 | `behavior-redaction` | foundation | behavior | hooks: hooks-redaction | Redacts secrets and PII from logs |
| 7 | `behavior-sessions` | foundation | behavior | hooks: hooks-session-naming; agents: session-analyst; nests: behavior-logging | Session management, naming, analysis, debugging |
| 8 | `behavior-shadow-amplifier` | foundation | behavior | agents: amplifier-smoke-test; nests: shadow (external) | Amplifier-specific shadow environment support |
| 9 | `behavior-status-context` | foundation | behavior | hooks: hooks-status-context | Injects environment and git status into agent context |
| 10 | `behavior-streaming-ui` | foundation | behavior | hooks: hooks-streaming-ui | Streaming UI for thinking blocks, tool calls, token usage |
| 11 | `behavior-tasks` | foundation | behavior | context: delegation-instructions, multi-agent-patterns; tool: tool-task | Legacy task tool (prefer behavior-agents for new work) |
| 12 | `behavior-todo-reminder` | foundation | behavior | tool: tool-todo; hooks: hooks-todo-reminder, hooks-todo-display | Todo tracking with automatic context reminders |
| 13 | `amplifier-expert-behavior` | amplifier-expert-behavior | behavior | context: ecosystem-overview; agents: amplifier:amplifier-expert | Ecosystem-wide Amplifier consultant |
| 14 | `core-expert-behavior` | core-expert-behavior | behavior | context: release-mandate; agents: core:core-expert | Kernel internals consultant |
| 15 | `recipes-behavior` | recipes-behavior | behavior | context: recipe-awareness; agents: recipe-author, result-validator; tool: tool-recipes | Multi-step YAML recipe orchestration |
| 16 | `design-intelligence-behavior` | design-intelligence-behavior | behavior | agents: design-system-architect, component-designer, animation-choreographer, layout-architect, art-director, responsive-strategist, voice-strategist | Design system agents (no tools/context) |
| 17 | `python-dev-behavior` | python-dev | composite | nests: behavior-python-lsp, python-quality-behavior | Comprehensive Python development |
| 18 | `behavior-python-lsp` | python-dev | behavior | context: python-lsp; agents: code-intel; tool: tool-lsp; nests: behavior-lsp-core | Python LSP intelligence |
| 19 | `python-quality-behavior` | python-dev | behavior | context: python-dev-instructions; agents: python-dev; tool: tool-python-check; hooks: hooks-python-check | Python code quality (ruff, pyright) |
| 20 | `shadow` | shadow | behavior | (empty - agents/tools inherited) | Generic shadow environment base |
| 21 | `skills-behavior` | skills-behavior | behavior | context: skills-instructions; tool: tool-skills | Full skills support with curated collection |
| 22 | `behavior-apply-patch` | behavior-apply-patch | behavior | context: editing-guidance; tool: tool-apply-patch | V4A diff-based file editing |
| 23 | `browser-testing-behavior` | browser-testing-behavior | behavior | context: browser-awareness; agents: browser-operator, browser-researcher, visual-documenter | Browser automation for web interaction |
| 24 | `superpowers-methodology-behavior` | superpowers-methodology-behavior | behavior | context: philosophy, instructions, using-superpowers-amplifier, modes-instructions; agents: implementer, spec-reviewer, code-quality-reviewer, code-reviewer, brainstormer, plan-writer; tool: tool-mode, tool-skills; hooks: hooks-mode; nests: behavior-modes | TDD + subagent-driven development methodology |
| 25 | `routing` | routing-matrix | behavior | context: routing-instructions, role-definitions; hooks: hooks-routing | Model routing matrix (13 roles) |
| 26 | `behavior-modes` | behavior-modes | behavior | context: modes-instructions; tool: tool-mode; hooks: hooks-mode, hooks-approval | Generic mode system for runtime behavior |
| 27 | `behavior-lsp-core` | behavior-lsp-core | behavior | context: lsp-general; agents: code-navigator; tool: tool-lsp | LSP core intelligence |

### 1.2 Modes

All modes are provided by `superpowers-methodology-behavior`. Default action is `block` for all (unlisted tools are blocked). `allow_clear` is `false` for all except `finish`.

| Mode | Shortcut | Safe Tools | Warn Tools | Confirm Tools | Transitions To | Purpose |
|------|----------|-----------|------------|---------------|----------------|---------|
| `brainstorm` | `brainstorm` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes, bash | (none) | (none) | write-plan, debug | Design refinement through collaborative dialogue |
| `write-plan` | `write-plan` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash | (none) | execute-plan, brainstorm, debug | Create detailed TDD implementation plan |
| `execute-plan` | `execute-plan` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash | (none) | verify, debug, brainstorm, write-plan | Orchestrate subagent-driven development pipeline |
| `debug` | `debug` | read_file, glob, grep, load_skill, LSP, python_check, delegate, bash | (none) | (none) | verify, brainstorm, execute-plan | Systematic 4-phase debugging |
| `verify` | `verify` | read_file, glob, grep, bash, LSP, python_check, load_skill | write_file, edit_file, delegate | (none) | finish, debug, execute-plan, brainstorm, write-plan | Evidence-based completion verification |
| `finish` | `finish` | read_file, glob, grep, bash, delegate, recipes, LSP, python_check, load_skill | write_file, edit_file | (none) | execute-plan, brainstorm | Branch completion (merge/PR/keep/discard) |

**Key restrictions across ALL modes:**
- `write_file` and `edit_file` are **blocked** in brainstorm, write-plan, execute-plan, and debug (forces delegation)
- `git push`, `git merge`, `gh pr create` are **prohibited** in all modes except finish
- Mode transitions require two calls (first denied by gate policy, second confirms)

### 1.3 Agents

| # | Agent | Origin | Model Role | Trigger Summary | Tool Modules |
|---|-------|--------|------------|-----------------|--------------|
| 1 | `amplifier-smoke-test` | foundation | fast | After shadow-operator creates shadow; validates Amplifier changes with scored rubric | tool-bash, tool-filesystem |
| 2 | `bug-hunter` | foundation | coding, general | User reports errors, unexpected behavior, or test failures; hypothesis-driven debugging | tool-filesystem, tool-search, tool-bash, tool-lsp |
| 3 | `ecosystem-expert` | foundation | general | Multi-repo coordination, cross-repo workflows, ecosystem architecture questions | tool-bash, tool-filesystem, tool-search |
| 4 | `explorer` | foundation | general | Broad multi-file exploration, codebase survey, documentation gathering | tool-filesystem, tool-search, tool-lsp |
| 5 | `file-ops` | foundation | fast | Targeted file read/write/edit/find/search on known files | tool-filesystem, tool-search |
| 6 | `foundation-expert` | foundation | general | Bundle composition, agent authoring, pattern guidance, philosophy decisions | tool-filesystem, tool-search |
| 7 | `git-ops` | foundation | fast | All git/GitHub operations: commits, PRs, branches, repo discovery | tool-bash, tool-filesystem |
| 8 | `integration-specialist` | foundation | general | External API/MCP integration, dependency audits, security/compatibility | tool-filesystem, tool-search, tool-bash, tool-web |
| 9 | `modular-builder` | foundation | coding, general | Complete spec exists with file paths, interfaces, pattern, criteria; implementation only | tool-filesystem, tool-search, tool-bash, tool-lsp |
| 10 | `post-task-cleanup` | foundation | fast | After todo list or major task completion; codebase hygiene review | tool-filesystem, tool-search, tool-bash |
| 11 | `security-guardian` | foundation | security-audit, critique, general | Before production deployment, after user data features, third-party integrations | tool-filesystem, tool-search, tool-bash, tool-web |
| 12 | `session-analyst` | foundation | fast | Session failures, events.jsonl analysis, transcript repair/rewind, session search | tool-filesystem, tool-search, tool-bash |
| 13 | `shell-exec` | foundation | fast | Shell command execution: builds, tests, package management, system admin | tool-bash |
| 14 | `test-coverage` | foundation | coding, general | New features, after bug fixes, test reviews; coverage analysis and test generation | tool-filesystem, tool-search, tool-bash, tool-lsp |
| 15 | `web-research` | foundation | fast | External documentation, library research, web searches | tool-web |
| 16 | `zen-architect` | foundation | reasoning, general | Code planning, architecture, review; creates specs for modular-builder | tool-filesystem, tool-search, tool-lsp |
| 17 | `code-intel` | python-dev | (default) | Complex Python LSP navigation: call graphs, type hierarchies, inferred types | tool-lsp |
| 18 | `python-dev` | python-dev | (default) | Python code quality checks (ruff, pyright), debugging Python-specific issues | tool-python-check |
| 19 | `shadow-operator` | shadow | (default) | Testing local git changes in isolation, multi-repo validation, clean-state testing | (inherits from parent) |
| 20 | `shadow-smoke-test` | shadow | (default) | Independent validation after shadow-operator creates environment; scored PASS/FAIL | (inherits from parent) |
| 21 | `brainstormer` | superpowers | (default) | After brainstorm-mode conversation validates design; writes formal design doc | tool-filesystem, tool-bash |
| 22 | `code-quality-reviewer` | superpowers | (default) | After spec-reviewer approves; assesses code quality, error handling, design | tool-filesystem, tool-bash, tool-search, tool-python-check |
| 23 | `code-reviewer` | superpowers | critique, reasoning, general | Branch/feature ready for pre-PR holistic review across all tasks | tool-filesystem, tool-bash, tool-search |
| 24 | `implementer` | superpowers | (default) | Single task from implementation plan; strict TDD RED-GREEN-REFACTOR | tool-filesystem, tool-bash, tool-search, tool-python-check |
| 25 | `plan-writer` | superpowers | (default) | After write-plan-mode conversation; formats validated plan as formal TDD document | tool-filesystem, tool-search |
| 26 | `spec-reviewer` | superpowers | (default) | After implementer completes task; verifies spec compliance line-by-line | tool-filesystem, tool-bash, tool-search, tool-python-check |

**Agents referenced in behaviors but defined externally (not in manifest):**

| Agent | Origin Bundle | Referenced By |
|-------|--------------|--------------|
| `amplifier:amplifier-expert` | amplifier | amplifier-expert-behavior |
| `core:core-expert` | amplifier-core | core-expert-behavior |
| `lsp:code-navigator` | amplifier-bundle-lsp | behavior-lsp-core |
| `recipes:recipe-author` | amplifier-bundle-recipes | recipes-behavior |
| `recipes:result-validator` | amplifier-bundle-recipes | recipes-behavior |
| `design-intelligence:design-system-architect` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:component-designer` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:animation-choreographer` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:layout-architect` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:art-director` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:responsive-strategist` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `design-intelligence:voice-strategist` | amplifier-bundle-design-intelligence | design-intelligence-behavior |
| `browser-tester:browser-operator` | amplifier-bundle-browser-tester | browser-testing-behavior |
| `browser-tester:browser-researcher` | amplifier-bundle-browser-tester | browser-testing-behavior |
| `browser-tester:visual-documenter` | amplifier-bundle-browser-tester | browser-testing-behavior |

### 1.4 Skills

| # | Skill | Origin Bundle | Context Mode | User Invocable | Model Role | Purpose |
|---|-------|--------------|-------------|----------------|------------|---------|
| 1 | `bundle-to-dot` | foundation | (default) | No | (default) | V3 bundle documentation: DOT diagram generation, freshness tracking |
| 2 | `creating-amplifier-modules` | foundation | (default) | No | (default) | mount() contract, protocol compliance, module directory structure |
| 3 | `adapt-skill` | amplifier-bundle-skills | (default) | No | general | Port skills from Claude Code/Cursor/etc. to Amplifier SKILL.md |
| 4 | `code-review` | amplifier-bundle-skills | (default) | **Yes** | critique | Three parallel review agents (reuse, quality, efficiency) then fix |
| 5 | `crusty-old-engineer` | amplifier-bundle-skills | (default) | No | (default) | Skeptical engineering advisor for architecture decisions |
| 6 | `image-vision` | amplifier-bundle-skills | (default) | No | (default) | LLM vision API wrapper scripts for image analysis |
| 7 | `mass-change` | amplifier-bundle-skills | (default) | **Yes** | reasoning | Parallel worker agents each open a PR for large-scale changes |
| 8 | `session-debug` | amplifier-bundle-skills | (default) | **Yes** | general | Diagnose current session issues via session-analyst delegation |
| 9 | `skillify` | amplifier-bundle-skills | (default) | No | general | Capture repeatable process into SKILL.md from conversation |
| 10 | `skills-assist` | amplifier-bundle-skills | (default) | No | general | Authoritative consultant on skill authoring conventions |
| 11 | `brainstorming` | superpowers | (default) | No | (default) | Mandatory design exploration before creative work |
| 12 | `dispatching-parallel-agents` | superpowers | (default) | No | (default) | One agent per independent problem domain in parallel |
| 13 | `executing-plans` | superpowers | (default) | No | (default) | Sequential plan execution with verification checkpoints |
| 14 | `finishing-a-development-branch` | superpowers | (default) | No | (default) | Verify tests, present 4 options (merge/PR/keep/discard) |
| 15 | `receiving-code-review` | superpowers | (default) | No | (default) | Evaluate review feedback with rigor, push back when warranted |
| 16 | `requesting-code-review` | superpowers | (default) | No | (default) | Dispatch code-reviewer subagent with crafted context |
| 17 | `subagent-driven-development` | superpowers | (default) | No | (default) | Fresh agent per task + mandatory two-stage review |
| 18 | `systematic-debugging` | superpowers | (default) | No | (default) | 4-phase root cause debugging (investigate, analyze, hypothesize, fix) |
| 19 | `test-driven-development` | superpowers | (default) | No | (default) | Strict RED-GREEN-REFACTOR cycle enforcement |
| 20 | `using-git-worktrees` | superpowers | (default) | No | (default) | Isolated git worktrees with smart directory selection |
| 21 | `using-superpowers` | superpowers | (default) | No | (default) | Mandatory skill-check before every response |
| 22 | `verification-before-completion` | superpowers | (default) | No | (default) | Fresh proof required before any success claim |
| 23 | `writing-plans` | superpowers | (default) | No | (default) | No-placeholder TDD implementation plans |
| 24 | `writing-skills` | superpowers | (default) | No | (default) | TDD for skill authoring (RED-GREEN-REFACTOR on skills) |
| 25 | `integration-testing-discipline` | superpowers-methodology-behavior | (default) | No | (default) | E2E testing: observe first, fix in batches, no mid-run fixes |
| 26 | `sdd-walkthrough` | superpowers-methodology-behavior | (default) | No | (default) | 5 realistic SDD task scenarios with delegate() patterns |
| 27 | `superpowers-reference` | superpowers-methodology-behavior | (default) | No | (default) | Complete reference tables for modes, agents, recipes, anti-patterns |

### 1.5 Recipes

| # | Recipe | Origin | Execution Mode | Steps | Has Approval Gates | Key Agents Used |
|---|--------|--------|---------------|-------|--------------------|-----------------|
| 1 | `generate-bundle-docs` | foundation | flat | 4 | No | zen-architect (enhance step) |
| 2 | `validate-agents` | foundation | flat | 12 | No | zen-architect (quality, tool analysis, report) |
| 3 | `validate-bundle-repo` | foundation | flat | 27 | No | zen-architect (approval, composition, conventions, enhance, report) |
| 4 | `validate-bundle` | foundation | flat | 4 (foreach) | No | zen-architect (report); sub-recipe: validate-single-bundle |
| 5 | `validate-single-bundle` | foundation | flat | 3 | No | zen-architect (report) |
| 6 | `brainstorming` | superpowers | **staged** | 0 (human-in-loop) | Yes (implicit) | brainstormer |
| 7 | `executing-plans` | superpowers | **staged** | 0 (human-in-loop) | Yes (implicit) | implementer, spec-reviewer, code-quality-reviewer |
| 8 | `finish-branch` | superpowers | **staged** | 0 (human-in-loop) | Yes (implicit) | code-reviewer |
| 9 | `git-worktree-setup` | superpowers | **staged** | 0 (human-in-loop) | Yes (implicit) | (none) |
| 10 | `subagent-driven-development` | superpowers | **staged** | 0 (foreach per task) | Yes (implicit) | implementer, spec-reviewer, code-quality-reviewer |
| 11 | `superpowers-full-development-cycle` | superpowers | **staged** | 0 (meta-recipe) | Yes (implicit) | All superpowers agents |
| 12 | `validate-implementation` | superpowers | **staged** | 0 (single-pass) | Yes (implicit) | spec-reviewer, code-quality-reviewer |
| 13 | `writing-plans` | superpowers | **staged** | 0 (human-in-loop) | Yes (implicit) | plan-writer |

**Note:** Staged superpowers recipes show 0 steps in the manifest because they use approval gates for human-in-loop control; the actual step logic is driven by mode instructions and agent delegation within each stage.

### 1.6 Context Files

| # | Context File | Origin | Always Loaded | Loaded By |
|---|-------------|--------|--------------|-----------|
| 1 | `CONTEXT_POISONING.md` | foundation | No | On-demand by agents |
| 2 | `IMPLEMENTATION_PHILOSOPHY.md` | foundation | **Yes** (via root system) | Most agents via @mention |
| 3 | `ISSUE_HANDLING.md` | foundation | **Yes** (via root system) | zen-architect, bug-hunter, modular-builder |
| 4 | `KERNEL_PHILOSOPHY.md` | foundation | **Yes** (via root system) | zen-architect, modular-builder, ecosystem-expert |
| 5 | `LANGUAGE_PHILOSOPHY.md` | foundation | **Yes** (via root system) | All agents via @mention |
| 6 | `MODULAR_DESIGN_PHILOSOPHY.md` | foundation | **Yes** (via root system) | Most agents via @mention |
| 7 | `POLYGLOT_BUNDLES.md` | foundation | No | On-demand |
| 8 | `agents/delegation-instructions.md` | foundation | **Yes** (via behavior-agents) | Root session orchestrator |
| 9 | `agents/multi-agent-patterns.md` | foundation | **Yes** (via behavior-agents) | Root session orchestrator |
| 10 | `agents/session-repair-knowledge.md` | foundation | No | session-analyst (eager @mention) |
| 11 | `agents/session-storage-knowledge.md` | foundation | No | session-analyst (eager @mention) |
| 12 | `amplifier-dev/dev-workflows.md` | foundation | **Conditional** (via behavior-amplifier-dev) | ecosystem-expert |
| 13 | `amplifier-dev/ecosystem-map.md` | foundation | **Conditional** (via behavior-amplifier-dev) | ecosystem-expert |
| 14 | `amplifier-dev/testing-patterns.md` | foundation | **Conditional** (via behavior-amplifier-dev) | ecosystem-expert |
| 15 | `amplifier-shadow-tests.md` | foundation | No | amplifier-smoke-test (eager) |
| 16 | `bundle-awareness.md` | foundation | **Conditional** (via foundation-expert-behavior) | Root session (thin pointer) |
| 17 | `shared/AWARENESS_INDEX.md` | foundation | **Yes** (via common-system-base) | Root session |
| 18 | `shared/PROBLEM_SOLVING_PHILOSOPHY.md` | foundation | **Yes** (via root system) | All agents via @mention |
| 19 | `shared/common-agent-base.md` | foundation | **Yes** (via all agents) | Every agent |
| 20 | `shared/common-system-base.md` | foundation | **Yes** (root session base) | Root session |
| 21 | `PYTHON_BEST_PRACTICES.md` | python-dev | No | python-dev agent (eager) |
| 22 | `python-dev-instructions.md` | python-dev | **Conditional** (via python-quality-behavior) | python-dev agent |
| 23 | `python-lsp.md` | python-dev | **Conditional** (via behavior-python-lsp) | code-intel agent |
| 24 | `philosophy.md` | superpowers | **Conditional** (via superpowers-methodology) | All superpowers agents |
| 25 | `instructions.md` | superpowers | **Conditional** (via superpowers-methodology) | Root (mode/skill check mandate) |
| 26 | `using-superpowers-amplifier.md` | superpowers | **Conditional** (via superpowers-methodology) | Root (skill check mandate) |
| 27 | `tdd-depth.md` | superpowers | No | implementer (eager) |
| 28 | `shared-anti-rationalization.md` | superpowers | No | Modes: brainstorm, debug, execute-plan |
| 29 | `spec-document-review-prompt.md` | superpowers | No | brainstorm mode (Phase 6) |
| 30 | `debugging-techniques.md` | superpowers | No | debug mode (eager) |
| 31 | `verification-failure-memories.md` | superpowers | No | verify mode (eager) |
| 32 | `visual-companion-guide.md` | superpowers | No | brainstorm mode (Phase 1.5) |
| 33 | `routing-instructions.md` | routing-matrix | **Conditional** (via routing behavior) | Agent authors, delegation |
| 34 | `role-definitions.md` | routing-matrix | **Conditional** (via routing behavior) | Agent authors, delegation |

---

## Part 2: Relationship Graph

### 2.1 Mode Transition State Machine

```
                           ┌──────────────────────┐
                           │    (no mode active)   │
                           │   Default operation   │
                           └──────────┬────────────┘
                                      │ user says "build X" / /brainstorm
                                      ▼
                          ┌───────────────────────┐
                     ┌───▶│      brainstorm        │◀──────────────────────┐
                     │    │  Design refinement      │                      │
                     │    └──────┬───────────┬──────┘                      │
                     │           │           │                             │
                     │   design  │    bug    │                             │
                     │   ready   │  found    │                             │
                     │           ▼           ▼                             │
                     │    ┌────────────┐ ┌────────┐                        │
                     │    │ write-plan │ │ debug  │◀───────────────┐       │
                     │    │ TDD tasks  │ │ 4-phase│               │       │
                     │    └──┬───┬──┬──┘ └──┬──┬──┘               │       │
                     │       │   │  │       │  │                  │       │
                     │  plan │   │  │ fixed │  │ design           │       │
                     │  done │   │  │       │  │ flaw             │       │
                     │       ▼   │  │       ▼  │                  │       │
                     │  ┌──────────┐│  ┌────────┐                 │       │
                     │  │execute-  ││  │ verify  │                │       │
                     │  │plan      ││  │Evidence │                │       │
                     │  │Subagent  ││  │ checks  │                │       │
                     │  │pipeline  ││  └──┬──┬───┘                │       │
                     │  └──┬──┬──┬─┘│     │  │                   │       │
                     │     │  │  │  │     │  │ fail              │       │
                     │     │  │  │  │     │  └────────────────────┘       │
                     │     │  │  │  │     │                               │
                     │     │  │  │  │     │ pass                          │
                     │     │  │  │  │     ▼                               │
                     │     │  │  │  │  ┌────────┐                         │
                     └─────┘  │  │  │  │ finish │─────────────────────────┘
                       spec   │  │  │  │Merge/PR│      (more work needed)
                      ambig.  │  │  └──│        │
                              │  │     └───┬────┘
                              │  │         │
                              │  │     mode cleared
                              │  │    (session done)
                              │  │
                              │  └──── bug found ──▶ debug
                              │
                              └──── missing prereq ──▶ write-plan
```

**Transition Rules:**
- `brainstorm` → `write-plan` (golden path: design approved) | `debug` (bug mentioned)
- `write-plan` → `execute-plan` (golden path: plan saved) | `brainstorm` (incomplete design) | `debug`
- `execute-plan` → `verify` (golden path: all tasks done) | `debug` (bug found) | `brainstorm` (spec ambiguous) | `write-plan` (missing prereq)
- `debug` → `verify` (golden path: fix verified) | `brainstorm` (design flaw) | `execute-plan` (more implementation needed)
- `verify` → `finish` (golden path: all evidence collected) | `debug` (verification fails) | `execute-plan` (missing tests) | `brainstorm` (missing feature) | `write-plan` (missing feature needing design)
- `finish` → `execute-plan` (tests failing) | `brainstorm` (more work) | **(cleared)** (session complete)

**Gate Policy:** All transitions require calling `mode(operation='set', name='<target>')` twice. The first call is denied by the gate policy; the second call confirms the transition.

### 2.2 Agent Delegation Map

This shows which agents delegate to which other agents, and under what conditions.

#### Root Session Delegation (delegation-instructions.md)

The root session operates in DELEGATE mode by default. These are **mandatory** delegations:

```
Root Session (orchestrator)
  │
  ├──▶ foundation:explorer ─────── when: >2 files need reading, codebase survey
  ├──▶ foundation:zen-architect ── when: architectural decisions needed
  ├──▶ foundation:modular-builder ─ when: implementation with complete spec
  ├──▶ foundation:bug-hunter ────── when: errors, unexpected behavior, test failures
  ├──▶ foundation:git-ops ────────── when: ANY git operation (commit, PR, push)
  ├──▶ foundation:session-analyst ── when: events.jsonl analysis, session repair
  ├──▶ python-dev:code-intel ────── when: code understanding, call graphs, types
  ├──▶ foundation:security-guardian  when: security review, pre-deployment
  ├──▶ foundation:web-research ──── when: external documentation lookup
  ├──▶ foundation:shell-exec ────── when: shell command execution
  └──▶ foundation:file-ops ────────── when: targeted single-file operations
```

#### Agent-to-Agent Delegation

```
zen-architect
  ├──▶ modular-builder ──── when: spec passes completeness checklist
  ├──▶ security-guardian ── when: security review needed
  ├──▶ test-coverage ────── when: test coverage work needed
  ├──▶ bug-hunter ─────────── when: validating designs work correctly
  ├──▶ post-task-cleanup ── when: codebase hygiene after tasks
  └──▶ python-dev:code-intel / lsp:code-navigator ── when: complex LSP navigation

modular-builder
  ├──▶ zen-architect ────── when: spec incomplete → STOP, return to architect
  ├──▶ explorer ──────────── when: need to explore codebase (should not happen if spec complete)
  └──▶ bug-hunter ─────────── when: need to debug issues

post-task-cleanup
  ├──▶ zen-code-architect ─ when: refactoring needed [NOTE: references "zen-code-architect" which does not exist as an agent; likely means zen-architect]
  └──▶ bug-hunter ─────────── when: bugs discovered during cleanup

explorer
  ├──▶ lsp:code-navigator ─ when: complex multi-step code navigation
  ├──▶ python-dev:code-intel when: complex Python navigation
  └──▶ bug-hunter ─────────── when: potential bugs uncovered

bug-hunter
  ├──▶ lsp:code-navigator ─ when: complex multi-step LSP navigation
  └──▶ python-dev:code-intel when: complex Python navigation

ecosystem-expert
  ├──▶ amplifier:amplifier-expert ── when: which repo owns what
  ├──▶ core:core-expert ──────────── when: kernel contract questions
  ├──▶ foundation:foundation-expert  when: bundle composition questions
  └──▶ shadow:shadow-operator ────── when: shadow environment needed

foundation-expert
  ├──▶ amplifier:amplifier-expert ── when: ecosystem-wide questions
  └──▶ core:core-expert ──────────── when: kernel contracts/protocols

shadow-operator
  └──▶ shadow-smoke-test ─── when: after shadow.create() succeeds or fails (handoff manifest)

session-analyst
  └──▶ (none - executes directly; NEVER delegates to self to avoid infinite loop)

python-dev (agent)
  └──▶ python-dev:code-intel when: semantic code navigation needed
```

#### Superpowers Pipeline Delegation (execute-plan mode)

```
execute-plan orchestrator
  │
  │  FOR EACH TASK:
  ├──▶ superpowers:implementer ──── Stage 1: implement task with TDD
  │     │
  │     └──▶ (returns DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED)
  │
  ├──▶ superpowers:spec-reviewer ── Stage 2: verify spec compliance
  │     │
  │     └──▶ (returns APPROVED | NEEDS CHANGES → re-delegate to implementer)
  │
  └──▶ superpowers:code-quality-reviewer ── Stage 3: code quality check
        │
        └──▶ (returns APPROVED | NEEDS CHANGES → re-delegate to implementer)

  Max 3 review iterations per stage before escalating to user.
```

#### Superpowers Design Pipeline (brainstorm → write-plan)

```
brainstorm mode (orchestrator owns conversation)
  │
  └──▶ superpowers:brainstormer ── Phase 5: write design doc artifact (MANDATORY delegation)
       └──▶ (writes docs/plans/YYYY-MM-DD-<topic>-design.md, commits)

write-plan mode (orchestrator owns discussion)
  │
  └──▶ superpowers:plan-writer ─── Phase 3: write plan document artifact (MANDATORY delegation)
       └──▶ (writes docs/plans/YYYY-MM-DD-<feature-name>.md)

finish mode
  │
  └──▶ superpowers:code-reviewer ── Optional holistic review before disposition
```

### 2.3 Context Loading Chain

#### Always-Loaded Context (every session)

These are loaded into the root session system prompt regardless of mode:

```
Root Session System Prompt
  ├── common-system-base.md ──────── Identity, todo discipline, validation protocol
  │    ├── @common-agent-base.md ─── Quality standards, tool policy, security
  │    └── @AWARENESS_INDEX.md ────── Ecosystem awareness, module types, doc catalog
  │
  ├── IMPLEMENTATION_PHILOSOPHY.md ─ Ruthless simplicity, cross-platform, Occam's Razor
  ├── MODULAR_DESIGN_PHILOSOPHY.md ─ Bricks & studs, regeneration over patching
  ├── LANGUAGE_PHILOSOPHY.md ────── AI-first language selection, LSP-first navigation
  ├── KERNEL_PHILOSOPHY.md ──────── Mechanism not policy, minimal kernel
  ├── ISSUE_HANDLING.md ──────────── 7-phase issue workflow
  ├── PROBLEM_SOLVING_PHILOSOPHY.md  Investigation-first, evidence-based
  │
  ├── delegation-instructions.md ──── DELEGATE by default, domain claims
  ├── multi-agent-patterns.md ─────── Parallel dispatch, sequential chains, design-first
  │
  ├── bundle-awareness.md ─────────── Thin pointer to foundation-expert (via foundation-expert-behavior)
  │
  ├── philosophy.md (superpowers) ── TDD, YAGNI, gate function, anti-rationalization
  ├── instructions.md (superpowers) ── Mode/skill check mandate before every response
  ├── using-superpowers-amplifier.md  Skill invocation mandate for Amplifier
  ├── modes-instructions.md ────────── Generic mode system documentation
  │
  ├── routing-instructions.md ─────── Model role selection guidance
  ├── role-definitions.md ──────────── 13 role definitions with decision flowchart
  │
  ├── recipe-awareness.md ──────────── Recipe orchestration awareness
  ├── skills-instructions.md ───────── Skills tool usage guidance
  └── browser-awareness.md ──────────── Browser automation awareness
```

#### Mode-Activated Context (loaded when mode is entered)

```
/brainstorm
  ├── brainstorm.md (mode file itself)
  ├── @visual-companion-guide.md ─── Phase 1.5 (on demand)
  ├── @spec-document-review-prompt.md Phase 6 (on demand)
  └── @shared-anti-rationalization.md Cross-phase reminder

/write-plan
  └── write-plan.md (mode file itself)

/execute-plan
  ├── execute-plan.md (mode file itself)
  └── @shared-anti-rationalization.md Cross-phase reminder

/debug
  ├── debug.md (mode file itself)
  ├── @debugging-techniques.md ──── Companion techniques
  └── @shared-anti-rationalization.md Cross-phase reminder

/verify
  ├── verify.md (mode file itself)
  └── @verification-failure-memories.md Cautionary failure patterns

/finish
  └── finish.md (mode file itself)
```

#### Agent-Activated Context (loaded into agent sub-sessions)

Each agent gets `common-agent-base.md` plus its own `@mentions`:

```
bug-hunter ────────── IMPLEMENTATION_PHILOSOPHY, MODULAR_DESIGN_PHILOSOPHY, ISSUE_HANDLING,
                      LANGUAGE_PHILOSOPHY, KERNEL_PHILOSOPHY, PROBLEM_SOLVING_PHILOSOPHY

zen-architect ─────── Same as bug-hunter

modular-builder ───── Same as bug-hunter

explorer ──────────── LANGUAGE_PHILOSOPHY only

foundation-expert ─── All docs/ files, all context/ files, examples/, behaviors/, agents/ (heavy context sink)

session-analyst ───── session-storage-knowledge, session-repair-knowledge

ecosystem-expert ──── ecosystem-map, dev-workflows, testing-patterns

code-intel ────────── LANGUAGE_PHILOSOPHY, python-lsp.md

python-dev (agent) ── PYTHON_BEST_PRACTICES, LANGUAGE_PHILOSOPHY

superpowers agents ── philosophy.md (superpowers), LANGUAGE_PHILOSOPHY

shadow-operator ───── shadow-instructions.md, ARCHITECTURE.md

shadow-smoke-test ─── smoke-test-rubric.md, host-only-rubric.md, agent-handoff-protocol.md
```

---

## Part 3: Expected Behavioral Logic (Scenarios)

### 3.1 Scenario: User Wants to Build a New Feature

**Entry conditions:** User says "Build X", "Add a caching layer", "I want to create a new feature", or any creative/implementation request.

```
Step 1: SKILL CHECK (mandatory)
  Mechanism: using-superpowers-amplifier.md + instructions.md
  Tool: load_skill(search="brainstorm")
  Behavior: LLM MUST check for applicable skills before responding.
  Result: brainstorming skill loaded.

Step 2: MODE SUGGESTION
  Mechanism: instructions.md
  Behavior: LLM suggests /brainstorm mode to the user.
  Output: "This looks like a new feature. I'd suggest /brainstorm to explore
           the design before implementation."

Step 3: MODE ACTIVATION (on user consent or /brainstorm slash command)
  Mechanism: mode tool
  Tool: mode(operation='set', name='brainstorm') [first call denied, second confirms]
  Restrictions: write_file BLOCKED, edit_file BLOCKED, git push BLOCKED
  Behavior: Announcement message displayed.

Step 4: BRAINSTORM PHASES 1-4
  Mechanism: brainstorm.md mode instructions
  Tool: read_file, glob, grep (explore project), delegate (optional)
  Behavior:
    Phase 1: Understand context (check files, docs, recent commits)
    Phase 1.5: Offer visual companion if visual topics (check Node.js)
    Phase 2: Ask ONE clarifying question per message (multiple-choice preferred)
    Phase 3: Propose 2-3 approaches with trade-offs, YAGNI applied
    Phase 4: Present design section-by-section (200-300 words), validate each with user

Step 5: DESIGN DOCUMENT CREATION
  Mechanism: MANDATORY delegation to superpowers:brainstormer
  Tool: delegate(agent='superpowers:brainstormer', ...)
  Behavior: Brainstormer writes docs/plans/YYYY-MM-DD-<topic>-design.md and commits.
  Restriction: Orchestrator NEVER writes the file itself.

Step 6: SPEC REVIEW
  Mechanism: brainstorm.md Phase 6
  Tool: delegate(agent=None, model_role='critique', context_depth='none')
  Behavior: 4-point self-review checklist, then antagonistic spec review (max 3 cycles).
  Decision point:
    → Approved: proceed to Phase 7
    → Issues Found: re-delegate to brainstormer with fixes, re-review

Step 7: USER APPROVAL GATE
  Mechanism: brainstorm.md Phase 7
  Behavior: Present summary, wait for explicit user approval.
  Decision point:
    → Approved: transition to write-plan
    → Changes requested: loop back to Phase 4

Step 8: TRANSITION TO WRITE-PLAN
  Mechanism: mode tool
  Tool: mode(operation='set', name='write-plan') [two calls]
  Restrictions: write_file BLOCKED, bash WARN-gated

Step 9: PLAN DISCUSSION
  Mechanism: write-plan.md mode instructions
  Behavior:
    - Check for design document from /brainstorm
    - Discuss task breakdown with user (ordering, dependencies, scope)
    - Decide file decomposition BEFORE individual tasks
    - Plans >15 tasks MUST be split into phases

Step 10: PLAN CREATION
  Mechanism: MANDATORY delegation to superpowers:plan-writer
  Tool: delegate(agent='superpowers:plan-writer', ...)
  Behavior: Plan-writer reads design, explores codebase patterns, writes detailed plan
            with TDD steps (2-5 min each) to docs/plans/YYYY-MM-DD-<feature-name>.md

Step 11: EXECUTION CHOICE
  Mechanism: write-plan.md after-plan
  Behavior: Present two options:
    A) /execute-plan mode (manual orchestration for ≤3 tasks)
    B) subagent-driven-development recipe (automated for >3 tasks)

Step 12: TRANSITION TO EXECUTE-PLAN
  Mechanism: mode tool
  Tool: mode(operation='set', name='execute-plan') [two calls]
  Restrictions: write_file BLOCKED, bash WARN-gated

Step 13: WORKSPACE ISOLATION (optional but recommended)
  Mechanism: execute-plan.md suggestions
  Tool: recipes(operation='execute', recipe_path='@superpowers:recipes/git-worktree-setup.yaml')
  Behavior: Creates isolated worktree to protect main branch.

Step 14: TASK EXECUTION PIPELINE (per task)
  Mechanism: execute-plan.md three-agent pipeline

  14a. IMPLEMENT
    Tool: delegate(agent='superpowers:implementer', context_depth='none', model_role='coding')
    Behavior: Implementer follows strict TDD (RED-GREEN-REFACTOR), makes atomic commit.
    Decision point:
      → DONE: proceed to review
      → DONE_WITH_CONCERNS: proceed, note concern
      → NEEDS_CONTEXT: STOP, provide context, re-delegate
      → BLOCKED: STOP, investigate or escalate

  14b. SPEC REVIEW
    Tool: delegate(agent='superpowers:spec-reviewer', context_depth='recent', context_scope='agents')
    Behavior: Reads actual code (not implementer report), compares to spec line-by-line.
    Decision point:
      → APPROVED: proceed to quality review
      → NEEDS CHANGES: re-delegate to implementer (max 3 iterations)

  14c. CODE QUALITY REVIEW
    Tool: delegate(agent='superpowers:code-quality-reviewer', context_depth='recent', context_scope='agents')
    Behavior: Runs test suite independently, checks clarity, error handling, design, security.
    Decision point:
      → APPROVED: mark task complete, move to next
      → NEEDS CHANGES: re-delegate to implementer (max 3 iterations)
      → 3 non-converging cycles: escalate to user

Step 15: ALL TASKS COMPLETE → TRANSITION TO VERIFY
  Mechanism: mode tool
  Tool: mode(operation='set', name='verify') [two calls]
  Restrictions: write_file WARN, edit_file WARN, delegate WARN

Step 16: VERIFICATION
  Mechanism: verify.md mode instructions
  Behavior:
    Check 1: Run FULL test suite, record exact pass/fail counts
    Check 2: Verify specific behavior with concrete example
    Check 3: Run linter, type checker, test edge cases
    Red-Green regression cycle if applicable
  Output: Structured Verification Report with VERIFIED or NOT VERIFIED verdict.
  Decision point:
    → VERIFIED: transition to /finish
    → NOT VERIFIED: transition to /debug

Step 17: TRANSITION TO FINISH
  Mechanism: mode tool
  Tool: mode(operation='set', name='finish') [two calls]
  Restrictions: write_file WARN, edit_file WARN

Step 18: BRANCH COMPLETION
  Mechanism: finish.md mode instructions
  Behavior:
    1. Run test suite (block if failing)
    2. Optional: delegate holistic review to superpowers:code-reviewer
    3. Summarize work (git log, git diff --stat)
    4. Determine base branch
    5. Present exactly 4 options: MERGE, PR, KEEP, DISCARD
    6. Execute chosen option (DISCARD requires typed confirmation)
    7. Clean up worktree (except KEEP)
  Exit: mode cleared, session complete.
```

**Total estimated agent delegations for a medium feature:** 8-20+ (brainstormer, plan-writer, N*(implementer + spec-reviewer + code-quality-reviewer), optional code-reviewer, git-ops for commits)

---

### 3.2 Scenario: User Reports a Bug

**Entry conditions:** User says "tests are failing", "I'm getting a KeyError", "something is broken", or reports any error/unexpected behavior.

```
Step 1: SKILL CHECK
  Mechanism: using-superpowers-amplifier.md
  Tool: load_skill(search="debug")
  Result: systematic-debugging skill loaded.

Step 2: MODE SUGGESTION
  Mechanism: instructions.md
  Behavior: LLM suggests /debug mode.
  Output: "This sounds like a bug. I'd suggest /debug to investigate systematically."

Step 3: MODE ACTIVATION
  Tool: mode(operation='set', name='debug') [two calls]
  Restrictions: write_file BLOCKED, edit_file BLOCKED
  Behavior: Load systematic-debugging skill instructions.

Step 4: PHASE 1 - REPRODUCE & INVESTIGATE (orchestrator does this, not agent)
  Mechanism: debug.md Phase 1
  Tools: read_file, grep, glob, bash, LSP
  Behavior:
    - Read error messages and stack traces COMPLETELY
    - Reproduce the bug consistently
    - Check recent changes (git diff, git log)
    - Gather evidence at component boundaries

  Decision point: If multi-file investigation needed →
    Tool: delegate(agent='foundation:bug-hunter', ...) for investigation-only (no fixes)

Step 5: PHASE 2 - PATTERN ANALYSIS (orchestrator)
  Mechanism: debug.md Phase 2
  Tools: read_file, grep, LSP
  Behavior:
    - Find working examples in codebase
    - Compare reference implementations COMPLETELY
    - Identify EVERY difference between working and broken
    - Understand dependencies

Step 6: PHASE 3 - HYPOTHESIS & TEST (orchestrator)
  Mechanism: debug.md Phase 3
  Tools: bash, grep
  Behavior:
    - Form single explicit hypothesis: "I think X is the root cause because Y"
    - Design minimal test (one variable at a time)
    - Run test
  Decision point:
    → Hypothesis confirmed: proceed to Phase 4
    → Not confirmed: return to Phase 1 with new information

Step 7: PHASE 4 - FIX (DELEGATE - orchestrator MUST NOT fix directly)
  Mechanism: debug.md Phase 4
  Tool: delegate(agent='foundation:bug-hunter', ...) OR delegate(agent='superpowers:implementer', ...)
  Behavior: Provide root cause, evidence, and required change to agent.
  Restriction: write_file and edit_file are BLOCKED in debug mode.

Step 8: VERIFY FIX
  Mechanism: debug.md post-fix
  Tool: bash (run tests, reproduce original scenario)
  Behavior: Orchestrator verifies fix using bash (safe tool in debug).

  Decision point:
    → Fix verified: transition to /verify
    → Fix reveals design flaw: transition to /brainstorm
    → More implementation needed: transition to /execute-plan
    → 3+ failed fixes: STOP, discuss architecture with user

Step 9: TRANSITION
  Tool: mode(operation='set', name='verify') [or other target]
```

---

### 3.3 Scenario: User Asks a Question About the Codebase

**Entry conditions:** User says "What does the event handling flow look like?", "How does authentication work?", "Show me how X connects to Y", or any exploration/understanding request.

```
Step 1: ASSESS SCOPE
  Mechanism: delegation-instructions.md
  Behavior: Determine if question requires:
    a) Single-file lookup (≤2 files) → handle directly
    b) Multi-file exploration → delegate to explorer
    c) Semantic code understanding → delegate to python-dev:code-intel
    d) Architectural analysis → delegate to zen-architect

Step 2a: SINGLE-FILE (direct handling)
  Tools: read_file, grep, LSP hover/goToDefinition
  Behavior: Read the file(s), answer directly.
  No mode needed. No delegation.

Step 2b: MULTI-FILE EXPLORATION
  Tool: delegate(agent='foundation:explorer', context_depth='none', ...)
  Instruction MUST include: primary question, scope hints (directories, file types), constraints
  Behavior: Explorer performs breadth-first sweep:
    1. Plan exploration goals (todo tool)
    2. Map terrain (filesystem listings)
    3. Deepen selectively (LSP for contracts, grep for patterns)
    4. Synthesize structured report: Overview, Key Findings (path:line), Gaps, Next Actions

Step 2c: SEMANTIC CODE UNDERSTANDING
  Tool: delegate(agent='python-dev:code-intel', ...)
  Behavior: Code-intel uses LSP operations:
    - hover for type info
    - incomingCalls/outgoingCalls for call graphs
    - findReferences for usage analysis
    - goToDefinition for navigating imports
  Returns findings with path:line references and type information.

Step 2d: ARCHITECTURAL ANALYSIS
  Tool: delegate(agent='foundation:zen-architect', ...)
  Behavior: Zen-architect uses ANALYZE or ARCHITECT mode:
    - LSP findReferences to measure coupling
    - LSP hover to document contracts
    - Produces structured analysis with options and recommendations

Step 3: SYNTHESIZE AND RELAY
  Mechanism: delegation-instructions.md rule
  Behavior: Always relay key findings in the final response text.
  Never assume user has seen tool/agent output.
```

---

### 3.4 Scenario: User Wants to Run a Recipe

**Entry conditions:** User says "run the validation recipe", "validate my bundle", "execute this recipe", or references a recipe by name.

```
Step 1: IDENTIFY RECIPE
  Mechanism: recipes-behavior (recipe-awareness.md)
  Behavior: Match user intent to available recipe.

Step 2: EXECUTE RECIPE
  Tool: recipes(operation='execute', recipe_path='<path>', context={...})
  Behavior: Recipe engine takes over orchestration.

  For FLAT recipes (e.g., validate-bundle-repo):
    - Steps execute sequentially
    - Bash steps run deterministically
    - Agent steps (zen-architect) handle LLM analysis
    - Conditions control which steps run (quality-classification gates LLM analysis)
    - Data flows between steps via output variables

  For STAGED recipes (e.g., subagent-driven-development):
    - Each stage requires human approval before proceeding
    - Tool: recipes(operation='approvals') to check pending approvals
    - Tool: recipes(operation='approve', session_id='...', stage_name='...', message='...')
    - Stages may use foreach to iterate over tasks

Step 3: MONITOR PROGRESS
  Tool: recipes(operation='list') to see active sessions
  Behavior: For staged recipes, user sees approval prompts between stages.

Step 4: RECIPE COMPLETION
  Behavior: Recipe produces a final output (e.g., validation report).
  The synthesize-report step (usually zen-architect) produces the final summary.

Example - validate-bundle-repo flow:
  1. environment-check (bash) → env_check
  2. validate-all-flags (bash) → validation_flags
  3. packaging-check (bash) → packaging_check
  4. build-check (conditional on pyproject.toml) → build_check
  5. repo-discovery (bash) → discovery_results
  6. validate-all-bundles (bash) → individual_validation
  7. behavior-hygiene-validation (bash) → behavior_hygiene_results
  8. standalone-completeness-validation (bash) → standalone_completeness_results
  9. experiments-validation (bash) → experiments_validation_results
  10. context-sink-compliance (bash) → context_sink_results
  11. tool-placement-analysis (bash) → tool_placement_results
  12. validate-recipes (sub-recipe, conditional) → recipe_validation
  13. quality-classification (bash) → quality_classification
  14. [conditional] quick-approval OR composition-analysis+repo-conventions (zen-architect)
  15. bundle-doc-freshness-check (bash)
  16. bundle-doc-regen (bash + optional zen-architect enhance)
  17. synthesize-report (zen-architect) → final_report
```

---

### 3.5 Scenario: Small Task (< 20 Lines)

**Entry conditions:** User says "fix this typo", "rename this variable", "add a docstring to this function", or any clearly small, well-scoped change.

```
Step 1: SKILL CHECK (still mandatory per using-superpowers-amplifier.md)
  Tool: load_skill(search="...") — check for applicable skills
  Behavior: Recognize this is a small change. No mode needed.

Step 2: ASSESS SCOPE
  Mechanism: instructions.md exit conditions
  Behavior: Task is documentation-only, exploration, or small change (<20 lines).
  Decision: Make the change directly, then /verify.

Step 3: DIRECT IMPLEMENTATION
  Tools: read_file → edit_file (or delegate to file-ops for simple edits)
  Behavior: Make the targeted edit. No brainstorm, no plan.

Step 4: VERIFICATION
  Mechanism: verification-before-completion skill (auto-triggered before claiming done)
  Tools: bash (run affected tests), python_check (if Python)
  Behavior: Run fresh verification, read output, confirm success.

Step 5: OFFER COMMIT
  Mechanism: delegation-instructions.md
  Tool: delegate(agent='foundation:git-ops', ...) with context_depth='recent'
  Behavior: git-ops creates conventional commit with Amplifier co-author.

Total: 2-4 steps, no modes, minimal delegation.
```

---

### 3.6 Scenario: User Wants to Create a Bundle or Agent

**Entry conditions:** User says "create a new bundle", "write an agent", "add a behavior", or any bundle/agent authoring request.

```
Step 1: MANDATORY EXPERT CONSULTATION
  Mechanism: bundle-awareness.md directive
  Behavior: "BEFORE any bundle/behavior/module work, delegate to foundation:foundation-expert"
  Tool: delegate(agent='foundation:foundation-expert', ...)

Step 2: FOUNDATION-EXPERT GUIDANCE
  Mechanism: foundation-expert.md (context sink with heavy @mentions)
  Behavior: Expert provides:
    - Thin bundle pattern (don't redeclare tools/hooks)
    - Behavior composition pattern
    - Agent authoring requirements (WHY/WHEN/WHAT/HOW)
    - Context sink pattern (heavy docs in agents, thin awareness in root)
    - Working examples from examples/ catalog

Step 3: IMPLEMENTATION
  Based on expert guidance, create:
    1. Thin behavior YAML
    2. ~25-40 line awareness context file
    3. Agent file as context sink with heavy @mentions
    4. Nothing in always-loaded shared context

Step 4: VALIDATION
  Tool: recipes(operation='execute', recipe_path='@foundation:recipes/validate-agents.yaml')
  Behavior: Validates structural requirements, tool access, description quality.
```

---

## Appendix A: Orphaned and Conflicting References

### Orphaned Agent References

| Referenced Agent | Referenced By | Status |
|-----------------|--------------|--------|
| `zen-code-architect` | post-task-cleanup.md ("delegate to zen-code-architect") | **ORPHAN**: No agent named `zen-code-architect` exists. Likely intended: `zen-architect` |
| `database-architect` | zen-architect.md (exit conditions) | **ORPHAN**: No agent named `database-architect` found in any manifest |
| `api-contract-designer` | zen-architect.md (exit conditions) | **ORPHAN**: No agent named `api-contract-designer` found in any manifest |
| `foundation:analyst` | multi-agent-patterns.md | **ORPHAN**: No agent named `analyst` found; likely illustrative example |
| `foundation:architect` | multi-agent-patterns.md | **ORPHAN**: No agent named `architect` found; likely illustrative example |
| `foundation:builder` | multi-agent-patterns.md | **ORPHAN**: No agent named `builder` found; likely illustrative example |

### Cross-Reference Validation Notes

1. **shadow-operator tools**: Manifest shows empty `tool_modules: []` but behavioral extraction says it uses shadow tool operations. The shadow tool is likely inherited from the parent session or provided by the shadow bundle itself rather than declared in the agent manifest.

2. **shadow-smoke-test tools**: Same pattern — empty `tool_modules: []` but uses shadow exec commands. Tools inherited from parent.

3. **design-intelligence agents**: 7 agents declared in `design-intelligence-behavior` but none have manifest entries with behavioral extractions. These are defined in the external `amplifier-bundle-design-intelligence` bundle.

4. **browser-tester agents**: 3 agents declared in `browser-testing-behavior` but defined in external `amplifier-bundle-browser-tester`.

5. **Duplicate context loading**: `delegation-instructions.md` and `multi-agent-patterns.md` are included by BOTH `behavior-agents` and `behavior-tasks`. If both behaviors are composed, context appears twice. The `behavior-tasks` description notes it is legacy; `behavior-agents` is the recommended replacement.

6. **Mode tool duplication**: `tool-mode` is declared by both `superpowers-methodology-behavior` and `behavior-modes` (which superpowers nests). The nesting relationship means the tool is available once, but the declaration is redundant.

7. **tool-skills duplication**: Declared by both `behavior-agents` and `skills-behavior`. Same resolution via deduplication at load time.

### Behavioral Conflicts

| Conflict | Details | Resolution |
|----------|---------|------------|
| `behavior-tasks` vs `behavior-agents` | Both provide delegation context and agent orchestration | Use `behavior-agents` (recommended); `behavior-tasks` is legacy |
| Mode write restrictions vs agent capabilities | Modes block write_file/edit_file but agents have tool-filesystem | Agents run in sub-sessions with their own tool access; mode restrictions apply only to the orchestrator session |
| `using-superpowers-amplifier.md` skill-check mandate vs subagent dispatch | "Skip skill-check entirely if dispatched as a subagent" | Subagents focus on delegated task only; skill-check is root-session-only |

## Appendix B: Composition Order Effects

The dependency chain determines load order. Key ordering effects:

1. **amplifier-expert-behavior** loads early → `amplifier:amplifier-expert` agent available before foundation agents
2. **behavior-agents** loads before **superpowers-methodology-behavior** → delegation instructions available before mode system
3. **superpowers-methodology-behavior** nests **behavior-modes** → mode tool is available via nesting, not duplicate declaration
4. **python-dev-behavior** nests both **behavior-python-lsp** and **python-quality-behavior** → both code-intel and python-dev agents available together
5. **behavior-python-lsp** nests **behavior-lsp-core** → LSP tool and code-navigator agent available in Python context
6. **routing-matrix** loads after superpowers → routing instructions can reference superpowers agent model roles
7. **behavior-sessions** nests **behavior-logging** → session-analyst agent gets logging hooks automatically

## Appendix C: Model Role Usage Summary

Based on agent manifest declarations and routing-matrix guidance:

| Role | Agents Using It |
|------|----------------|
| `fast` | amplifier-smoke-test, file-ops, git-ops, post-task-cleanup, session-analyst, shell-exec, web-research |
| `coding` | bug-hunter, modular-builder, test-coverage |
| `general` | bug-hunter, ecosystem-expert, explorer, foundation-expert, integration-specialist, modular-builder, security-guardian, test-coverage |
| `reasoning` | zen-architect |
| `critique` | code-reviewer (superpowers), security-guardian |
| `security-audit` | security-guardian |
| (default/unspecified) | code-intel, python-dev, shadow-operator, shadow-smoke-test, brainstormer, code-quality-reviewer, implementer, plan-writer, spec-reviewer |

**Note:** Agents with `(default/unspecified)` model role rely on the routing matrix's fallback behavior. The `role-definitions.md` decision flowchart should be applied to assign explicit roles.
