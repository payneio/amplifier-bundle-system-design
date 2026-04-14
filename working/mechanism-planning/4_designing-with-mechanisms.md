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
4. Does the LLM need to decide when to invoke a capability? **Tool**
5. Does it need isolated reasoning with its own context? **Agent**
6. Is it just reference information? **Content**

**Distinguishing hooks from modes:** Hooks are Python modules — use them when you need programmatic logic (parse responses, compute values, call APIs on lifecycle events). Modes are declarative `.md` files — use them when you need tool policy tiers and injected guidance without writing code.

**Distinguishing skills from agents:** Inline skills are cheaper (no sub-session overhead) and portable (Agent Skills spec). Fork skills converge with agents but require less infrastructure (a directory vs. a bundle). Use agents when you need: resumable sessions, specific tool composition, or deep context isolation.

---

## Failure Modes (Misplaced Attachment)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| **Policy leakage** (too low) | Safety rules in skills or recipe prompts — inconsistent enforcement | Move to a **mode** with tool policy tiers |
| **Automated workflow hidden in skills** | Step sequences that *can run without user interaction between steps* encoded in skill bodies — brittle, no checkpointing | Move to a **recipe** (exception: interactive conversational workflows where the user steers at every phase — see Workflow Ordering below) |
| **Expertise smearing** (too high) | Heuristics duplicated across recipe step prompts | Centralize in a **skill** |
| **Skill hypertrophy** | A skill that spawns agents, manages state, enforces policy | Split: policy to mode, workflow to recipe, expertise stays in skill |
| **Capability fiction** | APIs described in context but not exposed as tools | Wire as a **tool** (or MCP resource) |
| **Cognitive overload** | Single agent prompt does everything | Decompose into **delegated agents** with focused concerns |
| **Knowledge entanglement** | Docs copy-pasted into agent prompts, skills, and recipe steps | Centralize as **content** files, reference via `@mention` |
| **Missing hook, using mode** | You need programmatic logic (compute, API calls) but used a mode | Write a **hook** module — modes are declarative only |
| **Composition loophole** | Mode blocks `write_file` but allows `delegate` or `recipes` as safe — sub-agents bypass parent mode restrictions via their own sessions | Audit which tools can spawn child sessions. If `delegate`/`recipes` are safe, sub-agents can write files, run code, and launch pipelines regardless of the parent mode's restrictions. This may be intentional (e.g., `execute-plan` mode) or a loophole. Name it explicitly in the plan. |

### Enforcement Levels: Structural vs Conventional

Not all design decisions are equally enforceable. Empirical evidence from cross-session behavioral analysis shows that **tool restrictions reliably shape behavior; prose instructions frequently don't.**

In 4 real sessions of one bundle's `write-plan` mode, two behaviors described only in prose guidance -- "discuss file decomposition before tasks" and "present execution choice to user" -- were skipped in every session. Meanwhile, tool restrictions (`write_file` blocked) were enforced in every session, every time. The conclusion: tool availability determines behavior more than prose instructions.

When designing a mechanism plan, classify each behavioral expectation:

| Level | Enforced by | Reliability | Example |
|-------|------------|------------|---------|
| **Structural** | Tool policies, hook gating, blocked tools | High -- will fail or be prevented if violated | `write_file` blocked in design mode; mode gate policy requires double-confirmation to transition |
| **Conventional** | Prose in mode body, skill guidance, agent instructions | Variable -- model follows when convenient, skips under pressure | "Always validate with the user before proceeding"; "discuss file decomposition before individual tasks" |
| **Inferred** | Neither stated nor enforced; emerges from tool availability patterns | Unpredictable | Agent uses `delegate(explorer)` because `read_file` is available but the instruction says "analyze" without specifying how |

**Design implication:** If a behavior is critical enough to appear in a plan, ask: "What happens if the model skips this?" If the answer is "the workflow breaks or produces bad output," encode it structurally -- move it from prose into tool policies, hook enforcement, or recipe step boundaries. If the answer is "output quality degrades but it's still usable," conventional guidance is acceptable.

**Structural enforcement is doubly effective.** Tool policies don't just block prohibited actions -- they shape model behavior so the blocker rarely fires. In practice, zero blocked-tool error events have been observed across thousands of sessions, despite active `default_action: "block"` policies. Models read the safe-tools list and self-restrict without attempting prohibited tools. This means structural enforcement provides value even when it never fires: the guardrail shapes behavior *and* catches violations.

**Anti-pattern:** Relying on conventional guidance for safety-critical behavior. A mode that says "always get user approval before writing files" in its prose body but lists `write_file` as safe will write files without asking.

### Workflow Ordering: Recipes vs Mode + Companion Skill

Multi-step workflows need ordering. The question is where that ordering lives. It depends on who drives the workflow — the pipeline or the user.

**Recipes** own ordering for automated pipelines. Each step runs in an isolated agent session. State persists on disk. Approval gates pause for human review between stages. If the workflow can run without user conversation between steps, it belongs in a recipe.

**Mode + companion skill** owns ordering for interactive conversational workflows. When the user needs to steer at every phase — asking clarifying questions, choosing between options, providing feedback, changing direction — that conversation runs in the root session. A mode provides tool governance (what the session can and can't do). A companion skill loaded at mode entry provides the phase structure (what to do, when to delegate, when to pause for user input). Together they create a guided interactive workflow.

| Workflow type | Mechanism | Why |
|---------------|-----------|-----|
| Fixed steps, no user interaction between them | **Recipe** (flat) | Checkpointing, persistent state, isolated step sessions |
| Fixed steps, user approval needed between stages | **Recipe** (staged) | Approval gates pause for user between stages |
| Conversational, user steers at every phase | **Mode + companion skill** | Root session handles conversation; skill guides phases |
| Both automated and interactive paths needed | **Both** | Recipe for the automated pipeline, skill for the interactive path |

**When to use recipes vs ad-hoc delegation.** Recipes are powerful infrastructure but high-ceremony -- in practice, actual recipe execution is rare despite near-universal composition. Most multi-step work is handled through ad-hoc delegation chains rather than declarative recipes. Design a recipe when the workflow will be repeated, needs resumability across session interruptions, or requires approval gates between stages. Use sequential delegation for workflows that will only run once or that need conversational steering between steps.

**When workflow-in-skill is wrong:** A skill encoding a sequence of steps that could run as a recipe — with no user interaction needed between steps. This is brittle (no checkpointing, no persistent state, no resumability) and gains nothing over a recipe. Move it to a recipe.

**When workflow-in-skill is right:** A skill guiding a multi-phase conversation where the user's input at each phase shapes the next. Recipes can't do this — they run steps in isolated agent sessions with no conversational back-and-forth. The skill describes phases and decision points; the LLM adapts them to the conversation.

**Guardrails for companion skills that encode workflow ordering:**

1. **Build the recipe equivalent when possible.** If the workflow has a meaningful automated version, build both. The recipe handles "run this end-to-end with checkpoints." The skill handles "walk me through this interactively."
2. **Keep the skill as a phase guide, not a script.** Describe phases and decision points. Don't dictate exact tool calls or rigid step sequences. The LLM adapts to what the user actually says.
3. **Accept that skills are stateless.** If the session disconnects mid-workflow, the phase tracking is lost. For workflows where resumability matters, the recipe path is the answer.
4. **Don't enforce policy from the skill.** Policy enforcement belongs in the mode's tool policy tiers. The skill guides; the mode constrains.

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

7. **Loaded skills can be compacted away -- and the reload creates a death spiral.** A skill loaded once enters message history as a tool result. When compaction truncates it, the model detects the missing guidance and reloads the skill, which adds tokens that accelerate the next compaction, which destroys the skill again. In observed sessions, this cycle produced 200+ reloads of a single skill, with a 10x increase in skill loads after compaction began. **Mitigations:** (a) For skills that must persist throughout a session, consider converting to a content file (never compacted) and accepting the per-turn tax. (b) For skills needed only in a specific phase, load at phase entry and design the phase to complete before compaction is likely. (c) Keep skills concise (<2K tokens) so compaction targets larger tool results first. (d) For multi-phase sessions, accept that skill guidance will degrade and design for graceful degradation rather than perfect recall.

### Calculate Your Token Floor

The per-turn floor is the minimum token cost of every LLM call before any conversation happens. It is invisible unless you calculate it, and it accumulates silently across composed behaviors.

```
Your bundle's per-turn floor:
  Content files (your own @mentions + context.include):  ____ tokens
  Content files (from composed behaviors):               ____ tokens
  Skills L1 visibility (~50-100 per skill):              ____ tokens
  Active mode body (when on):                            ____ tokens
  Ephemeral hook injections:                             ____ tokens
  Reserved (output buffer + safety margin):              ____ tokens
  ──────────────────────────────────────────────────────
  Total per-turn floor:                                  ____ tokens
  Budget for conversation: context_window - total floor
```

**Worked example (systems-design bundle composed on foundation):**

| Component | Tokens | Source |
|-----------|--------|--------|
| Foundation context files (15+ files) | ~12,000 | `delegation-instructions.md`, `multi-agent-patterns.md`, `AWARENESS_INDEX.md`, philosophy files, superpowers instructions, etc. |
| Systems-design content files (5 files) | ~4,000 | `instructions.md`, `system-design-principles.md`, `tradeoff-frame.md`, `adversarial-perspectives.md`, `structured-design-template.md` |
| Skills L1 visibility (~20 skills) | ~1,000 | One-line descriptions of all composed skills |
| Active mode body (when in `/systems-design`) | ~1,000 | Mode markdown injected ephemerally |
| Hook injections (status, design context) | ~300 | Ephemeral per-turn injections |
| Reserved | ~6,000 | Output buffer + safety margin |
| **Total per-turn floor** | **~24,300** | **On a 200K context window, ~12% consumed before conversation starts** |

This floor means 12% of the context window is permanently unavailable for conversation, tool results, and agent summaries. With a 50-turn session, message history compaction starts much earlier than it would with a leaner bundle. Every additional content file or composed behavior makes this worse.

**Compaction reality:** 87% of sessions trigger compaction, and 66% of compaction events reach strategy level 5 or higher (aggressive message removal and tool result truncation). The higher your per-turn floor, the sooner compaction fires and the more aggressively it prunes working context. A 24K-token floor on a 200K window means compaction activates earlier in the session, fires more frequently, and destroys skill content and tool results sooner than a leaner bundle. Agents carrying heavy @-mentioned documentation (e.g., architect agents with design frameworks) can hit maximum compaction in as few as 8 turns.

**When reviewing a mechanism plan:** Add up the floor. If it exceeds 15-20% of the context window, audit which content files could be skills (loaded on demand) or agent @mentions (loaded in child context only).

---

## Parallelism and Concurrency

Several mechanisms support parallel execution. Knowing when and how to parallelize is a major design lever -- it affects latency, token cost, and result quality.

### Two Tiers of Parallelism

Amplifier supports parallelism at two levels, and they have very different profiles:

**Tool parallelism (~24% of all LLM responses):** Routine and automatic. The LLM emits multiple tool calls in a single response -- reading several files, running concurrent searches, executing bash alongside python_check. This happens naturally for independent operations and requires no special design. The dominant pattern is `read_file + read_file` (concurrent file reads). Design for this by default -- any independent tool calls should be issued in the same response.

**Agent parallelism (~6% of delegate responses):** Deliberate and high-value. Multiple `delegate()` calls dispatched in a single turn, each running in an independent session. Sessions that use parallel agents are 6x longer than sequential-only sessions, reflecting that this pattern is reserved for substantial, decomposable work. The dominant pattern is fan-out exploration (`explorer + explorer`), followed by parallel reviews (`spec-reviewer + code-quality-reviewer`) and parallel self-delegations for independent work tracks.

### Where Agent Parallelism Is Available

| Mechanism | Parallel capability | How it works |
|-----------|-------------------|-------------|
| **Agents** | Multiple `delegate()` calls in a single assistant turn | Each agent runs in an independent session concurrently. No shared state. Results return when all complete. |
| **Recipes** | `foreach` steps with items | Each item gets its own step execution. Steps within a foreach can run concurrently. |
| **Fork skills** | Skill body can dispatch parallel agents | The adversarial-review skill spawns 5 agents in parallel, each reviewing from a different perspective. |

### When to Parallelize Agents

Parallelism is beneficial when:
- **Tasks are independent.** No data flows from one task to another. Each can be fully specified upfront.
- **Tasks benefit from isolation.** Different focus areas, different agent expertise, different model roles.
- **Latency matters.** Three agents running in parallel complete in ~1x time, not ~3x.
- **Tasks are bounded.** Each parallel unit has clear scope and completion criteria.

Parallelism is harmful when:
- **Results of one task inform another.** Sequential dependency requires sequential execution. Use `context_scope="agents"` so each agent sees prior agents' results.
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

**Default to clean slate.** When delegating to agents, use `context_depth: "none"` unless the agent genuinely needs conversational context. In practice, 84% of all delegations use clean-slate context -- the ecosystem has independently converged on this as the norm. Clean-slate agents start with focused instructions and no inherited baggage, which produces more targeted work and avoids inheriting context pressure from the parent session. Use `context_depth: "recent"` only when the agent needs to understand what the user asked for. Use `"all"` almost never -- it copies the full conversation history into the child, including all the context pressure.

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

**Model routing is actively used, not theoretical.** In practice, ~80% of sessions specify model roles. `fast` (~45%) and `general` (~38%) dominate, with specialized roles (`coding`, `critique`, `reasoning`, `research`) handling the remaining ~17%. Complex sessions routinely dispatch 3 different model tiers (haiku for utility, sonnet for coding, opus for reasoning) within a single workflow. The recommended fallback chains below match the patterns observed in production agent configurations.

**Fallback chains** provide resilience: the most specific role first, falling back to more available options. Always end with `general` or `fast`.

**Standard fallback chains by role:**

| Role | Recommended chain | Rationale |
|------|------------------|-----------|
| `reasoning` | `[reasoning, general]` | Falls back to capable mid-tier |
| `critique` | `[critique, reasoning, general]` | Critique benefits from reasoning as second choice |
| `coding` | `[coding, general]` | Most providers have code-capable models |
| `ui-coding` | `[ui-coding, coding, general]` | Spatial reasoning → code → general |
| `writing` | `[writing, creative, general]` | Long-form → creative → general |
| `creative` | `[creative, general]` | Aesthetic judgment → general |
| `security-audit` | `[security-audit, critique, general]` | Security → analytical evaluation → general |
| `research` | `[research, general]` | Extended context → general |
| `fast` | `fast` | Terminal -- fast agents rarely need fallback |
| `image-gen` | `[image-gen, creative, general]` | Sparse provider coverage; always needs fallback |

### Model Selection and Parallelism

Parallel agents can each run on different models. A common pattern:
- Dispatch 3 `fast` explorers to survey different areas (cheap, concurrent)
- Feed results to 1 `reasoning` architect for synthesis (expensive, focused)

This maximizes cost efficiency: the expensive model only runs once, on distilled input.

### Expected Delegation Distribution

When designing a bundle's agent topology, be aware of where delegations actually go: `foundation:explorer` (~43% of all delegations) and `foundation:git-ops` (~26%) together account for ~69% of agent dispatch. This reflects two entrenched patterns: exploration is always delegated to preserve parent context, and git operations are always delegated for safety protocols. Custom agents (reviewers, architects, builders) collectively account for ~23% of delegations. `self`-delegation for token management is ~8%.

**Design implication:** Optimize for the high-frequency patterns first. If your bundle's agents trigger heavy exploration, ensure the explorer agent's model role is cost-appropriate (`fast` is usually sufficient). If your workflow involves frequent commits, ensure git-ops delegation is frictionless.

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

### Reference Budgets by Agent Archetype

These are starting points, not rules. Adjust based on task scope and instruction specificity. For calibration: the median session is 8 user turns, 36% of sessions are under 5 turns, and only 9% exceed 30 turns. An agent with a 20-turn budget is consuming more turns than most entire sessions -- that's a substantial investment, not a quick lookup.

| Agent archetype | Suggested turns | Character of work |
|----------------|----------------|-------------------|
| File/utility agent (explorer, file-ops, git-ops) | 3-8 | Read specific files, form opinion, return |
| Reviewer/critic (spec-reviewer, code-quality, design-critic) | 8-15 | Analyze an artifact, produce structured assessment |
| Architect/designer (zen-architect, systems-architect) | 12-20 | Multi-step reasoning, consider alternatives, produce spec |
| Writer/documenter (design-writer, technical-writer) | 5-10 | Produce output from already-gathered input |
| Implementer/builder (modular-builder, implementer) | 10-20 | Write code, run tests, iterate on failures |
| Fork skill sub-agents (e.g., adversarial review perspectives) | 5-8 | Single-perspective evaluation of a shared artifact |

**Why these numbers:** A mechanism plan without turn budgets will use whatever the orchestrator's default is. In practice, this means agents explore until they hit the global loop limit, producing diminishing-return work in the later turns. Explicit budgets force focused work and make cost predictable.

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

**Mode adoption in practice.** Mode activation has very low adoption compared to skills -- the gate policy (warn on first attempt, requiring retry) creates friction that discourages programmatic activation. Meanwhile, skills that provide equivalent behavioral guidance (e.g., `brainstorming`, `writing-plans`) are loaded in the vast majority of sessions with no friction. **Design implication:** If your mechanism plan relies on modes for behavioral guidance that isn't safety-critical, consider whether a companion skill achieves the same result with less friction. Reserve modes for their structural strength -- tool policies and explicit phase boundaries that change what the session *can do*, not just what it *should do*.

### Recipe Approval Gates

Staged recipes pause execution between stages and require explicit `approve` or `deny`. This is the right mechanism when:
- Work is expensive and difficult to undo (implementation, deployment)
- The user needs to review an intermediate artifact (design doc, plan)
- Different stages might be routed to different people

Approval gates support messages (`approve(message="merge")`) that subsequent stages can read, allowing the user to influence downstream behavior.

### Recipe Denial Handling

When a user denies an approval gate, the recipe stops. The current behavior is terminal -- there is no built-in retry or feedback loop. Design implications:

- **Design stages so partial completion is safe.** If stage 1 produces artifacts and stage 2 is denied, the stage 1 artifacts should be independently useful or easy to clean up.
- **Consider a revision pattern.** If denial commonly leads to "try again with adjustments," build the recipe so the denied stage can be re-executed with modified context. This may require manual `recipes(operation="execute")` with updated parameters rather than automatic retry.
- **Document expected denial outcomes.** A mechanism plan should state what happens at each gate on denial -- "user can re-run with different parameters" or "artifacts from prior stages remain, no cleanup needed."

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

**Key design decisions and their rationale:**

- **Three agent model roles** (`reasoning`, `critique`, `writing`) rather than one default model: the design workflow moves through distinct cognitive phases -- deep analysis, adversarial evaluation, and sustained prose -- each with different model requirements. Routing the critic to `critique` (extra-high reasoning effort) produces sharper evaluations than the default `general` model would.
- **Content files (~4K tokens) kept as always-loaded content, not skills:** Agents @mention these files in their own sub-sessions, so converting them to skills wouldn't reduce child session costs -- only root session costs. The trade-off was judged acceptable for a design-focused bundle where these frameworks are relevant on most turns. A general-purpose bundle should convert reference frameworks to skills.
- **`recipes` not listed as safe in design modes:** Unlike the superpowers bundle (where `recipes` being safe created a loophole allowing full implementation pipelines from within `write-plan`), the systems-design modes keep `recipes` out of the safe tool list. This is structural enforcement: the design phase cannot accidentally launch implementation workflows.
- **Fork skill for adversarial review (not an agent):** The 5-perspective review spawns sub-agents internally but doesn't need persistent state, resumable sessions, or its own tool surface. A fork skill is lighter-weight infrastructure for the same parallel pattern.
- **No turn budgets were specified in the initial plan** -- the evaluation flagged this as the largest gap. Recommended budgets derived from task complexity: architect ANALYZE 10-15, DESIGN 15-20, critic 10-15, writer 5-8, adversarial sub-agents 5-8.

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

## Mechanism Plan Review Checklist

When reviewing a mechanism plan (your own or someone else's), verify each of these. The list is ordered to match the guide's structure.

**Mechanism assignment:**
- [ ] Each concern has one primary owner (no duplicated authority)
- [ ] Decision hierarchy correctly applied: policy → mode, workflow → recipe, expertise → skill, reasoning → agent
- [ ] No anti-patterns from the Failure Modes table (especially composition loopholes and workflow-in-skills)

**Enforcement levels:**
- [ ] Critical behaviors are structurally enforced (tool policies, hook gating), not just described in prose
- [ ] Tool policy explicitly names safe, warned, and blocked tools for each mode
- [ ] Composition loopholes assessed: if `delegate` or `recipes` are safe while write tools are blocked, is that intentional?

**Context economics:**
- [ ] Per-turn token floor calculated (content files + composed behaviors + L1 visibility + mode body + hooks)
- [ ] Floor is below 15-20% of context window (above this, audit for content-to-skill conversions)
- [ ] Always-loaded content files are justified -- could any be skills (loaded on demand) or agent @mentions (loaded in child context only)?
- [ ] Skill compaction risk assessed for critical methodology or workflow skills

**Execution design:**
- [ ] Turn budgets specified for all agents and recipe steps
- [ ] Model roles assigned with fallback chains ending in `general` or `fast`
- [ ] Parallelism opportunities identified (independent tasks → parallel agents or recipe foreach)
- [ ] Sequential dependencies identified (findings-compound tasks → sequential with `context_scope="agents"`)

**Human-in-the-loop:**
- [ ] Checkpoints placed at high-stakes transitions (after analysis/before implementation, after implementation/before deployment)
- [ ] Approval gate denial behavior documented (what happens on deny? can the user retry with modifications?)
- [ ] Low-frequency, high-stakes: recipe gates. High-frequency, low-stakes: hooks. Phase transitions: modes.

---

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
