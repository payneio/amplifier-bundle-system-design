# Mechanism Plan Evaluation

Evaluation of `docs/plans/2026-04-13-mechanism-plan.md` against `working/understanding-mechanisms/designing-with-mechanisms.md`.

---

## Where the plan aligns well

**Concern ownership (Authority Rule)**: Every concern has exactly one owner. Tool governance -> modes. Workflow ordering -> recipes. Expertise -> skills. Complex reasoning -> agents. Ambient awareness -> hook. Reference knowledge -> content. No duplicated authority.

**Mechanism selection hierarchy**: The plan follows the "ask in order" decision tree correctly. Policy enforcement lives in modes (not skills). Reusable knowledge is in skills (not smeared across recipe prompts). Isolated reasoning is in agents (not crammed into one monolithic prompt). The hook handles the one truly programmatic, deterministic behavior (filesystem scanning).

**Context sink pattern**: All 3 agents are proper context sinks. Architect loads 3 reference files in its own sub-session. Critic loads 2. Writer loads 1. Parent pays ~400 tokens per delegation. This matches the guidance's emphasis on agents as "the primary context management tool."

**Agent decomposition**: Three agents with non-overlapping roles (architect generates, critic stress-tests, writer documents) avoids "cognitive overload." Model roles match the guidance's mapping: `reasoning` for deep analysis, `critique` for flaw-finding, `writing` for prose production.

**Knowledge centralization**: Reference frameworks are centralized in content files. Agents @mention what they need. No copy-pasting across recipe prompts or skill bodies. This avoids "knowledge entanglement."

**Hook vs mode distinction**: The hook handles programmatic logic (scan filesystem). The mode is purely declarative (tool policy tiers + injected guidance). Correct per the "hooks are Python modules, modes are declarative .md files" distinction.

**Human-in-the-loop design**: Modes as phase boundaries (lightweight user activation), recipes with staged approval gates (hard stops at high-stakes transitions). Flat recipes for fire-and-forget workflows. Matches the guidance's recommendation to place checkpoints "after analysis, before implementation" and at phase transitions.

---

## Gaps the plan should address

### GAP 1: No turn budgets specified

Reference: guidance section "Turn Budgets and Bounded Work"

The guidance says: "An agent with an open-ended instruction like 'analyze the codebase' will use its entire turn budget exploring." And: "Match turn budget to task complexity."

The plan specifies zero turn budgets for any agent or recipe step. Each agent needs a `max_turns` recommendation:

| Agent | Suggested budget | Rationale (from guidance) |
|-------|-----------------|--------------------------|
| systems-architect (ANALYZE) | 10-15 turns | Thorough: explore, iterate, synthesize |
| systems-architect (DESIGN) | 15-20 turns | Thorough+: 3 candidates + tradeoff evaluation |
| systems-architect (ASSESS) | 10-15 turns | Thorough: survey, analyze boundaries |
| systems-design-critic | 10-15 turns | Thorough: read code from 5 perspectives |
| systems-design-writer | 5-8 turns | Focused: write + commit, no exploration |
| adversarial-review sub-agents (x5) | 5-8 turns each | Focused: one perspective, bounded scope |

Recipe steps should also specify per-step turn limits.

### GAP 2: No model role fallback chains

Reference: guidance section "Model Selection"

The guidance says: "Every chain should end with `general`." The plan specifies `reasoning`, `critique`, `writing` but without fallback chains. If the routing matrix doesn't have a model matching `critique`, there's no fallback.

Recommended:
- systems-architect: `[reasoning, general]`
- systems-design-critic: `[critique, reasoning, general]`
- systems-design-writer: `[writing, creative, general]`
- adversarial-review fork: `[critique, reasoning, general]`

### GAP 3: No ephemeral cost estimate

Reference: guidance section "Context Window Economics"

The plan budgets content files at ~4k tokens but ignores ephemeral per-turn costs:

| Source | Estimated per-turn cost |
|--------|------------------------|
| Content files (Layer 1) | ~4,000 tokens |
| Skills visibility (Layer 3) | ~700-1,000 tokens (7+ skill L1 descriptions) |
| Active mode body (Layer 3) | ~500-1,500 tokens (unknown, not specified) |
| Hook injection (Layer 3) | ~100-300 tokens (design doc inventory) |
| **Total per-turn floor** | **~5,300-6,800 tokens** |

The guidance warns: "Ephemeral injections add up silently... can easily consume 3-4K tokens per turn." Mode bodies in particular should be specified with a token budget. The guidance says: "Keep mode guidance focused; move detailed methodology to a companion skill loaded once on mode activation." -- the plan does this correctly (mode is governance, skill is methodology), but the mode body size still needs a budget.

### GAP 4: No behavior composition impact

Reference: guidance section "Context Window Economics"

The guidance warns: "Watch behavior composition. Each `includes:` that adds `context.include` entries increases the permanent system prompt floor. Audit the total context footprint when composing multiple behaviors."

The plan's ~4k content files compose on TOP of foundation's context files. What's the total? Foundation likely adds several thousand tokens. The plan should note the expected total and confirm it's sustainable.

### GAP 5: Methodology skill compaction risk

Reference: guidance section "Context Lifecycle"

The methodology skills are loaded once via `load_skill()`. Per the guidance, L2 skill loads enter message history (Layer 2) and are subject to compaction. The 8-phase methodology governs the ENTIRE conversation. If it gets compacted in a long session, the LLM loses the workflow structure.

Options:
- (a) Re-load the methodology skill at critical phase transitions
- (b) Document that the methodology skill should be kept concise (<2k tokens) so compaction removes other things first
- (c) Accept the risk and note that long sessions may need the user to re-load

### GAP 6: Approval gate denial behavior not specified

Reference: guidance section "Human-in-the-Loop Design"

The staged recipes have approval gates, but the plan doesn't specify what happens when a user DENIES at a gate. Does the recipe abort? Can it retry the previous stage? Can the user provide feedback that modifies the next attempt? Recipe denial is a real workflow -- design it explicitly.

---

## Potential issues to evaluate

### ISSUE 1: "Workflow hidden in skills"

Reference: guidance failure mode table

The guidance explicitly warns: "Step sequences encoded in skill bodies -- brittle, no checkpointing -> Move to a recipe."

The `systems-design-methodology` skill contains an 8-phase sequence with explicit ordering, phase gates (Phase 1 blocks until validation), and conditional skill loading at specific phases. This IS a workflow encoded in a skill.

**However**: This is a deliberate trade-off. The interactive version NEEDS conversation back-and-forth that recipes can't provide. Recipes drive automated pipelines; modes + skills drive interactive sessions. The same workflow exists as BOTH (systems-design-cycle recipe for automated, methodology skill for interactive).

**Recommendation**: Acknowledge this as a conscious departure from the guidance in the plan. Add a note: "The methodology skills encode workflow ordering as a known trade-off -- recipes can't handle interactive conversation. The same pipeline exists as a recipe for the automated path."

### ISSUE 2: Content files vs skills for reference frameworks

Reference: guidance rule of thumb #2

The guidance says: "A 3K-token methodology guide as a content file costs 3K tokens x every turn. As a skill, it costs ~100 tokens/turn (L1 visibility) plus 3K tokens once when loaded (L2), and that load is compactable."

The plan has 4 reference frameworks (~3.2k tokens total) as always-loaded content files:
- `system-design-principles.md` (~800)
- `tradeoff-frame.md` (~800)
- `adversarial-perspectives.md` (~800)
- `structured-design-template.md` (~800)

These ARE reference material. The root session only needs them during active design work. Outside of design phases, they're dead weight. Making them skills would save ~3.2k tokens/turn when no mode is active.

**Counter-argument**: Agents @mention these files in their sub-sessions. @mentions work with content files; they don't depend on the root session loading them. So converting to skills wouldn't break agent access.

**Recommendation**: Consider converting the 4 framework files from content to skills. Keep only `instructions.md` (~800 tokens) as always-loaded content. The methodology skill (loaded at mode entry) would trigger loading the relevant framework skills. Total permanent cost drops from ~4k to ~800 tokens.

### ISSUE 3: Exploration recipe parallelism mechanism

Reference: guidance section "Parallelism and Concurrency"

The plan says step 2 of `systems-design-exploration` uses "3 parallel delegate() calls in a single recipe step." But in a recipe step, a single agent runs. For that agent to make 3 parallel delegate() calls to itself, it would need to spawn 3 sub-agents of itself. This is mechanically unclear.

The guidance mentions recipe `foreach` as the natural parallelism pattern for recipes: "Each item gets its own step execution." A `foreach` over `[simplest-viable, most-scalable, most-robust]` would give clean per-candidate isolation.

**Recommendation**: Specify whether this is foreach-based parallelism or single-step-with-parallel-delegation. If the latter, spell out who the delegate targets are.

---

## Summary scorecard

| Guidance area | Rating | Notes |
|---------------|--------|-------|
| Attachment points | **Strong** | All mechanisms correctly attached |
| Concern ownership | **Strong** | One concern, one owner throughout |
| Mechanism selection | **Strong** | Decision hierarchy followed |
| Failure mode avoidance | **Good** | One known departure (workflow in skills), justified |
| Context window economics | **Needs work** | Content budget present, ephemeral/composition costs missing |
| Parallelism | **Needs clarification** | Fork skill correct, recipe parallelism unclear |
| Context lifecycle | **Good** | One risk (methodology skill compaction) |
| Model selection | **Good** | Roles correct, fallback chains missing |
| Turn budgets | **Missing** | No turn budgets for any mechanism |
| Human-in-the-loop | **Good** | Gate denial behavior unspecified |

The plan is architecturally sound. The gaps are mostly operational details (turn budgets, fallback chains, cost estimates) rather than fundamental design errors. The one structural question worth resolving is whether the 4 framework content files should be skills instead.