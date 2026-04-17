I t# Behavioral Model: systems-design Bundle

**Source**: Mechanism plan extraction  
**Generated**: 2026-04-15  
**Status**: Derived from plan; subject to composition validation

---

## 1. Overview

### Bundle Identity

| Field | Value |
|-------|-------|
| Name | `systems-design` |
| Purpose | Standalone and composable Amplifier bundle providing structured system design exploration — modeling, alternatives, tradeoffs, risks, and documentation |
| Type | Behavioral bundle |
| Installation | Via `amplifier bundle add git+...@main --app` with subdirectory `behaviors/systems-design.yaml` |

### Direct Dependencies

The bundle declares the following dependencies:
- `amplifier-foundation` (base capability)
- `tool-mode` (mode execution)
- `tool-skills` (skill loading and invocation)
- `hooks-mode` (hook system)
- `hooks-design-context` (design document awareness)
- `behavior-modes` (mode routing)
- `foundation:explorer` (agent: multi-file codebase exploration)
- `foundation:zen-architect` (agent: module-level design reasoning)
- `foundation:git-ops` (agent: git/GitHub operations)
- `foundation:file-ops` (agent: file system operations)

### Component Inventory

| Type | Count | Components |
|------|-------|------------|
| **Modes** | 2 | `systems-design`, `systems-design-review` |
| **Agents** | 3 | `systems-architect`, `systems-design-critic`, `systems-design-writer` |
| **Skills** | 7 | `systems-design-methodology` (inline), `systems-design-review-methodology` (inline), `tradeoff-analysis` (inline), `architecture-primitives` (inline), `adversarial-review` (fork), `system-type-web-service` (inline), `system-type-event-driven` (inline) |
| **Recipes** | 4 | `codebase-understanding`, `systems-design-exploration`, `systems-design-cycle`, `systems-design-review` |
| **Context Files** | 5 | `instructions.md`, `system-design-principles.md`, `tradeoff-frame.md`, `adversarial-perspectives.md`, `structured-design-template.md` |
| **Hooks** | 1 | `hooks-design-context` |
| **Total** | **23** | |

---

## 2. Tool Governance

### Tool Availability Matrix by Mode

#### Mode: `systems-design`

| Tool | Policy | Status | Notes |
|------|--------|--------|-------|
| `read_file` | Safe | ✓ | Code and spec reading |
| `glob` | Safe | ✓ | File discovery |
| `grep` | Safe | ✓ | Content search |
| `web_search` | Safe | ✓ | External research |
| `web_fetch` | Safe | ✓ | Documentation retrieval |
| `LSP` | Safe | ✓ | Semantic code navigation |
| `delegate` | Safe | ✓ | Agent invocation |
| `load_skill` | Safe | ✓ | Skill loading |
| `recipes` | Safe | ✓ | Recipe execution |
| `todo` | Safe | ✓ | Task tracking |
| `team_knowledge` | Safe | ✓ | Knowledge base access |
| `mode` | Safe | ✓ | Mode transitions |
| `bash` | Warn | ⚠ | With caution |
| `write_file` | Block | ✗ | Blocked by default |
| `edit_file` | Block | ✗ | Blocked by default |
| `apply_patch` | Block | ✗ | Blocked by default |
| `python_check` | Block | ✗ | Blocked by default |

**Default action for unlisted tools**: Block

**Behavioral directives for mode**:
- Design thinking, not implementation
- Read code, don't write it
- Delegate document production to writer agent
- Delegate system-level analysis to architect agent

**Companion skill**: `systems-design-methodology` (inline)

**Transitions to**: `systems-design-review`

---

#### Mode: `systems-design-review`

| Tool | Policy | Status | Notes |
|------|--------|--------|-------|
| `read_file` | Safe | ✓ | Design and code reading |
| `glob` | Safe | ✓ | File discovery |
| `grep` | Safe | ✓ | Content search |
| `web_search` | Safe | ✓ | External research |
| `web_fetch` | Safe | ✓ | Documentation retrieval |
| `LSP` | Safe | ✓ | Semantic code navigation |
| `delegate` | Safe | ✓ | Agent invocation |
| `load_skill` | Safe | ✓ | Skill loading |
| `recipes` | Safe | ✓ | Recipe execution |
| `todo` | Safe | ✓ | Task tracking |
| `team_knowledge` | Safe | ✓ | Knowledge base access |
| `mode` | Safe | ✓ | Mode transitions |
| `bash` | Warn | ⚠ | With caution |
| `write_file` | Block | ✗ | Blocked by default |
| `edit_file` | Block | ✗ | Blocked by default |
| `apply_patch` | Block | ✗ | Blocked by default |
| `python_check` | Block | ✗ | Blocked by default |

**Default action for unlisted tools**: Block

**Behavioral directives for mode**:
- Evaluation, not modification
- Read code, compare against design claims, find gaps
- Produce assessments, not code changes

**Companion skill**: `systems-design-review-methodology` (inline)

**Transitions to**: `systems-design`

---

### Tool Governance Constraints & Limitations

The plan specifies tool policies for the two active modes, but cannot fully derive:

1. **Composition loopholes**: When this bundle delegates to foundation agents (`foundation:explorer`, `foundation:zen-architect`, `foundation:git-ops`, `foundation:file-ops`), those agents carry their own tool policies. If a mode blocks `write_file`, a delegated agent may still have it available (unblock), creating a composition loophole that can only be detected at runtime.

2. **Delegation necessity**: The plan specifies which agents are invoked but not whether delegation is enforced for specific operations or optional. This requires resolved transitive composition.

3. **Actual tool availability**: The plan declares tools as "safe/warn/confirm/block" but does not verify whether those tools are actually mounted in the Amplifier runtime. Availability depends on resolved dependencies.

---

## 3. Mode Behaviors

### Mode: `systems-design`

| Property | Value |
|----------|-------|
| **Purpose** | Structured system design exploration — modeling, alternatives, tradeoffs, risks, documentation |
| **Type** | Interactive conversation mode |
| **Companion Skill** | `systems-design-methodology` (inline, auto-loaded on entry) |
| **Transitions** | → `systems-design-review` |

**Tool Policy Summary**:
- Safe: `read_file`, `glob`, `grep`, `web_search`, `web_fetch`, `LSP`, `delegate`, `load_skill`, `recipes`, `todo`, `team_knowledge`, `mode`
- Warn: `bash`
- Block: `write_file`, `edit_file`, `apply_patch`, `python_check`
- Default: Block

**Behavioral Directives**:
1. Design thinking, not implementation
2. Read code, don't write it
3. Delegate document production to writer agent
4. Delegate system-level analysis to architect agent

**Entry Behavior**: 
- On mode entry, automatically load companion skill `systems-design-methodology`
- Skill orchestrates 8-phase conversation flow (see Section 5: Skill Behaviors for detailed workflow)

**Context Loading**:
- Loaded by skill: `context/system-design-principles.md`, `context/tradeoff-frame.md`, `context/structured-design-template.md`

---

### Mode: `systems-design-review`

| Property | Value |
|----------|-------|
| **Purpose** | Evaluate an existing design or proposed architectural change against the codebase |
| **Type** | Interactive evaluation mode |
| **Companion Skill** | `systems-design-review-methodology` (inline, auto-loaded on entry) |
| **Transitions** | → `systems-design` |

**Tool Policy Summary**:
- Safe: `read_file`, `glob`, `grep`, `web_search`, `web_fetch`, `LSP`, `delegate`, `load_skill`, `recipes`, `todo`, `team_knowledge`, `mode`
- Warn: `bash`
- Block: `write_file`, `edit_file`, `apply_patch`, `python_check`
- Default: Block

**Behavioral Directives**:
1. Evaluation, not modification
2. Read code, compare against design claims, find gaps
3. Produce assessments, not code changes

**Entry Behavior**:
- On mode entry, automatically load companion skill `systems-design-review-methodology`
- Skill orchestrates 6-step workflow (see Section 5: Skill Behaviors for detailed workflow)

**Context Loading**:
- Loaded by skill: `context/adversarial-perspectives.md`, `context/system-design-principles.md`

---

## 4. Agent Behaviors

### Agent: `systems-architect`

| Property | Value |
|----------|-------|
| **Purpose** | System-level design reasoning — modeling, candidate generation, tradeoff evaluation, assessment |
| **Model Role** | `reasoning` (deep architectural thinking) |
| **Operating Modes** | ANALYZE, DESIGN, ASSESS |
| **Trigger Conditions** | No explicit triggers; invoked via delegation |

**Behavioral Directives**:
1. Model first, solutions second
2. 3 candidates minimum (in DESIGN mode)
3. Evaluate against 8-dimension frame
4. Name unknowns explicitly
5. Apply YAGNI (You Aren't Gonna Need It)
6. Prefer simplest design whose failure modes are acceptable
7. Delegate module-level work to `foundation:zen-architect`

**Tool Requirements**:
- `read_file`, `glob`, `grep`, `LSP`, `web_search`, `web_fetch`, `delegate`

**Context Loading** (automatic on invocation):
- `context/system-design-principles.md`
- `context/tradeoff-frame.md`
- `context/structured-design-template.md`

**Operating Modes Explained**:

| Mode | Purpose | Entry Condition | Output |
|------|---------|-----------------|--------|
| **ANALYZE** | Model the system, extract constraints, identify unknowns | "Model first" directive; Phase 1 of design cycle | System map + constraints document |
| **DESIGN** | Generate 3+ candidate architectures, evaluate tradeoffs, refine design | After system map is validated | Design document with recommendation + reasoning |
| **ASSESS** | Evaluate existing codebase, identify boundaries, map flows | `systems-design-review` mode or manual invocation | Assessment report + findings |

**Exit Conditions**:
- **ANALYZE mode**: System map produced, validated by user
- **DESIGN mode**: Design document with recommendation produced
- **ASSESS mode**: Assessment report produced
- **Any mode**: Scope determined module-level and delegated to `foundation:zen-architect`

**Relationship to Modes**: Invoked from both `systems-design` and `systems-design-review` modes via companion skills

---

### Agent: `systems-design-critic`

| Property | Value |
|----------|-------|
| **Purpose** | Adversarial stress-testing from 5 perspectives — finds flaws, does NOT propose fixes |
| **Model Role** | `critique` (analytical evaluation) |
| **Operating Modes** | SRE, Security, Staff Engineer, Finance, Operator |
| **Trigger Conditions** | No explicit triggers; invoked at Phase 5 of design cycle (risk assessment) |

**Behavioral Directives**:
1. Read actual files, not summaries
2. Find flaws, don't fix them
3. Be specific — name concrete failure modes
4. Be calibrated — rank by severity and likelihood

**Tool Requirements**:
- `read_file`, `glob`, `grep`, `LSP`

**Context Loading** (automatic on invocation):
- `context/adversarial-perspectives.md`
- `context/system-design-principles.md`

**Operating Modes Explained**:

Each mode represents a distinct reviewer perspective:

| Perspective | Focus | Driving Questions |
|-------------|-------|-------------------|
| **SRE** | Operational reliability, failure modes, observability | Will this fail under load? Can we troubleshoot it? |
| **Security** | Threat models, vulnerabilities, attack surface | What's exposed? What can go wrong? |
| **Staff Engineer** | Maintainability, architectural debt, team scaling | Can we maintain this? Will it scale with the team? |
| **Finance** | Cost, infrastructure spend, ROI | What will this cost? What do we gain? |
| **Operator** | Deployability, operational overhead, runbooks | Can we operate this? How complex are runbooks? |

**Exit Conditions**:
- Severity-ranked risk assessment covering all 5 perspectives
- Specific failure modes named with likelihood and severity estimates
- No proposed fixes (that's not this agent's role)

**Relationship to Modes**: Invoked from `systems-design` mode at Phase 5, or from `systems-design-review` mode at Step 3

---

### Agent: `systems-design-writer`

| Property | Value |
|----------|-------|
| **Purpose** | Write formal design document to disk from validated design, then commit |
| **Model Role** | `writing` (long-form technical documentation) |
| **Operating Modes** | None (single-purpose writing agent) |
| **Trigger Conditions** | Invoked after design is validated through all prior phases |

**Behavioral Directives**:
1. Write ONLY what was validated
2. Do not add, invent, or decide
3. Do not ask questions
4. Do not conduct conversations
5. Always commit after writing

**Tool Requirements**:
- `write_file`, `bash`, `delegate`

**Context Loading** (automatic on invocation):
- `context/structured-design-template.md`

**Input Contract**:
- Receives validated design content via delegation instruction
- Must include all decision rationale, tradeoff analysis, risk assessment from prior phases

**Exit Conditions**:
- Design document written to disk at `docs/designs/YYYY-MM-DD-<topic>-design.md`
- Git commit created with appropriate metadata
- No further conversation or decisions

**Relationship to Modes**: Invoked from `systems-design` mode at Phase 8 (final output phase)

---

## 5. Skill Behaviors

### Inline Skills (Conversation Control)

#### Skill: `systems-design-methodology`

| Property | Value |
|----------|-------|
| **Purpose** | Governs 8-phase conversation flow for `/systems-design` mode. Orchestrates delegation to agents, presents results to user, feeds user input back. |
| **Type** | Inline (behavior control + orchestration) |
| **Mode Association** | `systems-design` |
| **Invocation** | Automatically loaded at `/systems-design` mode entry |
| **Conversation Driver** | Skill handles CONVERSATION; agents handle ANALYSIS |

**8-Phase Workflow**:

| Phase | Agent | Role | Input | Output | User Checkpoint |
|-------|-------|------|-------|--------|-----------------|
| 1 | `systems-architect` (ANALYZE) | System modeling | Problem statement | System map | ✓ **REQUIRED** validate before proceeding |
| 2 | `systems-architect` (ANALYZE) | Constraint extraction | System map | Constraints document | (implicit in map) |
| 3 | `systems-architect` (DESIGN) | Candidate exploration | System map + constraints | 3 architectural candidates | (may load `architecture-primitives` or system-type-* skill) |
| 4 | `systems-architect` (DESIGN) | Tradeoff analysis | Candidates | 8-dimension tradeoff matrix | (may load `tradeoff-analysis` skill if contested) |
| 5 | `systems-design-critic` | Risk assessment | Tradeoff evaluation | Risk summary (5 perspectives) | ✓ **CONDITIONAL** (default: yes; may suggest fork skill for parallel analysis) |
| 6 | `systems-architect` (DESIGN) | Design refinement | Risks + feedback | Refined design | (iterate if user input triggers revision) |
| 7 | `systems-architect` (DESIGN) | Migration planning | Refined design | Rollout strategy | (backward compat, rollback, success signals, timeline) |
| 8 | `systems-design-writer` | Document production | All validated content | Design document on disk + committed | (workflow complete) |

**Behavioral Directives**:
1. Handle CONVERSATION; agents handle ANALYSIS
2. Orchestrate, delegate to `systems-architect`, present results to user, feed back their input
3. Block progression at Phase 1 until user validates system map
4. May revisit earlier phases when:
   - User explicitly requests it
   - A later phase reveals an invalid assumption from an earlier phase
   - The architect identifies a constraint that invalidates the current system map

**Skill-to-Agent Delegation Pattern**:
- Skill receives user input
- Skill delegates to appropriate agent in appropriate operating mode
- Agent produces output (system map, candidates, tradeoff matrix, etc.)
- Skill presents output to user
- Skill receives user feedback and either:
  - Proceeds to next phase, OR
  - Loops back to earlier phase if feedback invalidates prior work

---

#### Skill: `systems-design-review-methodology`

| Property | Value |
|----------|-------|
| **Purpose** | Governs 6-step conversation flow for `/systems-design-review` mode |
| **Type** | Inline (behavior control + orchestration) |
| **Mode Association** | `systems-design-review` |
| **Invocation** | Automatically loaded at `/systems-design-review` mode entry |
| **Conversation Driver** | Skill handles CONVERSATION; agents handle ANALYSIS |

**6-Step Workflow**:

| Step | Agent | Role | Input | Output |
|------|-------|------|-------|--------|
| 1 | User + Skill | Understand design | Design docs, goals, constraints | Survey of design intent + codebase |
| 2 | Skill + LSP/grep | Evaluate vs code | Design claims, codebase | Gap analysis |
| 3 | `systems-design-critic` OR fork | Adversarial analysis | Design + code gaps | Risk assessment (5 perspectives) |
| 4 | Skill | Tradeoff validation | Risk output | Load `tradeoff-analysis` skill if needed |
| 5 | Skill + agents | Synthesize & recommend | All prior outputs | Recommendation: Proceed / Modify / Reconsider |
| 6 | Skill | Capture action items | User feedback | Structured action list |

**Behavioral Directives**:
1. Handle CONVERSATION; agents handle ANALYSIS
2. Read design thoroughly before any critique

**Step 3 Alternative Paths**:
- **Option A**: Delegate to `systems-design-critic` agent (asynchronous within session)
- **Option B**: Load `adversarial-review` fork skill (parallel multi-agent analysis in separate sub-session)

---

#### Skill: `tradeoff-analysis`

| Property | Value |
|----------|-------|
| **Purpose** | 8-dimension evaluation framework and matrix template for evaluating architectural alternatives |
| **Type** | Inline (analysis framework) |
| **Invocation** | Phase 4 of design cycle, or whenever alternatives must be compared |
| **Framework** | 8-dimension matrix with qualitative ratings |

**8 Dimensions**:

| Dimension | Meaning | Example Consideration |
|-----------|---------|----------------------|
| **Latency** | Response time, delay | End-to-end request latency, p99 percentile |
| **Complexity** | System and operational complexity | Number of moving parts, debugging difficulty |
| **Reliability** | Fault tolerance, mean time between failure | Availability target, recovery time |
| **Cost** | Infrastructure, licensing, personnel | Monthly spend, operational overhead |
| **Security** | Attack surface, threat model, defense depth | Exposure vectors, cryptographic strength |
| **Scalability** | Horizontal/vertical growth limits | Throughput ceiling, data volume limits |
| **Reversibility** | Ease of rollback, switchability | Can we undo this? How easily? |
| **Organizational Fit** | Team skills, existing practices, learning curve | Does the team know this tech? Will they maintain it? |

**Evaluation Rules**:
1. Force all analysis into 8-dimension frame
2. Qualitative ratings (`good` / `adequate` / `poor`) with concrete notes, NOT numeric scores
3. Every cell must have: rating + note (concrete, specific)
4. Identify 1-2 dominant dimensions
5. Explicitly state what chosen option SACRIFICES
6. Evaluate 2-5 alternatives (minimum 2, maximum 5)

**Exit Condition**: Completed tradeoff matrix with recommendation and explicit sacrifice statement

---

#### Skill: `architecture-primitives`

| Property | Value |
|----------|-------|
| **Purpose** | Catalog of reusable architectural primitives with what-when-wrong evaluation |
| **Type** | Inline (reference material + analysis) |
| **Invocation** | Phase 3 candidate exploration, if pattern selection is unclear |
| **Scope** | Boundaries/contracts, state machines, sync vs async, queues, caching, idempotency, retries, circuit breakers, consistency models, observability, blast-radius isolation |

**Evaluation Axes for Each Primitive**:
1. **What it is**: Definition and basic mechanics
2. **When it's right**: Conditions where this primitive solves problems cleanly
3. **When it's wrong**: Conditions where this primitive causes problems or fails

**Behavioral Directives**:
- Evaluate every primitive on all 3 axes
- Use primitives to populate candidate architectures

---

### Fork Skill (Parallel Multi-Agent Analysis)

#### Skill: `adversarial-review`

| Property | Value |
|----------|-------|
| **Purpose** | Multi-perspective adversarial review launching 5 parallel critic agents, synthesizing into unified risk assessment |
| **Type** | Fork (spawns parallel sub-sessions) |
| **Invocation** | User invokes during design, or at Phase 5 as alternative to delegating to `systems-design-critic` agent |
| **Input** | Design content via delegation instruction or design files in working directory |
| **Output** | Unified risk assessment synthesized from 5 perspectives |

**Execution Pattern**:
1. Receives design content via `$ARGUMENTS` variable or reads design files from session working directory
2. Spawns 5 parallel delegations:
   - `systems-design-critic` (SRE perspective)
   - `systems-design-critic` (Security perspective)
   - `systems-design-critic` (Staff Engineer perspective)
   - `systems-design-critic` (Finance perspective)
   - `systems-design-critic` (Operator perspective)
3. Each agent receives same design content
4. Waits for all 5 to complete asynchronously
5. Synthesizes outputs into single unified risk assessment

**Advantages over sequential `systems-design-critic`**:
- Parallel execution (faster for waiting on agent responses)
- All 5 perspectives complete independently without dependency on intermediate synthesis
- Can be invoked in parallel with other analysis (e.g., tradeoff analysis ongoing in parallel)

---

### System-Type Skills (Domain-Specific Patterns)

#### Skill: `system-type-web-service`

| Property | Value |
|----------|-------|
| **Purpose** | Domain-specific patterns, guarantees, failure modes, and anti-patterns for request/response web services |
| **Type** | Inline (reference material + guidance) |
| **Invocation** | Phase 3, when architect or user identifies system type as web service |
| **Scope** | REST/GraphQL/gRPC architectures |
| **Relationship to agent** | Loaded to inform `systems-architect` DESIGN mode decisions |

---

#### Skill: `system-type-event-driven`

| Property | Value |
|----------|-------|
| **Purpose** | Domain-specific patterns, guarantees, failure modes, and anti-patterns for event-driven systems |
| **Type** | Inline (reference material + guidance) |
| **Invocation** | Phase 3, when architect or user identifies system type as event-driven |
| **Scope** | Pub/sub, event sourcing, CQRS, sagas, delivery guarantees |
| **Relationship to agent** | Loaded to inform `systems-architect` DESIGN mode decisions |

---

## 6. Context & Cross-Cutting Concerns

### Context Files

All context files are marked `always_loaded: true` and loaded into the `systems-design` mode conversation automatically.

| File | Purpose | Estimated Tokens | Always Loaded | Notes |
|------|---------|------------------|---------------|-------|
| `context/instructions.md` | Standing-order routing table mapping trigger phrases (e.g., 'design a system for...', 'review this architecture...') to modes and recipes. No methodology, just routing. Includes mode-active guard to skip routing when a mode is already active. | 800 | ✓ | Route planning only; not methodology |
| `context/system-design-principles.md` | 6 core thinking tools: map first, four layers, tradeoff analysis, optimize/sacrifice framing, causal tracing, simplest-acceptable design | 800 | ✓ | Foundational thinking | 
| `context/tradeoff-frame.md` | 8-dimension evaluation framework (latency, complexity, reliability, cost, security, scalability, reversibility, organizational fit) with matrix template | 800 | ✓ | Used in Phase 4 |
| `context/adversarial-perspectives.md` | 5 reviewer perspectives (SRE, security, staff engineer, finance, operator) with driving questions and output structure | 800 | ✓ | Used in Phase 5 |
| `context/structured-design-template.md` | 11-section output template for design documents (problem framing through success metrics) | 800 | ✓ | Used in Phase 8 |

**Total estimated token load on mode entry**: ~4,000 tokens

---

### Ambient Design Document Awareness Hook

#### Hook: `hooks-design-context`

| Property | Value |
|----------|-------|
| **Name** | `hooks-design-context` |
| **Purpose** | Ambient design document awareness — scans `docs/designs/*.md` and injects a compact inventory of existing designs (titles and dates) before every LLM call |
| **Trigger** | Pre-completion hook (before each LLM call) |
| **Behavior** | 1. Scan `docs/designs/` for markdown files<br/>2. Extract title from first `#` heading<br/>3. Extract date from `YYYY-MM-DD` filename prefix<br/>4. Inject compact inventory into LLM context<br/>5. Silently inject nothing if `docs/designs/` doesn't exist (no error, no output) |
| **Token Cost** | Minimal (compact inventory format) |
| **Side Effects** | None (read-only, silent on empty) |

**Effect**: The agent always knows what designs exist without being told explicitly. This enables:
- Automatic awareness of prior design decisions
- Prevention of reinventing solutions already documented
- Natural reference to existing designs by date/title in conversation

---

### Delegation Chains and Routing Patterns

#### Routing: Trigger → Mode

The `context/instructions.md` file provides a routing table (standing-order) that maps user trigger phrases to modes and recipes:

**Implicit routing table structure** (derived from mechanism plan):

| Trigger Phrase | Route To | Invokes |
|---|---|---|
| "design a system for...", "help me design...", "how should we build..." | `systems-design` mode | `systems-design-methodology` skill → orchestrates 8-phase flow |
| "review this architecture...", "evaluate this design...", "is this design good?" | `systems-design-review` mode | `systems-design-review-methodology` skill → orchestrates 6-step flow |

**Mode-active guard**: If a mode is already active, routing is skipped (no re-entry of same mode).

---

#### Delegation Chain: Design Cycle (Detailed)

```
User invokes /systems-design
    ↓
systems-design-methodology skill enters ACTIVE
    ↓
Phase 1: Delegate to systems-architect (ANALYZE)
    ↓ [reads: system-design-principles, tradeoff-frame, structured-design-template]
    ↓ [produces: system map]
    ↓ [User validates: YES/NO]
    ↓
Phase 2-4: Delegate to systems-architect (DESIGN)
    ↓ [may load: architecture-primitives skill, system-type-* skill]
    ↓ [produces: 3 candidates + 8-dimension tradeoff matrix]
    ↓
Phase 5: Delegate to systems-design-critic (5 perspectives)
    ↓ [reads: adversarial-perspectives, system-design-principles]
    ↓ [produces: risk assessment]
    ↓ [User reviews: ACCEPT/REVISE]
    ↓
Phase 6-7: Delegate to systems-architect (DESIGN)
    ↓ [refines design, migration plan]
    ↓
Phase 8: Delegate to systems-design-writer
    ↓ [writes: docs/designs/YYYY-MM-DD-<topic>-design.md]
    ↓ [commits to git]
    ↓
Workflow complete
```

---

## 7. Recipe Workflows

### Recipe: `codebase-understanding`

| Property | Value |
|----------|-------|
| **Purpose** | Survey existing codebase and produce architectural overview |
| **Execution Mode** | Flat (sequential, no approvals) |
| **Entry Point** | Manual invocation or as prerequisite to other recipes |
| **Duration** | Single session |

**Workflow**:

| Step ID | Agent | Produces | Consumes | Purpose |
|---------|-------|----------|----------|---------|
| `survey-structure` | `foundation:explorer` | `structure_survey` | (none) | Walk codebase, map file structure, identify modules |
| `identify-boundaries` | `systems-architect` (ASSESS) | `boundary_analysis` | `structure_survey` | Find module boundaries, external interfaces |
| `map-flows` | `systems-architect` (ASSESS) | `flow_analysis` | `structure_survey`, `boundary_analysis` | Trace data/control flow, entry/exit points |
| `architectural-overview` | `systems-architect` (ASSESS) | `architectural_overview` | all prior outputs | Synthesize into system architecture description |

**Data Flow**:
```
foundation:explorer
    ↓ structure_survey
    ↓
systems-architect (ASSESS) ← boundary_analysis ← identify-boundaries
    ↓
    ↓ flow_analysis
    ↓
systems-architect (ASSESS)
    ↓ architectural_overview
```

**Approval Gates**: None (flat workflow)

**Relationship to Modes**: Standalone recipe; can be used before entering `systems-design` mode to gather codebase context

---

### Recipe: `systems-design-exploration`

| Property | Value |
|----------|-------|
| **Purpose** | Rapid parallel exploration of 3 architectural alternatives with tradeoff evaluation |
| **Execution Mode** | Flat (sequential, no approvals) |
| **Entry Point** | Manual recipe invocation with problem statement |
| **Duration** | Single session; faster than interactive mode |
| **Relationship to Modes** | Parallel alternative to 8-phase `/systems-design` interactive mode |

**Workflow**:

| Step ID | Agent | Produces | Consumes | Purpose |
|---------|-------|----------|----------|---------|
| `frame-problem` | `systems-architect` (ANALYZE) | `problem_frame` | (none) | Model system, identify constraints |
| `generate-candidates` | `systems-architect` (DESIGN) | `3 candidates` | `problem_frame` | Generate 3 distinct architectures |
| `evaluate-tradeoffs` | `systems-architect` (DESIGN) | `tradeoff_evaluation` | `problem_frame`, `3 candidates` | 8-dimension comparison matrix |
| `adversarial-review` | `systems-design-critic` | `adversarial_review` | `tradeoff_evaluation` | **CONDITIONAL**: Risk assessment from 5 perspectives |

**Data Flow**:
```
frame-problem (ANALYZE)
    ↓ problem_frame
    ↓
generate-candidates (DESIGN)
    ↓ 3 candidates
    ↓
evaluate-tradeoffs (DESIGN)
    ↓ tradeoff_evaluation
    ↓
[if with_adversarial_review == 'true']
adversarial-review (critic)
    ↓ adversarial_review
```

**Conditional Step**:
- Step 4 (`adversarial-review`) is conditional on recipe context variable `with_adversarial_review`
- Default: `'false'` (skip risk assessment)
- If `'true'`: Include 5-perspective risk assessment

**Approval Gates**: None (flat workflow)

**Relationship to Modes**: 
- Automated pipeline parallel to `/systems-design` interactive mode
- Both use same agents and principles
- Key difference: Recipe is fully autonomous; mode requires user interaction at checkpoints

**Use Case**: 
- Rapid design exploration without user checkpoint delays
- Automated design generation for batch scenarios
- Input to manual review process

---

### Recipe: `systems-design-cycle`

| Property | Value |
|----------|-------|
| **Purpose** | End-to-end system design with human checkpoints (approval gates) |
| **Execution Mode** | Staged (includes 3 approval gates) |
| **Entry Point** | Manual recipe invocation with problem statement |
| **Duration** | Multi-turn (resumable); gates halt execution for user input |
| **Relationship to Modes** | Automated alternative to 8-phase `/systems-design` interactive mode |

**Workflow**:

| Step ID | Agent | Produces | Consumes | Purpose | Approval Gate |
|---------|-------|----------|----------|---------|---------------|
| `build-system-map` | `systems-architect` (ANALYZE) | `system_map` | (none) | Model system | (implicit in step) |
| `extract-constraints` | `systems-architect` (ANALYZE) | `constraints_analysis` | `system_map` | Extract constraints | (implicit in step) |
| `generate-candidates` | `systems-architect` (DESIGN) | `3 candidates` | `system_map`, `constraints_analysis` | Generate 3 architectures | **`candidates`** |
| `evaluate-tradeoffs` | `systems-architect` (DESIGN) | `tradeoff_evaluation` | `3 candidates` | 8-dimension analysis | (implicit in step) |
| `adversarial-review` | `systems-design-critic` | `risk_assessment` | `tradeoff_evaluation` | Risk from 5 perspectives | (implicit in step) |
| `refine-design` | `systems-architect` (DESIGN) | `refined_design` | `tradeoff_evaluation`, `risk_assessment` | Incorporate feedback | **`risk-and-refinement`** |
| `write-document` | `systems-design-writer` | `design_document` | `refined_design` | Write to disk + commit | **`documentation`** |

**Data Flow**:
```
build-system-map (ANALYZE)
    ↓ system_map
    ↓
extract-constraints (ANALYZE)
    ↓ constraints_analysis
    ↓
generate-candidates (DESIGN)
    ↓ 3 candidates ← [GATE: candidates]
    ↓
evaluate-tradeoffs (DESIGN)
    ↓ tradeoff_evaluation
    ↓
adversarial-review (critic)
    ↓ risk_assessment
    ↓
refine-design (DESIGN) ← [GATE: risk-and-refinement]
    ↓ refined_design
    ↓
write-document (writer)
    ↓ design_document ← [GATE: documentation]
```

**Approval Gates**:

| Gate | Purpose | User Input | Feeds To |
|------|---------|-----------|----------|
| **`candidates`** | Validate 3 candidates are viable before tradeoff analysis | "Approve candidates" / "Request changes" / revise prompt | Subsequent steps use approved candidates |
| **`risk-and-refinement`** | Approve risk assessment and decide on design refinement | Risk assessment message + user acceptance / revision | Refinement agent uses feedback |
| **`documentation`** | Final approval before writing and committing design document | "Write document" / "Request changes" / revise | Writer agent receives approval |

**Relationship to Modes**: 
- Automated alternative to `/systems-design` interactive mode
- Same 8-phase structure (phases 1-2 collapse into steps 1-2; phases 3-4 are steps 3-4; etc.)
- Key difference: Recipe enforces gates; mode allows dynamic conversation

**Use Case**: 
- Design-driven development when complete automation with checkpoints is desired
- Documentation-first design process
- Design + commit cycle in single coordinated workflow

---

### Recipe: `systems-design-review`

| Property | Value |
|----------|-------|
| **Purpose** | Multi-stage architecture review with approval gates |
| **Execution Mode** | Staged (includes 2 approval gates) |
| **Entry Point** | Manual recipe invocation with design document path + codebase context |
| **Duration** | Multi-turn (resumable); gates halt for user input |
| **Relationship to Modes** | Automated alternative to 6-step `/systems-design-review` interactive mode |

**Workflow**:

| Step ID | Agent | Produces | Consumes | Purpose | Approval Gate |
|---------|-------|----------|----------|---------|---------------|
| `survey-codebase` | `foundation:explorer` | `codebase_survey` | (none) | Map file structure, boundaries | (implicit) |
| `identify-boundaries` | `systems-architect` (ASSESS) | `system_map` | `codebase_survey` | Extract system architecture | **`analysis`** |
| `adversarial-analysis` | `systems-design-critic` | `adversarial_analysis` | `system_map` | Risk from 5 perspectives | (implicit) |
| `synthesize-risks` | `systems-design-critic` | `risk_assessment` | `adversarial_analysis` | Rank by severity/likelihood | (implicit) |
| `write-report` | `systems-design-writer` | `final_report` | `risk_assessment` | Write review to disk + commit | **`report`** |

**Data Flow**:
```
survey-codebase (explorer)
    ↓ codebase_survey
    ↓
identify-boundaries (architect ASSESS)
    ↓ system_map ← [GATE: analysis]
    ↓
adversarial-analysis (critic)
    ↓ adversarial_analysis
    ↓
synthesize-risks (critic)
    ↓ risk_assessment
    ↓
write-report (writer)
    ↓ final_report ← [GATE: report]
```

**Approval Gates**:

| Gate | Purpose | User Input | Feeds To |
|------|---------|-----------|----------|
| **`analysis`** | Validate system map extraction before risk analysis | "Analysis correct" / "Needs revision" | Risk analysis uses validated map |
| **`report`** | Final approval before writing and committing review report | "Write report" / "Request changes" | Writer agent receives approval |

**Naming Coincidence**: 
- This recipe is named `systems-design-review` (same as the mode)
- Amplifier distinguishes them by type: mode is `.md` file in `modes/`, recipe is `.yaml` file in `recipes/`
- **Mode** invoked via slash command (`/systems-design-review`) or `mode(operation='set', name='systems-design-review')`
- **Recipe** invoked via `recipes(operation='execute', recipe_path='@systems-design:recipes/systems-design-review.yaml')`

**Relationship to Modes**:
- Automated alternative to 6-step `/systems-design-review` interactive mode
- Same analysis structure; recipe enforces gates; mode allows dynamic conversation

**Use Case**:
- Formal architecture reviews with approval workflow
- Design evaluation for production readiness
- Structured risk assessment + documentation

---

## 8. Behavioral Scenarios

### Scenario 1: Interactive Design Cycle (Mode-Driven)

**Trigger**: User types `/systems-design` or sets mode `systems-design`

**Mechanism Chain**:

```
1. Mode entry: /systems-design activated
   ↓ Companion skill auto-loaded: systems-design-methodology
   ↓ Context files injected (5 × 800 tokens)
   
2. Phase 1: System Modeling
   ↓ Skill delegates to systems-architect (ANALYZE mode)
   ↓ Agent reads: system-design-principles, tradeoff-frame, structured-design-template
   ↓ Agent produces: system_map (model of system, components, interfaces, flows)
   ↓ Skill presents map to user
   ↓ User validates: "Yes, that's the system" or "No, missing X"
   ↓ [BLOCKED if user rejects — return to Phase 1]
   
3. Phase 2: Constraint Extraction
   ↓ Skill delegates to systems-architect (ANALYZE mode)
   ↓ Agent extracts: latency requirements, reliability targets, scaling needs, cost constraints, security requirements, organizational constraints
   ↓ Agent produces: constraints_analysis
   ↓ [Implicit validation — proceed to Phase 3]
   
4. Phase 3: Candidate Generation
   ↓ Skill delegates to systems-architect (DESIGN mode)
   ↓ Agent may load: architecture-primitives (if patterns unclear) or system-type-web-service (if recognized)
   ↓ Agent produces: 3 distinct candidates (minimum)
   ↓ Skill presents candidates to user
   
5. Phase 4: Tradeoff Analysis
   ↓ Skill delegates to systems-architect (DESIGN mode)
   ↓ Skill may load: tradeoff-analysis (if analysis contested)
   ↓ Agent evaluates all candidates on 8 dimensions
   ↓ Agent produces: tradeoff_evaluation (matrix + recommendation)
   ↓ Skill presents matrix and recommendation to user
   
6. Phase 5: Risk Assessment
   ↓ Skill delegates to systems-design-critic (or suggests fork skill)
   ↓ Critic reads actual files
   ↓ Critic produces: risk assessment from 5 perspectives (SRE, Security, Staff Engineer, Finance, Operator)
   ↓ Skill presents risks to user
   
7. Phase 6: Design Refinement
   ↓ Skill delegates to systems-architect (DESIGN mode)
   ↓ Agent incorporates user feedback, addresses risks
   ↓ Agent produces: refined_design
   ↓ [Loop back to Phase 6 if user wants further iteration]
   
8. Phase 7: Migration Planning
   ↓ Skill delegates to systems-architect (DESIGN mode)
   ↓ Agent produces: rollout strategy, backward compatibility plan, rollback triggers, success/failure signals, timeline
   ↓ [Implicit validation]
   
9. Phase 8: Document Production
   ↓ Skill delegates to systems-design-writer
   ↓ Writer reads: structured-design-template
   ↓ Writer produces: docs/designs/YYYY-MM-DD-<topic>-design.md
   ↓ Writer commits to git
   ↓ Mode exits
   
End: Design documented and committed; mode deactivated
```

**Context Flow**:
- **On mode entry**: 5 context files injected (~4,000 tokens)
- **Phase 1 (ANALYZE)**: system-design-principles, tradeoff-frame, structured-design-template
- **Phase 5 (Critic)**: adversarial-perspectives, system-design-principles
- **Phase 8 (Writer)**: structured-design-template

**Expected Outcome**:
- User has iterated on system model with agent (validated at Phase 1)
- User has reviewed 3 candidates and tradeoff analysis (Phase 4)
- User has seen risk assessment from 5 perspectives (Phase 5)
- User has refined design based on risk (Phase 6)
- Design document written to disk and committed with git metadata

**Potential Loops**:
- If Phase 1 validation fails: loop back and re-model
- If Phase 5 risks are severe: loop back to Phase 6 to refine design
- If Phase 6 refinement changes tradeoffs significantly: loop back to Phase 4

---

### Scenario 2: Automated Design Exploration (Recipe-Driven)

**Trigger**: User invokes recipe `systems-design-exploration` with context variable `with_adversarial_review=true`

**Mechanism Chain**:

```
1. Recipe entry: systems-design-exploration execution starts
   ↓ No skill intervention; recipe orchestrates steps directly
   
2. Step 1: Frame Problem
   ↓ Recipe delegates to systems-architect (ANALYZE mode)
   ↓ Agent loads: system-design-principles, tradeoff-frame, structured-design-template
   ↓ Agent produces: problem_frame (system map + constraints)
   ↓ [No user checkpoint]
   
3. Step 2: Generate Candidates
   ↓ Recipe delegates to systems-architect (DESIGN mode)
   ↓ Agent consumes: problem_frame
   ↓ Agent produces: 3 candidates
   ↓ [No user checkpoint]
   
4. Step 3: Evaluate Tradeoffs
   ↓ Recipe delegates to systems-architect (DESIGN mode)
   ↓ Agent consumes: problem_frame, 3 candidates
   ↓ Agent may load: tradeoff-analysis skill internally
   ↓ Agent produces: tradeoff_evaluation (8-dimension matrix)
   ↓ [No user checkpoint]
   
5. Step 4: Adversarial Review
   ↓ [CONDITIONAL: if with_adversarial_review == 'true']
   ↓ Recipe delegates to systems-design-critic
   ↓ Critic loads: adversarial-perspectives, system-design-principles
   ↓ Critic produces: adversarial_review (5 perspectives)
   ↓ [No user checkpoint]
   
6. Recipe completes
   ↓ All outputs available to user for manual review
   ↓ No document written (recipe does not invoke writer)
   
End: Exploration complete; outputs returned to session for user review
```

**Context Flow**:
- **ANALYZE agent**: system-design-principles, tradeoff-frame, structured-design-template
- **DESIGN agent**: same as ANALYZE (context may be retained in agent session)
- **Critic agent** (if enabled): adversarial-perspectives, system-design-principles

**Expected Outcome**:
- Fully formed design with tradeoffs and risk assessment
- No user checkpoint delays
- Outputs available immediately for manual review
- No document yet written (user must decide next step: iterate, refine, or write)

**Differences from Scenario 1**:
- No interaction at checkpoints (no validation of system map)
- No iteration loops (runs to completion)
- No automatic document writing (user manually invokes writer if satisfied)
- Faster turnaround for initial design exploration

---

### Scenario 3: Architecture Review (Agent Delegation Chain)

**Trigger**: User enters `/systems-design-review` mode with existing design document and codebase

**Mechanism Chain**:

```
1. Mode entry: /systems-design-review activated
   ↓ Companion skill auto-loaded: systems-design-review-methodology
   ↓ Hook triggers: hooks-design-context scans docs/designs/, injects inventory
   ↓ Context files injected: adversarial-perspectives, system-design-principles
   
2. Step 1: Understand Design
   ↓ Skill + user interaction
   ↓ User provides: design document path, goals, constraints
   ↓ Skill reads design file
   ↓ Skill surveys codebase via foundation:explorer (implicit or explicit)
   ↓ Skill produces: design intent summary, codebase overview
   
3. Step 2: Evaluate Against Codebase
   ↓ Skill uses: LSP, grep, read_file
   ↓ Skill compares design claims to actual code
   ↓ Skill produces: gap analysis (what design claims vs what code actually does)
   
4. Step 3: Adversarial Analysis
   ↓ Skill offers two options:
     a) Delegate to systems-design-critic (sequential in main session)
     b) Load fork skill adversarial-review (parallel in sub-sessions)
   ↓ [User chooses or default to (a)]
   ↓ Option (a): systems-design-critic produces 5-perspective risk assessment
   ↓ Option (b): Fork spawns 5 parallel critic agents, synthesizes results
   
5. Step 4: Tradeoff Validation
   ↓ Skill loads tradeoff-analysis if user disputes risks or tradeoffs
   ↓ [Conditional — only if needed]
   
6. Step 5: Synthesize & Recommend
   ↓ Skill + systems-architect (implicit)
   ↓ Skill produces: Recommendation (Proceed / Proceed with modifications / Reconsider)
   ↓ Skill presents recommendation to user
   
7. Step 6: Capture Action Items
   ↓ Skill + user interaction
   ↓ Skill captures: Action items, assigned owners, deadlines
   ↓ Mode exits
   
End: Review complete; action items captured
```

**Context Flow**:
- **On mode entry**: adversarial-perspectives, system-design-principles injected
- **Pre-completion hook**: hooks-design-context injects design inventory (minimal tokens)
- **Step 3 (Critic)**: adversarial-perspectives, system-design-principles loaded to critic
- **Step 4 (Tradeoff)**: tradeoff-frame loaded if needed

**Expected Outcome**:
- Design review complete against actual codebase
- Risk assessment from 5 perspectives
- Concrete action items with owners
- Recommendation for next steps (proceed, modify, or reconsider)

**Possible Sub-Paths**:
- If Option (b) fork skill invoked: 5 parallel agents spawn in sub-sessions, results synthesized in main session
- If gaps are severe: Skill may suggest returning to Phase 1 (understand design more deeply) before proceeding
- If action items are substantial: Skill may suggest entering `/systems-design` mode to iterate design

---

## 9. Plan-Derived Limitations

The mechanism plan provides detailed component specifications but has intentional and structural limits. The following CANNOT be determined from the plan alone:

### 1. Transitive Dependency Tree

**What the plan specifies**: Direct dependencies only
- `systems-design` bundle depends on: `amplifier-foundation`, `tool-mode`, `tool-skills`, `hooks-mode`, `hooks-design-context`, `behavior-modes`, `foundation:explorer`, `foundation:zen-architect`, `foundation:git-ops`, `foundation:file-ops`

**What cannot be derived**: 
- What does `foundation:explorer` depend on?
- What does `foundation:zen-architect` depend on?
- Are there circular dependencies?
- What is the full transitive closure?
- What version constraints exist?

**Why it matters**: Composition validation, conflict detection, and dependency tree optimization require resolved transitive dependencies.

---

### 2. Composition Loopholes (Tool Policy Escalation)

**What the plan specifies**: Tool policies for `systems-design` and `systems-design-review` modes
- Both modes block: `write_file`, `edit_file`, `apply_patch`, `python_check`

**What cannot be derived**:
- When `systems-design` mode delegates to `foundation:zen-architect`, what tool policies does that agent have?
- If `foundation:zen-architect` has `write_file` as SAFE, does that bypass the mode's BLOCK?
- Can a user achieve `write_file` by delegating through the right agent composition?
- Are delegation guardrails enforced at the Amplifier runtime level or trust-based?

**Why it matters**: 
- Determines whether tool policies are truly enforced or whether composition-based escalation is possible
- Affects security and safety model

**Runtime validation required**: Resolved dependency tree + delegation guardrail enforcement model

---

### 3. Delegation Necessity Map

**What the plan specifies**: Which agents are invoked in which workflows
- Phase 1: `systems-architect` (ANALYZE)
- Phase 5: `systems-design-critic`
- Phase 8: `systems-design-writer`
- etc.

**What cannot be derived**:
- For which operations is delegation REQUIRED vs OPTIONAL?
- Can the skill itself execute some analyses (e.g., tradeoff evaluation) without delegating to `systems-architect`?
- Are there operations that the skill could do but SHOULD NOT (design thinking guard)?
- What is the enforcement mechanism?

**Why it matters**: 
- Determines whether "block write operations" is enforced at tool level or guardrail level
- Affects architectural integrity and design isolation

---

### 4. Actual Token Costs

**What the plan specifies**: Estimated tokens for context files
- Each of 5 context files: 800 tokens (estimated)
- Total on mode entry: ~4,000 tokens (estimated)

**What cannot be derived**:
- Actual measured token consumption for each file
- Overhead from loading multiple files simultaneously
- Token cost of agent context loading (system-design-principles is loaded to MULTIPLE agents)
- Cost of hook injection (hooks-design-context scans and injects inventory)
- Actual model input size for different context patterns

**Why it matters**: 
- Affects budget planning and model selection
- May inform decisions about always-loaded vs on-demand context
- Token costs accumulate across multiple agents in parallel recipes

**Runtime measurement required**: Token metering during actual execution

---

### 5. Model Role Specifications & Constraints

**What the plan specifies**: Model role for `systems-architect` is `reasoning`
- Purpose: deep architectural thinking

**What cannot be derived**:
- Is `reasoning` model role available in this Amplifier installation?
- What are the latency and cost tradeoffs?
- Can the agent fall back to `general` if `reasoning` is unavailable?
- Are there model role constraints on specific operations (e.g., `systems-design-critic` marked as `critique` — is that role available)?

**Why it matters**: 
- Determines feasibility of running the bundle in different environments
- Affects delegation behavior at runtime
- May inform alternative configurations if some roles unavailable

---

### 6. Hook Triggering & Composition

**What the plan specifies**: 
- Hook `hooks-design-context` triggers on "before each LLM call"
- Scans `docs/designs/` and injects inventory

**What cannot be derived**:
- How does "before each LLM call" compose with other hooks?
- If multiple hooks trigger on same event, what is execution order?
- Can a hook prevent or modify the LLM call?
- What happens if `docs/designs/` scan is expensive (e.g., 1000 design files)?
- Is the scan cached or repeated on every call?

**Why it matters**: 
- Affects latency and overhead of every conversation
- May cause unexpected behavior if hooks interact poorly
- Determines observability and debugging difficulty

---

### 7. Recipe Approval Gate Mechanics

**What the plan specifies**: Recipes include approval gates
- `systems-design-cycle` has 3 gates: `candidates`, `risk-and-refinement`, `documentation`
- `systems-design-review` has 2 gates: `analysis`, `report`

**What cannot be derived**:
- How does the recipe resume after an approval gate?
- If a user provides message at gate (e.g., "merge"), how is that fed to subsequent steps?
- Can user feedback from one gate invalidate prior steps?
- What happens if user denies a gate (reject/cancel)?
- Is there a timeout on gates?
- Can gates be skipped or made optional?

**Why it matters**: 
- Determines whether staged recipes are practical for long-running workflows
- Affects UX and integration with CI/CD systems
- May inform decisions about approval gate placement

---

### 8. Skill Loading & Context Forking

**What the plan specifies**: 
- Skills may load additional context files (e.g., Phase 3 may load `architecture-primitives`)
- Fork skill `adversarial-review` spawns parallel agents

**What cannot be derived**:
- Can skills load context files that conflict with mode-loaded context?
- What happens if `architecture-primitives` contradicts `system-design-principles`?
- In fork skill, how is context distributed to 5 parallel agents?
- Can each critic agent see the others' work, or is analysis strictly independent?
- How long does fork skill wait for all 5 agents to complete?

**Why it matters**: 
- Determines context consistency and conflict resolution
- Affects latency of parallel agents
- May cause unexpected behavior if context conflicts poorly

---

### 9. Error Handling & Failure Modes

**What the plan specifies**: None

**What cannot be derived**:
- What happens if an agent fails during a phase?
- Can recipes resume from a prior checkpoint?
- Is there logging and audit trail?
- How are validation failures handled (e.g., user rejects system map at Phase 1)?
- What is the failure recovery strategy?

**Why it matters**: 
- Determines robustness of the system
- Affects operator experience and debugging
- May inform decisions about distributed execution

---

### 10. Actual Behavior Under Load

**What the plan specifies**: No load characteristics

**What cannot be derived**:
- What is the latency for a full 8-phase design cycle?
- How long does adversarial-review fork take with 5 parallel agents?
- What happens when multiple users enter `/systems-design` mode simultaneously?
- Are there rate limits or queues?
- How does system behavior scale with codebase size?

**Why it matters**: 
- Determines practical usability
- Affects planning for shared team usage
- May inform decisions about caching or precomputation

---

## Summary: Plan Sufficiency

The mechanism plan is **detailed and sufficient for**:
✓ Understanding mode and agent purposes  
✓ Tracing single-path workflows (user enters mode → skill → agents → output)  
✓ Identifying all components and their relationships  
✓ Extracting design principles and evaluation frameworks  

The mechanism plan is **insufficient for**:
✗ Composition validation (transitive dependencies not resolved)  
✗ Tool policy enforcement (loopholes not identified)  
✗ Runtime behavior prediction (latency, error handling, load characteristics)  
✗ Actual token costs (estimates only)  
✗ Model role availability (not verified)  
✗ Hook interaction effects (not specified)  
✗ Recipe state management (resumption mechanics unclear)  
✗ Context conflict resolution (not addressed)  

---

**Document generated from mechanism plan extraction**  
**Status: Ready for composition validation**  
**Next steps**: Resolve dependencies, verify tool policies, measure actual token costs
