# system-design-intelligence

An Amplifier bundle that provides a structured systems design methodology for agentic development. Produces rigorous architectural output with tradeoff analysis, multiscale reasoning, and failure mode coverage.

## What it does

Adds a `/design` mode, specialist agents, design skills, and multi-step recipes to any Amplifier session. When activated, it guides structured exploration of system architecture before any code is written.

```
amplifier bundle add git+https://github.com/<org>/amplifier-system-design@main --app
```

Or as a behavior (no foundation, for composition into other bundles):

```
amplifier bundle add git+https://github.com/<org>/amplifier-system-design@main#subdirectory=behaviors/system-design.yaml --app
```

## Bundle structure

```
.
├── bundle.md                     # Root bundle (includes foundation + behavior)
├── bundle.dot / bundle.png       # Composition diagram
├── behaviors/
│   └── system-design.yaml        # Wiring layer: hooks, tools, agents, context
├── agents/
│   ├── systems-architect.md      # Deep reasoning (model_role: reasoning)
│   ├── design-critic.md          # Adversarial review (model_role: critique)
│   └── design-writer.md          # Document generation (model_role: writing)
├── context/
│   ├── instructions.md           # Detection + routing standing orders
│   ├── system-design-principles.md  # 6 thinking tools
│   ├── tradeoff-frame.md         # 8-dimension analysis matrix
│   ├── adversarial-perspectives.md  # 5 review lenses
│   └── structured-design-template.md  # Output template
├── modes/
│   ├── system-design.md          # /design — 8-phase exploration
│   └── design-review.md          # /design-review — 6-step evaluation
├── modules/
│   └── hooks-design-context/     # Hook: injects design doc awareness
├── recipes/
│   ├── architecture-review.yaml  # Staged, 2 approval gates
│   ├── design-exploration.yaml   # Parallel 3-archetype generation
│   └── codebase-understanding.yaml  # Sequential survey
├── skills/
│   ├── adversarial-review/       # Fork skill (5 parallel review agents)
│   ├── tradeoff-analysis/        # Inline skill
│   ├── architecture-primitives/  # Inline skill
│   ├── system-type-web-service/  # Inline skill
│   └── system-type-event-driven/ # Inline skill
└── docs/
    ├── amplifier-facilities/     # Reference docs on Amplifier mechanisms
    │   └── agent-mechanisms.md   # How all 7 mechanisms compose
    ├── agentic-system-design.md  # Design methodology reference
    └── bundle-composition-strategy.md
```

## Mechanisms used

This bundle uses all seven Amplifier mechanisms. Each has a specific role:

| Mechanism | Instances | Purpose |
|-----------|-----------|---------|
| **Modes** | `/design`, `/design-review` | Tool policy enforcement during design phases |
| **Agents** | `systems-architect`, `design-critic`, `design-writer` | Isolated sub-sessions with focused model roles |
| **Skills** | 5 (1 fork, 4 inline) | On-demand design expertise |
| **Recipes** | 3 | Multi-step workflows with checkpointing |
| **Hooks** | `hooks-design-context` | Ambient design doc awareness |
| **Tools** | `tool-mode`, `tool-skills` (external) | Mode transitions and skill loading |
| **Content** | 5 context files | Design principles, templates, standing orders |

See `docs/amplifier-facilities/agent-mechanisms.md` for how these mechanisms compose and interact.

## Usage

### Interactive design sessions

Enter design mode to explore a system architecture:

```
/design
```

This constrains tools to read-only, injects design methodology guidance, and walks through 8 phases: scope, prior art, architecture generation (3 archetypes), tradeoff analysis, risk review, decision, documentation, and next steps.

### Design review

Review an existing design document:

```
/design-review
```

Six-step evaluation: read the document, identify claims, stress-test assumptions, analyze tradeoffs, grade coverage, and produce a findings report.

### Recipes

Run multi-step workflows with agent handoffs:

```python
# Architecture review (staged, 2 approval gates)
recipes(operation="execute",
        recipe_path="@system-design-intelligence:recipes/architecture-review.yaml",
        context={"target_path": "src/", "focus_areas": "authentication, caching"})

# Design exploration (parallel 3-archetype generation)
recipes(operation="execute",
        recipe_path="@system-design-intelligence:recipes/design-exploration.yaml",
        context={"problem_statement": "How should we handle user sessions at scale?"})

# Codebase understanding (sequential survey)
recipes(operation="execute",
        recipe_path="@system-design-intelligence:recipes/codebase-understanding.yaml",
        context={"target_path": "src/"})
```

### Skills

Load design expertise on demand:

```
load_skill(skill_name="tradeoff-analysis")
load_skill(skill_name="architecture-primitives")
load_skill(skill_name="adversarial-review")     # Fork: spawns 5 parallel review agents
```

### Agents

Delegate directly to specialist agents:

```python
delegate(agent="system-design-intelligence:systems-architect",
         instruction="Analyze the authentication architecture in src/auth/")

delegate(agent="system-design-intelligence:design-critic",
         instruction="Review this design document for blind spots",
         context_depth="recent")

delegate(agent="system-design-intelligence:design-writer",
         instruction="Write the design document from the analysis above",
         context_scope="agents")
```

## Composition diagram

The `bundle.dot` file contains a DOT graph showing all composition and runtime relationships. Render it:

```bash
dot -Tpng bundle.dot -o bundle.png
```

Or open `dotviewer.html` in a browser to view it interactively.

## How it works

The root `bundle.md` includes `amplifier-foundation` (for tools, agents, session management) and the `system-design` behavior. The behavior wires everything together:

1. **Includes** the `modes` behavior (from `amplifier-bundle-modes`) for mode infrastructure
2. **Registers hooks**: `hooks-mode` (mode enforcement) and `hooks-design-context` (design doc awareness)
3. **Configures tools**: `tool-mode` (agent-initiated mode transitions) and `tool-skills` (pointed at local `skills/` directory)
4. **Declares agents**: Three specialists with different `model_role` values
5. **Injects context**: Design principles, tradeoff frames, adversarial perspectives, templates, and standing orders into the root session

The context files are injected into the root session (~3,770 tokens total). Agents carry their own heavy context via `@mention` references, acting as context sinks. Skills are loaded on demand. Modes inject guidance ephemerally per turn.

## Development

### Adding a new skill

Create a directory under `skills/` with a `SKILL.md` file following the [Agent Skills spec](https://agentskills.io/specification). The `tool-skills` module discovers it automatically.

### Adding a new mode

Create a `.md` file under `modes/` with YAML frontmatter defining tool policies. `hooks-mode` discovers it via the `search_paths` config.

### Adding a new agent

Create a `.md` file under `agents/` with `meta:` frontmatter. Add it to the `agents: include:` list in `behaviors/system-design.yaml`.

### Adding a new recipe

Create a `.yaml` file under `recipes/`. Reference your agents by their namespaced names (`system-design-intelligence:systems-architect`).

### The hook module

`modules/hooks-design-context/` is a Python hook module that scans for `docs/designs/*.md` files and injects their inventory into agent context before every LLM call. To modify:

```bash
cd modules/hooks-design-context
# Edit amplifier_module_hooks_design_context/__init__.py
# Test locally by running Amplifier with a local source override
```

## Documentation

| Document | Description |
|----------|-------------|
| `docs/amplifier-facilities/agent-mechanisms.md` | How Amplifier's 7 mechanisms compose (with architecture diagrams) |
| `docs/agentic-system-design.md` | The design methodology this bundle implements |
| `docs/bundle-composition-strategy.md` | Design decisions behind this bundle's structure |
| `docs/amplifier-facilities/` | Individual reference docs for each mechanism |

## License

MIT