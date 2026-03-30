# System Design Intelligence Bundle: Project Plan v1

## Goal

Build a `system-design-intelligence` bundle that materially improves how an
AI agent approaches system design work -- for both new and existing codebases.

The bundle should make the agent behave more like a strong systems architect:
modeling systems before solving, reasoning at multiple scales, analyzing tradeoffs
rather than mimicking best practices, tracing causal chains, and working from
architectural primitives. (See `agentic-system-design.md` for the full thesis.)

## Principles

- **Deliver value daily.** Every phase produces something usable and testable.
  No phase that's purely research or scaffolding.
- **Lightest mechanism first.** Content files and skills before tools and hooks.
  Markdown before Python.
- **Test against real work.** Each phase is validated by using the bundle on
  actual design tasks, not hypothetical ones.
- **Compose, don't replace.** Build on foundation's infrastructure. Complement
  zen-architect, don't compete with it. Enable composition with superpowers.

## Bundle Composition Strategy

Include foundation for infrastructure (tools, providers, orchestrator, hooks,
delegate, skills, recipes, modes). Replace the root instruction with our own.
Add our design-specific content, agents, skills, modes, and recipes on top.

Foundation's design philosophy files (IMPLEMENTATION_PHILOSOPHY, KERNEL_PHILOSOPHY,
etc.) load only in agent sessions (zen-architect), never in our root context.
They don't interfere with our approach. zen-architect remains available for
module-level work as a complementary layer beneath our system-level design.

Full analysis: `docs/bundle-composition-strategy.md`

---

## Phase 0: Bundle Skeleton
_Day 1 morning. Deliverable: a running bundle._

Create the minimal bundle structure that loads and runs on foundation.

### Tasks

- Create the repository structure:
  ```
  system-design-intelligence/
    bundle.md                    # Root bundle (thin, includes foundation)
    behaviors/
      system-design.yaml         # Core behavior wiring
    context/
      (empty, populated in Phase 1)
    agents/
      (empty, populated in Phase 4)
    skills/
      (empty, populated in Phase 2)
    modes/
      (empty, populated in Phase 3)
    recipes/
      (empty, populated in Phase 5)
  ```

- Write `bundle.md`:
  - `includes: [foundation]`
  - Minimal instruction with placeholder @mentions
  - Verify it loads: `amplifier run --bundle ./bundle.md "hello"`

- Write `behaviors/system-design.yaml`:
  - Empty behavior skeleton that will accumulate context, agents, skills, modes

### Done When

Bundle loads successfully, inherits all foundation capabilities, and responds
to prompts. This is pure scaffolding but confirms the composition works.

---

## Phase 1: Core Design Content
_Day 1 afternoon through Day 2. Deliverable: measurably better design output._

Write the always-present context files that establish the agent's design
methodology. This is the highest-leverage work -- pure markdown, no code, and
it immediately changes how the agent approaches design problems.

### The Five Upgrades (from agentic-system-design.md)

Each upgrade maps to content we'll create:

| Upgrade | Content Target |
|---------|---------------|
| 1. Model the system before solving | Structured response template |
| 2. Force multiscale reasoning | Layer framework in principles |
| 3. Tradeoff analysis, not mimicry | Tradeoff methodology in principles |
| 4. Reason causally | Causal reasoning guidance in principles |
| 5. Architectural primitives | Standing behaviors list |

### Tasks

- **`context/system-design-principles.md`** (~2,000 tokens)
  Core principles document. Not Amplifier-specific. Generic system design wisdom:
  - Model the system before solving (goals, constraints, actors, resources,
    interfaces, feedback loops, failure modes, time horizons, tradeoffs)
  - Multiscale reasoning (principle, structural, operational, evolutionary)
  - Tradeoff analysis framework (latency, complexity, reliability, cost,
    security, scalability, reversibility, organizational fit)
  - Causal reasoning (first-order effects, second-order effects, unintended
    consequences, monitoring signals)
  - Simplicity as constraint (structural, interface, operational, evolutionary,
    organizational simplicity)
  - Standing behaviors: surface assumptions, distinguish local vs global
    optimization, identify tight coupling, look for single points of failure,
    prefer reversible decisions, separate mechanism from policy

- **`context/structured-design-template.md`** (~800 tokens)
  Default template for any nontrivial design problem:
  1. Problem framing
  2. Assumptions (explicit)
  3. System boundaries
  4. Components and responsibilities
  5. Data/control flows
  6. Risks and failure modes
  7. Tradeoffs (what does this optimize for, what does it sacrifice?)
  8. Recommended design
  9. Simplest credible alternative
  10. Migration/rollout plan
  11. Metrics to validate success

- **`context/instructions.md`** (~1,000 tokens)
  Standing orders for the root session:
  - When to suggest /design mode (detect design-related requests)
  - When to delegate to design agents vs handle directly
  - Methodology calibration (not everything needs full design treatment)
  - "Generate at least 3 architectures: simplest viable, most scalable,
    most robust. Then recommend with reasoning."

- Wire these into `bundle.md` via @mentions and into `behaviors/system-design.yaml`
  via `context.include`.

### Testing

Run the bundle on 2-3 real design prompts and compare output quality with and
without the content files. Examples:
- "Design an authentication system for a multi-tenant SaaS application"
- "How should we structure the caching layer for this API?" (with a real codebase)
- "Evaluate the current architecture of [existing project]"

### Done When

The agent demonstrably produces more structured, thorough design output: explicit
assumptions, multiple alternatives, tradeoff analysis, failure modes. The
structured template should be visibly shaping the response format.

---

## Phase 2: Design Skills
_Days 2-4. Deliverable: on-demand design knowledge loaded when relevant._

Create skills for specialized design knowledge that shouldn't consume tokens
every turn. Skills are progressive disclosure -- the agent sees their names
automatically, loads full content when relevant.

### Tasks

- **`skills/tradeoff-analysis/SKILL.md`**
  Detailed tradeoff analysis methodology:
  - The fixed comparison frame (8 dimensions)
  - How to identify what a design optimizes for and what it makes worse
  - Tradeoff matrix template
  - Common tradeoff patterns (consistency vs availability, simplicity vs
    flexibility, latency vs throughput)
  - "The architecturally catalytic question: What does this design optimize
    for, and what does it make worse?"

- **`skills/adversarial-review/SKILL.md`** (fork skill)
  Multi-perspective adversarial review:
  - `context: fork` -- spawns isolated subagent
  - `model_role: critique`
  - Launches parallel review from 5 perspectives: SRE (how does this fail in
    production?), security reviewer (what is the abuse path?), staff engineer
    (where is hidden complexity?), finance owner (what cost curve appears later?),
    operator (what becomes painful at 2am?)
  - Synthesizes into a unified risk assessment

- **`skills/architecture-primitives/SKILL.md`**
  Catalog of reusable architectural abstractions:
  - Boundaries and ownership, contracts/interfaces, source of truth, sync vs
    async, state machines, queues, caches, idempotency, retries, backpressure,
    consistency models, observability, blast radius isolation
  - For each: what it is, when it's right, when it's WRONG
  - "An agent that knows many patterns is less useful than one that knows when
    each pattern is wrong."

- **`skills/system-type-web-service/SKILL.md`** (first system type)
  Domain-specific guidance for web service architecture:
  - Common patterns (REST, GraphQL, gRPC)
  - Scaling patterns (horizontal, vertical, autoscaling)
  - Data layer patterns (RDBMS, NoSQL, caching, CDN)
  - Observability (structured logging, distributed tracing, metrics, SLOs)
  - Common failure modes and mitigations
  - Anti-patterns specific to web services

- **`skills/system-type-event-driven/SKILL.md`** (second system type)
  Domain-specific guidance for event-driven/message-based systems:
  - Patterns (pub/sub, event sourcing, CQRS, saga)
  - Ordering, delivery guarantees, idempotency
  - Schema evolution
  - Common failure modes

### Testing

Verify skills are discoverable (`load_skill(list=true)` shows them) and that
the agent loads them appropriately during design conversations. Test the
adversarial review fork skill produces genuinely multi-perspective output.

### Done When

The agent can draw on specialized design knowledge without always paying the
token cost. The adversarial review skill produces output from all 5 perspectives.
System type skills provide relevant domain guidance when loaded.

---

## Phase 3: Design Mode
_Days 3-5. Deliverable: structured design workflow with guardrails._

Create a `/design` mode following superpowers' hybrid pattern. This is the
structured interactive workflow for system design exploration.

### Tasks

- **`modes/design.md`**
  Tool policies:
  - `safe`: read_file, glob, grep, web_search, web_fetch, load_skill, LSP,
    delegate, recipes
  - `warn`: bash
  - `default_action`: block (write_file, edit_file blocked)
  - `allowed_transitions`: [design-review, brainstorm, write-plan, debug]
  - `allow_clear`: false

  Phased process (adapting superpowers' hybrid pattern):
  1. **Understand context** -- read existing code/docs, understand what exists
  2. **Model the system** -- identify boundaries, actors, constraints, dependencies
     before proposing solutions. Produce system map.
  3. **Ask questions** -- one at a time, to refine understanding of requirements,
     constraints, and priorities
  4. **Explore alternatives** -- generate at least 3 designs (simplest viable,
     most scalable, most robust) with explicit tradeoffs
  5. **Evaluate tradeoffs** -- systematic comparison across the fixed frame.
     Load tradeoff-analysis skill.
  6. **Present design** -- section-by-section, validate each with user
  7. **Adversarial review** -- load adversarial-review skill or delegate to
     design-critic agent
  8. **Delegate artifact** -- delegate to design-writer agent to produce the
     design document

  Anti-rationalization table (design-specific):
  - "This is too simple for a design doc" -- Simple systems become complex.
  - "I already know the right architecture" -- Assumptions kill designs.
  - "We don't have time for alternatives" -- Bad designs cost 10x more.
  - "The requirements aren't clear enough" -- Design reveals requirements.
  - "Let me just start coding" -- write_file is blocked. Design first.

- **`modes/design-review.md`**
  A mode for evaluating existing designs or proposed changes:
  - Read-only + delegate
  - Enforce multi-perspective review
  - Checklist: design integrity, constraints satisfaction, failure modes,
    DX, implementation viability, simplicity, tooling consistency
  - `allowed_transitions`: [design, brainstorm, execute-plan]

- Wire modes into the behavior YAML with `search_paths`.

### Testing

Activate `/design` and verify:
- Write tools are blocked
- The agent follows the phased process
- Questions come one at a time
- Multiple alternatives are generated
- Tradeoff analysis skill is loaded
- Section-by-section validation happens
- Anti-rationalization prevents shortcuts

### Done When

`/design` mode produces a structured, validated design through interactive
conversation. The agent cannot skip phases or jump to implementation. The
hybrid pattern works: conversation in mode, artifact via delegation.

---

## Phase 4: Design Agents
_Days 4-7. Deliverable: specialist design expertise via delegation._

Create agents that carry heavy design reference documentation in their own
context windows, keeping the root session lean.

### Tasks

- **`agents/systems-architect.md`**
  The primary system-level design agent.
  - `model_role: [reasoning, general]`
  - Tools: filesystem, search, web, LSP (no bash -- design only)
  - System instruction: the full system design methodology
  - @mentions: our design principles + structured template + architecture
    primitives content (heavy docs in agent context, not root)
  - Three modes (adapting zen-architect's pattern):
    - ANALYZE: system modeling, boundary identification, constraint discovery
    - DESIGN: multi-alternative generation, tradeoff analysis, recommendation
    - ASSESS: evaluate existing systems against design principles
  - Produces: system design documents, not implementation specs
  - Scope: system-level (service topology, technology selection, NFRs).
    Delegates to zen-architect for module-level specification.

- **`agents/design-critic.md`**
  Adversarial review from multiple perspectives.
  - `model_role: [critique, reasoning, general]`
  - Tools: filesystem, search, web (read-only)
  - Instruction: review designs from 5 perspectives (SRE, security, staff
    engineer, finance, operator)
  - Does NOT generate designs -- only finds flaws and blind spots
  - Output: risk assessment, severity-ranked concerns, questions to resolve

- **`agents/design-writer.md`**
  Pure artifact writer (like superpowers' brainstormer).
  - `model_role: [writing, general]`
  - Tools: filesystem (has write access)
  - Receives validated design from delegation, structures into document
  - Template: Overview, Context, Goals, Constraints, Architecture, Components,
    Data Flow, Failure Modes, Tradeoffs, Alternatives Considered, Migration
    Plan, Success Metrics, Open Questions
  - Does NOT make design decisions -- all decisions were made during /design
    conversation

- Wire agents into the behavior YAML.

### Testing

Delegate to each agent from the root session and verify:
- systems-architect produces structured design output with alternatives
- design-critic finds genuine flaws (not just restating the design)
- design-writer produces clean documents without inventing content
- The delegation chain works: /design mode -> systems-architect -> design-critic
  -> design-writer

### Done When

The three-agent design pipeline works end-to-end. A user in /design mode can
get system-level design analysis, adversarial review, and a written design
document through delegation.

---

## Phase 5: Recipes for Architecture Understanding
_Week 2, first half. Deliverable: repeatable multi-step design workflows._

Create recipes for the multi-step design processes from investigation.md:
understanding existing systems, evaluating designs, and structured review.

### Tasks

- **`recipes/architecture-review.yaml`** (staged)
  Multi-perspective architecture review of an existing codebase:
  - Stage 1: Reconnaissance
    - Explorer agent surveys codebase structure
    - Systems-architect identifies boundaries, dependencies, patterns
    - Approval gate: user confirms scope
  - Stage 2: Analysis
    - Parallel analysis from multiple perspectives (foreach + parallel):
      design integrity, failure modes, DX, scalability, security
    - Design-critic synthesizes concerns
    - Approval gate: user reviews findings
  - Stage 3: Report
    - Design-writer produces assessment document

- **`recipes/design-exploration.yaml`** (flat)
  Parallel exploration of design alternatives:
  - Classify the system type (web service, event-driven, etc.)
  - Load relevant system-type skill
  - Generate 3 architectures (foreach + parallel): simplest, most scalable,
    most robust
  - Evaluate each against the tradeoff framework
  - Synthesize comparison matrix

- **`recipes/codebase-understanding.yaml`** (flat)
  Get architectural understanding of an existing codebase or subsystem:
  - Survey directory structure and dependencies
  - Identify module boundaries and coupling patterns
  - Map data flows and control flows
  - Identify architectural patterns in use
  - Assess complexity distribution
  - Produce architectural overview document

### Testing

Run each recipe against a real codebase (amplifier-core or amplifier-foundation
are good candidates). Verify:
- Multi-step execution with context accumulation works
- Parallel perspectives produce distinct insights (not repetition)
- Approval gates pause at the right points
- Output documents are useful

### Done When

Users can run repeatable design workflows that produce consistent, thorough
architectural analysis without manual orchestration.

---

## Phase 6: Constraint Management
_Week 2, second half. Deliverable: explicit constraint tracking in design._

Design is fundamentally about constraints and tradeoffs. This phase adds
explicit constraint management capabilities.

### Tasks

- **`skills/constraint-discovery/SKILL.md`**
  Methodology for systematic constraint identification:
  - Categories: technical, organizational, regulatory, timeline, resource,
    compatibility, operational
  - Discovery techniques: stakeholder interviews, codebase analysis,
    dependency mapping, failure mode analysis
  - Constraint documentation template
  - Constraint interaction analysis (which constraints conflict?)

- **`skills/tradeoff-evaluation/SKILL.md`**
  Deeper methodology for evaluating tradeoffs once constraints are known:
  - Decision matrix construction
  - Sensitivity analysis (which tradeoff assumptions matter most?)
  - Reversibility assessment
  - Second-order effect tracing
  - "What would have to be true for this to be the wrong choice?"

- **Evaluate whether constraint tracking needs a tool**
  Can the agent track constraints through conversation context alone, or does
  it need a structured data store? If conversation context is sufficient
  (likely for single-session design work), skills are enough. If constraints
  need to persist across sessions or be validated programmatically, we need
  a tool.

### Testing

Use the constraint discovery skill during a design session and verify:
- The agent identifies constraints systematically (not just the obvious ones)
- Conflicting constraints are surfaced
- Tradeoff evaluation produces genuine analysis, not just pros/cons lists

### Done When

Constraint management is an explicit, structured part of the design process
rather than something that happens ad-hoc.

---

## Phase 7: Design Modeling (Experimental)
_Week 3+. Deliverable: early experiments in design simulation._

This is the most speculative phase, addressing the question from investigation.md:
can we create models that proposed designs can be tested against before full
implementation?

### Tasks

- **Research: what representation works?**
  Explore what format captures enough about a system to be useful for
  simulation without being as expensive as building it:
  - Component diagrams (mermaid, dot-viz) -- visual but not executable
  - Interface contracts (OpenAPI, protobuf) -- precise but narrow
  - State machines -- executable for workflow-heavy systems
  - Dependency graphs -- useful for coupling analysis
  - Data flow diagrams -- useful for throughput analysis
  - Something new? An "architecture description language" that captures
    components, interfaces, constraints, and expected behaviors?

- **Experiment: system-type models**
  Can we encode a "web service model" or "event-driven model" that captures
  the expected components, interactions, and constraints for that system type?
  If so, proposed designs could be compared against the model to find gaps
  (missing observability, no circuit breakers, no backpressure handling).

- **Experiment: design-vs-codebase comparison**
  Given a design document and an existing codebase, can the agent identify
  where the implementation has drifted from the design? This may require a
  tool that maintains a structured design model and compares it against
  actual code structure.

### Testing

This phase is explicitly experimental. Success is learning what works, not
shipping a finished product. Document findings for future work.

### Done When

We have a clear picture of what design modeling approaches are tractable with
current LLM capabilities and which require custom tooling.

---

## Summary Timeline

| Phase | When | Mechanism | Deliverable |
|-------|------|-----------|-------------|
| 0: Skeleton | Day 1 AM | Bundle | Running bundle on foundation |
| 1: Content | Day 1-2 | Context files | Better design output immediately |
| 2: Skills | Days 2-4 | Skills | On-demand design knowledge |
| 3: Mode | Days 3-5 | Mode | Structured /design workflow |
| 4: Agents | Days 4-7 | Agents | Specialist design delegation |
| 5: Recipes | Week 2a | Recipes | Repeatable design workflows |
| 6: Constraints | Week 2b | Skills (maybe tool) | Explicit constraint management |
| 7: Modeling | Week 3+ | Experimental | Design simulation experiments |

Phases overlap intentionally. Content and skills work can happen in parallel.
Mode and agent work build on each other. Each phase is independently valuable
-- if we stop after Phase 3, we still have a useful design bundle.

## What Success Looks Like

After Phase 4 (end of week 1), a user should be able to:

1. Start a session with our bundle
2. Say "help me design [system X]" and get suggested into /design mode
3. Experience a structured design conversation: system modeling, questions one
   at a time, multiple alternatives with tradeoff analysis, section-by-section
   validation
4. Get adversarial review from multiple perspectives
5. Receive a well-structured design document
6. Optionally transition to superpowers for implementation

After Phase 5 (end of week 2), they can also:

7. Run a recipe to get architectural understanding of an existing codebase
8. Run a recipe for multi-perspective architecture review
9. Track and evaluate design constraints explicitly

## Open Questions

- **Superpowers interop**: How do our `allowed_transitions` interact with
  superpowers modes? Should /design -> /brainstorm be a supported flow?
  (Likely yes, but needs testing with both bundles composed.)

- **System type detection**: Can the agent reliably classify what kind of system
  it's looking at, and automatically load the right system-type skill? Or should
  this be user-directed?

- **Design persistence**: Should design artifacts (constraint lists, system
  models, ADRs) persist across sessions? If so, how? AGENTS.md? A dedicated
  file? A tool with storage?

- **Scope boundary with zen-architect**: Where exactly does system-level design
  end and module-level design begin? The intent is complementary, but the
  handoff protocol needs to be defined.

- **Testing methodology**: How do we objectively measure "better design output"?
  Rubric-based evaluation? Side-by-side comparison? User feedback? We should
  define this before Phase 1 testing.

## References

- `agentic-system-design.md` -- The thesis: five upgrades for systems-thinking agents
- `investigation.md` -- Original feature list and goals
- `docs/bundle-composition-strategy.md` -- Include foundation, replace design content
- `docs/amplifier-facilities/` -- Research on each Amplifier extension mechanism
- `related-projects/` -- Cloned repos for code-level investigation
