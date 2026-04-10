---
name: systems-design-methodology
description: "Use when the /systems-design mode is active. 8-phase structured design methodology -- problem framing, constraints, candidate architectures, tradeoff analysis, risk review, refinement, migration planning, and documentation. Governs conversation flow, delegation patterns, and user validation checkpoints."
---

# System Design Methodology

Companion skill for the `/systems-design` mode. The mode gates tools; this skill governs behavior.

## Core Rule

**You handle the CONVERSATION. Agents handle the ANALYSIS.**

You guide the user through design phases, validate understanding at each step, and delegate analytical work to `system-design-intelligence:systems-architect`. The architect does the system-level reasoning (it runs on a `reasoning`-role model with design methodology context). You present its output to the user, collect feedback, and feed that feedback into the next delegation.

## Phase Flow

Progress through these phases in order. Each phase ends with explicit user validation before moving on. You may revisit earlier phases if the user's feedback reveals gaps.

### Phase 1: Problem Framing

Gather the user's initial description, then delegate to the architect to build the system map:

```
delegate(
  agent="system-design-intelligence:systems-architect",
  instruction="ANALYZE mode. Build a system map for: [user's description].
    Produce: goals, constraints, actors, interfaces, failure modes, time horizons.
    Do NOT propose solutions -- map the problem only.",
  context_depth="recent"
)
```

Present the architect's system map to the user. Ask: **"Does this capture the problem correctly? What am I missing?"**

Do NOT proceed until the user validates the problem framing. If they correct the map, re-delegate with the corrections.

### Phase 2: Constraints and Assumptions

Surface everything assumed but not stated:

- Scale expectations (users, requests/sec, data volume)
- Team capabilities and size
- Budget and timeline constraints
- Existing systems that must be integrated
- Regulatory or compliance requirements

Present as a numbered list of explicit assumptions. Ask: **"Which of these are wrong? What constraints am I missing?"**

### Phase 3: Candidate Architectures

Delegate to the architect to generate candidates using the validated system map and constraints:

```
delegate(
  agent="system-design-intelligence:systems-architect",
  instruction="DESIGN mode. Using this validated system map and constraints:
    [system map from Phase 1, with user corrections]
    [constraints and assumptions from Phase 2, with user corrections]
    Generate 3 candidate architectures:
    1. Simplest viable -- minimum design meeting core requirements
    2. Most scalable -- optimized for growth
    3. Most robust -- optimized for reliability and operational simplicity
    For each: components, boundaries, data flows, technology choices, what it optimizes for.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's candidates to the user. Ask: **"Which direction feels right? Should we explore any of these deeper?"**

Load the `architecture-primitives` skill if pattern selection is unclear.

### Phase 4: Tradeoff Analysis

Delegate to the architect to evaluate the user's preferred candidates against the 8-dimension tradeoff frame:

```
delegate(
  agent="system-design-intelligence:systems-architect",
  instruction="DESIGN mode -- tradeoff analysis only.
    Evaluate these candidates against the 8-dimension tradeoff frame:
    [candidates the user wants compared]
    User's preferred direction: [if stated]
    Produce the filled comparison matrix.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's comparison matrix to the user. Ask: **"Do these ratings match your understanding? Are any dimensions more important than I've weighted?"**

Load the `tradeoff-analysis` skill for deeper methodology if the tradeoffs are contested or unclear.

### Phase 5: Risks and Failure Modes

For the leading candidate, identify:
- Critical failure modes and blast radius
- Single points of failure
- Scaling bottlenecks
- Operational complexity
- Security surface

If the design warrants deep adversarial review, delegate to `system-design-intelligence:systems-design-critic` or suggest `/adversarial-review`.

Present risks ranked by severity. Ask: **"Which of these risks are acceptable? Which need mitigation in the design?"**

### Phase 6: Design Refinement

Delegate to the architect to incorporate the user's risk feedback:

```
delegate(
  agent="system-design-intelligence:systems-architect",
  instruction="DESIGN mode -- refinement pass.
    Current architecture: [leading candidate from Phase 3/4]
    User feedback from risk review:
    - Unacceptable risks requiring mitigation: [list]
    - Accepted limitations: [list]
    - Priority adjustments: [list]
    Produce a refined architecture incorporating these changes.",
  context_depth="recent",
  context_scope="agents"
)
```

Present the architect's refined design to the user. Ask: **"Is this the design you want to proceed with?"**

### Phase 7: Migration and Success Metrics

If this replaces or modifies an existing system:
- Migration strategy (incremental vs big-bang)
- Rollback plan
- Success metrics and monitoring

If greenfield:
- Phased rollout plan
- Success metrics and thresholds
- What signals indicate the design is failing

### Phase 8: Document the Design

When the user approves the design, delegate to `system-design-intelligence:systems-design-writer`:

```
delegate(
  agent="system-design-intelligence:systems-design-writer",
  instruction="Write the design document for [topic]. Include: [summary of all validated sections]",
  context_depth="all",
  context_scope="agents"
)
```

Pass ALL validated content from the conversation. The writer structures it -- it does not make decisions.

## Skills Available Per Phase

| Skill | When to load |
|-------|-------------|
| `architecture-primitives` | Phase 3 -- selecting patterns for candidates |
| `tradeoff-analysis` | Phase 4 -- detailed tradeoff methodology |
| `adversarial-review` | Phase 5 -- parallel 5-perspective stress test |
| `system-type-web-service` | Phase 3 -- when designing web services or APIs |
| `system-type-event-driven` | Phase 3 -- when designing event-driven or message-based systems |

## The Catalytic Question

At the end of every design, ask:

> **"What would have to be true for this to be the wrong choice?"**

This surfaces hidden assumptions and identifies the monitoring signals that tell you the design is failing.
