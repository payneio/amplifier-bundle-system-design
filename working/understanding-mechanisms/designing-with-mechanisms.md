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

| Mechanism | Attaches to | Lifetime | State location | Authored as | Token impact |
|-----------|-------------|----------|----------------|-------------|-------------|
| Mode | Session | Togglable, ephemeral re-injection | `session_state["active_mode"]` | `.md` with YAML frontmatter | Ephemeral per-turn cost while active; never stored |
| Recipe | Workflow execution | Per-invocation, resumable | `state.json` on disk | `.yaml` | Each step runs in isolated context; only text output propagates |
| Agent | Sub-session | One-shot or resumable | Kernel session (in-memory) | `.md` with YAML frontmatter | Context sink -- parent pays ~200-500 tokens for summary |
| Skill | Task pattern | On-demand (inline or forked) | None (stateless) or fork session | `SKILL.md` in a directory | L1 visibility: ~1K tokens/turn ephemeral; L2 load: compactable tool result |
| Hook | Lifecycle event | Session lifetime | Module state + `session_state` | Python module | Ephemeral injections: per-turn cost; non-ephemeral: stored permanently |
| Tool | LLM decision | Session lifetime | Module state | Python module | Results stored in message history; primary compaction target |
| Content | Context window | Per-injection | None (consumed by LLM) | `.md` files | Fixed cost every turn; immune to compaction |

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

## Context Window Economics

Every mechanism has a token cost. Understanding that cost -- and which costs are fixed vs compactable -- is essential for designing bundles that stay effective across long sessions.

### The Three-Layer Model

The context window sent to the LLM on each turn has three distinct layers with different persistence and compaction behavior:

```
Context Window (e.g., 200K tokens)
+-- LAYER 1: System Prompt (never compacted)
|   Instruction body + all @mentioned files + context.include files
|   Re-read from disk every turn. Fixed cost. Immune to compaction.
|
+-- LAYER 2: Message History (compactable)
|   User/assistant messages, tool calls and results.
|   Accumulates during session. Compacted when budget pressure hits 92%.
|   8-level cascade: truncate tool results -> remove old messages -> stub.
|
+-- LAYER 3: Ephemeral Injections (per-turn, not stored)
|   Skills visibility list, active mode body, hook injections.
|   Appended AFTER compaction runs. Never enters message history.
|   Cost repeats every turn but never compounds.
|
+-- RESERVED
    4096 tokens safety margin + 50% of max_output_tokens + 800 for compaction notice
```

**Budget formula:** `context_window - (max_output_tokens x 0.5) - 4096`

Compaction triggers at 92% of budget and targets 50%. The system prompt sits outside the compactable portion entirely -- it's a permanent tax.

### How Each Mechanism Affects the Budget

| Mechanism | Layer | Compactable? | Cost model |
|-----------|-------|-------------|------------|
| **Content** (@mentions) | System prompt | Never | Fixed per turn. Every @mentioned file's full text is included in every LLM call. |
| **Content** (context.include) | System prompt | Never | Same as @mentions. Accumulates across behavior composition. |
| **Agents** (delegation) | Message history | Yes | Parent pays only ~200-500 tokens per delegation (tool call + summary result). Child absorbs all exploration tokens in its own context. |
| **Skills** (L1 visibility) | Ephemeral | Never | ~1,000-1,500 tokens per turn (all skill names + descriptions). Scales with number of composed skills. |
| **Skills** (L2 load) | Message history | Yes | Full skill content returned as tool result. Subject to normal compaction (truncated, then removed). |
| **Skills** (fork) | Isolated session | N/A | Like agents: runs in child context, parent sees only the result. |
| **Hooks** (ephemeral injection) | Ephemeral | Never | Per-turn cost while hook fires. Not stored. Disappears after each LLM call. |
| **Hooks** (persistent injection) | Message history | Yes | Stored permanently via `context.add_message()`. Subject to compaction. |
| **Modes** | Ephemeral | Never | Full mode markdown body injected every turn while active. Stops immediately on deactivation. |
| **Recipes** | Isolated per step | N/A | Each step runs in a fresh child session. Only text output propagates via `{{variables}}`. No conversation history carries between steps. |
| **Tools** (results) | Message history | Yes, first | Tool results are the primary compaction target. Truncated to 250 chars before messages are removed. Last 5 results protected. |

### Design Implications

**The fixed-cost trap.** Content files and context.include entries are the most dangerous budget item because they're invisible -- always present, never compacted, and they accumulate across behavior composition. A bundle that composes three behaviors each adding 2K tokens of context has a 6K token permanent floor before any conversation starts.

**Compaction favors tool results over conversation.** The 8-level cascade truncates tool results first (Levels 1-2), then removes old messages (Level 3+). This means heavy tool use is more sustainable than heavy context file use -- tool results eventually get compacted away, but @mentioned content never does.

**Ephemeral injections add up silently.** Skills visibility (~1K tokens) + an active mode (~500-2K tokens) + status context hooks can easily consume 3-4K tokens per turn that never appear in the message history but still eat into the available window.

**Agents are the primary context management tool.** The context sink pattern isn't just about specialization -- it's about token economics. Delegating a 20-file exploration to an agent costs the parent ~400 tokens. Doing it directly costs ~20K tokens that persist in message history until compacted.

### Rules of Thumb for Bundle Authors

1. **Content files: budget per byte.** Every token in an @mentioned file is paid on every turn. Keep always-present content concise and high-value. Move detailed reference material to skills (loaded on demand) or agent @mentions (loaded in child context only).

2. **Skills over content for reference material.** A 3K-token methodology guide as a content file costs 3K tokens x every turn. As a skill, it costs ~100 tokens/turn (L1 visibility) plus 3K tokens once when loaded (L2), and that load is compactable.

3. **Fork skills over inline skills for heavy work.** If a skill's execution involves reading many files or producing large outputs, use `context: fork` to run it in an isolated child session.

4. **Modes should be concise.** Mode content is injected ephemerally every turn. A 1,000-word mode file costs ~750 tokens per turn for every turn it's active. Keep mode guidance focused; move detailed methodology to a companion skill loaded once on mode activation.

5. **Watch behavior composition.** Each `includes:` that adds `context.include` entries increases the permanent system prompt floor. Audit the total context footprint when composing multiple behaviors.

6. **Prefer ephemeral over persistent hook injections.** Use `ephemeral=True` for hook context injections unless the information must survive across turns. Ephemeral injections don't accumulate in message history.

---

## Parallelism and Concurrency

Several mechanisms support parallel execution. Knowing when and how to parallelize is a major design lever -- it affects latency, token cost, and result quality.

### Where Parallelism Is Available

| Mechanism | Parallel capability | How it works |
|-----------|-------------------|-------------|
| **Agents** | Multiple `delegate()` calls in a single assistant turn | Each agent runs in an independent session concurrently. No shared state. Results return when all complete. |
| **Recipes** | `foreach` steps with items | Each item gets its own step execution. Steps within a foreach can run concurrently. |
| **Fork skills** | Skill body can dispatch parallel agents | The adversarial-review skill spawns 5 agents in parallel, each reviewing from a different perspective. |
| **Tools** | Multiple tool calls in one LLM response | The orchestrator executes all tool calls from a single response concurrently before the next LLM call. |

### When to Parallelize

Parallelism is beneficial when:
- **Tasks are independent.** No data flows from one task to another. Each can be fully specified upfront.
- **Tasks benefit from isolation.** Different focus areas, different agent expertise, different model roles.
- **Latency matters.** Three agents running in parallel complete in ~1x time, not ~3x.
- **Tasks are bounded.** Each parallel unit has clear scope and completion criteria.

Parallelism is harmful when:
- **Results of one task inform another.** Sequential dependency requires sequential execution.
- **Tasks need to converge iteratively.** Use recipe `while` loops or session resumption instead.
- **Shared context is needed.** Parallel agents can't see each other's in-progress work.

### Parallel Design Patterns

**Fan-out / fan-in (agents):** Dispatch multiple agents, synthesize their results in the parent session or in a final synthesis agent.

```
Parent dispatches 3 explorer agents (parallel)
  → Agent A surveys src/auth/
  → Agent B surveys src/api/
  → Agent C surveys src/models/
Parent (or synthesis agent) combines findings
```

**Parallel review (fork skill):** A fork skill spawns sub-agents that each evaluate the same artifact from different perspectives.

**Parallel recipe items (foreach):** A recipe foreach processes a list of items, each in its own step session. Useful for batch operations across repos, files, or components.

**Tool-level parallelism:** Multiple tool calls in a single LLM response (e.g., reading 3 files simultaneously). This is automatic -- the LLM naturally emits parallel tool calls for independent operations.

### Parallelism and Token Cost

Parallel agents multiply the *throughput* without multiplying the parent's context cost. Three parallel agents cost the parent ~1,200 tokens total (3 x ~400 tokens each), the same as three sequential agents. But wall-clock time is ~1/3.

The trade-off: parallel agents can't share discoveries. If Agent A finds something that would change Agent B's analysis, Agent B won't know. For exploratory work where findings compound, sequential delegation with `context_scope="agents"` (each agent sees prior agents' results) produces better-informed analysis at the cost of higher latency.

---

## Context Lifecycle: Persistent, Ephemeral, and Disposable

Beyond token *cost*, the lifecycle question is: **"Does this context need to persist, or can it be thrown away once it's served its purpose?"**

### Three Lifecycles

| Lifecycle | Where it lives | When it disappears | Mechanisms |
|-----------|---------------|-------------------|------------|
| **Persistent** | System prompt or message history | Never (system prompt) or when compacted (history) | Content files, tool results, non-ephemeral hook injections |
| **Ephemeral** | Appended per-turn, not stored | After each LLM call | Mode body, skills visibility, ephemeral hook injections |
| **Disposable** | Isolated child session | When child session completes | Agents, recipe steps, fork skills |

### The Disposable Context Pattern

The most powerful context management tool is **throwing context away**. When work runs in an agent, recipe step, or fork skill, the entire working context -- file reads, searches, intermediate reasoning, dead-end explorations -- is discarded when the task completes. Only the distilled output survives.

This is not a limitation. It's the design. The parent session doesn't need to know *how* the agent explored 20 files -- it needs the *conclusion*.

**Rule of thumb:** If a sub-task involves more than 2-3 tool calls, or if the intermediate work products (file contents, search results) aren't needed after the task is done, use a disposable context -- agent, recipe step, or fork skill.

### Choosing the Right Lifecycle

| Question | If yes → | If no → |
|----------|----------|---------|
| Must the LLM see this on every single turn? | Persistent (content file) | Something cheaper |
| Is it phase-specific guidance? | Ephemeral (mode) | Persistent or disposable |
| Is it one-time reference material? | Disposable (skill load, compactable) or on-demand (skill L2) | Content file |
| Is it heavy exploration producing a summary? | Disposable (agent) | Root session tool calls |
| Does the user need to see intermediate steps? | Persistent (root session) | Disposable (agent) |

### Context Lifecycle and Session Length

Persistent context accumulates. Ephemeral context repeats but doesn't grow. Disposable context vanishes.

Over a 50-turn session:
- **Persistent content file (2K tokens):** 2K every turn = 100K total consumption (never recovered)
- **Ephemeral mode (2K tokens, active for 10 turns):** 2K x 10 = 20K total, then zero
- **Disposable agent delegations (10 delegations):** ~400 tokens each x 10 = 4K in parent (compactable)

Sessions that rely heavily on disposable context (agents, recipe steps) stay lean longer than sessions that accumulate persistent context (direct tool use, content files).

---

## Model Selection

Different mechanisms can run on different models. This is a significant cost, quality, and latency lever that's easy to overlook.

### Where Model Selection Applies

| Mechanism | Model control | How configured |
|-----------|--------------|---------------|
| **Root session** | Bundle's default model | Provider configuration in bundle YAML |
| **Agent** | `model_role` in agent frontmatter | Declares what kind of model the agent needs |
| **Delegation override** | `model_role` parameter in `delegate()` | Parent overrides child's default model role |
| **Recipe step** | Inherited from the step's agent | Each step runs with its agent's model role |
| **Fork skill** | Can specify `model_role` in skill metadata | Fork session uses the specified model |

### Matching Models to Tasks

Not every task needs the most capable model. The routing matrix maps roles to model tiers:

| Task character | Model role | Typical tier | When to use |
|---------------|-----------|-------------|-------------|
| Deep design, architecture, complex reasoning | `reasoning` | Heavy (Opus-class) | System design, architectural decisions, complex planning |
| Finding flaws, critical evaluation | `critique` | Mid + high reasoning | Code review, design review, adversarial analysis |
| Code generation, debugging | `coding` | Mid (Sonnet-class) | Implementation, bug fixing, test writing |
| Long-form prose, documentation | `writing` | Heavy (Opus-class) | Case studies, design docs, release notes |
| File operations, git commands, triage | `fast` | Cheap (Haiku-class) | Exploration, file ops, routine utilities |
| General-purpose, varied work | `general` | Mid (Sonnet-class) | Catch-all for agents without clear specialization |

### Model Selection as a Design Decision

When designing a bundle's agent constellation, model roles define the cost and capability profile:

**Example: The systems-design bundle**
- `systems-architect`: `reasoning` -- needs deep multi-step analysis
- `systems-design-critic`: `critique` -- needs to find flaws, not generate solutions
- `systems-design-writer`: `writing` -- needs sustained, high-quality prose

A bundle that routes an explorer agent to `fast` instead of `general` might pay 1/10th the cost per delegation. Over a session with 20 explorations, that's a substantial difference.

**Fallback chains** provide resilience: `[ui-coding, coding, general]` tries the most specific model first, falling back to more available options. Always end with `general` or `fast`.

### Model Selection and Parallelism

Parallel agents can each run on different models. A common pattern:
- Dispatch 3 `fast` explorers to survey different areas (cheap, concurrent)
- Feed results to 1 `reasoning` architect for synthesis (expensive, focused)

This maximizes cost efficiency: the expensive model only runs once, on distilled input.

---

## Turn Budgets and Bounded Work

Unbounded work is the most common source of runaway cost and quality degradation. Several mechanisms provide bounds.

### Where Bounds Apply

| Mechanism | Bound | Effect when hit |
|-----------|-------|----------------|
| **Agent** | `max_turns` in agent config | Agent stops and returns whatever it has |
| **Orchestrator** | `loop_iterations_limit` (per user turn) | System reminder injected telling agent to wrap up |
| **Recipe step** | Step's agent turn limit | Step completes with partial output |
| **Recipe** | `max_iterations` on while loops | Loop exits regardless of condition |

### Why Bounds Matter

An agent with an open-ended instruction like "analyze the codebase" will use its entire turn budget exploring. This isn't necessarily useful -- after a point, the agent is exploring diminishing-return areas or re-examining what it already found.

Tighter bounds produce more focused work:

| Turn budget | Character of work |
|------------|-------------------|
| 3-5 turns | Focused: read specific files, form opinion, return |
| 10-15 turns | Thorough: explore an area, iterate on findings, synthesize |
| 25+ turns | Exhaustive: deep investigation, multi-approach analysis |

### Designing for Bounded Work

1. **Scope the instruction tightly.** "Survey `src/auth/` and report on authentication patterns" is better than "understand the codebase."
2. **Match turn budget to task complexity.** A file-reading utility agent needs 3-5 turns. An architect designing a system needs 15-20.
3. **Prefer multiple bounded agents over one unbounded agent.** Three 5-turn explorers produce more focused results than one 15-turn explorer, and they can run in parallel.
4. **Recipe steps are naturally bounded.** Each step has a focused instruction and its own turn budget. Multi-step work becomes a sequence of bounded tasks.

### The Interaction Between Bounds and Context

Turn budgets interact with context window economics. An agent with a generous turn budget will accumulate more tool results in its own context, potentially triggering compaction within the child session. This is usually fine -- the child's compaction is independent of the parent's. But for very long-running agents, the child may lose track of early findings as its own context compacts.

For tasks that require synthesizing a large body of findings, consider: gather in one agent (or multiple parallel agents), then synthesize in a fresh agent that receives only the summaries.

---

## Human-in-the-Loop Design

Where and how to place human checkpoints affects both the quality of outcomes and the user experience. Not every mechanism supports human interaction equally.

### Interaction Models by Mechanism

| Mechanism | Human interaction | Timing |
|-----------|------------------|--------|
| **Root session** | Every turn is a human exchange | Continuous |
| **Mode** | User activates/deactivates; agent can suggest transitions | Phase boundaries |
| **Recipe (staged)** | Approval gates between stages | Between workflow phases |
| **Recipe (flat)** | None -- fire and forget | N/A |
| **Agent** | None during execution; parent session can interact before/after | Before dispatch and after return |
| **Fork skill** | None during execution | N/A |
| **Hook** | Can trigger `confirm` tool policy (user approves tool calls) | Per tool call |

### Designing Checkpoint Placement

**High-value checkpoints** (place these):
- After analysis, before implementation (user validates direction)
- After implementation, before deployment (user validates result)
- At phase transitions (brainstorm → plan → execute → verify)

**Low-value checkpoints** (avoid these):
- Between individual tool calls within a task
- Between recipe steps within a single stage
- For decisions the agent has clear criteria to make

### Modes as Phase Boundaries

Modes serve as natural human checkpoints because the user explicitly activates them. The transition from `/brainstorm` to `/write-plan` to `/execute-plan` creates deliberate pause points where the user consciously shifts the workflow phase.

This is lighter-weight than recipe approval gates (which block execution until approved) and more structured than raw conversation (which has no explicit phase transitions).

### Recipe Approval Gates

Staged recipes pause execution between stages and require explicit `approve` or `deny`. This is the right mechanism when:
- Work is expensive and difficult to undo (implementation, deployment)
- The user needs to review an intermediate artifact (design doc, plan)
- Different stages might be routed to different people

Approval gates support messages (`approve(message="merge")`) that subsequent stages can read, allowing the user to influence downstream behavior.

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

When mechanism choice gets confusing, work through these questions:

> **1. "Where should this attach, and who triggers it?"**

Attach at the **highest level where it remains valid** -- session-wide constraints go in modes, not skills. **Code-decided behavior** (must happen every time) goes in hooks. **LLM-decided behavior** (model judges when) goes in tools. Recipes own ordering, skills own expertise, agents own reasoning. Don't smear one into another.

> **2. "Should this context persist, or can it be thrown away?"**

Work that produces a summary but doesn't need its intermediate context to persist belongs in a **disposable** context -- agents, recipe steps, fork skills. Work the LLM needs every turn belongs in **persistent** context -- content files. Phase-specific guidance belongs in **ephemeral** context -- modes. Default to disposable. The session stays leaner.

> **3. "What does this cost the context window?"**

Content files are a permanent per-turn tax that compaction can never recover. Skills are loaded on demand and compactable. Modes are ephemeral and stop when deactivated. Agents are context sinks where the parent pays hundreds of tokens for work that would cost tens of thousands in-session. Budget per byte for anything in the system prompt.

> **4. "Can parts of this work run in parallel?"**

Independent tasks with no shared state are candidates for parallel agents, recipe foreach, or parallel tool calls. Parallel agents multiply throughput without multiplying parent context cost. The trade-off: parallel units can't share discoveries mid-flight. For work where findings compound, use sequential delegation with `context_scope="agents"`.

> **5. "What model capability does this need?"**

Route cheap, bounded, well-defined work to `fast` models. Route deep analysis to `reasoning`. Route evaluation to `critique`. Route prose to `writing`. A bundle that routes every agent to the default model is overpaying for utility work and under-serving complex reasoning. Model roles are declared in agent frontmatter and can be overridden at delegation time.

> **6. "How much work should this be allowed to do?"**

Tighter turn budgets produce more focused results. Three 5-turn agents produce better-scoped analysis than one 15-turn agent with vague instructions. Scope the instruction tightly, match the turn budget to the task's actual complexity, and prefer multiple bounded agents over one open-ended one.

> **7. "Where do humans need to weigh in?"**

Place human checkpoints at high-stakes transitions: after analysis before implementation, after implementation before deployment. Modes serve as lightweight phase boundaries (user consciously shifts workflow). Recipe approval gates serve as hard stops (execution pauses until approved). Avoid checkpoints at high-frequency, low-stakes points -- that's what hooks are for.

---

Questions 1 picks the mechanism. Questions 2-3 shape how it manages context. Questions 4-6 shape how it executes. Question 7 shapes where the human stays in control.

These questions interact. An agent (Q1) with disposable context (Q2) running on a fast model (Q5) with a tight turn budget (Q6) in parallel with two peers (Q4) is a very different design than a single agent on a reasoning model with open-ended scope. Both are valid -- the questions force you to make the choice deliberately.
