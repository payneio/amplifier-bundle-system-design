# Bundle Behavioral Specification — Foundation

> **Generated:** 2026-04-08
> **Source data:** `.composition-effects.json`, `.manifest-summary.json`, superpowers mode/agent definitions
> **Scope:** Deterministic behavioral analysis of the composed bundle stack

---

## Part 1: Component Inventory

### 1.1 Bundles

The dependency tree contains 30 resolved bundles. Key bundles by role:

| Bundle | Type | Description |
|--------|------|-------------|
| `foundation` | root | Base layer — shared agents, context, tools |
| `superpowers-methodology-behavior` | behavior | Modes, superpowers agents, SDD pipeline, recipes |
| `behavior-agents` | behavior | Agent delegation infrastructure |
| `behavior-modes` | behavior | Mode system, transitions, tool cascades |
| `recipes-behavior` | behavior | Recipe execution engine |
| `skills-behavior` | behavior | Skill loading and discovery |
| `routing-matrix` | behavior | Model routing (`model_role` → provider) |
| `python-dev` | root | Python tooling (pyright, ruff, LSP) |
| `python-dev-behavior` | behavior | Python development workflows |
| `lsp-python` | root | Python LSP integration |
| `behavior-python-lsp` | behavior | LSP tool wiring for Python |
| `python-quality-behavior` | behavior | `python_check` tool behaviors |
| `behavior-lsp-core` | behavior | Core LSP protocol |
| `shadow` | root | Shadow environment support |
| `design-intelligence-behavior` | behavior | Design intelligence patterns |
| `hook-shell-behavior` | behavior | Shell/bash tool hooks |
| `mcp-behavior` | behavior | MCP server integration |
| `behavior-apply-patch` | behavior | `apply_patch` tool |
| `browser-testing-behavior` | behavior | Browser-based testing |
| `behavior-sessions` | behavior | Session management |
| `behavior-status-context` | behavior | Git/env status context injection |
| `behavior-redaction` | behavior | Sensitive data redaction |
| `behavior-todo-reminder` | behavior | Todo tool usage reminders |
| `behavior-streaming-ui` | behavior | Streaming UI formatting |
| `behavior-logging` | behavior | Session logging |
| `amplifier-expert-behavior` | behavior | Amplifier self-knowledge |
| `core-expert-behavior` | behavior | Core platform expertise |
| `foundation-expert-behavior` | behavior | Foundation bundle expertise |

**Component totals:** 26 agents, 6 modes, 27 skills, 13 recipes, 27 behavior YAMLs, 39 context files.

---

### 1.2 Modes

All 6 modes have `default_action: block` and `allow_clear: false` (except `finish` which has `allow_clear: true`).

> **Critical infrastructure note:** The `mode` and `todo` tools appear as `blocked_by_default` in the tool availability matrix. However, they are configured as **`infrastructure_tools`** in hooks-mode, meaning they **bypass the mode tool cascade entirely**. The LLM can always call `mode()` and `todo()` regardless of which mode is active. The matrix listing is an artifact of static analysis — runtime behavior differs.

| Mode | Shortcut | Safe Tools | Warn Tools | Blocked Tools | Default Action | Allowed Transitions | Purpose |
|------|----------|------------|------------|---------------|----------------|---------------------|---------|
| **brainstorm** | `brainstorm` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes, bash | *(none)* | write_file, edit_file, apply_patch, team_knowledge | block | write-plan, debug | Design refinement through collaborative dialogue; explore approaches and trade-offs |
| **write-plan** | `write-plan` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash | write_file, edit_file, apply_patch, team_knowledge | block | execute-plan, brainstorm, debug | Create detailed TDD implementation plan with exact paths, code, commands |
| **execute-plan** | `execute-plan` | read_file, glob, grep, web_search, web_fetch, load_skill, LSP, python_check, delegate, recipes | bash | write_file, edit_file, apply_patch, team_knowledge | block | verify, debug, brainstorm, write-plan | Orchestrate 3-agent pipeline (implementer → spec-reviewer → code-quality-reviewer) |
| **debug** | `debug` | read_file, glob, grep, load_skill, LSP, python_check, delegate, bash | *(none)* | write_file, edit_file, recipes, web_search, web_fetch, apply_patch, team_knowledge | block | verify, brainstorm, execute-plan | Systematic 4-phase debugging — root cause before fixes |
| **verify** | `verify` | read_file, glob, grep, bash, LSP, python_check, load_skill | write_file, edit_file, delegate | recipes, web_search, web_fetch, apply_patch, team_knowledge | block | finish, debug, execute-plan, brainstorm, write-plan | Evidence-based completion verification — no claims without fresh proof |
| **finish** | `finish` | read_file, glob, grep, bash, delegate, recipes, LSP, python_check, load_skill | write_file, edit_file | web_search, web_fetch, apply_patch, team_knowledge | block | execute-plan, brainstorm | Complete work — verify tests, present merge/PR/keep/discard options, clean up |

---

### 1.3 Agents

#### Superpowers Agents (from `amplifier-bundle-superpowers`)

| Agent | Model Role | Trigger / Purpose | Own Tools |
|-------|-----------|-------------------|-----------|
| **implementer** | coding, general | Single task from implementation plan; TDD RED→GREEN→REFACTOR | filesystem, bash, search, python_check |
| **plan-writer** | reasoning, general | Writes detailed implementation plan document from validated discussion | filesystem, search |
| **brainstormer** | reasoning, general | Writes design document from validated brainstorm conversation | filesystem, bash |
| **spec-reviewer** | critique, reasoning, general | Post-implementation spec compliance check; APPROVED / NEEDS CHANGES verdict | filesystem, bash, search, python_check |
| **code-quality-reviewer** | critique, reasoning, general | Post-spec-review code quality assessment; 6 dimensions + severity levels | filesystem, bash, search, python_check |
| **code-reviewer** | critique, reasoning, general | Holistic changeset review (entire branch/feature); cross-task integration | filesystem, bash, search |

#### Foundation and Other Agents

| Agent | Source Bundle | Purpose |
|-------|-------------|---------|
| bug-hunter | foundation | Targeted bug fixes with TDD |
| explorer | foundation | Codebase exploration and navigation |
| file-ops | foundation | File system operations |
| git-ops | foundation | Git operations (commits, PRs, branches) |
| web-research | foundation | Web search and content fetching |
| shell-exec | foundation | Shell command execution |
| ecosystem-expert | foundation | Package/dependency expertise |
| integration-specialist | foundation | Cross-component integration |
| modular-builder | foundation | Modular component construction |
| security-guardian | foundation | Security review |
| session-analyst | foundation | Session analysis and repair |
| test-coverage | foundation | Test coverage analysis |
| zen-architect | foundation | Architecture review |
| post-task-cleanup | foundation | Post-task cleanup operations |
| foundation-expert | foundation | Foundation bundle expertise |
| amplifier-smoke-test | foundation | Platform smoke testing |
| code-intel | lsp | Code intelligence via LSP |
| python-dev | python-dev | Python development specialist |
| shadow-operator | shadow | Shadow environment operations |
| shadow-smoke-test | shadow | Shadow environment testing |

---

### 1.4 Skills

| Skill | Associated Mode | Match Type | Purpose |
|-------|----------------|------------|---------|
| **brainstorming** | brainstorm | name_overlap | Workflow guidance for brainstorming sessions |
| **session-debug** | debug | name_overlap | Diagnose issues in current Amplifier session |
| **systematic-debugging** | debug | name_overlap | 4-phase debugging methodology |
| **executing-plans** | execute-plan | name_overlap | Plan execution workflow with review checkpoints |
| **finishing-a-development-branch** | finish | name_overlap | Branch completion — merge/PR/keep/discard |
| **verification-before-completion** | verify | name_overlap | Evidence-based verification before claims |
| **writing-plans** | write-plan | name_overlap | Workflow for creating implementation plans |
| using-superpowers | *(global)* | — | Startup skill — how to find and use skills |
| superpowers-reference | *(global)* | — | Complete reference tables for modes/agents/recipes |
| subagent-driven-development | *(execute-plan)* | — | SDD pipeline orchestration |
| dispatching-parallel-agents | *(any)* | — | Parallel agent dispatch patterns |
| test-driven-development | *(any)* | — | TDD methodology |
| receiving-code-review | *(execute-plan/verify)* | — | Evaluating reviewer feedback critically |
| requesting-code-review | *(verify/finish)* | — | Code review request workflow |
| code-review | *(user-invoked)* | — | `/code-review` command |
| mass-change | *(user-invoked)* | — | `/mass-change` command — parallel PRs |
| session-debug | *(user-invoked)* | — | `/session-debug` command |
| using-git-worktrees | *(any)* | — | Workspace isolation via worktrees |
| sdd-walkthrough | *(execute-plan)* | — | Worked example of SDD pipeline |
| integration-testing-discipline | *(any)* | — | E2E testing principles |
| creating-amplifier-modules | *(any)* | — | Creating new Amplifier modules |
| bundle-to-dot | *(any)* | — | Bundle documentation DOT graph generation |
| adapt-skill | *(any)* | — | Port skills from other AI assistants |
| skillify | *(any)* | — | Capture repeatable process as skill |
| skills-assist | *(any)* | — | Skills system consultant |
| writing-skills | *(any)* | — | Creating and editing skills |
| image-vision | *(any)* | — | Image analysis via vision APIs |
| crusty-old-engineer | *(any)* | — | Architectural skepticism advisor |

---

### 1.5 Recipes

| Recipe | Purpose |
|--------|---------|
| **subagent-driven-development** | Full 3-agent pipeline per task with review retries and final holistic review |
| **executing-plans** | Human-guided batch execution with self-review (no per-task sub-agents) |
| **superpowers-full-development-cycle** | End-to-end: brainstorm → write-plan → execute → verify → finish |
| **writing-plans** | Plan creation workflow |
| **brainstorming** | Brainstorming session workflow |
| **finish-branch** | Branch completion with approval gates |
| **git-worktree-setup** | Create isolated worktree workspace |
| **validate-implementation** | Validate externally-completed work against plan |
| **validate-bundle** | Bundle manifest validation |
| **validate-single-bundle** | Single bundle validation |
| **validate-bundle-repo** | Repository-level bundle validation |
| **validate-agents** | Agent definition validation |
| **generate-bundle-docs** | Generate bundle documentation |

---

### 1.6 Composition Loopholes

These are structurally significant: a mode blocks direct file writes but makes `delegate` or `recipes` safe, enabling sub-sessions that bypass the calling mode's restrictions.

| Mode | Safe Tool | What It Enables | Implication |
|------|-----------|----------------|-------------|
| **brainstorm** | `delegate` | Sub-agent runs in own session with full tool access | Brainstorm can trigger file writes indirectly via brainstormer agent |
| **brainstorm** | `recipes` | Launch `subagent-driven-development` → full implementation pipeline | Brainstorm can launch entire build pipelines despite write_file being blocked |
| **debug** | `delegate` | Sub-agent (bug-hunter/implementer) writes fixes in own session | Debug investigation stays read-only; fixes happen in agent sub-sessions |
| **execute-plan** | `delegate` | Implementer agent writes code in own session | Core mechanic — execute-plan's entire purpose is delegation |
| **execute-plan** | `recipes` | Launch SDD recipe for multi-task automated execution | Recipe handles foreach loops and approval gates automatically |
| **write-plan** | `delegate` | Plan-writer agent creates plan document in own session | Write-plan cannot write files directly; plan-writer agent does it |
| **write-plan** | `recipes` | Launch writing-plans recipe for automated plan creation | Recipe alternative to manual delegation |
| **finish** | `delegate` | Code-reviewer agent runs holistic review in own session | Finish can delegate review before presenting merge options |
| **finish** | `recipes` | Launch finish-branch recipe with approval gates | Recipe automates the test → options → cleanup flow |

> **Note:** `verify` mode does NOT have `delegate` or `recipes` as safe — `delegate` is on **warn** and `recipes` is **blocked**. This is the only mode where the orchestrator is expected to do verification work directly rather than delegating it.

---

## Part 2: Relationship Graph

### 2.1 Mode Transition State Machine

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                                                          │
                    │     ┌────────────┐                                       │
          ┌─────────┼────▶│ brainstorm │◀───────────────────┐                  │
          │         │     └─────┬──────┘                    │                  │
          │         │           │                           │                  │
          │         │     golden path                 design flaw /            │
          │         │           │                    need clarification        │
          │         │           ▼                           │                  │
          │         │     ┌────────────┐                    │                  │
          │         ├────▶│ write-plan │◀───────────────────┼──────────┐       │
          │         │     └─────┬──────┘                    │          │       │
          │         │           │                           │          │       │
          │         │     golden path              blocked prereq     │       │
          │         │           │                           │          │       │
          │         │           ▼                           │          │       │
          │         │    ┌──────────────┐                   │          │       │
    new   │    bug  │    │ execute-plan │───────────────────┘          │       │
   work   │  found  │    └──────┬───────┘                             │       │
          │         │           │                                     │       │
          │         │     golden path                          missing│       │
          │         │           │                            feature/ │       │
          │         │           ▼                              tests  │       │
          │         │      ┌────────┐          ┌─────┐                │       │
          │         └──────│ verify │─────────▶│debug│────────────────┘       │
          │          fail  └───┬────┘          └──┬──┘                        │
          │                    │                  │                           │
          │              golden path        fix reveals                      │
          │               (pass)           design flaw ───────────────┘       │
          │                    │                  │                           │
          │                    ▼                  │ fix needs more impl       │
          │              ┌──────────┐             └───────────────────────────┘
          │              │  finish  │                  (→ execute-plan)
          │              └────┬─────┘
          │                   │
          └───────────────────┤ more work → brainstorm
                              │ more tasks → execute-plan
                              │
                              ▼
                        mode(clear)
                      Session Complete
```

**Transition summary (allowed_transitions from YAML frontmatter):**

| From | To (allowed) |
|------|-------------|
| brainstorm | write-plan, debug |
| write-plan | execute-plan, brainstorm, debug |
| execute-plan | verify, debug, brainstorm, write-plan |
| debug | verify, brainstorm, execute-plan |
| verify | finish, debug, execute-plan, brainstorm, write-plan |
| finish | execute-plan, brainstorm *(+ mode clear)* |

**Gate policy:** All mode transitions require a two-step confirmation. The first `mode(set)` call is denied by the gate policy; the second call confirms the transition.

---

### 2.2 Delegation Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR (main session)                  │
│                                                                     │
│  brainstorm mode ──delegate──▶ superpowers:brainstormer             │
│       │                         (writes design doc)                 │
│       └──delegate──▶ superpowers:spec-reviewer                     │
│                       (adversarial spec review, up to 3 cycles)    │
│                                                                     │
│  write-plan mode ──delegate──▶ superpowers:plan-writer              │
│                                 (writes implementation plan)        │
│                                                                     │
│  execute-plan mode ──┬─delegate──▶ superpowers:implementer          │
│     (per task)       │              (RED→GREEN→REFACTOR→commit)     │
│                      ├─delegate──▶ superpowers:spec-reviewer        │
│                      │              (APPROVED / NEEDS CHANGES)      │
│                      └─delegate──▶ superpowers:code-quality-reviewer│
│                                    (APPROVED / NEEDS CHANGES)       │
│                                                                     │
│  debug mode ──delegate──▶ foundation:bug-hunter                     │
│       │                    (targeted bug fix with TDD)              │
│       └──delegate──▶ superpowers:implementer                       │
│                        (fix as part of larger impl)                 │
│                                                                     │
│  verify mode ──delegate(WARN)──▶ superpowers:code-reviewer          │
│                                   (optional holistic review)        │
│                                                                     │
│  finish mode ──delegate──▶ superpowers:code-reviewer                │
│       │                     (optional pre-merge review)             │
│       └──recipes──▶ superpowers:finish-branch                      │
│                      (automated completion pipeline)                │
└─────────────────────────────────────────────────────────────────────┘
```

**Key pattern:** Modes where `write_file`/`edit_file` are blocked MUST delegate for any file modifications. Modes where they are on `warn` CAN write directly (after warning) but prefer delegation for consistency.

---

### 2.3 Delegation Necessity by Mode

Derived from `composition-effects.json → delegation_necessity_map`:

| Capability | brainstorm | write-plan | execute-plan | debug | verify | finish |
|-----------|-----------|-----------|-------------|------|--------|--------|
| **File modification** | MUST delegate | MUST delegate | MUST delegate | MUST delegate | WARN (can direct) | WARN (can direct) |
| **Code execution (bash)** | CAN direct | WARN | WARN | CAN direct | CAN direct | CAN direct |
| **Exploration (read/grep/glob)** | CAN direct | CAN direct | CAN direct | CAN direct | CAN direct | CAN direct |
| **Git operations** | CAN direct | WARN | WARN | CAN direct | CAN direct | CAN direct |
| **Web access** | CAN direct | CAN direct | CAN direct | MUST delegate | MUST delegate | MUST delegate |
| **Skill loading** | CAN direct | CAN direct | CAN direct | CAN direct | CAN direct | CAN direct |

**Reading the table:**
- **MUST delegate** = tool is blocked; the only path is through a sub-agent
- **WARN** = tool triggers a warning on first use; can proceed after acknowledgment
- **CAN direct** = tool is safe; no friction
- **MUST delegate (web)** = debug/verify/finish block web_search and web_fetch; must delegate to `web-research` agent

---

## Part 3: Expected Behavioral Logic (Scenarios)

### Analysis Framework

Each step is tagged with its enforcement level:
- **[STRUCTURAL]** — Enforced by tool restrictions (will fail if violated)
- **[CONVENTIONAL]** — Described in mode prose/instructions (can be skipped, but shouldn't be)
- **[INFERRED]** — Deduced from tool availability patterns and composition effects

---

### Scenario 1: New Feature — Full Development Cycle

**Entry conditions:** User describes a new feature to build. No existing design or plan.

#### Phase A: Brainstorm Mode

**Prescriptive Rules:**
- `write_file`/`edit_file` blocked → orchestrator CANNOT create files [STRUCTURAL]
- `delegate` safe → orchestrator MUST delegate document creation to `brainstormer` [STRUCTURAL]
- `recipes` safe → orchestrator CAN launch brainstorming recipe [STRUCTURAL]
- `load_skill` safe → first action should load matching skill [CONVENTIONAL]
- Mode transitions gated by two-step confirmation [STRUCTURAL]

**Likely Runtime Pattern:**

1. `load_skill(search="brainstorm")` → loads `brainstorming` skill [CONVENTIONAL — mode text says "check for relevant skills"]
2. Create todo checklist with 9 items from mode definition [CONVENTIONAL]
3. Read project files (`read_file`, `glob`, `grep`) to understand context [CONVENTIONAL — Phase 1]
4. Ask ONE clarifying question at a time; wait for user response [CONVENTIONAL — Phase 2, strictly enforced by anti-rationalization]
5. Propose 2–3 approaches with trade-offs [CONVENTIONAL — Phase 3]
6. Present design in 200–300 word sections; get user validation per section [CONVENTIONAL — Phase 4]
7. `delegate(agent="superpowers:brainstormer", instruction="Write the design document...")` → brainstormer writes `docs/plans/YYYY-MM-DD-<topic>-design.md` [STRUCTURAL — only path to file creation]
8. Self-review: placeholder scan, consistency, scope, ambiguity check [CONVENTIONAL — Phase 6]
9. Adversarial review: `delegate(agent="superpowers:spec-reviewer", ...)` — up to 3 cycles [CONVENTIONAL — Phase 6]
10. Present summary to user; wait for explicit approval [CONVENTIONAL — Phase 7, "non-answer is not approval"]
11. `mode(operation='set', name='write-plan')` — first call denied, second call confirms [STRUCTURAL — gate policy]

**Exit conditions:** Design document saved to `docs/plans/`. User gives explicit approval.

#### Phase B: Write-Plan Mode

**Prescriptive Rules:**
- `write_file`/`edit_file` blocked → orchestrator CANNOT write plan [STRUCTURAL]
- `delegate` safe → orchestrator MUST delegate to `plan-writer` [STRUCTURAL]
- `bash` on warn → shell use triggers warning [STRUCTURAL]
- Design document MUST exist from brainstorm phase [CONVENTIONAL — prerequisite check]

**Likely Runtime Pattern:**

1. `load_skill(skill_name="writing-plans")` → loads matched skill [INFERRED — skill_mode_association]
2. Read design document from `docs/plans/` [CONVENTIONAL — Step 1]
3. Read source files to understand existing patterns, naming, test style [CONVENTIONAL — Step 1]
4. Discuss plan structure with user: task breakdown, ordering, scope boundaries [CONVENTIONAL — Step 2]
5. Decide file decomposition: new files, modified files, test locations [CONVENTIONAL — Step 2.5]
6. `delegate(agent="superpowers:plan-writer", instruction="Create implementation plan from the design at [path]...")` → plan-writer writes `docs/plans/YYYY-MM-DD-<feature>-implementation.md` [STRUCTURAL — only path to file creation]
7. Present plan summary with two execution options: `/execute-plan` or SDD recipe [CONVENTIONAL]
8. `mode(operation='set', name='execute-plan')` — two-step gate [STRUCTURAL]

**Exit conditions:** Plan saved to `docs/plans/`. User chooses execution approach.

#### Phase C: Execute-Plan Mode

**Prescriptive Rules:**
- `write_file`/`edit_file` blocked → orchestrator CANNOT implement code [STRUCTURAL]
- `delegate` safe → all implementation through sub-agents [STRUCTURAL]
- `recipes` safe → CAN launch SDD recipe for multi-task automation [STRUCTURAL]
- `bash` on warn → read-only shell use for status checks [STRUCTURAL]
- Three-agent pipeline is mandatory per task [CONVENTIONAL — "You MUST execute these three stages IN ORDER"]
- Sequential task execution only — never parallel implementers [CONVENTIONAL — Operational Rule 1]

**Likely Runtime Pattern:**

1. `load_skill(skill_name="executing-plans")` → loads matched skill [INFERRED — skill_mode_association]
2. Read implementation plan; create todo list with one item per task [CONVENTIONAL]
3. **If plan has > 3 tasks:** `recipes(operation="execute", recipe_path="@superpowers:recipes/subagent-driven-development.yaml", context={"plan_path": "..."})` [CONVENTIONAL — mode text: "YOU SHOULD use the recipe"]
4. **If manual orchestration (≤ 3 tasks), for each task:**
   - 4a. `delegate(agent="superpowers:implementer", instruction="Implement Task N of M...", context_depth="none")` [STRUCTURAL — only way to write code]
   - 4b. Wait for implementer completion; check status signal (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) [CONVENTIONAL]
   - 4c. `delegate(agent="superpowers:spec-reviewer", instruction="Review Task N...", context_depth="recent", context_scope="agents")` [CONVENTIONAL — mandatory per mode text]
   - 4d. If spec-reviewer returns FAIL → re-delegate to implementer with fix instructions (max 3 iterations) [CONVENTIONAL — Review Loop Limits]
   - 4e. `delegate(agent="superpowers:code-quality-reviewer", instruction="Review Task N...", context_depth="recent", context_scope="agents")` [CONVENTIONAL — mandatory per mode text]
   - 4f. If quality-reviewer returns FAIL → re-delegate to implementer with fix instructions (max 3 iterations) [CONVENTIONAL]
   - 4g. Both pass → mark task complete; proceed to next [CONVENTIONAL]
5. Present execution summary with commits list [CONVENTIONAL]
6. `mode(operation='set', name='verify')` — two-step gate [STRUCTURAL]

**Exit conditions:** All tasks complete with passing reviews. Summary presented to user.

#### Phase D: Verify Mode

**Prescriptive Rules:**
- `delegate` on warn → orchestrator should verify directly, not delegate verification [STRUCTURAL]
- `recipes` blocked → no pipeline launches [STRUCTURAL]
- `bash` safe → full shell access for running tests [STRUCTURAL]
- `write_file`/`edit_file` on warn → minor fixes possible after warning [STRUCTURAL]
- The Iron Law: "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE" [CONVENTIONAL — strictly enforced by prose]

**Likely Runtime Pattern:**

1. `load_skill(skill_name="verification-before-completion")` → loads matched skill [INFERRED — skill_mode_association]
2. **Check 1 — Tests pass:** `bash("pytest -v")` or equivalent; read full output, verify 0 failures [CONVENTIONAL — "Run the FULL test suite"]
3. **Check 2 — Behavior verified:** Run specific scenario demonstrating the feature works [CONVENTIONAL]
4. **Check 3 — Edge cases and regressions:** `python_check`, LSP diagnostics, edge case testing [CONVENTIONAL]
5. For bug fixes: Red-green regression cycle (run with fix → pass, revert → fail, restore → pass) [CONVENTIONAL]
6. Spot-check VCS diffs: `bash("git log --oneline main..HEAD")`, `bash("git diff --stat main")` [CONVENTIONAL — "Verifying Delegated Work"]
7. Optional holistic review: `delegate(agent="superpowers:code-reviewer", ...)` — will trigger warn, must confirm intent [STRUCTURAL — warn gate]
8. Present Verification Report in prescribed format [CONVENTIONAL]
9. **If pass:** `mode(operation='set', name='finish')` — two-step gate [STRUCTURAL]
10. **If fail:** `mode(operation='set', name='debug')` — two-step gate [STRUCTURAL]

**Exit conditions:** Verification Report produced. Verdict: VERIFIED or NOT VERIFIED.

#### Phase E: Finish Mode

**Prescriptive Rules:**
- `bash` safe → full shell access for git operations (push, merge, PR) [STRUCTURAL]
- `delegate` safe → can dispatch code-reviewer for pre-merge review [STRUCTURAL]
- `recipes` safe → can launch finish-branch recipe [STRUCTURAL]
- `write_file`/`edit_file` on warn → minor fixes possible [STRUCTURAL]
- `allow_clear: true` → only mode where session can fully exit [STRUCTURAL]
- Tests MUST pass before presenting options [CONVENTIONAL — "STOP. Do not proceed to Step 2 until tests pass."]

**Likely Runtime Pattern:**

1. `load_skill(skill_name="finishing-a-development-branch")` → loads matched skill [INFERRED — skill_mode_association]
2. `bash("pytest -v")` — verify tests pass [CONVENTIONAL — Step 1]
3. Optional: `delegate(agent="superpowers:code-reviewer", model_role="critique")` — holistic review [CONVENTIONAL — Step 1.5]
4. `bash("git log --oneline main..HEAD")`, `bash("git diff --stat main")` — summarize work [CONVENTIONAL — Step 2]
5. Present exactly 4 options: MERGE, PR, KEEP, DISCARD [CONVENTIONAL — Step 4]
6. Execute user's choice via `bash`:
   - MERGE: `git checkout main && git merge --ff-only <branch>` [CONVENTIONAL]
   - PR: `git push -u origin <branch> && gh pr create ...` [CONVENTIONAL]
   - KEEP: report and preserve [CONVENTIONAL]
   - DISCARD: require typed "discard" confirmation, then delete [CONVENTIONAL]
7. Worktree cleanup if applicable [CONVENTIONAL — Step 6]
8. `mode(operation='clear')` — exit development workflow [STRUCTURAL]

**Exit conditions:** Branch merged/PR'd/kept/discarded. Mode cleared.

---

### Scenario 2: Bug Report — Debug Mode Flow

**Entry conditions:** User reports a bug, test failure, or unexpected behavior.

**Prescriptive Rules:**
- `write_file`/`edit_file` blocked → orchestrator CANNOT apply fixes directly [STRUCTURAL]
- `delegate` safe → fixes via bug-hunter or implementer agent [STRUCTURAL]
- `recipes` blocked → no pipeline launches from debug mode [STRUCTURAL]
- `bash` safe → full shell for investigation (read-only intent) [STRUCTURAL]
- `web_search`/`web_fetch` blocked → cannot research online directly [STRUCTURAL]
- 4-phase process mandatory; no fixes before Phase 3 hypothesis confirmed [CONVENTIONAL]

**Likely Runtime Pattern:**

1. `load_skill(skill_name="systematic-debugging")` → loads matched skill [CONVENTIONAL — mode text: "check for relevant skills"]
2. **Phase 1 — Reproduce and Investigate** [CONVENTIONAL — "YOU do this"]:
   - 2a. `bash("pytest tests/... -v")` — reproduce the failure [STRUCTURAL — bash safe]
   - 2b. `read_file(...)` — read error messages, stack traces completely [STRUCTURAL]
   - 2c. `bash("git diff")`, `bash("git log --oneline -10")` — check recent changes [STRUCTURAL]
   - 2d. `grep(...)`, `LSP(operation="findReferences")` — trace data flow [STRUCTURAL]
3. **Phase 2 — Pattern Analysis** [CONVENTIONAL — "YOU do this"]:
   - 3a. Find working examples in codebase via `grep`/`glob` [STRUCTURAL]
   - 3b. Compare working vs. broken code [CONVENTIONAL]
   - 3c. Identify differences [CONVENTIONAL]
4. **Phase 3 — Hypothesis and Test** [CONVENTIONAL — "YOU do this"]:
   - 4a. State hypothesis clearly: "I think X is root cause because Y" [CONVENTIONAL]
   - 4b. `bash(...)` — run minimal test to confirm/deny [STRUCTURAL]
   - 4c. If not confirmed → return to Phase 1 with new information [CONVENTIONAL]
5. **Phase 4 — Fix** [STRUCTURAL — only delegation path available]:
   - 5a. `delegate(agent="foundation:bug-hunter", instruction="Fix confirmed bug. Root cause: [X]. Evidence: [Y]...")` [STRUCTURAL — only way to modify files]
   - 5b. After agent returns: `bash("pytest ...")` — verify fix yourself [CONVENTIONAL]
   - 5c. If fix fails after 3 attempts → STOP, discuss architecture with user [CONVENTIONAL]
6. `mode(operation='set', name='verify')` — two-step gate [STRUCTURAL]

**Exit conditions:** Root cause found, fix verified. Transition to verify or, if fix reveals design flaw, to brainstorm.

**Key behavioral constraint:** Web research is blocked in debug mode. If the bug requires online research, the orchestrator MUST delegate to `web-research` agent — this is the only path [STRUCTURAL].

---

### Scenario 3: Codebase Exploration / Question

**Entry conditions:** User asks about the codebase (e.g., "How does authentication work?" or "Show me the test structure").

**Prescriptive Rules:**
- No mode is automatically entered for exploration questions [INFERRED]
- In modeless state, all tools are available without restrictions [STRUCTURAL]
- If a mode IS active, exploration tools (read_file, glob, grep, LSP) are safe in ALL modes [STRUCTURAL]

**Likely Runtime Pattern:**

1. Assess scope of question [INFERRED]:
   - Simple question → answer directly using exploration tools
   - Deep investigation → consider delegating to specialized agents
2. **Direct exploration** (most common):
   - 2a. `glob("**/*.py")` — find relevant files [STRUCTURAL — safe in all modes]
   - 2b. `grep(pattern="class Auth", type="py")` — locate components [STRUCTURAL]
   - 2c. `read_file(...)` — read implementation [STRUCTURAL]
   - 2d. `LSP(operation="documentSymbol")` — understand structure [STRUCTURAL]
   - 2e. Present findings to user [CONVENTIONAL]
3. **Delegated exploration** (for deep dives):
   - 3a. `delegate(agent="foundation:explorer", instruction="Map the authentication subsystem...")` [INFERRED — delegate safe in most modes]
   - 3b. `delegate(agent="code-intel", instruction="Trace call hierarchy for login()")` [INFERRED]
4. No mode transition expected [INFERRED — exploration is a leaf activity]

**Exit conditions:** User's question answered. Session continues or user initiates a new task.

**Key behavioral note:** If the exploration reveals a bug, the orchestrator should suggest `/debug`. If it sparks a feature idea, suggest `/brainstorm`. The exploration itself does not require a mode.

---

### Scenario 4: Small Task (< 20 lines, skip modes)

**Entry conditions:** User requests a small, well-defined change (e.g., "Fix the typo in config.py" or "Add a log line to the handler").

**Prescriptive Rules:**
- No mode is required for trivial changes [INFERRED — modes are for structured development workflows]
- In modeless state, all tools including `write_file`/`edit_file` are available [STRUCTURAL]
- The superpowers methodology is designed for non-trivial features; it has no explicit small-task guidance [INFERRED]

**Likely Runtime Pattern:**

1. Read the target file: `read_file("config.py")` [STRUCTURAL]
2. Make the change: `edit_file(file_path="config.py", old_string="...", new_string="...")` [STRUCTURAL — no mode blocking]
3. Verify the change:
   - 3a. `python_check(paths=["config.py"])` — lint/type check [CONVENTIONAL]
   - 3b. `bash("pytest tests/test_config.py -v")` — run relevant tests [CONVENTIONAL]
4. Confirm to user: show the diff and test results [CONVENTIONAL]
5. Optionally commit: `bash("git add config.py && git commit -m 'fix: correct typo in config'")` [CONVENTIONAL]

**Exit conditions:** Change applied and verified. No mode transitions.

**Key behavioral note:** If a user enters a mode (e.g., `/brainstorm`) for a trivial task, the brainstorm mode will still enforce its full process — the anti-rationalization table explicitly says: "A todo list, a single-function utility — all of them." However, the LLM may suggest skipping modes if the task is genuinely trivial and no mode is active.

**Escalation path:** If the "small task" turns out to be more complex (file modifications cascade, tests break, design questions arise), the orchestrator should recommend entering the appropriate mode:
- Tests break → `/debug` [INFERRED]
- Design uncertainty → `/brainstorm` [INFERRED]
- Multiple files affected → `/write-plan` + `/execute-plan` [INFERRED]

---

### Cross-Scenario Behavioral Invariants

These hold regardless of which scenario is active:

| Invariant | Type | Description |
|-----------|------|-------------|
| **Tool cascade is absolute** | [STRUCTURAL] | If a tool is blocked, the LLM call will fail. No prose instruction can override this. |
| **Infrastructure tools bypass cascade** | [STRUCTURAL] | `mode()` and `todo()` always work regardless of active mode. |
| **Gate policy on transitions** | [STRUCTURAL] | First `mode(set)` call is denied; second confirms. Prevents accidental transitions. |
| **Sub-agent autonomy** | [STRUCTURAL] | Delegated agents run in their own sessions with their own tool access. Calling mode restrictions do not propagate. |
| **Skill-mode association** | [CONVENTIONAL] | Each mode has an associated skill loaded at entry. Skill provides WHAT; mode enforces HOW. |
| **No file writes in investigation modes** | [STRUCTURAL] | brainstorm, write-plan, execute-plan, debug all block `write_file`/`edit_file`. Only path is delegation. |
| **verify is the self-reliant mode** | [STRUCTURAL] | Only mode where `delegate` is on warn and `recipes` is blocked. Orchestrator verifies directly. |
| **finish is the only exit** | [STRUCTURAL] | Only mode with `allow_clear: true`. All other modes must transition; they cannot exit directly. |
| **Anti-rationalization is pervasive** | [CONVENTIONAL] | Every mode includes an anti-rationalization table preventing common shortcuts. |
| **Parallel dispatch default** | [CONVENTIONAL] | Independent delegations should be dispatched in parallel (from `dispatching-parallel-agents` skill). |
| **Sequential implementation** | [CONVENTIONAL] | Implementer tasks are NEVER dispatched in parallel (execute-plan Operational Rule 1). |
| **Review ordering** | [CONVENTIONAL] | spec-reviewer THEN code-quality-reviewer. Never reversed, never skipped (execute-plan Operational Rule 3). |
| **Three-fix escalation** | [CONVENTIONAL] | After 3 review-fix cycles without convergence, escalate to user with options. |

---

*End of behavioral specification.*
