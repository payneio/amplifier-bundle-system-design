---
mode:
  name: systems-design-review
  description: Evaluate an existing design or proposed change against the codebase -- multi-perspective review for integrity, constraints, failure modes, and hidden complexity.
  tool_policies:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - LSP
      - delegate
      - load_skill
      - recipes
      # -- Design-specific policy (diverges from foundation) --
      # todo: tracking review findings and action items across steps.
      # mode: users manage their own transitions (e.g. /systems-design-review -> /systems-design).
      # team_knowledge: "who owns this service?" and "what depends on this?" are core review questions.
      - todo
      - mode
      - team_knowledge
    warn:
      - bash
    block:
      # Write tools blocked -- this mode produces assessments, not code.
      - write_file
      - edit_file
      - apply_patch
      - python_check
    default_action: block
  allow_clear: false
---

# Design Review Mode

Evaluating an existing design or proposed architectural change. Write tools are
blocked -- this mode produces assessments, not code.

**Companion skill:** `systems-design-review-methodology` -- load it at mode entry for the
full 6-step workflow, delegation patterns, and user validation checkpoints.

## Agents

| Agent | Role | Steps |
|-------|------|-------|
| `systems-design-critic` | Adversarial review from 5 perspectives | 3 (Option A) |
| `systems-architect` | System-level assessment (ASSESS mode) | 2 (codebase evaluation) |

## Skills

| Skill | Step |
|-------|------|
| `systems-design-review-methodology` | All -- companion skill for this mode |
| `adversarial-review` | 3 (Option B) -- parallel 5-perspective stress test |
| `tradeoff-analysis` | 4 -- validating stated vs actual tradeoffs |

---

@system-design-intelligence:context/tradeoff-frame.md

@system-design-intelligence:context/adversarial-perspectives.md

@system-design-intelligence:context/system-design-principles.md
