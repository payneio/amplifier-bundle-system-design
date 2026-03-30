# Superpowers: Development Methodology Bundle

## What It Is

Superpowers is Amplifier's opinionated software development methodology bundle.
It provides a complete end-to-end workflow (brainstorm -> plan -> execute -> verify
-> finish) through 6 interactive modes, 5 specialized agents, 7 recipes, extensive
context documents, and a behavior YAML that wires everything together.

This is the most relevant existing bundle for our system design work because it
solves a structurally similar problem: how to guide an agent through a multi-phase
creative/analytical process with human checkpoints.

## How It Works

### Philosophy (7 Core Principles)

1. TDD is non-negotiable (RED -> GREEN -> REFACTOR)
2. Systematic over ad-hoc (root cause before fixes)
3. Evidence over claims (gate function: identify -> run -> read -> verify -> claim)
4. Complexity reduction as primary goal (YAGNI ruthlessly)
5. Structured planning before implementation
6. Isolation for safety (git worktrees)
7. Human checkpoints at critical points

### The Two Tracks

**Interactive track (modes)**: User steers, agent suggests mode transitions.
```
/brainstorm -> /write-plan -> /execute-plan -> /verify -> /finish
                                   |
                              /debug (off-ramp)
```

**Automated track (recipes)**: Full development cycle recipe with approval gates.

### The Hybrid Pattern (Key Innovation)

Each mode separates conversation from artifact creation:
- **Main agent owns conversation**: Questions, exploration, tradeoff discussion
- **Specialist agents own artifacts**: Design docs, plans, implementations
- **Write tools are blocked in modes**: Forces delegation to specialists

This prevents premature implementation and ensures human validation at each phase.

### Deep Dive: /brainstorm Mode

**Tool policies**: Read-only + delegate + recipes (write_file/edit_file BLOCKED)

**5-Phase Process**:
1. **Understand context** -- read code, existing designs, understand what exists
2. **Ask questions** -- ONE question per message, prefer multiple-choice
3. **Explore approaches** -- 2-3 options with tradeoffs, lead with recommendation
4. **Present design** -- section-by-section (200-300 words each), validate each
5. **Delegate document** -- MANDATORY delegation to brainstormer agent

**Hard gate**: Cannot delegate document creation until design is validated
section-by-section by the user.

**Anti-rationalization table**: Specific rebuttals for 8 common shortcuts (e.g.,
"I already know what to build" -> Assumptions kill designs. Follow the phases.)

### The Brainstormer Agent

Pure artifact writer. Receives validated design from delegation, structures it
into markdown document. Uses `model_role: [reasoning, general]`. Has write tools
(which the mode blocks from the main agent). Does NOT make decisions -- all
decisions were made during the brainstorm conversation.

Template: Goal -> Background -> Approach -> Architecture -> Components ->
Data Flow -> Error Handling -> Testing Strategy -> Open Questions

### The Two-Stage Review Pattern

After each implementation task, two separate reviews:
1. **Spec compliance** (spec-reviewer agent): Does it match the spec?
2. **Code quality** (code-quality-reviewer agent): Is it well-built?

Both must pass. Order matters -- spec first, quality second.

### The Full Development Cycle Recipe

440-line staged recipe composing all phases:
- Stage 1: Design (brainstorm + save) -> APPROVAL GATE 1
- Stage 2: Planning (create plan + save) -> APPROVAL GATE 2
- Stage 3: Implementation (worktree + SDD + verify) -> APPROVAL GATE 3
- Stage 4: Finish (merge/PR/keep/discard based on approval message)

### Methodology Calibration

Not every task needs the full pipeline:
- New multi-file feature -> full cycle
- Bug fix -> /debug -> /verify -> /finish
- Small change (<20 lines) -> make change, then /verify
- Documentation only -> no mode needed

### Key Implementation Files

- `bundle.md` -- Root definition
- `behaviors/superpowers-methodology.yaml` -- Core wiring (hooks, tools, agents, context)
- `modes/brainstorm.md` -- 202-line design exploration mode
- `agents/brainstormer.md` -- Design document writer
- `agents/implementer.md` -- TDD task implementer
- `agents/spec-reviewer.md` -- Spec compliance reviewer
- `agents/code-quality-reviewer.md` -- Quality reviewer
- `recipes/superpowers-full-development-cycle.yaml` -- End-to-end recipe
- `recipes/subagent-driven-development.yaml` -- Foreach + review loops
- `context/philosophy.md` -- 7 core principles
- `context/instructions.md` -- Standing orders + mode recommendation

## Relevance to System Design Bundle

Superpowers is our primary template. It demonstrates how to build a complete
methodology framework using Amplifier's extension mechanisms. Here are the
patterns we should adapt:

### Patterns to Adopt

1. **The hybrid pattern** -- conversation in mode, artifacts via agents. Our
   design exploration should follow this: interactive design discussion with the
   main agent, final design doc written by a specialist agent.

2. **Section-by-section validation** -- Present design decisions incrementally
   and validate each before proceeding. Don't dump the entire architecture in one
   message.

3. **Tool policy enforcement** -- Block writes during design exploration. This
   prevents the agent from jumping to implementation before the design is
   validated.

4. **Anti-rationalization tables** -- Build tables for common design shortcuts.
   These are remarkably effective at preventing the agent from taking shortcuts.

5. **Standing orders with auto-detection** -- Before every response, check if a
   mode applies. "If there is even a 1% chance a mode applies, suggest it."

6. **Methodology calibration** -- Match the depth of the design process to the
   complexity of the task. Not every change needs a full architecture review.

7. **Two-stage review** -- After producing a design, review for completeness
   first, then quality. Separating concerns improves both.

8. **Gate functions** -- Before claiming design is complete: identify proof, run
   verification, read results, verify claim. Evidence before assertions.

### Patterns to Extend

1. **Multiscale reasoning** -- Superpowers doesn't explicitly force multiscale
   thinking (principle, structural, operational, evolutionary). Our design bundle
   should make this mandatory.

2. **Tradeoff analysis framework** -- Superpowers mentions YAGNI and simplicity
   but doesn't have a structured tradeoff analysis methodology. Our bundle should
   include systematic comparison across dimensions (latency, complexity,
   reliability, cost, security, scalability, reversibility, organizational fit).

3. **Multiple design alternatives** -- Superpowers' brainstorm mode asks for 2-3
   approaches. We should formalize this: always generate simplest viable, most
   scalable, and most robust alternatives, then force a reasoned recommendation.

4. **Adversarial review perspectives** -- Superpowers has spec review and quality
   review. We should add multi-perspective adversarial review: SRE, security
   reviewer, staff engineer, finance owner, operator.

5. **Causal reasoning** -- Explicitly require tracing propagation: if X changes,
   what breaks? What is coupled that appears independent? Where are hidden
   dependencies?

6. **Design simulation** -- Ask for sequence diagrams, dependency graphs, state
   transitions, failure injection scenarios. Architecture quality rises when
   outputs become mechanistic.

### What NOT to Copy

- TDD-specific enforcement (not relevant to pure design work)
- Git worktree management (design doesn't need isolated branches)
- The implementation pipeline (implementer -> spec-review -> quality-review)
  -- though we may want our own design review pipeline

### Bundle Composition Strategy

Our bundle should be **composable with superpowers**, not a replacement. A user
working on a new feature might:
1. Start in our `/design` mode to explore the architecture
2. Transition to superpowers `/brainstorm` for implementation details
3. Then through the superpowers pipeline for implementation

This means our `allowed_transitions` should include superpowers modes, and
vice versa.
