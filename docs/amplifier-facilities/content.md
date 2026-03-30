# Content (Context Files): Static Knowledge Injection

## What It Is

Context files are plain markdown documents that get injected verbatim into the
LLM's system prompt. They are the simplest and most direct way to shape agent
behavior -- essentially "instruction manuals" the LLM reads at the start of each
turn.

## How It Works

### Two Loading Mechanisms

| Mechanism | Syntax | Where Used | Composition |
|-----------|--------|-----------|-------------|
| `@mentions` | `@bundle:path/file.md` | Markdown body | Stays with this instruction |
| `context.include` | `bundle:path/file.md` | YAML behaviors | Accumulates across composition |

Critical distinction: `@mentions` are replaced when another bundle overrides the
instruction. `context.include` propagates through the composition chain.

### @Mention Loading Pipeline

1. **Parse**: Regex extracts `@namespace:path` from markdown (excluding code blocks)
2. **Resolve**: Maps namespace to bundle, resolves to filesystem path
3. **Recursive load**: Content is read and scanned for nested @mentions (depth 3)
4. **Deduplicate**: SHA-256 hash prevents same content appearing twice
5. **Wrap**: Content formatted as `<context_file paths="@bundle:path -> /abs/path">...</context_file>`
6. **Assemble**: Prepended before main instruction in system prompt

### Dynamic System Prompt Factory

The system prompt is NOT static. A factory function is called on every LLM turn,
re-reading @mentioned files fresh. Files changed on disk are picked up next turn.

### Static vs Dynamic Context

| Aspect | Static (context files) | Dynamic (message history) |
|--------|----------------------|--------------------------|
| What | Markdown files from bundles | User/assistant/tool messages |
| When loaded | Session start + re-read each turn | Accumulated during session |
| Managed by | System prompt factory | ContextManager module |
| Compaction | Not compacted (always full) | Auto-compacted at token budget |

### ContextManager Module (Message History)

Separate from static context files, the ContextManager handles conversation
message history. Key capability: `get_messages_for_request(budget)` returns
messages fitting the token budget, compacting internally if needed. Compaction is
non-destructive ephemeral windowing -- the full history is always preserved.

### Context Organization Patterns

Foundation organizes context by audience:
- `shared/` -- core instructions for all sessions
- `agents/` -- context for agent-related behaviors
- `amplifier-dev/` -- development-specific (only loaded when that behavior is composed)

Superpowers organizes by concern:
- `philosophy.md` -- 7 core principles
- `instructions.md` -- standing orders + mode recommendation
- `tdd-depth.md` -- 474-line TDD reference
- `debugging-techniques.md` -- root-cause tracing patterns

### The "Context Sink" Pattern

Root sessions stay thin (only awareness pointers). Agent sessions carry heavy
documentation via @mentions. When an agent spawns, its @mentioned docs load in
its context -- not the parent's. This preserves the parent's context window.

### Key Implementation Files

- `amplifier-foundation/mentions/parser.py` -- @mention extraction
- `amplifier-foundation/mentions/resolver.py` -- Namespace resolution
- `amplifier-foundation/mentions/loader.py` -- Recursive loading + dedup
- `amplifier-foundation/bundle/_prepared.py:243-297` -- System prompt factory
- `amplifier-core/python/amplifier_core/interfaces.py:166-212` -- ContextManager protocol

## Relevance to System Design Bundle

Context files are the **foundation layer** of our system design bundle. They
establish the persistent knowledge and behavioral framework the agent always has.

### Immediate Opportunities

- **System design principles**: A core context file establishing the principles,
  patterns, and practices for system design. Not Amplifier-specific, but generic
  systems design wisdom: model the system before solving, force multiscale reasoning,
  tradeoff analysis over best-practice mimicry, causal reasoning, architectural
  primitives.

- **Structured response template**: A context file that establishes the default
  template for design work: problem framing, assumptions, boundaries, components,
  flows, risks, tradeoffs, design, migration, metrics. This ensures the agent
  doesn't produce shallow output.

- **Simplicity principles**: From the agentic-system-design doc -- structural
  simplicity, simplicity under change, simplicity as constraint. Including the
  compact simplicity rubric.

- **System type guides**: Context files for specific system types (web service,
  distributed system, etc.) that provide domain-specific patterns and pitfalls.
  These could be loaded conditionally based on what type of system is being designed.

### Context vs Skills

For our bundle, the key decision is which knowledge goes in always-present context
files vs on-demand skills:

| Put in Context (Always Present) | Put in Skills (On Demand) |
|--------------------------------|--------------------------|
| Core design principles | System-type specific patterns |
| Structured response templates | Tradeoff analysis methodology |
| Simplicity rubrics | Adversarial review perspectives |
| Standing behavioral orders | Architecture primitive catalog |

The principle: context files for things the agent should ALWAYS consider, skills
for specialized knowledge loaded when relevant. Context files cost tokens every
turn, so they should be concise and high-value.

### Token Budget Considerations

Context files consume tokens on every turn. The foundation bundle already loads
substantial context. Our system design content needs to fit within reasonable
budgets. Options:
- Keep core principles concise (~2K tokens)
- Use skills for detailed methodology (loaded on demand)
- Use the context sink pattern (heavy docs in agent sessions only)
- Use `context.include` in behaviors so only composed content loads
