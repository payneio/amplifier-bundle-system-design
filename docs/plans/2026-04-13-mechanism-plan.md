# Systems-Design Bundle: Mechanism Plan

A complete mechanism inventory for the `systems-design` Amplifier bundle. A bundle developer should be able to take this document (plus the objectives) and build every mechanism in the bundle.

---

## Section 1: Bundle Identity & Composition

The bundle is called `systems-design`. Ships as standalone (includes foundation) and as a composable behavior.

- **Root bundle** (`bundle.md`): Includes `amplifier-foundation` + `systems-design-behavior`.
- **Behavior YAML** (`behaviors/systems-design.yaml`): The wiring layer connecting:
  - Tool modules: `tool-mode` (mode infrastructure), `tool-skills` (skill loading, pointed at bundle's `skills/` directory)
  - Hook modules: `hooks-mode` (from modes bundle -- mode lifecycle), `hooks-design-context` (local -- ambient design doc awareness)
  - Agents: 3 specialist agents declared via `agents.include`
  - Context files: 5 files injected into every root session (~4k tokens total)
  - Nested behaviors: `behavior-modes` (from modes bundle)
- **External dependencies** (via foundation): `foundation:explorer` (codebase reconnaissance), `foundation:zen-architect` (module-level design), `foundation:git-ops` (commits), `foundation:file-ops` (file operations). Standard tools: read_file, glob, grep, LSP, web_search, web_fetch, delegate, todo, recipes, bash.
- **Installation paths**: Standalone via `amplifier bundle add git+...@main --app`. Behavior-only via `#subdirectory=behaviors/systems-design.yaml`.

---

## Section 2: Context Files

5 context files always-loaded into every root session (~4k tokens total). These provide shared vocabulary and reference frameworks used across modes, agents, and skills. They do NOT contain methodology (that's skills) or tool governance (that's modes).

| File | Purpose | ~Tokens |
|------|---------|---------|
| `context/instructions.md` | Detection & routing standing orders -- recognizes design requests and routes to the right mode/recipe/skill. Maps trigger phrases to mechanisms. No methodology, just routing. | ~800 |
| `context/system-design-principles.md` | 6 core thinking tools: map first, four layers, tradeoff analysis, optimize/sacrifice framing, causal tracing, simplest-acceptable design | ~800 |
| `context/tradeoff-frame.md` | 8-dimension evaluation framework (latency, complexity, reliability, cost, security, scalability, reversibility, organizational fit) with matrix template | ~800 |
| `context/adversarial-perspectives.md` | 5 reviewer perspectives (SRE, security, staff engineer, finance, operator) with driving questions and output structure | ~800 |
| `context/structured-design-template.md` | 11-section output template for design documents (problem framing through success metrics) | ~800 |

Design rationale: `instructions.md` is the router. The other 4 are reference frameworks that agents and skills point to. Always loaded because they're referenced across multiple mechanisms -- loading once (~4k tokens) is cheaper than having every agent re-load them.

---

## Section 3: Modes

Two modes governing interactive sessions. Modes provide tool governance and behavioral posture. They do NOT contain methodology -- that's handled by companion skills loaded at mode entry.

### Mode: `systems-design`

- **Purpose**: Structured system design exploration -- modeling, alternatives, tradeoffs, risks, documentation
- **Shortcut**: `/systems-design`
- **When to activate**: User says "design a system for...", "how should we architect...", "what's the right approach for..."
- **Tool policy**: Safe = read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode. Warn = bash. Blocked = write_file, edit_file, apply_patch, python_check. Default = block for unlisted.
- **Behavioral posture**: Design thinking, not implementation. Read code, don't write it. Delegate document production to writer agent. Delegate system-level analysis to architect agent.
- **On entry**: Load companion skill `systems-design-methodology` (8-phase workflow).
- **Transitions**: Can transition to `/systems-design-review`. Cannot be cleared (allow_clear: false).

### Mode: `systems-design-review`

- **Purpose**: Evaluate an existing design or proposed architectural change against the codebase
- **Shortcut**: `/systems-design-review`
- **When to activate**: User says "review this architecture...", "evaluate our system...", "is this design sound?"
- **Tool policy**: Safe = read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode. Warn = bash. Blocked = write_file, edit_file, apply_patch, python_check. Default = block for unlisted.
- **Behavioral posture**: Evaluation, not modification. Read code, compare against design claims, find gaps. Produce assessments, not code changes.
- **On entry**: Load companion skill `systems-design-review-methodology` (6-step workflow).
- **Transitions**: Can transition to `/systems-design`. Cannot be cleared (allow_clear: false).

Key design decision: Both modes have nearly identical tool policies (same core principle: design work reads but doesn't write). The difference is the companion skill loaded at entry. The mode is the governance shell; the skill is the brain.

---

## Section 4: Agents

Three specialist agents owned by the bundle, plus foundation agent usage. Agents are context sinks -- they carry heavy documentation in their own context windows.

### Agent: `systems-architect`

- **Purpose**: System-level design reasoning -- modeling, candidate generation, tradeoff evaluation, assessment
- **Model role**: `reasoning`
- **Three operating modes** (specified via delegation instruction, not Amplifier modes):
  - **ANALYZE**: Build system map (goals, constraints, actors, interfaces, feedback loops, failure modes). Validate map before proceeding.
  - **DESIGN**: Generate 3 candidates (simplest viable, most scalable, most robust). Evaluate against 8-dimension tradeoff frame. Recommend with explicit reasoning.
  - **ASSESS**: Evaluate existing architecture -- identify boundaries, coupling, debt, failure modes, scaling bottlenecks.
- **Context loaded** (via @mentions): system-design-principles.md, tradeoff-frame.md, structured-design-template.md
- **Key directives**: Model first, solutions second. 3 candidates minimum. Evaluate against 8-dimension frame. Name unknowns explicitly. Apply YAGNI. Prefer simplest design whose failure modes are acceptable. Delegate module-level work to foundation:zen-architect.
- **Tools needed**: read_file, glob, grep, LSP, web_search, web_fetch, delegate
- **Exit conditions**: System map produced (ANALYZE), design document with recommendation (DESIGN), assessment report (ASSESS), or scope determined module-level and delegated to foundation:zen-architect.

### Agent: `systems-design-critic`

- **Purpose**: Adversarial stress-testing from 5 perspectives -- finds flaws, does NOT propose fixes
- **Model role**: `critique`
- **5 perspectives**: SRE (operational resilience), Security (attack surface), Staff Engineer (hidden complexity), Finance (cost curves), Operator (runbook burden)
- **Context loaded** (via @mentions): adversarial-perspectives.md, system-design-principles.md
- **Key directives**: Read actual files, not summaries. Find flaws, don't fix them. Be specific -- name concrete failure modes. Be calibrated -- rank by severity and likelihood.
- **Output structure**: Critical Risks, Significant Concerns, Observations, What the Design Gets Right, Recommended Next Steps
- **Tools needed**: read_file, glob, grep, LSP
- **Exit conditions**: Severity-ranked risk assessment covering all 5 perspectives

### Agent: `systems-design-writer`

- **Purpose**: Write formal design document to disk from validated design, then commit
- **Model role**: `writing`
- **Context loaded** (via @mentions): structured-design-template.md
- **Key directives**: Write ONLY what was validated. Do not add, invent, or decide. Do not ask questions. Do not conduct conversations. Always commit after writing.
- **Output format**: docs/designs/YYYY-MM-DD-\<topic\>-design.md using 11-section template
- **Tools needed**: write_file, bash, delegate (to foundation:git-ops for commits)
- **Exit conditions**: Design document written and committed

### Foundation agent usage

| Agent | When used | By whom |
|-------|-----------|---------|
| `foundation:explorer` | Codebase reconnaissance (survey structure, find files) | Recipes, modes (via delegation) |
| `foundation:zen-architect` | Module-level design (interfaces, contracts, function signatures) | systems-architect delegates down |
| `foundation:git-ops` | Commit and push operations | systems-design-writer |
| `foundation:file-ops` | File operations in recipe steps | Recipes |

Key design decision: The three agents form a pipeline -- architect generates, critic stress-tests, writer documents. They never overlap roles. The architect's scope boundary is "system-level" -- module-level work delegates to foundation:zen-architect.

---

## Section 5: Skills

On-demand knowledge loaded via load_skill(). Three categories: methodology skills (companion skills for modes), domain skills (design knowledge), and system-type skills (conditional domain patterns).

### Skill context model (progressive disclosure)

| Level | What | Token cost | When |
|-------|------|-----------|------|
| L1: Description | description in frontmatter | ~100 tokens | Always -- visibility hook shows to LLM |
| L2: Content | Full SKILL.md body | ~1-5k tokens | On demand -- load_skill() |
| L3: References | Companion files in skill directory | 0 until accessed | Explicit read_file() |

### Methodology skills (companion skills -- loaded at mode entry)

**`systems-design-methodology`**
- **Type**: Inline skill (L2 content injected into current session)
- **Purpose**: Governs 8-phase conversation flow for /systems-design mode
- **Loaded when**: Automatically at /systems-design mode entry
- **Core directive**: Handle CONVERSATION; agents handle ANALYSIS. Orchestrate, delegate to systems-architect, present results to user, feed back their input.
- **Phases**:
  1. System modeling via architect/ANALYZE -- require user validation before proceeding
  2. Constraint extraction
  3. Candidate exploration via architect/DESIGN -- 3 candidates
  4. Tradeoff analysis via architect/DESIGN -- 8-dimension frame
  5. Risk assessment -- delegate to critic or suggest adversarial-review skill
  6. Design refinement via architect/DESIGN
  7. Migration planning
  8. Document production -- delegate to writer with ALL validated content
- **Key behaviors**: Blocks progression at Phase 1 until user validates system map. May revisit earlier phases. Loads other skills on demand (architecture-primitives at Phase 3 if patterns unclear, tradeoff-analysis at Phase 4 if tradeoffs contested).

**`systems-design-review-methodology`**
- **Type**: Inline skill
- **Purpose**: Governs 6-step conversation flow for /systems-design-review mode
- **Loaded when**: Automatically at /systems-design-review mode entry
- **Core directive**: Handle CONVERSATION; agents handle ANALYSIS. Read design thoroughly before any critique.
- **Phases**:
  1. Understand the design -- read docs, identify goals/constraints/tradeoffs, survey codebase
  2. Evaluate against codebase -- compare claims vs actual implementation via LSP/grep
  3. Adversarial analysis -- delegate to critic (Option A) or load adversarial-review skill (Option B)
  4. Tradeoff validation -- load tradeoff-analysis skill if needed
  5. Synthesize & recommend -- Proceed / Proceed with modifications / Reconsider
  6. Capture action items

### Domain skills (loaded on demand during design work)

**`tradeoff-analysis`**
- **Type**: Inline skill
- **Purpose**: 8-dimension comparison framework and matrix template
- **Loaded when**: Phase 4 of design, or whenever alternatives must be compared
- **Key directives**: Force all analysis into 8-dimension frame. Qualitative ratings (good/adequate/poor) with concrete notes, not numeric scores. Every cell must have rating + note. Identify 1-2 dominant dimensions. Explicitly state what chosen option sacrifices. Min 2, max 5 alternatives.

**`architecture-primitives`**
- **Type**: Inline skill
- **Purpose**: Catalog of reusable architectural primitives with what-when-wrong evaluation
- **Loaded when**: Phase 3 candidate exploration if pattern selection is unclear
- **Covers**: Boundaries/contracts, state machines, sync vs async, queues, caching, idempotency, retries, circuit breakers, consistency models, observability, blast-radius isolation
- **Key directive**: Evaluate every primitive on 3 axes -- what it is, when it's right, when it's wrong

**`adversarial-review`**
- **Type**: Fork skill (context: fork -- spawns isolated subagent with its own context window)
- **Model role**: critique
- **Purpose**: Multi-perspective adversarial review launching 5 parallel critic agents
- **Loaded when**: User invokes during design, or at Phase 5 as alternative to delegating to systems-design-critic
- **Key behavior**: Reads the design, spawns 5 parallel agents via delegate() (SRE, security, staff engineer, finance, operator), waits for all 5, synthesizes into unified risk assessment
- **Output**: Critical Risks, Significant Concerns, Observations, What the Design Gets Right, Recommended Next Steps

### System-type skills (loaded conditionally based on system type)

Follow a consistent pattern. Each provides domain-specific patterns, guarantees, failure modes, and anti-patterns for a particular system type. Loaded during Phase 3 when system type identified.

Pattern for all system-type skills:
- **Type**: Inline skill
- **Naming**: `system-type-<name>` (e.g., system-type-web-service, system-type-event-driven)
- **Structure**: API/communication patterns, scaling strategies, data layer choices, observability practices, failure mitigation, anti-patterns
- **Loaded when**: Phase 3, when architect or user identifies system type
- **L1 description** must be clear enough for LLM to match it to the system being designed

Concrete examples shipped with v1 (illustrate the pattern):
- `system-type-web-service` -- request/response web services, REST/GraphQL/gRPC
- `system-type-event-driven` -- pub/sub, event sourcing, CQRS, sagas, delivery guarantees

Adding more: Create new directory under skills/ with SKILL.md following same structure. Auto-discovered by tool-skills.

Key design decisions: Methodology skills are companion skills loaded at mode entry (mode = governance shell, skill = brain). Adversarial-review is a fork skill because it spawns 5 parallel agents. System-type skills are a pattern, not a fixed list.

---

## Section 6: Recipes

Automated multi-step pipelines using the same agents and principles as interactive modes. Recipes do NOT activate modes -- they are a parallel entry point (automated pipeline vs interactive session).

### `codebase-understanding`

- **Purpose**: Survey existing codebase and produce architectural overview
- **Execution mode**: Flat (no approval gates)
- **Objective served**: "Get a full systems understanding of an existing codebase"

| Step | Agent | Produces | Consumes |
|------|-------|----------|----------|
| 1. survey-structure | foundation:explorer | structure_survey | -- |
| 2. identify-boundaries | systems-architect (ASSESS) | boundary_analysis | structure_survey |
| 3. map-flows | systems-architect (ASSESS) | flow_analysis | structure_survey, boundary_analysis |
| 4. architectural-overview | systems-architect (ASSESS) | architectural_overview | all above |

Data flow: Explorer does reconnaissance, architect analyzes progressively. Each step builds on previous.

### `systems-design-exploration`

- **Purpose**: Rapid parallel exploration of 3 architectural alternatives with tradeoff evaluation
- **Execution mode**: Flat (no approval gates)
- **Objective served**: Design constraint management, quick alternative comparison

| Step | Agent | Produces | Notes |
|------|-------|----------|-------|
| 1. frame-problem | systems-architect (ANALYZE) | problem_frame | -- |
| 2. generate-candidates | systems-architect (DESIGN) | 3 candidates | 3-way parallel |
| 3. evaluate-tradeoffs | systems-architect (DESIGN) | tradeoff_evaluation | 8-dimension frame |
| 4. adversarial-review | systems-design-critic | adversarial_review | Conditional: only if `with_adversarial_review == 'true'` |

### `systems-design-cycle`

- **Purpose**: End-to-end system design with human checkpoints
- **Execution mode**: Staged (3 approval gates)
- **Objective served**: Full structured design with user validation

| Step | Agent | Produces | Gate |
|------|-------|----------|------|
| 1. build-system-map | systems-architect (ANALYZE) | system_map | -- |
| 2. extract-constraints | systems-architect | constraints_analysis | **candidates** |
| 3. generate-candidates | systems-architect (DESIGN) | 3 candidates | |
| 4. evaluate-tradeoffs | systems-architect (DESIGN) | tradeoff_evaluation | **risk-and-refinement** |
| 5. adversarial-review | systems-design-critic | risk_assessment | |
| 6. refine-design | systems-architect (DESIGN) | refined_design | **documentation** |
| 7. write-document | systems-design-writer | design_document | |

3 approval gates:
1. **candidates** -- user approves problem framing before generating alternatives
2. **risk-and-refinement** -- user approves candidates and tradeoffs before risk assessment
3. **documentation** -- user approves refined design before final document

User approval messages are passed to subsequent steps for steering.

### `systems-design-review`

- **Purpose**: Multi-stage architecture review with approval gates
- **Execution mode**: Staged (2 approval gates)
- **Objective served**: "Evaluate a systems design proposal"

| Step | Agent | Produces | Gate |
|------|-------|----------|------|
| 1. survey-codebase | foundation:explorer | codebase_survey | -- |
| 2. identify-boundaries | systems-architect (ASSESS) | system_map | **analysis** |
| 3. perspective-analysis | systems-architect (ASSESS) | 5-perspective analysis | |
| 4. synthesize-risks | systems-design-critic | risk_assessment | **report** |
| 5. write-report | systems-design-writer | final_report | |

2 approval gates:
1. **analysis** -- user approves survey and map before deep analysis
2. **report** -- user approves risk assessment before final report

### Mode vs recipe relationship

| Entry point | Driven by | Best for |
|-------------|-----------|----------|
| /systems-design mode | User interactively | Exploratory, unclear scope, lots of back-and-forth |
| systems-design-cycle recipe | Automated pipeline | Well-scoped problems, structured checkpoints |
| /systems-design-review mode | User interactively | Reviewing with questions and discussion |
| systems-design-review recipe | Automated pipeline | Standard review with structured output |

Both use the same agents, principles, and context. The difference is who drives.

---

## Section 7: Hook

One hook module owned by the bundle.

### `hooks-design-context`

- **Type**: Python hook module (code-decided, fires on lifecycle events)
- **Purpose**: Ambient design document awareness -- scans `docs/designs/*.md` and injects inventory of existing designs before every LLM call
- **When it fires**: Before each LLM call (pre-completion hook)
- **What it does**: Scans `docs/designs/` for markdown files, extracts titles and dates, injects compact inventory into LLM context. Agent always knows what designs exist without being told.
- **Token cost**: Minimal -- just a list of filenames and titles, not full documents
- **Why a hook and not a skill or context file**: Needs to run code (scan filesystem at runtime) and fire automatically (no explicit loading). Skills are on-demand; context files are static. This is dynamic and ambient.

---

## Section 8: Interaction Map

How mechanisms connect across the four primary user journeys.

### Journey 1: "Design a new system" (interactive)

```
User says "design a system for..."
  -> instructions.md (context) detects trigger, routes to /systems-design
  -> systems-design mode activates (tool governance: no writes)
  -> systems-design-methodology skill auto-loads (8-phase workflow)

Phase 1-2: Modeling & constraints
  -> Skill directs: delegate to systems-architect (ANALYZE)
  -> Architect loads: system-design-principles.md, tradeoff-frame.md
  -> Returns system map -> skill requires user validation before proceeding

Phase 3: Candidate exploration
  -> Skill directs: delegate to systems-architect (DESIGN)
  -> Skill may load: architecture-primitives skill (if patterns unclear)
  -> Skill may load: system-type-* skill (if system type identified)
  -> Architect generates 3 candidates

Phase 4: Tradeoff analysis
  -> Skill directs: delegate to systems-architect (DESIGN)
  -> Skill may load: tradeoff-analysis skill (if tradeoffs contested)
  -> Architect evaluates against 8-dimension frame

Phase 5: Risk assessment
  -> Skill directs: delegate to systems-design-critic
    OR user invokes adversarial-review fork skill (5 parallel agents)
  -> Critic loads: adversarial-perspectives.md

Phase 6-7: Refinement & migration
  -> Skill directs: delegate to systems-architect (DESIGN)

Phase 8: Document production
  -> Skill directs: delegate to systems-design-writer
  -> Writer loads: structured-design-template.md
  -> Writer writes to docs/designs/, commits via foundation:git-ops
```

### Journey 2: "Review an existing design" (interactive)

```
User says "review this architecture..."
  -> instructions.md detects trigger, routes to /systems-design-review
  -> systems-design-review mode activates (tool governance: no writes)
  -> systems-design-review-methodology skill auto-loads (6-step workflow)

Step 1-2: Understand & evaluate
  -> Skill directs: read design docs, survey codebase
  -> May delegate to foundation:explorer for reconnaissance
  -> Compare design claims against actual code via LSP/grep

Step 3: Adversarial analysis
  -> Option A: delegate to systems-design-critic
  -> Option B: user invokes adversarial-review fork skill

Step 4: Tradeoff validation
  -> Skill may load: tradeoff-analysis skill

Step 5-6: Synthesize & action items
  -> Recommend: Proceed / Proceed with modifications / Reconsider
```

### Journey 3: "Design a system" (automated pipeline)

```
User runs systems-design-cycle recipe
  -> Step 1: systems-architect (ANALYZE) -> system_map
  -> Step 2: systems-architect -> constraints_analysis
  -- APPROVAL GATE: candidates --
  -> Step 3: systems-architect (DESIGN) -> 3 candidates
  -> Step 4: systems-architect (DESIGN) -> tradeoff_evaluation
  -- APPROVAL GATE: risk-and-refinement --
  -> Step 5: systems-design-critic -> risk_assessment
  -> Step 6: systems-architect (DESIGN) -> refined_design
  -- APPROVAL GATE: documentation --
  -> Step 7: systems-design-writer -> design_document
```

### Journey 4: "Understand this codebase"

```
User runs codebase-understanding recipe (or instructions.md routes)
  -> Step 1: foundation:explorer -> structure_survey
  -> Step 2: systems-architect (ASSESS) -> boundary_analysis
  -> Step 3: systems-architect (ASSESS) -> flow_analysis
  -> Step 4: systems-architect (ASSESS) -> architectural_overview
```

### Ambient behavior (always active)

`hooks-design-context` fires before every LLM call -> scans `docs/designs/*.md` -> injects inventory.

### Mechanism interaction summary

| Mechanism | Role in the system |
|-----------|-------------------|
| Context files | Shared vocabulary and frameworks (always loaded, ~4k tokens) |
| Modes | Tool governance shell (what you can/can't do) |
| Methodology skills | Conversation brain (loaded at mode entry, governs phases) |
| Domain skills | On-demand knowledge (loaded during specific phases) |
| System-type skills | Conditional domain patterns (loaded when system type identified) |
| Fork skill | Heavy parallel work (adversarial review spawns 5 agents) |
| Agents | Specialist sub-sessions (architect designs, critic reviews, writer documents) |
| Recipes | Automated pipelines (same agents, driven by recipe engine not user) |
| Hook | Ambient awareness (design doc inventory, no user action needed) |
| Foundation agents | Infrastructure (explorer for recon, zen-architect for module-level, git-ops for commits) |

---

## Deferred Capabilities

Design modeling and simulation (from objectives bonus section) is deferred from this plan. The objectives envision encoding system models (e.g., "amplifier bundle model", "web service model") that proposed designs could be tested against before implementation. This is valuable but speculative -- the mechanism type and interaction model are unclear. Revisit after v1 establishes the core design workflow.
