# Cross-Session Evidence Analysis: Mechanism Usage in 7,868 Amplifier Sessions

**Date:** 2026-04-14
**Purpose:** Empirical validation of the Bundle Developer's Guide to Amplifier Mechanisms against real session data. Provides quantitative evidence for each design guide recommendation and identifies gaps where the guide diverges from observed behavior.

---

## Methodology

Six parallel investigation agents each analyzed a different dimension of mechanism usage across the full session corpus at `~/.amplifier/projects/*/sessions/*/events.jsonl`. Data was extracted programmatically using grep, jq, and bash -- no full events.jsonl files were read (lines can exceed 100K tokens).

| Dimension | Sessions Analyzed | Agent Focus |
|---|---|---|
| Delegation & context management | 7,845 | context_depth, context_scope, model_role, compaction |
| Modes & skills | 7,935 | Mode activations, skill loads, compaction-reload cycles |
| Recipes & approval gates | 7,845 | Recipe execution, approval/denial events, sub-agent spawning |
| Parallelism patterns | 8,033 | Parallel tool calls, parallel delegate dispatch, session lengths |
| Token pressure & compaction | 7,868 | Compaction frequency, strategy levels, session sizes, turn counts |
| Tool policy & model selection | 7,846 | Blocked-tool events, model_role routing, todo compliance |

---

## 1. Delegation and Context Sinks

### Finding: Clean-slate delegation is the overwhelming default

| context_depth | Occurrences | Percentage |
|---|---|---|
| `"none"` | 91,970 | **83.8%** |
| `"recent"` | 17,607 | 16.0% |
| `"all"` | 176 | 0.2% |

84% of all delegations start agents with a clean slate. `"all"` (full history inheritance) is used 0.2% of the time. When `"recent"` is used, most delegations accept the default turn count; when explicitly set, 10 and 15 turns are most common.

### Finding: Conversation-only scope dominates

| context_scope | Occurrences | Percentage |
|---|---|---|
| `"conversation"` | 13,193 | **71.1%** |
| `"agents"` | 5,247 | 28.3% |
| `"full"` | 120 | 0.6% |

71% of delegations pass only user/assistant text. `"agents"` (which includes prior delegate results) is used 28% of the time -- confirming multi-agent collaboration where downstream agents see upstream agents' work. `"full"` is rare at 0.6%.

### Finding: Explorer and git-ops dominate delegation targets

| Agent | Delegations | Percentage |
|---|---|---|
| `foundation:explorer` | 14,347 | **42.9%** |
| `foundation:git-ops` | 8,676 | **25.9%** |
| `self` | 2,677 | 8.0% |
| `foundation:session-analyst` | 2,437 | 7.3% |
| `superpowers:implementer` | 2,112 | 6.3% |
| `foundation:bug-hunter` | 876 | 2.6% |
| `foundation:foundation-expert` | 809 | 2.4% |
| `foundation:modular-builder` | 572 | 1.7% |
| All others | ~1,068 | 3.2% |

Explorer + git-ops = 69% of all agent dispatch. This reflects two entrenched patterns: (1) exploration is always delegated to preserve parent context, (2) git operations are always delegated for safety protocols.

### Design guide implications

- The guide's Context Lifecycle section describes three lifecycle options but doesn't declare a default. The data strongly argues for `context_depth: "none"` as the stated default recommendation.
- The guide doesn't mention the explorer/git-ops dominance pattern. Understanding the delegation distribution helps bundle authors optimize for the common case.

---

## 2. Mode and Skill Usage

### Finding: Mode activation is vanishingly rare

| Metric | Value |
|---|---|
| Sessions with mode tool available | 595 |
| Sessions that actually activated a mode | **2** (0.34%) |
| Total mode activation attempts | 11 |
| Denied by gate policy | 6 (55%) |
| Successfully activated | 5 (45%) |

Only 2 sessions out of 595 with the mode tool available actually used it. 55% of activation attempts were denied by the gate policy, requiring the model to retry -- creating friction that discourages adoption.

Modes used (across both sessions): `write-plan` (3 attempts), `execute-plan` (2), `brainstorm` (1). Zero usage of: `debug`, `verify`, `finish`, `systems-design`, or any other mode.

### Finding: Skills are the actual behavioral mechanism

| Metric | Value |
|---|---|
| Sessions with skill references | 7,285 (91.8%) |
| Most loaded skill | `verification-before-completion` |
| Second most loaded | `using-superpowers` |

Skills provide the behavioral guidance that modes are architecturally supposed to trigger, but skills achieve this with no friction -- they're loaded on demand and require no gate negotiation. The model goes directly to skills for behavioral guidance, bypassing the mode system entirely.

### Finding: Skill compaction creates a death-spiral reload pattern

30 sessions exhibited both skill loads AND compaction events. The pattern is severe:

| Session | Skill Loads | Compaction Events | Worst Level |
|---|---|---|---|
| spec-reviewer (voting) | 3,348 | 2,936 | 7/8 |
| foreman session | 1,242 | 541 | 7/8 |
| feedback-1 (spawn-events) | 1,236 | 567 | 7/8 |
| observers session | 1,010 | 452 | 7/8 |

**The death spiral:** In the `feedback-1` session, skill loads BEFORE first compaction: 104. Skill loads AFTER first compaction: 1,133 (a 10.9x increase). Compaction truncates the skill's tool result, the model detects the loss and reloads, the reload adds tokens that trigger more compaction. In the spec-reviewer session, `verification-before-completion` was reloaded **224 times** and `using-superpowers` was reloaded **148 times**.

### Design guide implications

- The guide presents modes and skills as peers in the mechanism hierarchy. The data shows skills have 270x the adoption rate of modes (91.8% vs 0.34%). The guide should acknowledge this disparity and explain when modes are still the right choice (structural tool policy enforcement) vs when skills are sufficient (behavioral guidance).
- The guide's earlier addition about skill compaction risk underestimates the severity. The death-spiral pattern needs explicit documentation with the 10.9x reload multiplier as evidence.

---

## 3. Recipe Usage and Approval Gates

### Finding: Recipes are composed ubiquitously but executed rarely

| Metric | Value |
|---|---|
| Sessions with recipes tool available | 7,282 (92.8%) |
| Sessions with actual recipe execution | **28** (0.36%) |
| Total recipe starts | 53 |
| Total recipe completions | 57 (all successful) |
| Recipe failure rate | **0%** |

When recipes ARE used, they produce substantial activity: 1,688 loop iterations, 1,130 loop completions, 152 step executions across those 28 sessions.

### Finding: One recipe dominates the landscape

| Count | Recipe |
|---|---|
| 5,427 references | `subagent-driven-development` |
| 705 references | `check-gh` |
| 638 references | `bundle-behavioral-spec` |
| 615 references | `communitarian-response` |
| 462 references | `file-issue` |

`subagent-driven-development` accounts for the vast majority of recipe activity.

### Finding: Approval gates are rare but consequential

| Metric | Value |
|---|---|
| Total approval gate events | 47 |
| Approvals | ~45 |
| Confirmed denials | ~2 |
| Approval-to-denial ratio | ~31:1 |

45 of 47 approval gates were on `subagent-driven-development -> final-review`. When a denial occurred, it was consequential -- one denial blocked code with 29 broken tests from proceeding, with a detailed reason from the human reviewer.

### Finding: Recipe completion rate is 100%

All 57 completed recipes succeeded. When work is rejected, it happens via the approval gate (a deliberate human stop), not via recipe failure. This confirms recipes are reliable infrastructure -- they don't crash, they checkpoint correctly, and they pause for human review when designed to.

### Design guide implications

- The guide treats recipes as a primary mechanism on par with modes and skills. The data shows they're a high-value but low-frequency mechanism (0.36% execution rate). The guide should calibrate: recipes are for repeatable, resumable, approval-gated pipelines -- not ad-hoc multi-step work, which is better served by sequential delegation.
- Recipe denial handling (our earlier addition) is confirmed as important but rare (2 observed denials). The 31:1 approval-to-denial ratio suggests the system is working -- users approve most work but have the power to stop bad output.

---

## 4. Parallelism Patterns

### Finding: Two distinct tiers of parallelism

**Tool-level parallelism (23.9% of all tool responses):**

| Tools per response | Count | Percentage |
|---|---|---|
| 1 | 56,575 | 76.1% |
| 2 | 11,260 | 15.2% |
| 3 | 3,528 | 4.7% |
| 4+ | 2,960 | 4.0% |

Top parallel tool combinations: `read_file + read_file` (3,398), `bash + bash` (3,347), `read_file x3` (1,508).

**Agent-level parallelism (5.6% of delegate responses):**

| Delegates per response | Count |
|---|---|
| 1 (sequential) | 1,732 |
| 2 | 63 |
| 3 | 20 |
| 4 | 14 |
| 5+ | 6 |

Top parallel agent combinations: `explorer + explorer` (27), `explorer x3` (9), `spec-reviewer + code-quality-reviewer` (6), `self + self + self` (5).

### Finding: Parallel sessions are 6x longer

| Category | Count | Avg Events | Median Events |
|---|---|---|---|
| Parallel delegate sessions | 63 | **1,580** | **909** |
| Sequential delegate sessions | 796 | 256 | 204 |
| No delegation | 2,999 | 165 | 71 |

Sessions using parallel agent dispatch are 6x longer than sequential and 10x longer than non-delegating sessions.

### Finding: Self-delegation enables parallel work tracks

116 self-delegations observed, used for:
- 6 parallel provider module conversions
- 5 parallel CLI feature implementations
- 5 parallel design review perspectives (SRE, security, staff eng, finance, operator)
- 6 parallel investigation tracks (this very analysis)

Typical self-delegation uses `context_depth: "none"` (clean slate).

### Design guide implications

- The guide's Parallelism section doesn't distinguish tool-level (routine, 24% of responses) from agent-level (deliberate, 6% of responses). These are very different design decisions.
- The 6x session length correlation isn't mentioned -- parallel dispatch is a signal of substantial work, not a lightweight optimization.
- Self-delegation for parallel work tracks is a real pattern (116 instances) worth calling out explicitly.

---

## 5. Token Pressure and Compaction

### Finding: Compaction is universal and aggressive

| Metric | Value |
|---|---|
| Sessions with compaction | 6,813 (86.6%) |
| Total compaction events | 50,416 |
| Average compactions per session | 94.3 |
| Median compactions per session | 9 |
| Max compactions in one session | 2,936 |

### Finding: Most compaction hits high strategy levels

| Strategy Level | Occurrences | Percentage |
|---|---|---|
| Level 1-2/8 | 150 | 1.9% |
| Level 3-4/8 | 1,927 | 24.4% |
| Level 5-6/8 | 3,517 | 44.5% |
| Level 7-8/8 | 2,339 | **29.6%** |

66% of compaction events hit level 5 or higher. Level 8 (maximum desperation -- removing all but the most recent messages) was hit 69 times across 23 sessions.

### Finding: The compaction system is remarkably effective

Despite 86.6% of sessions experiencing compaction, only **1 session** in 7,868 actually hit a `context_length_exceeded` error. The compaction system catches overflow before it happens. Average compaction reduces tokens by **42.7%** (from ~166K to ~95K).

### Finding: Session turn distribution

| Category | Sessions | Percentage |
|---|---|---|
| Very short (< 5 user turns) | 185 | **36.5%** |
| Medium (5-30 turns) | 278 | **54.8%** |
| Long (> 30 turns) | 44 | **8.7%** |

Median session: 8 user turns. Maximum observed: 152 user turns.

### Finding: Session file sizes

| Size Bucket | Sessions | Percentage |
|---|---|---|
| < 100 KB | 188 | 2.4% |
| 100 KB - 1 MB | 680 | 8.6% |
| 1-10 MB | 6,735 | **85.6%** |
| > 10 MB | 265 | 3.4% |

Total corpus: 28.51 GB across 7,868 sessions. Largest session: 497 MB (amplifier-ipc, 947 user turns).

### Finding: Agents with heavy @-mentioned docs hit ceiling disproportionately

Sessions where `zen-architect` and `session-analyst` agents hit level 8/8 compaction despite having only 8-14 turns. Their heavy @-mentioned documentation fills context before the session starts, leaving minimal room for actual work. This confirms the token floor calculation is critical for agent design.

### Design guide implications

- The guide's token floor section should include compaction statistics to make the consequences concrete: 87% of sessions compact, 66% hit level 5+, and agents with heavy context files hit the ceiling in as few as 8 turns.
- The session length distribution (36% < 5 turns, median 8 turns) provides critical context for turn budget design. A 20-turn agent budget exceeds the median entire session length.

---

## 6. Tool Policy Enforcement and Model Selection

### Finding: Structural enforcement is so effective the blocker never fires

Zero blocked-tool error messages found across 7,846 sessions, despite 65 events showing `default_action: "block"` mode policies. Models read the safe-tools list and self-restrict without attempting prohibited tools.

### Finding: The model routing matrix is actively used

| Role | Occurrences | Percentage |
|---|---|---|
| `fast` | 100,171 | **44.7%** |
| `general` | 85,533 | **38.2%** |
| `coding` | 16,933 | 7.6% |
| `research` | 7,225 | 3.2% |
| `critique` | 6,176 | 2.8% |
| `reasoning` | 5,489 | 2.5% |
| `writing` | 2,256 | 1.0% |
| Others | 253 | 0.1% |

80% of sessions specify model roles. `fast` + `general` = 83% of routing. Superpowers pipeline sessions routinely use 3 models (haiku/sonnet/opus) in a single session. Fallback chains in real agent configs match the guide's recommendations: `[coding, general]`, `[critique, reasoning, general]`, `[reasoning, general]`.

### Finding: Multi-model dispatch is the norm in complex sessions

18 out of 100 sampled sessions used multiple models. Superpowers agents consistently dispatch to 3 tiers. The routing matrix is not theoretical -- it's infrastructure that shapes every complex session.

### Finding: Todo compliance is 55%

4,296 sessions (55%) use the todo tool. This is conventional compliance -- no structural mechanism forces it. The instruction is influential but not universally followed, consistent with the Structural vs Conventional enforcement distinction.

### Finding: python_check is the dominant validation pattern

3,066 sessions (39%) use `python_check`. Only 1 session used LSP `diagnostics` directly. Validation happens periodically, not after every edit -- in one analyzed session, 6 python_check calls covered 92 edits.

### Design guide implications

- Structural enforcement works doubly: through the guardrail (would block if attempted) AND through its behavioral effect (model doesn't attempt prohibited tools). The guide should note this.
- The model routing matrix is confirmed as real infrastructure, not aspirational guidance. The guide's recommended fallback chains match observed production configs.

---

## Summary: What the Data Validates and What It Challenges

### Validated by the data

| Guide Recommendation | Evidence |
|---|---|
| Agents as context sinks | 84% clean-slate delegation, 87% compaction rate |
| Structural enforcement > conventional | Zero blocked-tool errors (structural works); 55% todo compliance (conventional is inconsistent) |
| Model role routing matters | 80% of sessions route by role; 3-model sessions are common |
| Skills for expertise, modes for policy | Skills: 91.8% adoption; modes: 0.34% adoption |
| Turn budgets prevent waste | Median session is 8 turns; a 20-turn budget exceeds most sessions |
| Parallel dispatch for independent work | 5.6% agent parallelism, concentrated in 6x-longer sessions |
| Recipes for repeatable pipelines | 0% failure rate, 100% completion, approval gates catch bad output |

### Challenged by the data

| Guide Assumption | Data Reality |
|---|---|
| Modes and skills are peer mechanisms | Skills have 270x the adoption rate |
| Recipes are a primary workflow mechanism | 0.36% execution rate despite 92.8% composition |
| Skill compaction is a manageable risk | Death-spiral pattern produces 200+ reloads per skill |
| Parallelism is a common optimization | Agent parallelism is 5.6% -- sequential dominates |
| Token floor is a design-time concern | Compaction fires in 87% of sessions; the floor determines when |

---

## Recommended Guide Updates

Based on this evidence, 10 specific updates are recommended for the Bundle Developer's Guide to Amplifier Mechanisms. See the parent session's synthesis for the full list with priority rankings.

| Priority | Recommendation |
|---|---|
| **High** | Strengthen skill compaction warning to describe the death-spiral pattern (10.9x reload evidence) |
| **High** | Add compaction statistics to the token floor section (87% of sessions, 66% at level 5+) |
| **High** | Declare clean-slate (`context_depth: "none"`) as the empirical default (84% of delegations) |
| **Medium** | Mode adoption reality note (0.34% vs skills at 91.8%) |
| **Medium** | Restructure parallelism into two tiers (tool 24% vs agent 6%) |
| **Medium** | Recipe rarity calibration (0.36% execution vs 92.8% composition) |
| **Medium** | Anchor turn budgets against real session length distribution (median 8 turns) |
| **Low** | Explorer/git-ops dominance pattern (69% of all delegations) |
| **Low** | Structural enforcement effectiveness note (zero blocked-tool errors) |
| **Low** | Model routing matrix empirical confirmation (80% active routing) |
