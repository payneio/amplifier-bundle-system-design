# System Design Instructions

<STANDING-ORDER>

## Detect Design Requests

When the user asks about system design, architecture, technology selection, or system evaluation, suggest the appropriate mode or mechanism:

| User Intent | Suggest |
|-------------|---------|
| "Design a system for..." / "How should we architect..." | `/systems-design` mode |
| "Review this architecture..." / "Evaluate our system..." | `/systems-design-review` mode |
| "Compare X vs Y for our use case..." | `/systems-design` mode (Phase 4: tradeoff analysis) |
| Quick design question (< 5 min) | Answer directly, no mode needed |
| "Run an architecture review of this codebase" | `systems-design-review` recipe |
| "Help me understand this codebase" | `codebase-understanding` recipe |

## Mode Entry

When activating a mode, load its companion skill immediately:

| Mode | Companion Skill |
|------|----------------|
| `/systems-design` | `systems-design-methodology` |
| `/systems-design-review` | `systems-design-review-methodology` |

The mode gates tools. The companion skill governs behavior.

## Methodology Calibration

Not every design question needs the full pipeline. Match the approach to the scope:

| Scope | Approach |
|-------|----------|
| **Quick opinion** (technology choice, pattern question) | Answer directly. Load `tradeoff-analysis` or `architecture-primitives` skill if helpful. |
| **Focused design** (single component, one decision) | `/systems-design` mode, but skip to the relevant phase. |
| **Full system design** (new system, major feature) | `/systems-design` mode, all phases. Or `systems-design-cycle` recipe for hands-off with approval gates. |
| **Existing system review** | `/systems-design-review` mode or `systems-design-review` recipe. |
| **Codebase understanding** | `codebase-understanding` recipe. |

## Available Mechanisms

**Modes:**
- `/systems-design` -- structured design exploration with section-by-section user validation
- `/systems-design-review` -- evaluate existing designs against codebase reality

**Recipes:**
- `systems-design-cycle` -- full design pipeline with approval gates (problem framing, candidates, risk, refinement, documentation)
- `systems-design-review` -- staged multi-perspective review with approval gates
- `systems-design-exploration` -- parallel 3-archetype generation with tradeoff evaluation
- `codebase-understanding` -- survey, boundaries, flows, architectural overview
- `bundle-behavioral-spec` -- generate behavioral specification for an Amplifier bundle

**Skills (methodology):**
- `systems-design-methodology` -- companion skill for `/systems-design` mode (8 phases)
- `systems-design-review-methodology` -- companion skill for `/systems-design-review` mode (6 steps)

**Skills (domain):**
- `adversarial-review` -- parallel 5-perspective stress test (fork skill)
- `tradeoff-analysis` -- 8-dimension comparison frame and methodology
- `architecture-primitives` -- catalog of patterns with when-right and when-wrong
- `system-type-web-service` -- domain patterns for web services
- `system-type-event-driven` -- domain patterns for event-driven systems

**Agents:**
- `systems-architect` -- system-level design (ANALYZE, DESIGN, ASSESS modes)
- `systems-design-critic` -- adversarial review from 5 perspectives (for recipe/delegation use)
- `systems-design-writer` -- writes validated designs to documents

</STANDING-ORDER>
