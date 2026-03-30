# Skills: On-Demand Domain Knowledge Packages

## What It Is

A skill is a reusable, on-demand knowledge package that agents can discover and
load via the `load_skill` tool. Skills follow the open Agent Skills specification
(agentskills.io) and provide progressive disclosure: metadata is always visible,
full content loads on demand, and companion files are accessible as needed.

Skills are the lightest-weight mechanism for extending agent capabilities. They're
just directories containing a `SKILL.md` file with YAML frontmatter + markdown.

## How It Works

### Skill Structure

```
my-skill/
  SKILL.md           # Required -- YAML frontmatter + markdown body
  patterns.md        # Optional companion file (Level 3)
  examples/
    example.py       # Optional companion
```

### SKILL.md Format

```yaml
---
name: my-skill
description: "What this skill provides and when to use it"
version: 1.0.0
---

# My Skill

Instructions the agent follows when this skill is loaded.
Can reference companion files via ${SKILL_DIR}/patterns.md.
```

### Three Levels of Progressive Disclosure

| Level | What | Token Cost | When |
|-------|------|-----------|------|
| L1: Metadata | name + description | ~100 tokens | Always -- visibility hook |
| L2: Content | Full SKILL.md body | ~1-5K tokens | On demand -- load_skill() |
| L3: References | Companion files | 0 until accessed | Explicit read_file() |

### Visibility Hook

A `SkillsVisibilityHook` fires before every LLM call, injecting available skill
names and descriptions into context. The agent doesn't need to call `load_skill(list=true)`
-- skills are automatically surfaced.

### Fork Skills (context: fork)

When a skill has `context: fork` in frontmatter, loading it spawns an isolated
subagent. The skill's body becomes the subagent's instruction. The subagent gets
its own context window, tools, and conversation -- then returns a result.

This bridges the gap between skills (lightweight knowledge) and agents (isolated
execution). Fork skills can specify:
- `model_role` for model selection (coding, reasoning, critique, etc.)
- `allowed-tools` to restrict available tools
- `provider_preferences` for model routing

### Real Skills Inventory

**Built-in power skills** (user-invoked via slash commands):
- `code-review` -- spawns 3 parallel review agents (fork skill)
- `mass-change` -- 3-phase orchestrator for large-scale changes (fork skill)
- `session-debug` -- delegates to session-analyst (fork skill)

**Superpowers skills**:
- `superpowers-reference` -- complete mode/agent/recipe reference tables
- `integration-testing-discipline` -- E2E testing discipline

**External skills** (from obra/superpowers):
- brainstorming, systematic-debugging, verification-before-completion,
  test-driven-development, writing-plans, subagent-driven-development

### Enhanced Features

- Shell preprocessing: `` !`command` `` in body replaced with stdout at load time
- Variable substitution: `${SKILL_DIR}`, `$ARGUMENTS`, `$0`, `$1`...
- Security: untrusted (remote) skills have shell commands blocked
- Git URL sources: skills can be loaded from remote git repos
- `disable-model-invocation: true` hides from auto-visibility
- `user-invocable: true` registers as `/name` slash command
- `auto-load: true` loads at session startup

### Key Implementation Files

- `amplifier-bundle-skills/modules/tool-skills/__init__.py` -- SkillsTool (793 lines)
- `amplifier-bundle-skills/modules/tool-skills/discovery.py` -- Discovery + metadata
- `amplifier-bundle-skills/modules/tool-skills/hooks.py` -- Visibility hook
- `amplifier-bundle-skills/modules/tool-skills/preprocessing.py` -- Shell/var processing
- `amplifier-bundle-skills/modules/tool-skills/model_resolver.py` -- 5-level model selection

## Relevance to System Design Bundle

Skills are arguably the **highest-leverage mechanism** for our system design bundle,
especially for initial experiments. They're lightweight, fast to create, and can
deliver immediate value.

### Immediate Opportunities

- **System design methodology skill**: A comprehensive skill containing the
  structured response template from the agentic-system-design doc (problem framing,
  assumptions, boundaries, components, flows, risks, tradeoffs, design, migration,
  metrics). Loaded when the agent encounters a design problem.

- **System type skills**: Separate skills for different system types (web service,
  web app, distributed system, peer-to-peer, event-driven). Each contains patterns,
  common pitfalls, and evaluation criteria specific to that system type. The agent
  loads the relevant one based on what kind of system is being designed.

- **Tradeoff analysis skill**: A skill that guides the agent through structured
  tradeoff analysis using the fixed frame (latency, complexity, reliability, cost,
  security, scalability, reversibility, organizational fit).

- **Adversarial review skill**: A fork skill that spawns multiple review agents
  with different perspectives (SRE, security reviewer, staff engineer, finance
  owner, operator) -- similar to how code-review spawns parallel review agents.

- **Architecture primitives skill**: A skill containing reusable abstractions
  (boundaries, contracts, state machines, queues, caches, idempotency, etc.) with
  guidance on when each pattern is appropriate AND when it's wrong.

### Skills vs Other Mechanisms

For our bundle, skills should be the **default starting point** because:
- Zero Python code needed (just markdown files)
- Progressive disclosure saves tokens (only loaded when relevant)
- Fork skills provide agent-like isolation when needed
- Easy to iterate and experiment (just edit SKILL.md)
- Cross-harness portable (Agent Skills spec)

Graduate to other mechanisms when:
- Need structured data manipulation -> tool
- Need automated real-time feedback -> hook
- Need multi-step workflows -> recipe
- Need persistent agent specialization -> agent
- Need always-present guidance -> context file
