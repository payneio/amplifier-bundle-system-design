_Better systems design bundle: new and existing codebases_

Create a `system-design-intelligence` bundle. Thin bundle on foundation -- get infrastructure for free, replace instruction and design content with our own. zen-architect stays available for module-level work; our bundle operates at system level above it.

Work is organized into checkpoints. Each ships something usable.

## Checkpoint 1: Core design content

**Context files** loaded into the root session that establish design methodology:

- `context/system-design-principles.md` -- Core principles: model the system before solving (goals, constraints, actors, interfaces, feedback loops, failure modes); multiscale reasoning (principle, structural, operational, evolutionary layers); tradeoff analysis over best-practice mimicry; causal reasoning (first/second-order effects, unintended consequences); simplicity as constraint not aesthetic.
- `context/structured-design-template.md` -- Default output template for nontrivial problems: problem framing, explicit assumptions, system boundaries, components, data/control flows, risks, tradeoffs, recommended design, simplest credible alternative, migration plan, success metrics.
- `context/instructions.md` -- Standing orders: detect design requests and suggest /design mode, generate at least 3 architectures (simplest viable, most scalable, most robust), always answer "what does this design optimize for and what does it sacrifice?"

**Test**: Run against real design prompts. Output should be visibly more structured -- explicit assumptions, multiple alternatives, tradeoff analysis, failure modes.

## Checkpoint 2: On-demand design knowledge via skills

**Skills** for specialized knowledge that shouldn't cost tokens every turn:

- `skills/tradeoff-analysis/` -- The fixed comparison frame (latency, complexity, reliability, cost, security, scalability, reversibility, organizational fit). Tradeoff matrix template. Common tradeoff patterns.
- `skills/adversarial-review/` -- Fork skill (`context: fork`, `model_role: critique`). Spawns a subagent that reviews from 5 perspectives: SRE, security reviewer, staff engineer, finance owner, operator. Produces unified risk assessment.
- `skills/architecture-primitives/` -- Catalog of reusable abstractions (boundaries, contracts, state machines, queues, caches, idempotency, backpressure, consistency models, etc.) with guidance on when each is appropriate AND when it's wrong.
- `skills/system-type-web-service/` -- Domain patterns, scaling approaches, data layer, observability, failure modes, anti-patterns for web service architecture.
- `skills/system-type-event-driven/` -- Pub/sub, event sourcing, CQRS, saga, ordering/delivery guarantees, schema evolution.

**Test**: Skills appear in visibility hook. Agent loads them during design conversations. Adversarial review produces genuinely distinct perspectives.

## Checkpoint 3: Structured design workflow via /system-design mode

**Mode** following the superpowers hybrid pattern (conversation in mode, artifacts via agent delegation):

- `modes/design.md` -- Blocks write tools. Safe: read_file, glob, grep, web tools, delegate, load_skill, LSP. Phased process: (1) understand context, (2) model the system, (3) ask questions one at a time, (4) explore 3+ alternatives with tradeoffs, (5) evaluate against fixed frame, (6) present section-by-section with user validation, (7) adversarial review, (8) delegate artifact creation. Anti-rationalization table for design shortcuts. Transitions to: design-review, brainstorm, write-plan.
- `modes/design-review.md` -- Read-only evaluation mode. Multi-perspective review checklist: design integrity, constraint satisfaction, failure modes, DX, implementation viability, simplicity.

**Test**: /design blocks writes, enforces phased process, questions come one at a time, alternatives are generated, anti-rationalization prevents skipping steps.

## Checkpoint 4: Specialist design agents

**Agents** that carry heavy design reference docs in their own context (context sink pattern):

- `agents/systems-architect.md` -- `model_role: [reasoning, general]`. No bash (design-only). Three modes: ANALYZE (system modeling, boundary identification, constraint discovery), DESIGN (multi-alternative generation, tradeoff analysis, recommendation), ASSESS (evaluate existing systems). Produces design documents, not implementation specs. Delegates to zen-architect for module-level work.
- `agents/design-critic.md` -- `model_role: [critique, reasoning, general]`. Read-only. Reviews from SRE/security/engineering/finance/operator perspectives. Finds flaws; does NOT generate designs.
- `agents/design-writer.md` -- `model_role: [writing, general]`. Has write access. Pure artifact writer (like superpowers brainstormer). Receives validated design, structures into document. Does not make design decisions.

**Test**: Delegation chain works end-to-end from /design mode through all three agents.

## Checkpoint 5: Repeatable design workflows via recipes

**Recipes** for multi-step design processes:

- `recipes/architecture-review.yaml` -- Staged recipe with approval gates. Stage 1: explorer surveys codebase, systems-architect identifies boundaries. Stage 2: parallel analysis from multiple perspectives (foreach), design-critic synthesizes. Stage 3: design-writer produces assessment.
- `recipes/design-exploration.yaml` -- Classify system type, load relevant skill, generate 3 architectures in parallel (foreach), evaluate each against tradeoff framework, synthesize comparison matrix.
- `recipes/codebase-understanding.yaml` -- Survey structure, identify boundaries and coupling, map data/control flows, assess complexity distribution, produce architectural overview.

**Test**: Run against a real codebase (amplifier-core or amplifier-foundation). Parallel perspectives produce distinct insights. Approval gates pause at right points.

## Checkpoint 6: Constraint management

**Skills** (and potentially a tool if structured persistence is needed):

- `skills/constraint-discovery/` -- Systematic identification by category (technical, organizational, regulatory, timeline, resource, compatibility, operational). Constraint interaction analysis for conflicts.
- `skills/tradeoff-evaluation/` -- Decision matrix construction, sensitivity analysis, reversibility assessment, second-order effect tracing. "What would have to be true for this to be the wrong choice?"
- Evaluate whether constraints need a tool for structured tracking or if conversation context is sufficient.

**Test**: Agent identifies constraints systematically, surfaces conflicts, produces genuine tradeoff analysis.

## Checkpoint 7: Design modeling (experimental)

Explore whether proposed designs can be tested against models before full implementation:

- Research what representation captures enough to be useful (component diagrams, interface contracts, state machines, dependency graphs, architecture description language).
- Experiment with system-type models ("web service model", "event-driven model") that encode expected components and constraints so proposed designs can be checked for gaps.
- Experiment with design-vs-codebase drift detection.

This checkpoint is explicitly experimental. Success is learning what's tractable.

## Open questions

- How do our mode transitions interop with superpowers? Users composing both bundles should be able to flow from /design to /brainstorm to /execute-plan.
- Can system type be detected automatically, or is it user-directed?
- Should design artifacts (constraint lists, system models, ADRs) persist across sessions?
- Where exactly does system-level design hand off to zen-architect's module-level design?
- How do we measure "better design output" objectively? Rubric? Side-by-side? User feedback?
