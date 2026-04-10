# The 8-Dimension Tradeoff Frame

Every design decision answers this:

> **"What does this optimize for, and what does it sacrifice?"**

If you cannot answer this clearly for a design, the design is not yet understood.

## The Frame

Evaluate every design alternative against these fixed dimensions. Do not invent new dimensions -- force the analysis into this frame so alternatives are comparable.

| Dimension | Key Question | Watch For |
|-----------|-------------|-----------|
| **Latency** | How fast must it respond? | P50 vs P99 distinction; latency budgets per hop |
| **Complexity** | How many concepts must be held in mind? | Operational complexity vs code complexity -- they diverge |
| **Reliability** | What is the acceptable failure rate? | Partial degradation vs total failure; blast radius |
| **Cost** | What are the resource costs now and at scale? | Cost curves that are linear now but exponential later |
| **Security** | What is the attack surface? | Authentication, authorization, data exposure, supply chain |
| **Scalability** | What grows with usage, time, and org size? | The thing that scales worst is the bottleneck |
| **Reversibility** | How hard is it to undo this decision? | Data model choices are least reversible; API contracts are hard; implementation details are easy |
| **Organizational fit** | Does this match the team's actual ability? | A design the team cannot operate is a failed design |

## How to Apply

1. **Identify the alternatives.** Fewer than 2 means you haven't explored enough. More than 5 means narrow first.
2. **Fill the matrix.** Force every cell to have a rating and a note. Empty cells are unexamined risk.
3. **Identify the dominant tradeoff.** Which 1-2 dimensions most differentiate the options? That is where the real decision lies.
4. **State what you are sacrificing.** The recommendation is incomplete without this.
5. **Ask: "What would have to be true for this to be the wrong choice?"** This surfaces hidden assumptions and identifies monitoring signals.

## Comparison Matrix Template

| Dimension | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Latency | [rating + note] | [rating + note] | [rating + note] |
| Complexity | ... | ... | ... |
| Reliability | ... | ... | ... |
| Cost | ... | ... | ... |
| Security | ... | ... | ... |
| Scalability | ... | ... | ... |
| Reversibility | ... | ... | ... |
| Org fit | ... | ... | ... |
| **Optimizes for** | [1-line summary] | [1-line summary] | [1-line summary] |
| **Sacrifices** | [1-line summary] | [1-line summary] | [1-line summary] |

Use qualitative assessments (good/adequate/poor) with a concrete note explaining why. Numeric scores create false precision.