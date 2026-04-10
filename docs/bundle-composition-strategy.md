# Bundle Composition Strategy: Include Foundation or Build Clean?

## Recommendation: Include Foundation for Infrastructure, Replace Design Content

After surveying every design-related element in the foundation bundle at the code
level, the recommendation is a **hybrid approach**: include foundation as a base
for its infrastructure, but replace the design-related content rather than
inheriting it.

The reasoning comes down to what foundation actually loads and where.

## What Foundation Actually Loads (and Where)

Foundation has a deliberate two-tier architecture:

**ROOT session** (~11.5K tokens, always present): Orchestration behavior --
how to delegate, multi-agent patterns, tool selection. Almost no design
philosophy. The ROOT teaches the agent to be a coordinator, not a designer.

**AGENT sessions** (~24K tokens for zen-architect): All the actual design
philosophy lives here -- loaded via @mentions when agents are spawned. The
ROOT never pays for this content.

This means including foundation does NOT inject its design opinions into our
root session. zen-architect's Wabi-sabi philosophy, the Amplifier-specific
KERNEL_PHILOSOPHY, etc. only appear when someone delegates to zen-architect.

## The Decision Matrix

### Infrastructure We Need (INCLUDE from Foundation)

These are non-design infrastructure elements we'd have to rebuild from scratch:

- Session orchestrator (loop-streaming) and context manager (context-simple)
- Core tools: filesystem, bash, web, search
- Hooks: logging, streaming-ui, redaction, status-context
- The delegate tool and agent spawning infrastructure
- The skills tool and skill discovery system
- The recipes tool
- The modes infrastructure (hooks-mode, tool-mode)

Building these from scratch would be weeks of work for zero design value.

### Design-Related Elements in ROOT Context

| Element | Tokens | Design Value | Amplifier-Specific? | Action |
|---------|--------|-------------|---------------------|--------|
| delegation-instructions.md | 2,900 | High (orchestrator pattern) | 50% (agent names) | INCLUDE, rewrite agent names |
| multi-agent-patterns.md | 1,750 | High (dispatch patterns) | 30% (agent names) | INCLUDE, rewrite agent names |
| Incremental Validation Protocol | 500 | High (universal) | 10% | INCLUDE as-is |
| "Respect User Time" principle | 200 | High (universal) | 0% | INCLUDE as-is |
| "Professional Objectivity" | 150 | High (universal) | 0% | INCLUDE as-is |
| AWARENESS_INDEX.md | 1,400 | None | 95% | EXCLUDE |
| bundle-awareness.md | 425 | None | 100% | EXCLUDE |
| Amplifier identity preamble | 900 | None | 100% | REPLACE |
| Cache management, git format | 1,500 | None | 100% | EXCLUDE |

**Net: ~5.5K of the 11.5K ROOT tokens are design-valuable and should stay.**

### Design-Related Elements in AGENT Context (zen-architect's @mentions)

These ONLY load when zen-architect is spawned, NOT in our root session:

| File | Tokens | Universally Applicable? | Action |
|------|--------|------------------------|--------|
| IMPLEMENTATION_PHILOSOPHY.md | 4,000 | 70% (core philosophy, decision framework) | EXTRACT good parts into our own files |
| MODULAR_DESIGN_PHILOSOPHY.md | 1,100 | 80% (bricks & studs) | INCLUDE as-is (best token/value) |
| KERNEL_PHILOSOPHY.md | 2,000 | 60% (mechanism vs policy, 12 tenets) | EXTRACT tenets, drop Amplifier governance |
| LANGUAGE_PHILOSOPHY.md | 2,000 | 70% (verification spectrum, AI-first) | INCLUDE as-is |
| PROBLEM_SOLVING_PHILOSOPHY.md | 700 | 95% (investigate before act) | INCLUDE as-is |
| ISSUE_HANDLING.md | 8,000 | 50% (7-phase workflow, but bloated) | EXTRACT ~2K of universal process |

**These don't load in our root session, so they don't contaminate our design
context.** But they DO shape how zen-architect behaves when we delegate to it.

## The Concrete Proposal

### Bundle Structure

```yaml
---
bundle:
  name: systems-design
  version: 0.1.0
  description: Systems design capabilities for agentic development

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
---

# System Design Intelligence

@systems-design:context/system-design-principles.md
@systems-design:context/instructions.md

---

@foundation:context/shared/common-system-base.md
```

### What This Gets Us

**From foundation (inherited, zero effort):**
- All tools, providers, orchestrator, hooks, streaming
- The delegate tool + agent spawning
- Skills and recipes infrastructure
- Modes infrastructure
- Foundation agents (explorer, file-ops, git-ops, web-research, etc.)
- zen-architect (available but with its own context, not ours)

**From our bundle (our additions):**
- Our own context files (system design principles, structured templates)
- Our own agents (systems architect, design critic, constraint analyst)
- Our own modes (/design, /systems-design-review)
- Our own skills (system types, tradeoff analysis, architecture primitives)
- Our own recipes (architecture review, design exploration)
- Our instruction (replaces foundation's instruction via composition)

### Key Design Decisions

**1. Keep zen-architect available, don't replace it.**

zen-architect is good at module-level architecture within a codebase. Our agents
operate at the system level -- service boundaries, technology selection, non-
functional requirements. These are complementary scopes. A user could:
- Use our `/design` mode for system-level architecture
- Delegate to our systems-architect agent for high-level design
- Then delegate to zen-architect for module-level specification within that design

zen-architect's Amplifier-specific philosophy files load in ITS context, not ours.
They don't pollute our design conversation.

**2. Replace the root instruction, keep infrastructure context.**

Bundle composition means our instruction replaces foundation's. We control the
system prompt entirely. But foundation's behaviors still compose their context
(delegation-instructions.md, multi-agent-patterns.md) because they use
`context.include` which accumulates.

This is fine -- those files teach orchestration patterns (how to delegate, when
to use parallel agents) which are valuable regardless of design methodology.

**3. Add our own context files rather than modifying foundation's.**

Foundation's philosophy files (IMPLEMENTATION_PHILOSOPHY, KERNEL_PHILOSOPHY, etc.)
contain good material mixed with Amplifier-specific content. Rather than forking
and editing them, we'll create our own context files that incorporate the
universally-applicable principles alongside our system design content.

This avoids maintenance burden of tracking foundation's philosophy file changes.

**4. Don't include superpowers initially.**

Superpowers adds ~6K tokens of methodology context (TDD, standing orders) and
6 modes focused on implementation workflow. For our experiments:
- We'll build our own design-focused modes
- We'll study superpowers' patterns but implement our own versions
- Users who want both can compose: `includes: [foundation, superpowers, system-design]`

Later, we should ensure our `allowed_transitions` work with superpowers modes
so users can flow between design and implementation.

## Foundation Agents: Which Ones to Keep Available

All foundation agents are "available" (in the agents registry) but only consume
tokens when actually spawned. So "keeping" them costs nothing.

### Actively Useful for Design Work

| Agent | Why Useful |
|-------|-----------|
| explorer | Codebase reconnaissance for understanding existing systems |
| web-research | Research technologies, patterns, prior art |
| security-guardian | Security perspective on proposed designs |
| zen-architect | Module-level architecture (complementary scope) |

### Available but Not Design-Specific

| Agent | Status |
|-------|--------|
| bug-hunter | Available for debugging, not design-relevant |
| modular-builder | Implementation, not design |
| file-ops, git-ops | Utility, keep for infrastructure |
| test-coverage | Implementation concern |

### Our New Agents (to add)

| Agent | Role | model_role |
|-------|------|-----------|
| systems-architect | System-level design, topology, technology selection | [reasoning, general] |
| systems-design-critic | Multi-perspective adversarial review | [critique, reasoning, general] |
| constraint-analyst | Constraint discovery and tradeoff evaluation | [reasoning, general] |
| codebase-surveyor | Architecture-focused codebase understanding | general |

## What This Looks Like in Practice

A user working with our bundle would experience:

1. Start a session -- gets our system design principles in context, plus
   foundation's orchestration infrastructure
2. Say "help me design the authentication system" -- our standing orders detect
   this and suggest `/design` mode
3. In `/design` mode -- write tools blocked, agent follows our structured design
   process (model system, multiscale reasoning, tradeoff analysis, alternatives)
4. Agent delegates to `systems-architect` for deep analysis, `explorer` for
   codebase survey, `systems-design-critic` for adversarial review
5. When design is validated section-by-section -- delegates to a systems-design-writer
   agent to produce the artifact (following superpowers' hybrid pattern)
6. User transitions to `/brainstorm` or `/execute-plan` (superpowers, if composed)
   for implementation details

## Token Budget Estimate

| Source | Tokens | Content |
|--------|--------|---------|
| Foundation infrastructure context | ~5,500 | Orchestration, delegation, validation |
| Our design principles | ~2,000 | Core system design methodology |
| Our instructions/standing orders | ~1,500 | Mode detection, process guidance |
| Skills (on-demand) | 0 (until loaded) | System types, tradeoffs, primitives |
| Agent context (on-demand) | 0 (until spawned) | Heavy design reference docs |
| **Total root session** | **~9,000** | Lean, focused on design orchestration |
