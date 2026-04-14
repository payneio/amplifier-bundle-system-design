# Behavioral Specification: systems-design Bundle

**Version**: 1.0.0  
**Date**: 2026-04-13  
**Bundle**: amplifier-bundle-system-design  
**Scope**: Complete behavioral and compositional analysis of the systems-design bundle and its 23-component dependency tree

---

## 1. Overview

### Bundle Identity
- **Name**: systems-design
- **Purpose**: Structured system design exploration and architectural review through multi-perspective analysis and tradeoff evaluation
- **Primary Mechanisms**: Two complementary interactive modes (`systems-design`, `systems-design-review`); three specialist agents (architect, critic, writer); and a rich ecosystem of supporting skills for domain patterns, tradeoff analysis, and adversarial review

### Component Inventory

| Category | Count | Components |
|----------|-------|------------|
| **Modes** | 2 | systems-design, systems-design-review |
| **Agents** | 3 | systems-architect, systems-design-critic, systems-design-writer |
| **Skills** | 6 | systems-design-methodology, systems-design-review-methodology, adversarial-review, architecture-primitives, system-type-web-service, system-type-event-driven, tradeoff-analysis |
| **Context Files** | 5 | system-design-principles, tradeoff-frame, structured-design-template, adversarial-perspectives, instructions |
| **Recipes** | 4 | bundle-behavioral-spec, codebase-understanding, systems-design-cycle, systems-design-exploration, systems-design-review |
| **Total Direct** | 20 | — |

### Full Dependency Tree

**Root dependencies** (direct bundle references):
- amplifier-foundation (for common patterns, agents, skills)
- amplifier-core (for kernel contracts)

**23-component transitive closure** (alphabetical):
amplifier-core, amplifier-expert-behavior, amplifier-foundation, behavior-agents, behavior-apply-patch, behavior-logging, behavior-modes, behavior-python-lsp, behavior-redaction, behavior-sessions, behavior-status-context, behavior-streaming-ui, behavior-todo-reminder, browser-testing-behavior, core-expert-behavior, design-intelligence-behavior, foundation-expert-behavior, hook-shell-behavior, lsp-python, mcp-behavior, python-dev, python-dev-behavior, recipes-behavior, routing-matrix, shadow, skills-behavior, systems-design, systems-design-behavior

---

## 2. Tool Governance

### Tool Availability Matrix (Per Mode)

#### Mode: `systems-design`
| Tool Category | Classification | Tools |
|---|---|---|
| **Safe (default allow)** | safe | read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode |
| **Warn (allow after warning)** | warn | bash, apply_patch, python_check |
| **Confirm (require user gate)** | confirm | *(none)* |
| **Blocked** | block | write_file, edit_file (file-write tools blocked: design produces thinking, not code) |
| **Default action** | — | **warn** for unlisted tools |

**Behavioral directive**: This mode produces design thinking and documents, not implementation. File writes are delegated to systems-design-writer agent.

#### Mode: `systems-design-review`
| Tool Category | Classification | Tools |
|---|---|---|
| **Safe** | safe | read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode |
| **Warn** | warn | bash |
| **Confirm** | confirm | *(none)* |
| **Blocked** | block | write_file, edit_file, apply_patch, python_check (review produces assessments only, no code) |
| **Default action** | — | **block** for unlisted tools |

**Behavioral directive**: This mode evaluates designs and generates findings, not modifications. All file operations are read-only.

### Delegation Necessity Map

| Mode | Operation | Necessity | Policy |
|---|---|---|---|
| systems-design | File modification | WARN | write_file/edit_file warn, can proceed after warning; delegated to systems-design-writer |
| systems-design | Code execution | WARN | bash warns, can proceed after warning |
| systems-design | Exploration | MUST delegate | File reading >2 files blocked; delegated to foundation:explorer |
| systems-design | Git operations | WARN | bash warns; foundation:git-ops agent available |
| systems-design | Web access | MUST delegate | Web tools blocked; delegated to foundation:web-research |
| systems-design | Skill loading | WARN | load_skill warns |
| systems-design-review | File modification | WARN | write_file/edit_file warn, can proceed after warning |
| systems-design-review | Code execution | WARN | bash warns, can proceed after warning |
| systems-design-review | Exploration | MUST delegate | Exploration tools blocked; delegated to foundation:explorer |
| systems-design-review | Git operations | WARN | bash warns; foundation:git-ops available |
| systems-design-review | Web access | MUST delegate | Web tools blocked; delegated to foundation:web-research |
| systems-design-review | Skill loading | WARN | load_skill warns |

### Composition Loopholes

**Finding**: No composition loopholes detected.

Both modes prevent direct tool use while enabling delegation, which is the intended pattern. Subagents spawned via delegate() inherit the parent mode's restrictions through the tool-availability enforcement layer.

---

## 3. Mode Behaviors

### Mode: `systems-design`

**Purpose**: Structured system design exploration through an 8-phase workflow — modeling the system, exploring alternatives, analyzing tradeoffs, stress-testing against risks, validating with the user, and producing a design document.

**When to activate**:
- User initiates structured system design exploration
- User needs to model a system, explore alternatives, analyze tradeoffs, or validate a design
- User says "Design a system for...", "How should we architect...", or similar

**Tool Policy**:
- **Blocked (no exceptions)**: write_file, edit_file, apply_patch, python_check
- **Safe (allow)**: read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode
- **Warn (allow after warning)**: bash
- **Default action**: block unlisted tools

**Entry Conditions**:
- `/systems-design` mode activated by user
- Immediately load companion skill `systems-design-methodology` at mode entry
- Load context files: `system-design-principles.md`, `tradeoff-frame.md`, `structured-design-template.md`

**Exit Conditions**:
- allow_clear is false — mode cannot be cleared by the user directly; only mode-tool transitions are allowed
- Phase 8 completes: design document written and validated

**Behavioral Directives** (Standing Orders):
1. **Never write code or modify files directly** — delegate document creation to systems-design-writer agent in Phase 8
2. **Load companion skill systems-design-methodology at mode entry** for the full 8-phase workflow, delegation patterns, and user validation checkpoints
3. **Block all write tools** — this mode produces assessments and thinking, not code
4. **Allow user mode transitions** via mode tool (e.g., `/systems-design` → `/systems-design-review`)
5. **Use todo tool for tracking** progress through the 8 design phases
6. **Load context files** at entry: system-design-principles, tradeoff-frame, structured-design-template
7. **Delegate system-level reasoning** to systems-architect agent in ANALYZE/DESIGN/ASSESS modes (never inline reasoning)

**Workflow Phases** (from companion skill):
1. **System modeling** — systems-architect in ANALYZE mode; build system map (goals, constraints, actors, interfaces, feedback loops)
2. **Constraint extraction** — identify scale, team, budget, integration, compliance assumptions
3. **Candidate exploration** — systems-architect in DESIGN mode; generate 3 candidates (simplest viable, most scalable, most robust)
4. **Tradeoff analysis** — evaluate candidates against 8-dimension frame; identify dominant tradeoff dimensions
5. **Risk assessment** — systems-design-critic (or adversarial-review skill) stress-tests from 5 perspectives
6. **Design refinement** — systems-architect in DESIGN mode; incorporate feedback and refine based on risks
7. **Migration planning** — define incremental vs big-bang rollout and rollback plan
8. **Document production** — delegate to systems-design-writer; write validated design to disk

**Mode Transition Paths**:
- `/systems-design` → `/systems-design-review` (after design to switch to review mode)
- Cannot clear self (allow_clear: false)

---

### Mode: `systems-design-review`

**Purpose**: Evaluate an existing design or proposed architectural change against the codebase through multi-perspective review, producing assessments (not code modifications).

**When to activate**:
- User wants to evaluate an existing design against the codebase
- User wants to review a proposed architectural change
- User needs multi-perspective stress testing for failure modes and hidden complexity
- User needs to validate tradeoffs (stated vs actual) in a design

**Tool Policy**:
- **Blocked**: write_file, edit_file, apply_patch, python_check
- **Safe**: read_file, glob, grep, web_search, web_fetch, LSP, delegate, load_skill, recipes, todo, team_knowledge, mode
- **Warn**: bash
- **Default action**: block unlisted tools

**Entry Conditions**:
- `/systems-design-review` mode activated by user
- Immediately load companion skill `systems-design-review-methodology` at mode entry
- Load context files: `system-design-principles.md`, `adversarial-perspectives.md`

**Exit Conditions**:
- allow_clear is false — mode cannot be cleared by the user; only mode-tool transitions allowed
- Step 6 completes: action items captured or recommendation delivered

**Behavioral Directives**:
1. **Block all write tools** — this mode produces assessments only, not code
2. **Load companion skill systems-design-review-methodology** for full 6-step workflow and user validation checkpoints
3. **Delegate deep analysis** to systems-design-critic or use adversarial-review skill (Step 3)
4. **Validate tradeoffs** against actual system design and implementation (Step 4)
5. **Use team_knowledge tool** to answer "who owns this?" questions
6. **Allow user transitions** via mode tool

**Workflow Phases** (from companion skill):
1. **Design understanding** — read design document, identify goals/constraints/tradeoffs, survey codebase
2. **Codebase evaluation** — compare design claims against actual implementation; use LSP and grep to find gaps
3. **Adversarial analysis** — delegate to systems-design-critic (Option A) or load adversarial-review skill (Option B) for 5-perspective stress test
4. **Tradeoff validation** — load tradeoff-analysis skill if needed; verify stated and unstated tradeoffs
5. **Synthesis & recommendation** — present assessment (health, critical risks, tradeoff alignment); recommend Proceed/Proceed with modifications/Reconsider
6. **Action items** — if proceeding with modifications, produce prioritized list of changes

**Mode Transition Paths**:
- `/systems-design-review` → `/systems-design` (transition to design work after review)
- Cannot clear self (allow_clear: false)

---

## 4. Agent Behaviors

### Agent: `systems-architect`

**Purpose**: Designs systems at the architecture level by modeling service boundaries, data flows, technology selection, and non-functional requirements, producing design documents (not implementation specs).

**Model Role**: reasoning (deep architectural reasoning; complex multi-step analysis)

**Trigger Conditions**:
- New system design or major feature design request
- Request to compare or select architectural approaches or technologies
- Request to review, evaluate, or find bottlenecks in an existing system's architecture
- System-level topology, service boundary, or multi-system integration questions
- Non-functional requirements definition (scalability, reliability, security, cost)
- Migration or rollout strategy design

**Operating Modes**: Three distinct modes available
- **ANALYZE**: System modeling — build system map covering goals, constraints, actors, interfaces, feedback loops, failure modes, time horizons; validate map before proceeding
- **DESIGN**: Candidate exploration — generate 3 candidate architectures (simplest viable, most scalable, most robust); evaluate against 8-dimension tradeoff frame; recommend one with explicit reasoning
- **ASSESS**: Structured assessment — identify service/module boundaries; map coupling using LSP; find architectural debt; analyze failure modes; detect scaling bottlenecks; produce assessment report

**Core Behavioral Directives**:
1. **Model first, solutions second** — build system map in ANALYZE mode and validate before exploring alternatives
2. **Generate 3 candidates minimum** in DESIGN mode: simplest viable, most scalable, most robust
3. **Evaluate against 8-dimension tradeoff frame** (latency, complexity, reliability, cost, security, scalability, reversibility, organizational fit)
4. **Recommend one option with explicit reasoning** — state what it optimizes for and what it sacrifices
5. **Apply YAGNI ruthlessly** — remove unnecessary complexity from all alternatives
6. **Delegate module-level work** (interfaces, contracts, data structures, function signatures) to foundation:zen-architect
7. **Use LSP for semantic analysis** (findReferences, incomingCalls, outgoingCalls, hover, diagnostics) in ASSESS mode; use grep for text patterns
8. **Name unknowns explicitly** — surface what is not known and what signals would indicate design failure
9. **Prefer simplest design** whose failure modes are acceptable
10. **Analyze tradeoffs** rather than mimicking best practices
11. **Trace consequences** via causal reasoning — first-order, second-order, unintended
12. **Examine designs at principle, structural, operational, and evolutionary layers**

**Tool Requirements**:
- read_file, glob, grep (for codebase analysis)
- LSP (hover, findReferences, incomingCalls, outgoingCalls, goToDefinition, diagnostics)
- web_search, web_fetch (research)
- delegate (to foundation:zen-architect for module-level work)

**Context Loading** (always):
- `system-design-principles.md` (design principles reference)
- `tradeoff-frame.md` (8-dimension evaluation frame)
- `structured-design-template.md` (output template)
- `foundation:context/shared/common-agent-base.md` (shared agent base)

**Exit Conditions**:
- System map produced and validated (end of ANALYZE)
- Design document with recommended option and tradeoff analysis produced (end of DESIGN)
- Structured assessment report produced (end of ASSESS)
- Problem scope determined to be module-level → delegate to foundation:zen-architect

---

### Agent: `systems-design-critic`

**Purpose**: Stress-tests designs from 5 adversarial perspectives (SRE, security, staff engineer, finance, operator) and produces a severity-ranked risk assessment finding flaws without generating alternative designs.

**Model Role**: critique (analytical evaluation; finding flaws in existing work)

**Trigger Conditions**:
- Design is completed and needs review before committing to implementation
- Evaluating a proposed architectural change for risks and failure modes
- Called from a recipe (recipe-driven review) or delegated review
- Multi-perspective stress testing requested

**Core Behavioral Directives**:
1. **Read actual design files** — do not review based on summaries; read referenced files and survey codebase
2. **Find flaws, do NOT fix them** — identify what is wrong, risky, or missing; do NOT propose alternative architectures
3. **Be specific** — critique must name concrete failure modes, not generic issues
4. **Be calibrated** — rank findings by actual severity and likelihood; not everything is critical
5. **Evaluate from 5 adversarial perspectives**:
   - **SRE**: failure modes, blast radius, single points of failure, graceful degradation, recovery procedures, monitoring/alerting/SLO needs
   - **Security Reviewer**: attack surface, untrusted input entry points, auth/authz boundaries, sensitive data protection, lateral movement risk, rate limiting gaps, compliance requirements
   - **Staff Engineer**: hidden complexity, implicit assumptions, invisible coupling, testability difficulty, wrong-level abstractions
   - **Finance Owner**: variable costs at scale, superlinear cost growth, cost cliffs, hidden operational costs, vendor lock-in
   - **Operator**: zero-downtime deployment/rollback, diagnostic speed, manual intervention burden, health verification, configuration manageability
6. **Structure output** as: Critical Risks, Significant Concerns, Observations, What the Design Gets Right, Recommended Next Steps

**Tool Requirements**:
- read_file (read design documents and codebase)
- grep, LSP (understand architecture)
- delegate (access context files)

**Context Loading** (always):
- `adversarial-perspectives.md` (5-perspective review framework and output structure)
- `system-design-principles.md` (design principles reference)
- `foundation:context/shared/common-agent-base.md` (shared base)

**Exit Conditions**:
- Severity-ranked risk assessment produced covering all 5 perspectives
- Output sections completed: Critical Risks, Significant Concerns, Observations, What the Design Gets Right, Recommended Next Steps

---

### Agent: `systems-design-writer`

**Purpose**: Writes a formal, structured design document to disk from a validated design passed via delegation, then commits the file.

**Model Role**: writing (long-form content; technical documentation)

**Trigger Conditions**:
- After a design has been fully validated through a `/systems-design` mode conversation
- When the user says "save it", "write up the design document", or equivalent after design approval
- When all design sections have been approved and a complete validated design is passed via delegation

**Core Behavioral Directives**:
1. **Write ONLY what was validated** in the design conversation — do NOT add content not present in delegation instruction
2. **Do NOT ask user questions** — the conversation phase is over
3. **Do NOT make design decisions** — all decisions were already made
4. **Do NOT conduct conversations or explore approaches**
5. **Do NOT skip sections** that have validated content
6. **ALWAYS commit after writing** the file
7. **Do NOT add requirements or considerations** not discussed in the validated design
8. **Do NOT invent tradeoff analysis** that wasn't part of the conversation
9. **Do NOT make architectural choices** (e.g., "I think we should use X instead")

**Operational Workflow**:
1. Receive complete validated design via delegation instruction
2. Determine file name: `docs/designs/YYYY-MM-DD-<topic>-design.md`
3. Create `docs/designs/` directory if it does not exist
4. Structure validated design into clean markdown using structured-design-template
5. Write document to target file path
6. Commit the file with appropriate co-author attribution

**Tool Requirements**:
- write_file (create/write design document)
- bash (create directories, git operations)
- delegate (to foundation:git-ops for commits and pushes)

**Context Loading** (always):
- `structured-design-template.md` (output template with 11 sections)
- `foundation:context/shared/common-agent-base.md` (shared base)

**Exit Conditions**:
- Design document written to `docs/designs/YYYY-MM-DD-<topic>-design.md`
- File committed to repository with Amplifier co-author attribution

---

## 5. Skill Behaviors

### Skill: `systems-design-methodology`

**Purpose**: Governs the 8-phase structured conversation flow for the `/systems-design` mode, defining when to delegate analytical work to specialist agents, when to load supporting skills, and how to validate user understanding at each phase gate.

**Invocation**: Loaded automatically at `/systems-design` mode entry

**Behavioral Directives**:
1. **Handle CONVERSATION; agents handle ANALYSIS** — delegate all system-level reasoning to systems-architect
2. **Present architect output to user** and feed back their feedback into next delegation
3. **Do NOT proceed past Phase 1** until user explicitly validates the problem framing
4. **Re-delegate to architect** if user corrections are given after Phase 1
5. **Load architecture-primitives skill** at Phase 3 if pattern selection is unclear
6. **Load tradeoff-analysis skill** at Phase 4 if tradeoffs are contested
7. **Delegate to systems-design-critic** or suggest `/adversarial-review` at Phase 5 for deep adversarial review
8. **Delegate to systems-design-writer** at Phase 8 with ALL validated content from conversation
9. **Do NOT let writer make decisions** — pass all validated content explicitly
10. **May revisit earlier phases** if user feedback reveals gaps

**Workflow Phases**:
1. **System modeling** (systems-architect, ANALYZE) — build system map; require user validation
2. **Constraints extraction** — surface scale, team, budget, integration, compliance assumptions
3. **Candidate exploration** (systems-architect, DESIGN) — generate 3 candidates; optionally load architecture-primitives or system-type skills
4. **Tradeoff analysis** (systems-architect, DESIGN) — evaluate against 8-dimension frame; optionally load tradeoff-analysis skill
5. **Risks & failure modes** — identify failure modes, SPOFs, scaling bottlenecks; optionally delegate to systems-design-critic; rank by severity
6. **Design refinement** (systems-architect, DESIGN) — incorporate feedback and refine based on risks
7. **Migration & success metrics** — define rollout strategy and failure signals
8. **Document production** (systems-design-writer) — write validated design; ask catalytic closing question

**Context Loaded**: Automatically includes common agent base and design principles

---

### Skill: `systems-design-review-methodology`

**Purpose**: Governs a 6-step conversational methodology for conducting structured design reviews, defining when to delegate adversarial analysis, load supporting skills, and facilitate user decision-making.

**Invocation**: Loaded automatically at `/systems-design-review` mode entry

**Behavioral Directives**:
1. **Handle CONVERSATION; agents handle ANALYSIS** — delegate deep analysis to systems-design-critic or adversarial-review skill
2. **Read design document or referenced files thoroughly** before any critique
3. **Identify stated goals, constraints, and tradeoffs** before evaluating
4. **Note what the design explicitly addresses** and what it is silent on
5. **Use read_file, grep, and LSP** to examine actual code when reviewing existing systems
6. **Compare design claims against real codebase** to identify gaps
7. **Choose Option A** (delegate to systems-design-critic) when codebase context accumulated
8. **Choose Option B** (adversarial-review skill) for self-contained designs
9. **Load tradeoff-analysis skill** after adversarial analysis if tradeoffs unclear
10. **Present assessment summary** with overall health, critical risks, and tradeoff alignment

**Workflow Phases**:
1. **Understand the Design** — read document, identify goals/constraints/tradeoffs, survey codebase, clarifying question
2. **Evaluate Against Codebase** — compare design claims against actual implementation; identify gaps
3. **Adversarial Analysis** — delegate to systems-design-critic (Option A) or load adversarial-review skill (Option B)
4. **Tradeoff Validation** — load tradeoff-analysis skill if needed; verify stated and unstated tradeoffs
5. **Synthesize & Recommend** — present assessment (health, critical risks, alignment); recommend Proceed/Proceed with modifications/Reconsider
6. **Capture Action Items** — if proceeding with modifications, produce prioritized list

---

### Skill: `adversarial-review`

**Purpose**: Conducts an adversarial multi-perspective review of a system design by launching five parallel critic agents (SRE, security, staff engineer, finance, operator) and synthesizing findings into a unified risk assessment.

**Invocation**: Skill command or interactive delegation; can be user-invoked during design conversation

**Behavioral Directives**:
1. **Act as a critic, not collaborator** — find flaws, not praise
2. **If $ARGUMENTS is empty**, search conversation history for most recent design document
3. **If no design found**, respond with specific prompt asking user to provide one
4. **Before launching agents**, read and understand design: read referenced files, identify key components/data flows/failure domains, note what design is silent on
5. **Launch all 5 review agents concurrently** in single message using delegate tool
6. **Pass each agent the full design context** so they have complete information
7. **Wait for all 5 agents to complete** before synthesizing
8. **Produce unified risk assessment** with: Critical Risks, Significant Concerns, Observations, What the Design Gets Right, Recommended Next Steps

**The 5 Perspectives**:
- SRE (operational resilience)
- Security Reviewer (attack surface, data protection)
- Staff Engineer (complexity, abstractions, testability)
- Finance Owner (cost curves, lock-in)
- Operator (runbooks, zero-downtime operations)

---

### Skill: `architecture-primitives`

**Purpose**: Structured catalog of reusable architectural primitives with what-when-wrong evaluation, helping designers choose between synchronous/async communication, state machines, queues, caches, consistency models, idempotency strategies, and blast-radius isolation.

**Invocation**: Referenced during Phase 3 candidate exploration if pattern selection is unclear

**Behavioral Directives**:
1. **Evaluate by 3 axes**: what it is, when it's right, **when it's wrong**
2. **Never recommend without considering failure conditions**
3. **Do NOT recommend sync** when caller doesn't need result to continue
4. **Do NOT recommend async** when immediate consistent response required
5. **Always identify single source of truth** for every piece of state
6. **Do NOT draw boundaries** when cross-boundary cost exceeds benefit
7. **Do NOT introduce premature contracts** between components still being designed together
8. **Require versioning strategy** before committing to any contract
9. **Treat queues as problem-solver, not problem-mover** — flag when queue grows unboundedly
10. **Do NOT use caches** when invalidation is harder than performance problem
11. **Always pair retries with idempotency** and circuit breaker
12. **Use jitter in backoff** to prevent synchronized retry storms
13. **Apply backpressure in pipelines** where dropping work is worse than slowing down
14. **Never model state with boolean flag bags** — use explicit state machine
15. **Frame consistency decisions per-data-type**, not system-wide
16. **Treat observability as mandatory** — system you cannot observe = system you cannot operate
17. **Apply blast-radius isolation** between components with different reliability requirements

**Primitives Covered**:
- Boundaries and contracts
- State machines vs flag bags
- Synchronous vs asynchronous communication
- Queues and buffering
- Caching and invalidation
- Idempotency and retries
- Circuit breakers and backoff
- Consistency models
- Observability strategies
- Blast-radius isolation

---

### Skill: `system-type-web-service`

**Purpose**: Domain patterns, guarantees, and failure modes for request/response web services including API style selection (REST/GraphQL/gRPC), scaling strategies, data layer choices, observability practices, and anti-patterns.

**Invocation**: Referenced during Phase 3 when designing web services or APIs

**Key Topics**:
- **API patterns**: REST (when: public APIs, CRUD, cacheability), GraphQL (when: multiple clients, different data shapes), gRPC (when: internal RPC, streaming, speed)
- **Scaling**: horizontal (stateless), vertical (databases), autoscaling (watch cold start), CDN/edge caching, read replicas
- **Data layers**: RDBMS (structured), document stores (natural shapes), key-value (caching), search engines (full-text)
- **Observability**: structured JSON logs (consistent fields), trace ID propagation, RED method (Rate/Errors/Duration), SLOs required before measuring
- **Failure mitigation**: timeouts, circuit breakers, bulkheads, jittered TTLs, request coalescing, cache warming, exponential backoff with jitter
- **Anti-patterns**: distributed monolith, god services, chatty interfaces, shared mutable state, premature microservices, ignored cold starts

---

### Skill: `system-type-event-driven`

**Purpose**: Domain patterns, guarantees, and failure modes for event-driven and message-based architectures including pub/sub, event sourcing, CQRS, sagas, and delivery guarantees.

**Invocation**: Referenced during Phase 3 when designing event-driven or message-based systems

**Key Topics**:
- **Pub/sub**: when (fan-out notifications, audit logging, read models); avoid (sync responses needed, ordering matters, one consumer)
- **Event sourcing**: when (audit, historical reconstruction, projections); avoid (CRUD-heavy, hard schema evolution)
- **CQRS**: when (different read/write patterns); avoid (essentially same models, consistency lag unacceptable)
- **Sagas**: for multi-step business processes spanning services; choreography (<4 steps), orchestration (>4 steps)
- **Delivery guarantees**: at-least-once (practical default) with idempotent consumers; avoid exactly-once (complexity)
- **Schema evolution**: versioned events, optional fields, new event types; never remove/rename fields without strategy
- **Dead letter queues**: mandatory in production; monitor depth, alert on arrivals, maintain replay mechanism
- **Anti-patterns**: event soup, events for sync queries, fat events, ordering ignored, no DLQ strategy, shared event bus

---

### Skill: `tradeoff-analysis`

**Purpose**: Provides the 8-dimension comparison framework and matrix template for evaluating design alternatives by forcing every tradeoff into structured comparison.

**Invocation**: Referenced during Phase 4 or whenever technology choices must be compared

**The 8 Dimensions**:
1. **Latency** — response time, perceived speed
2. **Complexity** — conceptual, implementation, operational
3. **Reliability** — uptime, fault tolerance, recoverability
4. **Cost** — infrastructure, labor, opportunity
5. **Security** — attack surface, data protection, compliance
6. **Scalability** — performance growth with load
7. **Reversibility** — can we switch away later?
8. **Organizational fit** — team skills, existing patterns, culture

**Behavioral Directives**:
1. **Force all analysis into 8-dimension frame** — not inventing new dimensions
2. **Use qualitative assessments** (good/adequate/poor) with concrete notes, not numeric scores
3. **Every matrix cell must have rating + note** — empty cells = unexamined risk
4. **Minimum 2, maximum 5 alternatives** — fewer = under-explored, more = narrow first
5. **Identify 1-2 dominant differentiating dimensions**
6. **Explicitly state what chosen option sacrifices** — required part of recommendation
7. **Ask "What would have to be true for this to be wrong?"** to surface assumptions and monitoring signals
8. **If you can't answer optimize-for/sacrifice clearly**, design is not yet understood

---

## 6. Context & Cross-Cutting Concerns

### Context Files & Standing Orders

#### `system-design-principles.md`
**Scope**: Core principles shaping how the LLM reasons about system design problems

**Six Core Principles**:
1. **Never jump to solutions** — build a map first (goals, constraints, actors, interfaces, feedback loops, failure modes)
2. **Examine at four layers**: Principle, Structural, Operational, Evolutionary
3. **Analyze tradeoffs using 8-dimension frame** instead of mimicking best practices
4. **For every design answer**: "What does this optimize for, and what does it sacrifice?"
5. **Trace causal propagation**: first-order, second-order, unintended consequences, monitoring signals
6. **Prefer simplest design** whose failure modes are acceptable (not simplest possible, not most scalable imaginable)

**Standing Behaviors**:
- Evaluate simplicity across 5 dimensions: conceptual, interface, operational, evolutionary, organizational
- Think broadly about system, design narrowly with minimum concepts/components/abstractions
- For any pattern: what problem does it solve here? What does it make worse? What simpler alternative was rejected?
- Surface implicit assumptions and make explicit
- Distinguish local vs global optimization
- Identify tight coupling — what changes together?
- Look for single points of failure as intentional design decisions
- Prefer reversible decisions early; defer irreversible until evidence exists
- Separate mechanism from policy
- Ask what scales with usage, time, org size
- Name unknowns and specify monitoring signals for design failure

#### `tradeoff-frame.md`
**Scope**: The 8-dimension evaluation framework used throughout design work

**Framework Usage**:
- Evaluation matrix: rows = alternatives (2-5), columns = 8 dimensions
- Each cell: rating (good/adequate/poor) + concrete note
- Identify dominant tradeoff dimensions (usually 1-2)
- Explicitly state what recommended option sacrifices
- No numeric scores — force qualitative assessment with notes

#### `structured-design-template.md`
**Scope**: Mandatory 11-section structure for nontrivial system designs

**11 Sections**:
1. **Problem Framing** — restate goals, constraints, scope
2. **Explicit Assumptions** — enumerate all assumptions
3. **System Boundaries** — inside vs outside system, interface points
4. **Components and Responsibilities** — major components, ownership, sources of truth
5. **Data and Control Flows** — data movement, triggers, critical paths
6. **Risks and Failure Modes** — failures, blast radius, recovery paths
7. **Tradeoffs** — evaluate against 8-dimension frame
8. **Recommended Design** — preferred design with reasoning over alternatives
9. **Simplest Credible Alternative** — minimal viable design; justify added complexity
10. **Migration and Rollout Plan** — incremental steps, cutover requirements, rollback
11. **Success Metrics** — measurable indicators and failure thresholds

#### `adversarial-perspectives.md`
**Scope**: The 5-perspective review framework with driving questions per role

**Five Reviewer Perspectives** (with driving questions each):
- **SRE**: What breaks? What are the recovery procedures? Can we operate this 24/7?
- **Security Reviewer**: What is the attack surface? Where is untrusted input? What's the blast radius of a breach?
- **Staff Engineer**: Where is hidden complexity? What assumptions are invisible? Is this testable? Are abstractions right-level?
- **Finance Owner**: What grows with load? Are there cost cliffs? Hidden operational costs? Vendor lock-in?
- **Operator**: Can we deploy zero-downtime? How fast can we diagnose? What's the manual burden? Can we verify health?

**Output Structure** (synthesis phase):
- Critical Risks (severity ranked)
- Significant Concerns
- Observations
- What the Design Gets Right
- Recommended Next Steps (top 3-5, ordered by risk reduction)

#### `instructions.md`
**Scope**: Standing-order routing table that detects system design requests and directs to appropriate mode/recipe/skill

**Routing Logic**:
- Detect user intent from natural language
- Match to correct mechanism (mode, recipe, skill, or direct answer)
- Load companion skill immediately upon mode entry
- Match methodology depth to scope

**Mode Activation Triggers**:
- "Design a system for..." → `/systems-design` mode
- "How should we architect..." → `/systems-design` mode
- "Review this architecture..." → `/systems-design-review` mode
- "Evaluate our system..." → `/systems-design-review` mode

**Recipe Triggers**:
- Full system design with approval gates → `systems-design-cycle` recipe
- Multi-perspective review with stages → `systems-design-review` recipe
- Quick 3-alternative exploration → `systems-design-exploration` recipe
- Codebase understanding needed → `codebase-understanding` recipe

---

## 7. Recipe Workflows

### Recipe: `bundle-behavioral-spec`

**Purpose**: Analyze a bundle's full composition and produce a behavioral specification document

**Execution Mode**: flat (no approval gates)

**Input Interface**: None required (self-contained bundle analysis)

**Workflow**:

| Step | Type | Agent | Produces | Consumes |
|------|------|-------|----------|----------|
| 1. parse-composition | bash | — | `manifest` | — |
| 2. analyze-composition | bash | — | `composition_effects` | — |
| 3. extract-behaviors | delegate | foundation:explorer | `behavior_extraction` | `manifest` |
| 4. synthesize-spec | delegate | foundation:file-ops | `spec_document` | `composition_effects`, `behavior_extraction` |

**Data Flow**:
- `manifest` (bundle YAML structure) → step 3
- `composition_effects` (deterministic analysis) → step 4
- `behavior_extraction` (per-component analysis) → step 4
- `spec_document` → written to `docs/bundle-behavioral-spec-<bundle>.md`

---

### Recipe: `codebase-understanding`

**Purpose**: Survey codebase structure, identify boundaries and coupling, map flows, produce architectural overview

**Execution Mode**: flat

**Workflow**:

| Step | Type | Agent | Produces | Consumes |
|------|------|-------|----------|----------|
| 1. survey-structure | delegate | foundation:explorer | `structure_survey` | — |
| 2. identify-boundaries | delegate | systems-architect | `boundary_analysis` | `structure_survey` |
| 3. map-flows | delegate | systems-architect | `flow_analysis` | `structure_survey`, `boundary_analysis` |
| 4. architectural-overview | delegate | systems-architect | `architectural_overview` | `structure_survey`, `boundary_analysis`, `flow_analysis` |

**Data Flow**:
- Structure survey feeds into all downstream analysis
- Boundary analysis informs flow mapping
- All analyses feed into final overview

---

### Recipe: `systems-design-cycle`

**Purpose**: End-to-end system design with approval gates—problem framing, candidates, risk assessment, refinement, documentation

**Execution Mode**: staged (3 approval gates)

**Workflow**:

| Step | Type | Agent | Produces | Gate |
|------|------|-------|----------|------|
| 1. build-system-map | delegate | systems-architect (ANALYZE) | `system_map` | — |
| 2. extract-constraints | delegate | systems-architect | `constraints_analysis` | candidates gate |
| 3. generate-candidates | delegate | systems-architect (DESIGN) | 3 candidate designs | candidates gate |
| 4. evaluate-tradeoffs | delegate | systems-architect (DESIGN) | `tradeoff_evaluation` | — |
| 5. adversarial-review | delegate | systems-design-critic | `risk_assessment` | risk-and-refinement gate |
| 6. refine-design | delegate | systems-architect (DESIGN) | `refined_design` | risk-and-refinement gate |
| 7. write-document | delegate | systems-design-writer | `design_document` | documentation gate |

**Approval Gates**:
1. **candidates gate** (after constraints analysis): User approves problem framing and constraints before generating candidates
2. **risk-and-refinement gate** (after candidates & tradeoff evaluation): User approves candidates and tradeoff analysis before risk assessment
3. **documentation gate** (after refinement): User approves refined design before producing final document

**Data Flow**:
- System map → informs all downstream work
- Constraints analysis → used in candidate generation and evaluation
- Tradeoff evaluation → feeds into risk assessment
- Risk assessment → feeds into design refinement
- All upstream work → fed into document writing

---

### Recipe: `systems-design-exploration`

**Purpose**: Explore 3 architectural alternatives in parallel, evaluate against tradeoff frame, synthesize recommendation

**Execution Mode**: flat

**Workflow**:

| Step | Type | Agent | Produces | Parallel |
|------|------|-------|----------|----------|
| 1. frame-problem | delegate | systems-architect (ANALYZE) | `problem_frame` | — |
| 2. generate-candidates | delegate | systems-architect (DESIGN) | 3 candidates | 3-way parallel |
| 3. evaluate-tradeoffs | delegate | systems-architect (DESIGN) | `tradeoff_evaluation` | — |
| 4. adversarial-review | delegate | systems-design-critic | `adversarial_review` | conditional |

**Parallelism**:
- Step 2: Generate 3 candidates in parallel (simplest viable, most scalable, most robust)
- Step 4: Only runs if `with_adversarial_review` == 'true'

**Data Flow**:
- Problem frame → candidate generation and tradeoff evaluation
- Candidates → tradeoff evaluation
- Tradeoff evaluation → optional adversarial review

---

### Recipe: `systems-design-review`

**Purpose**: Multi-stage architecture review with approval gates between reconnaissance, analysis, and reporting

**Execution Mode**: staged (2 approval gates)

**Workflow**:

| Step | Type | Agent | Produces | Gate |
|------|------|-------|----------|------|
| 1. survey-codebase | delegate | foundation:explorer | `codebase_survey` | — |
| 2. identify-boundaries | delegate | systems-architect (ASSESS) | `system_map` | analysis gate |
| 3. perspective-analysis | delegate | systems-architect (ASSESS) | 5-perspective analysis | analysis gate |
| 4. synthesize-risks | delegate | systems-design-critic | `risk_assessment` | report gate |
| 5. write-report | delegate | systems-design-writer | `final_report` | report gate |

**Approval Gates**:
1. **analysis gate**: User approves codebase survey and system map before proceeding to perspective analysis
2. **report gate**: User approves risk assessment before generating final report

**Parallelism**:
- Step 3: 5-perspective analysis runs in parallel (SRE, Security, Staff Engineer, Finance, Operator)

**Data Flow**:
- Codebase survey → feeds into boundary identification and analysis
- System map → feeds into perspective analysis and risk synthesis
- Risk assessment → feeds into final report

---

## 8. Behavioral Invariants

### System-Wide Guarantees

#### 1. **Design-First Philosophy**
- **Guarantee**: No implementation (code) is produced until design is documented and approved
- **Enforcement**: write_file and edit_file are blocked in both design modes; document production delegated to systems-design-writer
- **Invariant held**: All system-design and systems-design-review workflows require design approval before any output is written to disk

#### 2. **Separation of Concerns**
- **Guarantee**: Conversation orchestration is separate from analysis
- **Enforcement**: Companion skills (systems-design-methodology, systems-design-review-methodology) handle conversation flow; specialist agents (systems-architect, systems-design-critic, systems-design-writer) handle actual analysis and production
- **Invariant held**: The LLM does not perform inline system-level analysis; all analysis is delegated to agents

#### 3. **User Validation Gates**
- **Guarantee**: No phase proceeds without explicit user approval when required
- **Enforcement**: systems-design-methodology blocks progression at end of Phase 1 until system map validated; recipes implement staged approval gates
- **Invariant held**: Phase 1 (system modeling) always requires explicit user validation before proceeding to Phase 2

#### 4. **Tradeoff Explicitness**
- **Guarantee**: Every design recommendation explicitly states what is being optimized for and what is being sacrificed
- **Enforcement**: systems-architect operates against 8-dimension tradeoff frame; tradeoff-analysis skill requires explicit sacrifice statement
- **Invariant held**: No design recommendation is presented without clear optimization/sacrifice framing

#### 5. **Failure Mode Awareness**
- **Guarantee**: Every architectural primitive and pattern choice includes explicit consideration of failure modes and when it is wrong
- **Enforcement**: architecture-primitives skill structures evaluation as what-it-is, when-right, when-wrong; adversarial-review finds actual failure modes for designs
- **Invariant held**: Design review includes failure mode analysis from 5 adversarial perspectives

#### 6. **Simplicity-First Defaults**
- **Guarantee**: Simpler designs are preferred over complex ones unless complexity is justified by requirements
- **Enforcement**: YAGNI principle enforced in systems-architect behavioral directives; simplest viable candidate always generated alongside alternatives
- **Invariant held**: Architects generate "simplest viable" as one of 3 candidates; simplest design whose failure modes are acceptable is preferred

#### 7. **No Premature Optimization**
- **Guarantee**: Architectural decisions are not made based on hypothetical future requirements
- **Enforcement**: YAGNI ruthlessly applied; future-proofing explicitly forbidden in system-design-principles
- **Invariant held**: Designs optimize for current requirements; reversibility is evaluated separately in tradeoff frame

#### 8. **Codebase Ground Truth**
- **Guarantee**: Design claims are validated against actual implementation
- **Enforcement**: systems-design-review-methodology requires comparing design claims against actual code; LSP and grep used for concrete verification
- **Invariant held**: Design review process steps 2-3 verify stated design against actual codebase

---

### Detected Contradictions & Gaps

#### Potential Tension: Agent Autonomy vs. User Direction
**Finding**: systems-design-methodology allows revisiting earlier phases if user feedback reveals gaps, but exits when allow_clear=false. This is not contradictory but worth noting: the mode cannot be cleared by user directly, only transitioned out via mode tool.

**Resolution**: As designed — mode is "sticky" to prevent accidental exit; transitions via mode tool are available.

#### Potential Gap: Recipe Documentation vs. Mode Documentation
**Finding**: Recipes (systems-design-cycle, systems-design-review) implement similar workflows to modes (systems-design, systems-design-review), but they are presented as separate mechanisms. Recipes automate the mode workflow; modes are interactive sessions.

**Resolution**: As designed — recipes = automated pipelines with approval gates; modes = interactive sessions where user drives decisions. Both can be used but represent different entry points (hands-off recipe vs. engaged mode).

#### Clarification: Agent Model Role Selection
**Finding**: systems-architect is marked as using "reasoning" model role, but this is only inferred from description. No explicit model_role declaration in agent metadata provided.

**Guidance**: Use `model_role=reasoning` when delegating to systems-architect for complex multi-step design work; the reasoning role is appropriate for architecture design.

---

### Coverage Summary

**Components Documented**:
- ✅ 2 modes (systems-design, systems-design-review)
- ✅ 3 agents (systems-architect, systems-design-critic, systems-design-writer)
- ✅ 6 skills (systems-design-methodology, systems-design-review-methodology, adversarial-review, architecture-primitives, system-type-web-service, system-type-event-driven, tradeoff-analysis)
- ✅ 5 context files (system-design-principles, tradeoff-frame, structured-design-template, adversarial-perspectives, instructions)
- ✅ 4 recipes (bundle-behavioral-spec, codebase-understanding, systems-design-cycle, systems-design-exploration, systems-design-review)

**Coverage Quality**:
- Tool governance: Complete matrix and necessity map provided
- Mode behaviors: Full lifecycle documented for both modes
- Agent behaviors: Trigger conditions, operating modes, directives, and exit conditions specified
- Skill behaviors: Purpose, invocation, phases, and key directives documented
- Recipe workflows: Step-by-step walkthrough with data flow and parallelism noted
- Invariants: 8 system-wide guarantees documented with enforcement and integrity verification

**No Critical Gaps Detected**: The behavioral specification provides sufficient detail for an LLM to:
1. Understand when to activate which mode
2. Know which tools are available in each mode
3. Delegate appropriately to specialist agents
4. Load and invoke skills at the right phases
5. Execute recipes with understanding of data flow and approval gates
6. Maintain architectural integrity throughout design work

---

**End of Behavioral Specification**
