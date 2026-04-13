# Bundle Developer's Guide to Amplifier Mechanisms

## Introduction

Amplifier exposes [seven composable primitives](mechanisms/README.md) for building agent systems: 

- [modes](mechanisms/modes.md)
- [recipes](mechanisms/recipes.md)
- [skills](mechanisms/skills.md)
- [agents](mechanisms/agents.md)
- [hooks](mechanisms/hooks.md)
- [tools](mechanisms/tools.md)
- [content](mechanisms/content.md)

They overlap by design. The goal is not to pick one, but to assign **clear ownership** and **correct attachment points**, then compose them through **behaviors** — the YAML wiring layer that assembles mechanisms into bundles.

> **Use combinations freely. Avoid duplicated authority.**

## Attachment Points

> **Where does it bind, and how long does it live?**

| Mechanism | Attaches to | Lifetime | State location | Authored as |
|-----------|-------------|----------|----------------|-------------|
| Mode | Session | Togglable, ephemeral re-injection | `session_state["active_mode"]` | `.md` with YAML frontmatter |
| Recipe | Workflow execution | Per-invocation, resumable | `state.json` on disk | `.yaml` |
| Agent | Sub-session | One-shot or resumable | Kernel session (in-memory) | `.md` with YAML frontmatter |
| Skill | Task pattern | On-demand (inline or forked) | None (stateless) or fork session | `SKILL.md` in a directory |
| Hook | Lifecycle event | Session lifetime | Module state + `session_state` | Python module |
| Tool | LLM decision | Session lifetime | Module state | Python module |
| Content | Context window | Per-injection | None (consumed by LLM) | `.md` files |

---

## The Wiring Layer: Behaviors

Behaviors are YAML files that compose mechanisms into reusable capability packages. They are how mechanisms become available in a session.

```yaml
# Example: behaviors/my-feature.yaml
includes:
  - bundle: some-dependency:behaviors/base
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths: ["@my-bundle:modes"]
tools:
  - module: tool-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/tool-mode
    config:
      gate_policy: warn
  - module: tool-skills
    config:
      skills:
        - "@my-bundle:skills"
agents:
  include:
    - my-bundle:agents/specialist
context:
  include:
    - my-bundle:context/instructions.md
```

**Key pattern:** A behavior wires hooks, tools, agents, and context into a single composable unit. Bundles compose behaviors via `includes:`. This is the layer between individual mechanisms and the final bundle.

---

## What Each Mechanism Should Own

| Concern | Primary owner | Why not elsewhere |
|---------|---------------|-------------------|
| Session-wide constraints | **Mode** | Hooks enforce deterministically; skills/recipes can't guarantee session-wide policy |
| Multi-step workflow ordering | **Recipe** | Checkpointing and approval gates require persistent state |
| Task-specific expertise | **Skill** | Portable, discoverable, loadable on demand without sub-session overhead |
| Complex sub-task reasoning | **Agent** | Needs isolated context, own tool surface, potentially different model |
| Guaranteed lifecycle behavior | **Hook** | Fires deterministically, not subject to LLM judgment |
| LLM-decided capabilities | **Tool** | Model chooses when to invoke based on schema |
| Reference knowledge | **Content** | Passive — no execution, just context |

> **Authority Rule:** one concern, one source of truth.

---

## Choosing the Right Mechanism

Ask in order:

1. Must it always apply, regardless of what the LLM decides? **Hook** (code-decided enforcement) or **Mode** (policy overlay)
2. Is it a multi-step process with checkpoints? **Recipe**
3. Is it reusable task knowledge, loadable on demand? **Skill**
4. Does it need external system access? **Tool**
5. Does it need isolated reasoning with its own context? **Agent**
6. Is it just reference information? **Content**

**Distinguishing hooks from modes:** Hooks are Python modules — use them when you need programmatic logic (parse responses, compute values, call APIs on lifecycle events). Modes are declarative `.md` files — use them when you need tool policy tiers and injected guidance without writing code.

**Distinguishing skills from agents:** Inline skills are cheaper (no sub-session overhead) and portable (Agent Skills spec). Fork skills converge with agents but require less infrastructure (a directory vs. a bundle). Use agents when you need: resumable sessions, specific tool composition, or deep context isolation.

---

## Failure Modes (Misplaced Attachment)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| **Policy leakage** (too low) | Safety rules in skills or recipe prompts — inconsistent enforcement | Move to a **mode** with tool policy tiers |
| **Workflow hidden in skills** | Step sequences encoded in skill bodies — brittle, no checkpointing | Move to a **recipe** |
| **Expertise smearing** (too high) | Heuristics duplicated across recipe step prompts | Centralize in a **skill** |
| **Skill hypertrophy** | A skill that spawns agents, manages state, enforces policy | Split: policy to mode, workflow to recipe, expertise stays in skill |
| **Capability fiction** | APIs described in context but not exposed as tools | Wire as a **tool** (or MCP resource) |
| **Cognitive overload** | Single agent prompt does everything | Decompose into **delegated agents** with focused concerns |
| **Knowledge entanglement** | Docs copy-pasted into agent prompts, skills, and recipe steps | Centralize as **content** files, reference via `@mention` |
| **Missing hook, using mode** | You need programmatic logic (compute, API calls) but used a mode | Write a **hook** module — modes are declarative only |

---

## Practical Example: This Bundle

The `systems-design` bundle composes all seven mechanisms:

| Mechanism | Instance | Role |
|-----------|----------|------|
| **Modes** | `system-design`, `design-review` | Enforce read-only tool policy during design; block file writes until design is complete |
| **Recipes** | `architecture-review` (staged, 2 approval gates), `design-exploration` (parallel foreach), `codebase-understanding` (sequential) | Structure multi-step design workflows with checkpointing |
| **Agents** | `systems-architect` (reasoning), `systems-design-critic` (critique), `systems-design-writer` (writing) | Isolated sub-sessions with different model roles and focused concerns |
| **Skills** | `adversarial-review` (fork, 5 parallel agents), `tradeoff-analysis`, `architecture-primitives`, `system-type-web-service`, `system-type-event-driven` | Task expertise loaded on demand — the fork skill spawns its own review agents |
| **Hooks** | `hooks-mode` (from modes bundle) | Mode enforcement and context injection |
| **Tools** | `tool-mode`, `tool-skills` (via behavior YAML wiring) | LLM-accessible mode switching and skill loading |
| **Content** | `system-design-principles.md`, `structured-design-template.md`, `instructions.md` | Design philosophy, templates, and standing orders injected into root session |

All wired together through `behaviors/system-design.yaml`, which composes the modes behavior, configures the skills tool with local skill directories, declares the three agents, and includes the context files.

## Mental Model

| Mechanism | Verb | Triggered by |
|-----------|------|-------------|
| **Mode** | constrains | User or agent activates |
| **Recipe** | organizes | User or agent invokes |
| **Agent** | thinks | Parent delegates |
| **Skill** | knows how | Agent loads on demand |
| **Hook** | observes | Lifecycle event (deterministic) |
| **Tool** | acts | LLM decides to call |
| **Content** | informs | Resolution at load/injection time |

## Closing

When mechanism choice gets confusing, ask:

> **"Where should this attach, and who triggers it?"**

- Attach at the **highest level where it remains valid** — session-wide constraints go in modes, not skills.
- **Code-decided behavior** (must happen every time) goes in hooks. **LLM-decided behavior** (model judges when) goes in tools.
- **Recipes own ordering**, skills own expertise, agents own reasoning. Don't smear one into another.

That question — attachment point plus trigger — resolves almost everything.
