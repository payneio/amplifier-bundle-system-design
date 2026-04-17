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
- `systems-design-methodology` -- companion skill for `/systems-design` mode (9 phases, includes mandatory system classification)
- `systems-design-review-methodology` -- companion skill for `/systems-design-review` mode (7 steps, includes mandatory system classification)

**Skills (domain):**
- `adversarial-review` -- parallel 5-perspective stress test (fork skill)
- `tradeoff-analysis` -- 8-dimension comparison frame and methodology
- `architecture-primitives` -- catalog of patterns with when-right and when-wrong
- `system-type-web-service` -- domain patterns for web services
- `system-type-event-driven` -- domain patterns for event-driven systems

**Skills (system types — additional):**
- `system-type-data-pipeline` -- batch and streaming pipelines, DAG scheduling, data quality, backfill
- `system-type-workflow-orchestration` -- long-running processes, sagas, durable execution, human-in-the-loop
- `system-type-cli-tool` -- CLI tools and developer SDKs, configuration layering, plugin architecture
- `system-type-real-time` -- persistent connections, state sync, CRDTs, presence, fan-out
- `system-type-multi-tenant-saas` -- tenant isolation, noisy neighbor, billing metering, data partitioning
- `system-type-ml-serving` -- model serving, feature stores, training pipelines, LLM patterns
- `system-type-distributed` -- consensus, consistency models, replication, partitioning, failure detection
- `system-type-enterprise-integration` -- legacy modernization, strangler fig, API gateways, data integration
- `system-type-edge-offline` -- offline-first, sync protocols, conflict resolution, constrained resources
- `system-type-spa` -- single-page applications, client-side routing, state management, rendering strategies, PWA
- `system-type-peer-to-peer` -- P2P topologies, NAT traversal, peer discovery, data distribution, Sybil resistance
- `system-type-azure` -- Azure compute, identity (Entra ID), networking, data platform, messaging, deployment, cost management

**Skills (design philosophies):**
- `design-philosophy-linux` -- mechanism vs policy, composability, Unix philosophy as design lens
- `design-philosophy-domain-driven` -- bounded contexts, ubiquitous language, aggregates, context mapping
- `design-philosophy-object-oriented` -- SOLID, composition over inheritance, actor model, design patterns

**Agents:**
- `systems-architect` -- system-level design (ANALYZE, DESIGN, ASSESS modes)
- `systems-design-critic` -- adversarial review from 5 perspectives (for recipe/delegation use)
- `systems-design-writer` -- writes validated designs to documents

</STANDING-ORDER>
