---
mode:
  name: systems-design
  description: Structured system design exploration -- model the system, explore alternatives, analyze tradeoffs, validate design section-by-section with the user.
  tools:
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
      # todo: design has 8 phases; tracking progress through them is the point.
      # mode: bundle ships independently; users manage their own transitions.
      # team_knowledge: "does the team already have X?" is a core design question.
      - todo
      - mode
      - team_knowledge
    warn:
      - bash
    block:
      # Write tools blocked -- this mode produces design thinking, not files.
      # File creation is delegated to systems-design-writer in Phase 8.
      - write_file
      - edit_file
      - apply_patch
      - python_check
  default_action: block
  allow_clear: false
---

# System Design Mode

Structured design exploration. Write tools are blocked -- this mode produces
design thinking, not files. Document creation is delegated to `systems-design-writer`.

**Companion skill:** `systems-design-methodology` -- load it at mode entry for the
full 8-phase workflow, delegation patterns, and user validation checkpoints.

## Agents

| Agent | Role | Phases |
|-------|------|--------|
| `systems-architect` | System-level reasoning (ANALYZE / DESIGN / ASSESS) | 1, 3, 4, 6 |
| `systems-design-critic` | Adversarial review from 5 perspectives | 5 (optional) |
| `systems-design-writer` | Pure document production, zero design decisions | 8 |

## Skills

| Skill | Phase |
|-------|-------|
| `systems-design-methodology` | All -- companion skill for this mode |
| `architecture-primitives` | 3 -- selecting patterns for candidates |
| `tradeoff-analysis` | 4 -- detailed tradeoff methodology |
| `adversarial-review` | 5 -- parallel 5-perspective stress test |
| `system-type-web-service` | 3 -- when designing web services or APIs |
| `system-type-event-driven` | 3 -- when designing event-driven systems |

---

@systems-design:context/tradeoff-frame.md

@systems-design:context/adversarial-perspectives.md

@systems-design:context/system-design-principles.md
