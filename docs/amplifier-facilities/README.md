# Amplifier Extension Facilities: Research Index

Research documents investigating how Amplifier extends agent capabilities and how
each mechanism relates to building a system-design-intelligence bundle.

## Facilities Investigated

| Facility | Weight | File | TL;DR |
|----------|--------|------|-------|
| [Bundles](bundles.md) | Delivery mechanism | bundles.md | Composable config packages. Our bundle structure. |
| [Tools](tools.md) | Heavy | tools.md | LLM-decided capabilities. Custom tools for structured data. |
| [Hooks](hooks.md) | Medium | hooks.md | Code-decided lifecycle observers. Automated design feedback. |
| [Skills](skills.md) | **High leverage** | skills.md | On-demand knowledge. Fastest path to value. |
| [Recipes](recipes.md) | Medium-High | recipes.md | Multi-step workflows. Design process orchestration. |
| [Content](content.md) | **Foundation** | content.md | Always-present context. Core design principles. |
| [Agents](agents.md) | Medium-High | agents.md | Specialist sub-agents. Design experts with dedicated context. |
| [Modes](modes.md) | **High leverage** | modes.md | Runtime overlays. Structured design workflow phases. |
| [Superpowers](superpowers.md) | **Template** | superpowers.md | Development methodology bundle. Our primary pattern reference. |

## Priority Assessment for System Design Bundle

### Start Here (Day 1 Value)

1. **Content files** -- Core system design principles, structured response
   templates, simplicity rubrics. Immediate behavioral improvement with zero
   code. This is the backbone.

2. **Skills** -- System design methodology, system-type guides, tradeoff analysis
   framework, architecture primitives. On-demand knowledge that costs tokens only
   when relevant. Fast to create (just markdown).

3. **A /design mode** -- Following the superpowers hybrid pattern. Block writes,
   enforce structured design exploration, delegate artifacts to a specialist agent.
   Reuses the modes infrastructure that already exists.

### Build Next (Week 1)

4. **Agents** -- Systems architect agent, design critic agent, codebase surveyor
   agent. These carry heavy design reference docs in their own context windows.

5. **Recipes** -- Architecture review recipe, design exploration recipe with
   parallel multi-perspective analysis.

### Consider Later (Based on Experiments)

6. **Hooks** -- Design completeness monitor, constraint violation detector,
   architectural drift detection. These provide automated real-time feedback but
   require Python module development.

7. **Tools** -- Design model tool, tradeoff analysis tool, constraint tracker.
   Only if we find that structured data manipulation is needed beyond what
   skills/agents can provide.

## Key Design Decisions

### Bundle Composition Strategy

Our bundle should be **composable with superpowers**, not a replacement. Users
should be able to:
- Use our design facilities alongside superpowers' implementation workflow
- Transition from our /design mode to superpowers' /brainstorm or /execute-plan
- Use our design agents and skills independently of any mode

### Token Budget

Context files consume tokens every turn. Priority:
- Core design principles: ~2K tokens (always present)
- Detailed methodology: skills (loaded on demand, ~1-5K each)
- Heavy reference docs: agent context sinks (loaded only when agent spawns)

### The Five Upgrades (from agentic-system-design.md)

Each upgrade maps to Amplifier facilities:

| Upgrade | Primary Facility | Supporting Facility |
|---------|-----------------|-------------------|
| 1. Model the system before solving | Content (principles) | Mode (enforce modeling) |
| 2. Force multiscale reasoning | Content (template) | Skill (layer framework) |
| 3. Tradeoff analysis, not mimicry | Skill (methodology) | Agent (critic) |
| 4. Reason causally | Skill (causal framework) | Agent (propagation tracer) |
| 5. Architectural primitives | Skill (primitive catalog) | Content (standing behavior) |

## Source Repositories

Cloned into `../../related-projects/`:

| Repository | Purpose |
|-----------|---------|
| amplifier | Entry point, docs, governance |
| amplifier-core | Kernel, contracts, protocols |
| amplifier-foundation | Bundles, behaviors, examples, agents |
| amplifier-bundle-superpowers | Development methodology (our template) |
| amplifier-bundle-skills | Skills system |
| amplifier-bundle-recipes | Recipe system |
| amplifier-bundle-modes | Modes system |
| amplifier-module-tool-bash | Reference tool implementation |
| amplifier-module-tool-filesystem | Multi-tool module example |
| amplifier-bundle-filesystem | Bundle wrapping tool modules |
