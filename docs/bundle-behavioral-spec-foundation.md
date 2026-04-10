# Amplifier Foundation Bundle — Behavioral Specification

**Document Version:** 1.0  
**Bundle:** amplifier-foundation (Microsoft Amplifier Framework)  
**Generated:** 2026-04-10  
**Purpose:** Comprehensive behavioral and structural specification for all components in the Amplifier Foundation bundle

---

## 1. Overview

### 1.1 Bundle Identity

The **Amplifier Foundation** bundle provides the authoritative implementation framework, development tooling, multi-agent coordination patterns, design intelligence, Python development expertise, shadow environment testing, and comprehensive skill library for building production-grade AI applications on the Amplifier kernel.

### 1.2 Component Inventory

| Component Type | Count | Role |
|---|---|---|
| **Modes** | 6 | User-level workflow orchestration (brainstorm, write-plan, execute-plan, debug, verify, finish) |
| **Agents** | 14 | Specialist subagents for targeted tasks (exploration, debugging, implementation, review) |
| **Skills** | 25+ | Reusable process workflows (brainstorming, TDD, debugging, git operations) |
| **Context Files** | 15+ | Behavioral directives, philosophy, and standing orders injected into agent context |
| **Bundles** | ~8 | Sub-bundles (design-intelligence, python-dev, shadow, superpowers, routing-matrix, skills, stories) |
| **Recipes** | Multiple | Multi-step orchestrated workflows with approval gates |

### 1.3 Dependency Tree Structure

```
foundation (root)
├── amplifier-core (kernel)
├── amplifier-expert-behavior (ecosystem guidance)
├── core-expert-behavior (kernel protocol expertise)
├── foundation-expert-behavior (bundle composition expertise)
├── behavior-* (horizontal capabilities: sessions, status, todo, streaming, agents)
├── recipes-behavior (multi-step workflows)
├── design-intelligence (8 design agents)
├── python-dev (Python dev + LSP code intelligence)
├── shadow (container-based environment testing)
├── superpowers (6-mode development pipeline)
├── routing-matrix (13-role model selection system)
├── skills (25+ skill library)
└── Other modules: hook-shell, mcp, auth, logging, lsp-core
```

**Critical Path:** Core → Foundation → All other components depend on Foundation.

### 1.4 Philosophy & Foundational Principles

All components in Foundation operate under these non-negotiable principles:

1. **Ruthless Simplicity** — Every layer justifies its existence; no speculative abstractions
2. **Modular Regeneration** — Code is described and regenerated whole, not edited line-by-line
3. **Mechanism Not Policy** — The kernel provides only mechanism; modules implement policy
4. **Evidence Before Claims** — No completion claim without fresh verification output
5. **Delegation-First** — Main LLM orchestrates; specialists handle domain work
6. **Hypothesis-Driven Debugging** — Investigation before fixes; root cause not symptoms

---

## 2. Tool Governance

### 2.1 Tool Availability Matrix (Per Mode)

| Mode | Safe Tools | Warn Tools | Blocked Tools |
|---|---|---|---|
| **brainstorm** | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes, bash | — | write_file, edit_file, mode, todo, team_knowledge, apply_patch |
| **write-plan** | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash (warn) | write_file, edit_file, mode, todo, team_knowledge, apply_patch |
| **execute-plan** | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash (warn) | write_file, edit_file, mode, todo, team_knowledge, apply_patch |
| **debug** | read_file, glob, grep, load_skill, LSP, python_check, delegate, bash | — | write_file, edit_file, recipes, mode, todo, web_search, web_fetch, team_knowledge, apply_patch |
| **verify** | read_file, glob, grep, bash, LSP, python_check, load_skill | write_file, edit_file, delegate (warn) | recipes, mode, todo, web_search, web_fetch, team_knowledge, apply_patch |
| **finish** | read_file, glob, grep, bash, delegate, recipes, LSP, python_check, load_skill | write_file, edit_file (warn) | mode, todo, web_search, web_fetch, team_knowledge, apply_patch |

**Policy:**
- **Safe:** Direct use permitted without restriction
- **Warn:** Permitted after warning user; can proceed without confirmation
- **Blocked by default:** Requires delegation to specialized agent

### 2.2 Delegation Necessity Map (Per Mode × Operation)

| Mode | File Modification | Code Execution | Exploration | Git Operations | Web Access | Skill Loading |
|---|---|---|---|---|---|---|
| brainstorm | MUST delegate | CAN direct | CAN direct | CAN direct | CAN direct | CAN direct |
| write-plan | MUST delegate | WARN | CAN direct | WARN | CAN direct | CAN direct |
| execute-plan | MUST delegate | WARN | CAN direct | WARN | CAN direct | CAN direct |
| debug | MUST delegate | CAN direct | CAN direct | CAN direct | MUST delegate | CAN direct |
| verify | WARN | CAN direct | CAN direct | CAN direct | MUST delegate | CAN direct |
| finish | WARN | CAN direct | CAN direct | CAN direct | MUST delegate | CAN direct |

**Key Rules:**
- Write operations (`write_file`, `edit_file`) are either MUST-delegate or WARN depending on mode
- File modification in brainstorm/write-plan/execute-plan requires delegation to specialized agents
- Web access is restricted in debug/verify/finish modes
- Delegation tool itself is SAFE in brainstorm/execute-plan/debug/finish — enables sub-session bypass of restrictions

### 2.3 Composition Loopholes (Mode Restriction Bypass)

The system intentionally allows sub-sessions via the `delegate` and `recipes` tools to bypass parent mode restrictions:

| Mode | Loophole | Safe Tool | Enables |
|---|---|---|---|
| brainstorm | delegate is safe | delegate | Sub-agent execution with unrestricted tool access |
| brainstorm | recipes is safe | recipes | Full subagent-driven-development (full implementation via sub-sessions) |
| execute-plan | delegate is safe | delegate | Sub-agent execution with unrestricted tool access |
| execute-plan | recipes is safe | recipes | Full subagent-driven-development (full implementation via sub-sessions) |
| finish | delegate is safe | delegate | Sub-agent execution with unrestricted tool access |
| finish | recipes is safe | recipes | Full subagent-driven-development (full implementation via sub-sessions) |

**Design Rationale:** Sub-sessions inherit no parent mode restrictions because they run in fresh context (context_depth='none'). This is intentional — mode gates apply to the main session; sub-agents operate independently.

---

## 3. Mode Behaviors

### 3.1 Mode Taxonomy

Foundation implements **6 modes** organized into two phases:

**Phase 1 (Process Modes — Investigation & Design)**
- `brainstorm` — Collaborative design refinement through dialogue
- `write-plan` — Detailed implementation planning with TDD task breakdown
- `debug` — Systematic root-cause investigation with hypothesis-driven methodology

**Phase 2 (Execution & Completion Modes)**
- `execute-plan` — Subagent-driven implementation with mandatory two-stage review per task
- `verify` — Evidence-based completion verification (tests, behavior, edge cases)
- `finish` — Branch completion with structured merge/PR/keep/discard options

### 3.2 Mode: brainstorm

**Purpose:** Facilitate design refinement through collaborative dialogue, guiding the LLM and user to explore approaches, trade-offs, and design sections before any implementation begins.

**Tool Policy:**
- **Safe:** read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes, bash
- **Blocked:** write_file, edit_file, mode, todo, team_knowledge, apply_patch

**Behavioral Directives:**
- Ask ONE question per message; prefer multiple-choice over open-ended
- Propose 2-3 approaches with trade-offs; lead with recommendation
- Present design in sections scaled to complexity (200-300 words each)
- Apply YAGNI ruthlessly — remove unrequested features
- After spec self-review, gate on user approval before writing design document
- **MUST delegate** document creation to `superpowers:brainstormer` agent
- Do NOT write implementation code, create/modify source files, or run git operations

**Exit Conditions:**
- User approves written design document
- Golden path → transition to `write-plan` mode via `mode(operation='set', name='write-plan')`
- Design issues discovered → transition to `brainstorm` mode for re-refinement
- If user already has clear spec → transition to `write-plan` directly

### 3.3 Mode: write-plan

**Purpose:** Convert approved designs into detailed, byte-sized TDD implementation plans with exact file paths and complete code so any engineer can execute without domain context.

**Tool Policy:**
- **Safe:** read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes
- **Warn:** bash (must alert user before proceeding)
- **Blocked:** write_file, edit_file, mode, todo, team_knowledge, apply_patch

**Behavioral Directives:**
- Check for existing design; if absent, prompt user to run `/brainstorm` first
- Read design + relevant source files to understand current patterns
- Discuss task breakdown with user in natural clusters (not one question per turn)
- **DO NOT delegate plan document creation** — handle creation directly via `superpowers:plan-writer` agent
- Each task must be 2–5 minutes (one action); never combine "write test" + "write implementation"
- Every task must include: exact file paths, complete copy-pasteable code, exact commands, expected output, line references
- Plans >15 tasks must be split into phases
- Do NOT write vague tasks, combine actions, skip TDD, omit file paths, or leave decisions to implementer

**Exit Conditions:**
- Plan saved to `docs/plans/YYYY-MM-DD-<feature>-design.md`
- Golden path → transition to `execute-plan` mode via `mode(operation='set', name='execute-plan')` (second call confirms)
- Design incomplete → transition to `brainstorm` for clarification
- Plan reveals design issues → transition to `brainstorm`

### 3.4 Mode: execute-plan

**Purpose:** Orchestrate mandatory three-agent pipeline (implementer → spec-reviewer → code-quality-reviewer) to execute implementation plans task-by-task with write tools blocked and delegation enforced.

**Tool Policy:**
- **Safe:** read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes
- **Warn:** bash
- **Blocked:** write_file, edit_file, mode, todo, team_knowledge, apply_patch

**Behavioral Directives:**
- **NEVER write code directly** — write_file and edit_file are blocked by mode
- Dispatch one fresh subagent per task (never reuse agents across tasks)
- Execute mandatory three-stage pipeline per task: implementer → spec-reviewer → code-quality-reviewer
- Do NOT proceed to next task until both reviews pass
- After 3 failed fix attempts on same issue, stop and escalate to user with options
- Never dispatch multiple implementers in parallel (risk of conflicts)
- Use `context_depth='none'` for implementers; `context_depth='recent', context_scope='agents'` for reviewers
- If any task is BLOCKED or encounters NEEDS_CONTEXT, investigate and re-delegate with discovered context

**Exit Conditions:**
- All tasks marked complete with both spec and quality reviews passing
- Golden path → transition to `verify` mode
- Bug found during execution → transition to `debug` mode
- Spec ambiguity → transition to `brainstorm` mode
- Task blocked by missing prerequisite → escalate to user

### 3.5 Mode: debug

**Purpose:** Enforce rigid 4-phase systematic debugging process where investigation phases (1-3) are run by the main LLM, and all code fixes are delegated to `foundation:bug-hunter` or `superpowers:implementer` agents.

**Tool Policy:**
- **Safe:** read_file, glob, grep, load_skill, LSP, python_check, delegate, bash
- **Blocked:** write_file, edit_file, recipes, mode, todo, web_search, web_fetch, team_knowledge, apply_patch

**Behavioral Directives:**
- Enforce Phase 1 investigation before proposing any fixes
- Never guess, apply shotgun fixes, or skip phases
- Must reproduce bug consistently; check recent changes (git diff/log)
- Trace data flow backward through call stack to find bad data origin
- Find working examples and compare against broken code completely
- Form single specific hypothesis; test one variable at a time
- **MUST delegate all file-writing fixes** to `foundation:bug-hunter` or `superpowers:implementer`
- After 3 failed fix attempts, STOP and question the architecture instead of continuing to patch

**Phases:**
1. **Reproduce & Investigate** — Read error messages, reproduce, check recent changes
2. **Pattern Analysis** — Find working examples, compare completely against broken code
3. **Hypothesis & Test** — Form single hypothesis, design minimal test, verify with bash
4. **Fix (DELEGATE)** — Mandatory delegation to bug-hunter with confirmed root cause and evidence

**Exit Conditions:**
- Root cause found and fix verified
- Golden path → transition to `verify` mode
- Fix reveals design flaw → transition to `brainstorm` mode
- Fix needs implementation work → transition to `execute-plan` mode
- After 3 failures on same issue, stop and discuss architecture with user

### 3.6 Mode: verify

**Purpose:** Enforce evidence-based completion verification by requiring fresh, in-session proof before any success or completion claim can be made.

**Tool Policy:**
- **Safe:** read_file, glob, grep, bash, LSP, python_check, load_skill
- **Warn:** write_file, edit_file, delegate
- **Blocked:** recipes, mode, todo, web_search, web_fetch, team_knowledge, apply_patch

**Behavioral Directives:**
- Never claim completion without running verification command fresh in current session
- Execute Gate Function before any claim: IDENTIFY → RUN → READ → VERIFY → CLAIM
- Run FULL test suite, not subset
- Check linter/type checker and verify no regressions
- For bug fixes, run red-green regression cycle: test with fix (PASS) → revert → test without (FAIL) → restore → test with (PASS)
- **YOU must read test output yourself** — never accept agent reports as sufficient
- Treat any hedging language ("should", "probably", "seems") as violation of rule
- Present results using structured Verification Report format

**Exit Conditions:**
- All three verification checks complete with fresh evidence (tests, behavior, edge cases)
- Golden path (pass) → transition to `finish` mode
- Golden path (fail) → transition to `debug` mode
- Missing tests discovered → transition to `execute-plan` mode
- Missing feature discovered → transition to `brainstorm` or `write-plan` mode

### 3.7 Mode: finish

**Purpose:** Guide branch completion by verifying tests pass, summarizing work, presenting exactly 4 structured completion options (merge/PR/keep/discard), and executing the chosen option.

**Tool Policy:**
- **Safe:** read_file, glob, grep, bash, delegate, recipes, LSP, python_check, load_skill
- **Warn:** write_file, edit_file
- **Blocked:** mode, todo, web_search, web_fetch, team_knowledge, apply_patch

**Behavioral Directives:**
- Always verify tests pass before presenting options; STOP if tests fail
- Never proceed with merge or PR if tests are failing
- Present exactly 4 options with no added explanation: MERGE, PR, KEEP, DISCARD
- For MERGE: verify tests on merged result before deleting feature branch
- For DISCARD: show exact deletion list and require user to type "discard" for confirmation
- Clean up worktree only for MERGE/DISCARD; keep for KEEP; preserve for PR
- Never force-push without explicit user request

**Exit Conditions:**
- Option 1: Feature branch merged, tests verified, branch deleted, worktree removed
- Option 2: Branch pushed, PR created, worktree removed
- Option 3: Branch and worktree kept as-is
- Option 4: User typed "discard", branch deleted, worktree removed
- Early exit if tests fail: halt and do not proceed to options

---

## 4. Agent Behaviors

Foundation implements **14 specialist agents** organized by domain. Each operates as a one-shot sub-session with no context inheritance from parent.

### 4.1 Agents: Reconnaissance & Analysis

#### **foundation:explorer**
- **Purpose:** Deep local-context reconnaissance across multiple files; surveys code, docs, configuration, and user content
- **Trigger:** Task requires broad discovery across 2+ files; user asks to "explore", "survey", "understand", or "analyze"
- **Tools:** read_file, glob, grep, LSP (semantic), bash
- **Workflow:** Plan objectives → Map terrain → Deepen selectively → Synthesize findings → Recommend next actions
- **Exit:** Final response with Summary, Key Components (path:line refs), Coverage & Gaps, Suggested Next Actions

#### **foundation:file-ops**
- **Purpose:** Precise targeted file system operations (read, write, edit, find, search) without broader exploration
- **Trigger:** Task requires specific known files; single-file operations or batch changes
- **Tools:** read_file, write_file, edit_file, glob, grep
- **Workflow:** Read before edit → Precise old_string/new_string → Batch efficiently → Report results
- **Exit:** Operation Summary, Results with paths, Content, Issues encountered

### 4.2 Agents: Debugging & Verification

#### **foundation:bug-hunter**
- **Purpose:** Hypothesis-driven debugging using LSP-enhanced code intelligence; finds and fixes root causes
- **Trigger:** User reports error, tests fail, unexpected behavior, or caller encounters errors
- **Phases:** Evidence gathering → Reproduce → Narrow down → Hypothesis testing → Root cause → Fix → Verification → Prevention recommendations
- **Directives:** Trace actual code paths with LSP; use grep only for text patterns; never diagnose long-running as stuck without evidence; implement minimal fixes
- **Exit:** Original issue resolved, no side effects, regression test added, prevention recommendations provided

#### **foundation:session-analyst**
- **Purpose:** Analyzes, debugs, searches, and repairs Amplifier sessions; performs transcript surgery
- **Trigger:** Session won't resume, orphaned tool_calls detected, provider rejection errors, events.jsonl analysis needed
- **Directives:** NEVER use grep/cat on events.jsonl; extract fields only via jq; use amplifier-session.py for all repairs; default to REPAIR over REWIND
- **Workflow:** Locate script → Find sessions → Diagnose → Repair/Rewind → Verify
- **Exit:** VERDICT PASS/FAIL with evidence; second diagnose confirms healthy transcript

### 4.3 Agents: Exploration & Design

#### **foundation:zen-architect**
- **Purpose:** Plans and architectures code systems through complete module specifications; analysis-first development
- **Modes:** ANALYZE (problem decomposition), ARCHITECT (system design), REVIEW (code quality assessment)
- **Trigger:** New features, system redesign, code review, or before modular-builder specs needed
- **Directives:** Read philosophy files first; use LSP for code understanding; apply 5-question decision framework; design for regeneration
- **Workflow:** Mode selection → Context loading → Decision framework application → Pattern check → Response using template
- **Exit:** Complete specification with all 6 checklist items → Delegate to modular-builder

#### **foundation:modular-builder**
- **Purpose:** Translates complete specifications into working code modules; implementation-only agent
- **Trigger:** Complete spec exists with file paths, interfaces, pattern, success criteria
- **Directives:** STOP if any required input missing; read file max 10 times before asking; write README.md contract; use LSP before modifying contracts
- **Workflow:** Validate spec → Pre-coding setup → Module structure → Implementation → Testing → Completion verification → Handoff
- **Exit:** All tests pass, module works in isolation, public interface clean

### 4.4 Agents: Code Review & Quality

#### **superpowers:spec-reviewer**
- **Purpose:** Verifies implementations against task specifications for compliance (not quality)
- **Trigger:** After implementer completes each task in execute-plan
- **Directives:** Do NOT trust implementer claims; verify code independently; run tests yourself; check against spec line-by-line
- **Verdict:** APPROVED (spec fully met, no extras) or NEEDS CHANGES (issues listed)
- **Exit:** Both verdicts returned after spec compliance confirmed

#### **superpowers:code-quality-reviewer**
- **Purpose:** Reviews code quality across 6 dimensions (clarity, error handling, test quality, design, security, maintainability)
- **Trigger:** After spec-reviewer approves in execute-plan
- **Directives:** Only review after spec compliance confirmed; run project test suite; fix issues constructively; assess by behavior in action, not code review
- **Verdict:** APPROVED (no critical issues) or NEEDS CHANGES (issues listed)
- **Exit:** Structured review with Strengths, Issues by severity, Verdict, Required Actions

#### **superpowers:code-reviewer**
- **Purpose:** Holistic code review of complete changesets evaluating cross-task integration and production readiness
- **Trigger:** Branch ready for review before PR; entire session completed
- **Directives:** Review complete changeset holistically; check cross-task integration; verify architectural consistency; assess SOLID principles
- **Verdict:** APPROVED (no critical issues) or NEEDS CHANGES
- **Exit:** Structured output with Strengths, Critical/Important/Suggestion issues, Required Actions

### 4.5 Agents: Implementation & Execution

#### **superpowers:implementer**
- **Purpose:** Implements single task from plan using strict Test-Driven Development
- **Trigger:** Single task from implementation plan in execute-plan mode
- **Directives:** Write test first, watch it fail; delete pre-written code; implement minimal code; refactor only when green; commit atomically
- **Status Values:** DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED
- **Workflow:** RED → Verify RED → GREEN → Verify GREEN → REFACTOR → Self-review checklist
- **Exit:** Task complete or status indicating blocker/context need

#### **foundation:security-guardian**
- **Purpose:** Thorough security audits across OWASP Top 10, secrets, validation, crypto, dependencies
- **Trigger:** Before ANY production deployment (REQUIRED); after user data features; payment processing; API endpoints
- **Directives:** Apply framework, never silence fallbacks; explain why something is vulnerable; teach security principles; provide concrete code examples
- **Verdict:** PASS (no critical/high issues) or FAIL (issues found)
- **Exit:** Structured Security Audit Report with Executive Summary, Findings, Remediation Plan, Positive Findings, Testing Recommendations

### 4.6 Agents: Ecosystem & Coordination

#### **foundation:ecosystem-expert**
- **Purpose:** Guides multi-repo development, recommends testing patterns (Testing Ladder), maintains working memory (SCRATCH.md)
- **Trigger:** Multi-repo changes; cross-repo debugging; new modules; kernel contract changes
- **Directives:** Guide multi-repo coordination; recommend Testing Ladder (Unit → Local Override → Shadow → CI); maintain SCRATCH.md
- **Workflow:** Understand scope → Identify affected repos → Recommend testing → Guide workflows without enforcing
- **Exit:** Testing strategy + push order guidance provided

#### **foundation:git-ops**
- **Purpose:** ALWAYS delegate git/GitHub operations; enforces safety, conventional commits, Amplifier co-author attribution
- **Trigger:** Any git operation (commit, PR, push, branch, repo discovery, merge, rebase)
- **Directives:** NEVER update config/force-push/skip-hooks/amend without explicit request; check status before committing; Always verify branch
- **Commit Format:** `<type>: <description>` with Amplifier co-author and "Generated with Amplifier" footer
- **PR Format:** ## Summary (1-3 bullets) + ## Test plan (checklist)
- **Exit:** Commit hash, PR URL, or branch state returned

#### **foundation:integration-specialist**
- **Purpose:** Integrates external services, APIs, MCP servers; audits/manages dependencies for security, compatibility, technical debt
- **Trigger:** External service integration; API setup; MCP server connection; dependency analysis
- **Directives:** System boundaries focus; ruthless simplicity; use environment variables for credentials; validate all responses; set timeouts on all calls
- **Exit:** Integration Analysis Report or Dependency Audit Report with findings and recommendations

### 4.7 Agents: Framework & Foundation Expertise

#### **foundation:foundation-expert**
- **Purpose:** THE authoritative expert for Amplifier Foundation; bundle composition, behavior patterns, agent authoring, design philosophy
- **Trigger:** REQUIRED before any bundle/behavior/module work; design decisions; agent authoring; finding working examples
- **Modes:** COMPOSE (bundle building), PATTERN (examples/how-to), PHILOSOPHY (design decisions), AGENT (agent authoring)
- **Directives:** Defer to amplifier:amplifier-expert for ecosystem questions; defer to core:core-expert for kernel contracts; do NOT redeclare foundation's tools/config in bundles
- **Exit:** Complete guidance with examples; design decisions; or delegation to appropriate expert

#### **amplifier:amplifier-expert**
- **Purpose:** Authoritative consultant for ALL Amplifier ecosystem knowledge
- **Trigger:** Before ANY Amplifier-related work; ecosystem questions; getting started
- **Directives:** Use PROACTIVELY throughout lifecycle; consult before implementation; validate approaches after
- **Exit:** Accurate context on ecosystem, patterns, and best practices

#### **core:core-expert**
- **Purpose:** Expert consultant for kernel internals; module protocols, event system, kernel contracts
- **Trigger:** Building new modules; understanding kernel contracts; kernel vs module placement decisions
- **Directives:** Deep kernel knowledge; owns Session, Coordinator, Event system; determines kernel responsibility
- **Exit:** Clear protocol specifications; kernel contract guidance; ownership decisions

---

## 5. Skill Behaviors

Foundation implements **25+ reusable process skills** organized by domain.

### 5.1 Process Skills (Mandatory Before Tasks)

#### **systematic-debugging**
- **Purpose:** Enforce 4-phase systematic debugging with root-cause identification
- **Phases:** 1. Root Cause Investigation → 2. Pattern Analysis → 3. Hypothesis & Test → 4. Implementation
- **Invariant:** Never propose fixes without Phase 1 complete
- **Anti-Patterns:** Do NOT rationalize skipping phases; list of 13 rationalizations disqualifies them all
- **Exit:** Root cause found and fix verified; or architecture escalation after 3 failures

#### **test-driven-development**
- **Purpose:** Enforce strict RED-GREEN-REFACTOR with test-first discipline
- **Invariant:** Write test first, watch it fail, then write minimal code to pass
- **Directives:** Delete pre-written code and start over; never keep code "as reference"; test passes immediately = existing behavior (fix test)
- **Verification Checklist:** 8 items must all be satisfied before claiming completion
- **Exit:** All verification checklist items checked

#### **verification-before-completion**
- **Purpose:** No completion claims without fresh verification command output in same message
- **Gate Function:** IDENTIFY → RUN → READ → VERIFY → CLAIM
- **Violations:** Hedging language ("should", "probably"), satisfaction expressions ("Great!", "Perfect!"), agent report claims
- **Red-Green Regression Cycle (bug fixes):** With fix (PASS) → Revert → Without (FAIL) → Restore → With (PASS)
- **Exit:** Verification output confirms claim before assertion made

#### **brainstorming** ← Detailed in Mode Behaviors section

#### **writing-plans** ← Detailed in Mode Behaviors section

#### **writing-skills**
- **Purpose:** Apply TDD to skill creation itself
- **Invariant:** RED (write failing test with baseline scenario) → GREEN (write skill to address failures) → REFACTOR (close loopholes)
- **Directives:** Never write skill before running failing test; description must start with "Use when..."; max 1024 chars frontmatter
- **Deployment Checklist:** Must complete before moving to next skill (do NOT batch-create)
- **Exit:** All checklist items completed; skill tested and deployed

### 5.2 Architecture & Design Skills

#### **crusty-old-engineer**
- **Purpose:** Curmudgeonly senior engineering advisor; surfaces long-term consequences and hidden costs
- **Tone:** Direct, skeptical, calm, grounded in consequences; no promotional or evangelical language
- **Trigger:** Architectural decisions, legacy refactors, tooling choices, broad "how should I start?" questions
- **Directives:** Question unstated assumptions; identify hidden costs (maintenance, operations, ownership); call out known failure modes
- **Exit:** Realistic problem summary with trade-offs and viable path forward

#### **dispatching-parallel-agents**
- **Purpose:** Dispatch independent agents concurrently for 2+ tasks with no shared state or sequential dependencies
- **Trigger:** 3+ test files failing independently; multiple unrelated subsystems broken
- **Directives:** One agent per domain; construct instructions with exactly needed context; verify no conflicts on return
- **Exit:** All agents return summaries; coordinator reviews and integrates

### 5.3 Git & Development Workflow Skills

#### **using-git-worktrees**
- **Purpose:** Create isolated git worktrees with safety verification and auto-detect project setup
- **Trigger:** Before feature work; before executing plans
- **Directives:** Follow directory priority order; verify project-local directory is git-ignored; run baseline tests
- **Workflow:** Directory selection → .gitignore verification → Detect project type → Install dependencies → Run baseline tests
- **Exit:** Worktree created, tests passing, ready to implement

#### **finishing-a-development-branch**
- **Purpose:** Complete branch by verifying tests, presenting 4 options (merge/PR/keep/discard), executing choice
- **Trigger:** Tests pass, implementation complete
- **Directives:** Present exactly 4 options concisely; verify tests on merged result before deleting; require "discard" typing for confirmation
- **Exit:** Branch completed or disposed per user choice

#### **subagent-driven-development**
- **Purpose:** Execute implementation plan with fresh subagent per task + mandatory 2-stage review (spec → quality)
- **Trigger:** Plan exists; tasks are mostly independent
- **Directives:** Dispatch implementer once per task (fresh each time); spec review before quality; both must pass before next task
- **Workflow:** Setup → Per-task implementer → Spec review (loop until ✅) → Quality review (loop until ✅) → Final code review → Finish
- **Exit:** All tasks complete with both reviews passing

#### **executing-plans**
- **Purpose:** Load and execute plan sequentially with verification checkpoints (alternative to subagent-driven)
- **Trigger:** Plan exists; separate session execution with review gates preferred
- **Directives:** Read plan once; review critically with human partner; execute tasks exactly as written
- **Exit:** All tasks complete or blocker encountered

### 5.4 Code Review & Quality Skills

#### **receiving-code-review**
- **Purpose:** Evaluate and selectively implement review feedback with technical rigor
- **Directives:** NEVER say thank you; verify before implementing; push back with technical reasoning on incorrect suggestions
- **Workflow:** READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT (one item at a time)
- **Exit:** All actionable items addressed; false positives noted

#### **requesting-code-review**
- **Purpose:** Dispatch code-reviewer subagent with precise context for cross-task integration review
- **Trigger:** After each task (optional); before merging (mandatory)
- **Template:** {WHAT_WAS_IMPLEMENTED}, {PLAN_OR_REQUIREMENTS}, {BASE_SHA}, {HEAD_SHA}, {DESCRIPTION}
- **Exit:** Reviewer feedback returned; critical/important issues fixed

#### **code-review** (user-invocable)
- **Purpose:** Launch 3 parallel review agents (Reuse, Quality, Efficiency) for changed files
- **Trigger:** `/code-review` command
- **Workflow:** Git diff → Launch 3 agents in parallel → Fix all identified issues → Summarize
- **Exit:** Issues fixed or confirmed clean

### 5.5 Testing & Analysis Skills

#### **integration-testing-discipline**
- **Purpose:** Enforce E2E testing discipline; observe first, fix in batches
- **Directives:** NEVER fix during observation runs; let each run complete before taking action; record ALL failures; fix as coordinated batch in dependency order
- **Exit:** Observation complete → Batch fixes → Fresh validation run → All passing

#### **image-vision**
- **Purpose:** Analyze images using LLM vision APIs (Anthropic, OpenAI, Google, Azure)
- **Trigger:** Image content understanding, visual analysis, OCR, UI design review
- **Directives:** ALWAYS use wrapper scripts (vision-analyze.sh or robust version); never call Python directly; check exit code before trusting output
- **Failure Mode:** Report failure explicitly; do NOT fabricate observations
- **Exit:** Image analysis complete; or failure reported with guidance

#### **mass-change** (user-invocable)
- **Purpose:** Orchestrate large-scale parallelizable codebase changes via worker agents
- **Trigger:** `/mass-change <description>` command
- **Workflow:** Guard checks → Research → Decompose into 5-30 units → Present plan (user approval) → Spawn worker agents in parallel
- **Exit:** Final status table showing PRs created or failures per unit

#### **session-debug** (user-invocable)
- **Purpose:** Diagnose issues in current Amplifier session; misconfigured tools, failing operations
- **Trigger:** `/session-debug` command
- **Workflow:** Delegate to session-analyst → Check configuration → Identify patterns → Explain in plain language
- **Exit:** Problem explanation with concrete fix steps

### 5.6 Workflow & Execution Skills

#### **using-superpowers**
- **Purpose:** Establish mandatory skill-invocation discipline before ANY response
- **Invariant:** Check if skill applies BEFORE response (even at 1% chance); always load and follow
- **Directives:** Skip skill check only when dispatched as subagent; create todo per checklist item if applicable
- **Exit:** Skill loaded and being followed; then respond

#### **superpowers-reference**
- **Purpose:** Complete reference for Superpowers modes, agents, recipes, anti-patterns
- **Trigger:** Need to recall which mode applies or how to delegate
- **Exit:** Decision made on mode/agent selection

#### **skillify** (user-invocable)
- **Purpose:** Capture repeatable process from session into reusable SKILL.md
- **Trigger:** User says "skillify", "create skill", "save as skill", "capture workflow"
- **Workflow:** Analyze session → Interview user in clusters → Load skills-assist → Write SKILL.md → Test → Save
- **Exit:** SKILL.md written to disk; user told where and how to invoke

### 5.7 Specialized Skills

#### **adapt-skill**
- **Purpose:** Adapt skills from other AI platforms (Claude Code, Cursor, etc.) into Amplifier SKILL.md
- **Trigger:** User has skill from another platform to bring into Amplifier
- **Workflow:** Load skills-assist → Analyze source → Research platform → Design adapted version → Write SKILL.md → Test → Save
- **Exit:** Skill adapted and ready to use

#### **skills-assist**
- **Purpose:** Authoritative consultant for all skills-related questions
- **Trigger:** Creating/modifying skills; frontmatter questions; fork vs inline decisions
- **Exit:** Authoritative answer with examples from reference files

---

## 6. Context & Cross-Cutting Concerns

### 6.1 Behavioral Directive Contexts (Always-Loaded)

Foundation injects core behavioral contexts into every agent session:

| Context File | Purpose | Role |
|---|---|---|
| `common-agent-base.md` | Base operational standards (quality gates, tool usage, communication style, security) | Loaded by all agents |
| `common-system-base.md` | Task management discipline, tool policy, incremental validation protocol | Loaded by all agents |
| `IMPLEMENTATION_PHILOSOPHY.md` | Ruthless simplicity, minimal abstractions, 80/20, YAGNI, vertical slices | Injected into implementation work |
| `MODULAR_DESIGN_PHILOSOPHY.md` | Code as description; regenerate whole modules, not line-by-line edits | Injected into architecture work |
| `KERNEL_PHILOSOPHY.md` | Mechanism-not-policy, small/stable kernel, clean contracts, composition | Injected into kernel decisions |
| `LANGUAGE_PHILOSOPHY.md` | Code-graph tools first (LSP), text search fallback; compiler as code reviewer | Injected into code understanding work |
| `ISSUE_HANDLING.md` | 7-phase workflow for issues/PRs: investigate → root cause → gate → implement → shadow test → final validation → reflect | Injected when handling bugs |
| `CONTEXT_POISONING.md` | Each concept lives in exactly ONE place; delete duplicates; retcon history | Injected during documentation work |
| `PROBLEM_SOLVING_PHILOSOPHY.md` | Never start coding until complete picture understood; evidence before claims | Injected into debugging and analysis |

### 6.2 Standing Orders (Non-Negotiable Principles)

**Rule 1: Delegation-First Orchestration**
- Main LLM orchestrates; specialists execute
- MUST delegate: file exploration >2 files, code understanding, architecture, implementation, debugging, git operations
- Avoid: reading full events.jsonl, manual edits, complex multi-step LSP navigation

**Rule 2: Evidence Before Claims**
- No completion claim without fresh verification output in same message
- Run full test suite (not subset); read actual output; check exit codes
- Hedge language ("should", "probably") violates this rule
- Satisfaction expressions ("Great!", "Perfect!") before verification violate this rule

**Rule 3: Root Cause Not Symptoms**
- Never propose fixes without Phase 1 investigation complete
- Trace data flow backward through call stack to origin
- Find working examples and compare completely against broken code
- After 3 failed fixes on same problem, stop and escalate to user

**Rule 4: Ruthless Simplicity**
- Every layer justifies existence; no speculative abstractions
- YAGNI applied ruthlessly — remove unrequested features from all designs
- Simplest solution that works, no simpler
- Do NOT build for hypothetical future requirements

**Rule 5: TDD as Non-Negotiable**
- Write test first, watch it fail, implement minimal code
- Delete any code written before tests; no "keep as reference"
- Test passes immediately = testing existing behavior (fix test)
- 8-item verification checklist must all pass before claiming completion

**Rule 6: Skill Invocation Discipline**
- BEFORE any response (including clarifications), check if skill applies (even 1% chance)
- Load and follow skills; create todos per checklist items
- Never rationalize skipping skills based on perceived simplicity
- User instructions (CLAUDE.md, etc.) override skills only at top level

**Rule 7: No Mid-Process Code Changes During Testing**
- Observation phase: run tests, record ALL failures, make NO code changes
- Batch fix phase: address failures in dependency order as coordinated batch
- Validation phase: run fresh tests to verify all batch fixes
- Do NOT fix individual issues during E2E runs (integration-testing-discipline)

### 6.3 Delegation Chains & Escalation Paths

```
Main Session (Orchestrator)
├── Explorer needed → delegate: foundation:explorer
├── Bug found → delegate: foundation:bug-hunter
│   ├── Complex navigation needed → delegates to: lsp:code-navigator or python-dev:code-intel
│   └── Fix needed → delegates to: superpowers:implementer
├── Architecture needed → delegate: foundation:zen-architect
│   └── Implementation → delegates to: foundation:modular-builder
├── Git operations → delegate: foundation:git-ops
├── Code review → delegate: superpowers:code-reviewer (holistic) or superpowers:spec-reviewer (spec compliance)
├── Design phase → delegate: superpowers:brainstormer (after brainstorm mode)
├── Planning phase → delegate: superpowers:plan-writer (after write-plan mode)
├── Execution → delegate per task: superpowers:implementer (execute-plan mode)
│   ├── Task spec review → delegate: superpowers:spec-reviewer
│   └── Task quality review → delegate: superpowers:code-quality-reviewer
├── Security review → delegate: foundation:security-guardian
├── Multi-repo work → delegate: foundation:ecosystem-expert
├── External integrations → delegate: foundation:integration-specialist
└── Sessions analysis → delegate: foundation:session-analyst
```

### 6.4 Mode Transition Graph

```
brainstorm ─(design approved)→ write-plan ─(plan approved)→ execute-plan
    ↓ (design issues)              ↓ (incomplete)         ↓
    └────────────────────────────→ ↓                     (task complete)
    ↓ (already has spec)           ↑─────────────────────→ verify ─(all pass)→ finish
execute-plan ←─────────────────────┘ (more work)          ↓
    ↓ (bug found)                                    (tests fail)
    debug ─(fix verified)→ verify ─(pass)→ finish         ↓
    ↓ (architecture issue)          ↓               (issue found)
    brainstorm (re-design)      execute-plan       debug
                                    ↑
                                    └── (architecture issue)
                                         brainstorm
```

### 6.5 Behavioral Contradictions & Gaps

**Contradiction 1: Mode Restrictions vs Delegation**
- Brainstorm/write-plan/execute-plan block write_file/edit_file
- BUT delegate and recipes are SAFE in these modes
- → Allows sub-agents to bypass via sub-sessions (INTENTIONAL)
- **Resolution:** Sub-sessions inherit no parent restrictions; modes apply to main session only

**Contradiction 2: Git Operations in Different Modes**
- Debug: git operations listed as "CAN direct" (bash safe)
- Finish: git operations needed but bash is safe
- **Resolution:** Use git-ops agent for all git operations regardless; safety guarantees via agent protocol

**Gap 1: Explicit Context Injection Order**
- Many skills reference "load <philosophy file>" but no explicit sequencing
- **Recommendation:** Core philosophy files (IMPLEMENTATION, MODULAR) always first; domain-specific after

**Gap 2: Sub-Session Context Specification**
- Delegation shows context_depth/context_scope options but no default guidance
- **Recommendation:** context_depth='none' for independent work; context_depth='recent', context_scope='agents' for sequential work

**Gap 3: Model Role Selection Under Mode Restrictions**
- Modes don't specify which model_role is safe/unsafe
- **Recommendation:** Routing matrix (separate bundle) provides definitive role selection

---

## 7. Recipe Workflows

Foundation enables multi-step workflows via the `recipes` tool. Key recipes:

### 7.1 Standard Recipes

| Recipe | Purpose | Phases | Approval Gates |
|---|---|---|---|
| `superpowers-full-development-cycle.yaml` | End-to-end feature from idea to merged code | Brainstorm → Plan → Worktree → Execute → Verify → Finish | Brainstorm approval, Plan approval |
| `subagent-driven-development.yaml` | Task-by-task execution with 2-stage review per task | Per-task: Implementer → Spec review → Quality review | Per-task spec + quality |
| `executing-plans.yaml` | Batch task execution with checkpoints | Read plan → Execute batches → Verify → Report | Human approval between batches |
| `git-worktree-setup.yaml` | Isolated workspace creation | Directory selection → git-ignored check → Dependency install → Baseline tests | Project setup verification |
| `finish-branch.yaml` | Branch completion with merge/PR options | Test verification → Present options → Execute choice → Cleanup | User choice on completion option |

### 7.2 Validation Recipes

| Recipe | Purpose | Approval Gates |
|---|---|---|
| `validate-bundle-repo.yaml` | Check bundle documentation freshness; auto-regenerate if stale | Structural validation only |
| `validate-implementation.yaml` | Multi-task validation of externally-completed work | Per-task validation checks |
| `amplifier-smoke-test.yaml` | Validate Amplifier changes in shadow environment with 100-point rubric | Scored verdict: PASS/FAIL |
| `shadow-smoke-test.yaml` | Independent shadow validation (run after shadow-operator creates environment) | Scored verdict: PASS/FAIL |

---

## 8. Behavioral Invariants

### 8.1 System-Wide Guarantees

**Invariant 1: Delegation Protocol**
- Sub-agents inherit NO parent session context (context_depth='none' or explicit)
- Orchestrator is responsible for context construction for each sub-agent
- Sub-sessions run independently with unrestricted tool access
- Result: Always safe to delegate; guarantees isolation

**Invariant 2: Tool Availability Semantics**
- Safe tools → Direct use without restriction
- Warn tools → Permitted after alerting user; can proceed without confirmation
- Blocked tools → MUST delegate to specialized agent
- Exception: delegate and recipes tools themselves enable sub-session bypass (INTENTIONAL)

**Invariant 3: Two-Stage Review Pipeline**
- Spec-reviewer must run before code-quality-reviewer (never reverse)
- Both must pass before task marked complete
- After 3 review-fix iterations without convergence, escalate to user
- Violations: Task marked complete with only 1 review; quality review before spec compliance

**Invariant 4: Evidence Before Claims**
- Zero claims of completion, success, or passing without fresh output in same message
- Hedge language ("should", "probably", "seems") violates this invariant
- Satisfaction expressions before verification violate this invariant
- Violations tracked as completion failures

**Invariant 5: Root Cause Required**
- Fixes must address root cause, not symptoms
- Phase 1 investigation MUST complete before fix proposed
- After 3 failed fixes on same issue, escalate instead of continuing to patch
- Violations: Symptom fixes, skipped investigation, endless patch loops

**Invariant 6: TDD Discipline**
- Test written first, watched to fail, minimal code to pass
- Pre-written code must be deleted and started over
- All 8-item verification checklist items must pass before completion claimed
- Violations: Code before test, test passes immediately, claims without checklist

**Invariant 7: Skill Invocation**
- Skills loaded and followed when even 1% chance they apply
- Todos created per skill checklist items
- User instructions override skills only at top-level session policy
- Violations: Skipped skills due to perceived simplicity, rationalization patterns

### 8.2 Architectural Integrity Properties

**Property 1: Mode Isolation**
- Modes provide sandboxed execution with tool policies
- Modes prevent accidental writes during read-only phases (brainstorm, debug, write-plan)
- Modes provide guardrails for specific workflow phases
- Guarantee: User cannot accidentally commit mid-brainstorm or force-push mid-debug

**Property 2: Delegation Safety**
- All code modifications safe via delegated agents with protocols
- Main session can orchestrate without touching code directly
- Sub-agents responsible for correctness; orchestrator verifies results
- Guarantee: Coordination without direct implementation in restricted modes

**Property 3: Testing Discipline**
- Tests written before code; TDD enforced across entire execution pipeline
- Test failures halt execution (verify mode requires passing tests)
- Red-green regression cycles validate bug fixes
- Guarantee: Code correctness validated before completion claims

**Property 4: Transparency & Auditability**
- All major decisions tracked via git commits with Amplifier co-author attribution
- Tool invocations logged via standard Amplifier logging
- Decision trees stored in SCRATCH.md (working memory) or context files
- Guarantee: Complete audit trail of changes and decisions

---

## 9. Index & Quick Reference

### 9.1 Component Quick Lookup

**By Name:**
- Modes: brainstorm, write-plan, execute-plan, debug, verify, finish
- Agents: explorer, file-ops, bug-hunter, zen-architect, modular-builder, foundation-expert, git-ops, etc.
- Skills: systematic-debugging, test-driven-development, verification-before-completion, brainstorming, etc.

**By Domain:**
- Exploration/Analysis: explorer, foundation-expert, amplifier-expert
- Debugging: bug-hunter, systematic-debugging, session-analyst
- Design: zen-architect, brainstorm mode, brainstorming skill
- Implementation: modular-builder, superpowers:implementer, execute-plan mode
- Code Review: spec-reviewer, code-quality-reviewer, code-reviewer
- Git Operations: git-ops agent, all git operations
- Testing: test-driven-development skill, verify mode, integration-testing-discipline

### 9.2 Behavioral Directive Index

**Mandatory Before:**
- Any creative work → `brainstorming` skill
- Any implementation → `test-driven-development` skill
- Any completion claim → `verification-before-completion` skill
- Any skill work → `skills-assist` + `using-superpowers` skills
- Any response → Check if skill applies (using-superpowers discipline)

**Mandatory During:**
- Debugging → `systematic-debugging` phases
- Code review → Two-stage review (spec → quality)
- Multi-repo work → Foundation Ladder testing (unit → override → shadow → CI)
- E2E testing → No mid-run fixes (integration-testing-discipline)

**Mandatory After:**
- Task completion → Reflection & learning capture (ISSUE_HANDLING.md Phase 7)
- Branch work → cleanup via finish mode
- Bug fix → Regression test + prevention recommendations

### 9.3 Decision Trees

**What mode do I use?**
- Building/designing something → `brainstorm`
- Creating implementation plan → `write-plan`
- Executing plan → `execute-plan`
- Bug/issue appears → `debug`
- Work complete, ready to verify → `verify`
- Tests pass, ready to merge/PR → `finish`

**Which agent do I delegate to?**
- Exploring/surveying code → `foundation:explorer`
- Specific file operations → `foundation:file-ops`
- Bug with error message → `foundation:bug-hunter`
- Architectural decision needed → `foundation:zen-architect`
- Git operation → `foundation:git-ops`
- Code spec review → `superpowers:spec-reviewer`
- Code quality review → `superpowers:code-quality-reviewer`
- Holistic branch review → `superpowers:code-reviewer`

**Which skill do I load?**
- Before any implementation → `test-driven-development`
- Before any debugging → `systematic-debugging`
- Before any completion claim → `verification-before-completion`
- Before any response → `using-superpowers`
- Before feature work → `brainstorming`
- Before planning work → `writing-plans`
- Before git operations → Know to use agent, not direct bash

---

## 10. Document Notes & Limitations

**This specification covers:**
- Complete behavioral directives for all 6 modes
- Purpose, triggers, and exit conditions for all 14 agents
- Workflow phases for 25+ skills
- Tool governance matrices and delegation rules
- Standing orders and invariants that span all components
- Contradiction and gap analysis

**This specification does NOT cover:**
- Detailed API/contract specifications (see kernel documentation)
- Performance characteristics or timing guarantees
- Complete skill reference documentation (see individual SKILL.md files)
- Provider-specific model capabilities (see routing-matrix bundle)
- Concrete code examples (see skills and agent working examples)

**Known Limitations:**
1. Context injection sequencing not explicitly ordered (recommendation: philosophy files always first)
2. Model role safety guidance depends on routing-matrix bundle (separate from this doc)
3. Skill precedence when multiple apply not explicitly defined (recommendation: process skills before implementation)
4. Sub-session context defaults implied but not stated (recommendation: see delegation chains section)
5. Composition loopholes documented as feature, not security boundary (intentional design)

---

**Document Complete**

This behavioral specification synthesizes the dependency tree, composition effects, and 50+ behavioral extractions into a comprehensive reference for understanding and operating the Amplifier Foundation bundle. All components work together to enforce discipline, ensure correctness, and guide users through structured development workflows from design through merge.

For detailed component documentation, refer to individual SKILL.md files, agent descriptions, and behavior YAML specifications in the bundle source.
