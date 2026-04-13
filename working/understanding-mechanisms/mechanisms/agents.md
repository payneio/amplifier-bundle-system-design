# Agents: Specialized Sub-Agent Delegation

## What It Is

An agent is a specialist sub-agent that gets spawned as a child session via the
`delegate` tool. Agents are markdown files with `meta:` YAML frontmatter (not
`bundle:` frontmatter) that define a partial configuration overlay merged with
the parent session's config when spawned. They exist primarily as "context sinks"
-- absorbing heavy token costs in their own isolated context and returning only
concise summaries.

## How It Works

### Agent Definition File

```yaml
---
meta:
  name: zen-architect
  description: "Architecture design, code planning, and review. Use PROACTIVELY
    for code planning, architecture design, and review tasks."

model_role: [reasoning, general]

provider_preferences:
  - provider: anthropic
    model: claude-sonnet-*
---

# Architecture Agent

System instruction body -- the agent's persona and operational instructions.

---

@foundation:context/IMPLEMENTATION_PHILOSOPHY.md
@foundation:context/shared/common-agent-base.md
```

### Agent vs Bundle

Agents ARE bundles structurally. The difference is conventional:
- Bundles use `bundle:` frontmatter -- complete, ready-to-run configuration
- Agents use `meta:` frontmatter -- partial overlay merged with parent session

When spawned, agents inherit tools, providers, and hooks from the parent, with
configurable exclusions.

### The Delegate Tool

The `DelegateTool` handles the full agent lifecycle:
1. Parse parameters (agent name, instruction, context settings)
2. Validate agent (check registry, handle "self" and "namespace:path")
3. Apply provider preferences and model_role resolution
4. Build inherited context (two-parameter system)
5. Merge tools (exclusions apply to inheritance, explicit declarations win)
6. Call `session.spawn` capability (app-layer creates child session)
7. Return result with `session_id` for resumption

### Context Inheritance (Two Parameters)

**context_depth** -- HOW MUCH:
- `"none"` -- clean slate
- `"recent"` -- last N turns (default 5)
- `"all"` -- full conversation

**context_scope** -- WHICH content:
- `"conversation"` -- user/assistant text only
- `"agents"` -- includes delegate tool results
- `"full"` -- ALL tool results (truncated to 4000 chars)

### Model Role System

Agents declare what kind of model they need:
- `general` -- versatile (explorer, foundation-expert)
- `fast` -- utility tasks (file-ops, git-ops, shell-exec)
- `[coding, general]` -- code generation (bug-hunter, modular-builder)
- `[reasoning, general]` -- deep analysis (zen-architect)
- `[security-audit, critique, general]` -- security (security-guardian)

Fallback chains are tried left-to-right. The delegate tool can also override
model_role at call time.

### Foundation Agent Catalog (16 agents)

| Agent | Role | Specialization |
|-------|------|---------------|
| zen-architect | reasoning | Architecture design, planning, review |
| explorer | general | Multi-file codebase exploration |
| bug-hunter | coding | Systematic hypothesis-driven debugging |
| modular-builder | coding | Implementation from specifications |
| file-ops | fast | File read/write/edit/search |
| git-ops | fast | Git/GitHub with safety protocols |
| web-research | fast | Web search and information synthesis |
| security-guardian | security-audit | Security reviews, vulnerability assessment |
| session-analyst | fast | Session debugging, transcript repair |
| test-coverage | coding | Test coverage analysis |
| integration-specialist | general | External API/MCP integration |
| post-task-cleanup | fast | Codebase hygiene after tasks |

### Key Implementation Files

- `amplifier-foundation/agents/` -- All 16 agent definition files
- `amplifier-foundation/modules/tool-delegate/__init__.py` -- Delegate tool (1,252 lines)
- `amplifier-core/docs/SESSION_FORK_SPECIFICATION.md` -- Kernel fork mechanism

## Relevance to System Design Bundle

Agents are the mechanism for specialized design expertise that requires dedicated
context and potentially different model capabilities.

### Immediate Opportunities

- **Systems architect agent**: A reasoning-class agent that specializes in system
  modeling -- identifying goals, constraints, actors, resources, interfaces,
  feedback loops, failure modes. Uses the structured response template from the
  agentic-system-design doc. Could be the primary design agent.

- **Design critic agent**: A critique-class agent that reviews proposed designs
  from multiple perspectives. Loaded with adversarial review prompts (SRE, security,
  staff engineer, finance, operator). Uses `model_role: [critique, reasoning, general]`.

- **Constraint analyst agent**: Specialized in identifying, tracking, and evaluating
  design constraints and tradeoffs. Understands that architecture is about choosing
  what to sacrifice, not finding optimal solutions.

- **Codebase surveyor agent**: Extends the explorer pattern but focused on
  architectural understanding -- identifying module boundaries, dependency patterns,
  coupling hotspots, data flows, and architectural debt.

### The Context Sink Pattern for Design

The context sink pattern is especially valuable for design work because:
- Design exploration requires reading many files (codebase survey)
- Different perspectives require different context (SRE vs security vs DX)
- The parent session needs to stay lean for the long design conversation
- Each specialist agent can carry heavy design reference documentation

### Agents vs Skills for Design Capabilities

| Use an Agent When | Use a Skill When |
|-------------------|-----------------|
| Need isolated context window | Knowledge injection is sufficient |
| Need specific model capabilities | Current model works fine |
| Multi-turn investigation needed | Single-shot guidance works |
| Heavy doc consumption required | Lightweight patterns needed |
| Tool restrictions differ from parent | Same tools work |
