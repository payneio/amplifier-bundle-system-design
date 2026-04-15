# Behavior Maker: Journey Log

## What This Project Is

A bundle for modeling and planning Amplifier bundles using mechanisms. It provides recipes and tooling for the bundle development lifecycle: going from objectives to behavioral models to implementation plans to implementations -- and back.

## How We Got Here

### Phase 1: Understanding Mechanisms (sessions in amplifier-system-design)

We started by creating comprehensive documentation of Amplifier's bundle mechanisms -- the composable primitives that make up bundles:

- **7 mechanism types documented**: modes, agents, skills, recipes, hooks, content/context files, tools
- **Per-mechanism reference docs** created in `docs/understanding-mechanisms/mechanisms/`
- **Bundle developer's guide** created: `docs/understanding-mechanisms/designing-with-mechanisms.md` -- a comprehensive guide for designing bundles using these primitives, including token management considerations, design patterns, and anti-patterns

The guide went through multiple iterations (see `docs/mechanism-planning/` for the revision history) and was empirically validated against 7,868 real Amplifier sessions (see `docs/mechanism-modeling/8_cross-session-evidence-analysis.md`).

### Phase 2: Mechanism Planning (sessions in amplifier-system-design)

We used the mechanism guide to design the systems-design bundle:

1. **Wrote objectives**: `docs/examples/systems-design/objectives.md` -- what the bundle should accomplish
2. **Created a mechanism plan**: `docs/examples/systems-design/mechanism-plan.md` -- a complete mechanism inventory specifying every mode, agent, skill, recipe, hook, and context file, with enough detail for a bundle developer to build it
3. **Implemented the bundle** from the plan (the actual systems-design bundle in amplifier-bundle-system-design)

The planning was conversational -- objectives + mechanism guide given to the AI, which produced the plan through brainstorming discussion. No recipe or formal pipeline was involved at this stage.

### Phase 3: Behavioral Modeling (sessions in amplifier-system-design)

We created tooling to model bundle behavior:

1. **Implementation-to-model recipe** (`recipes/bundle-behavioral-spec.yaml`): Takes an implemented bundle, deterministically parses its composition (dependency tree, tool policies, delegation maps), then LLM-extracts behavioral information from each component, and synthesizes a behavioral model document. Uses Python scripts for deterministic parsing (`recipes/scripts/`).

2. **Generated a model from the systems-design implementation**: `docs/examples/systems-design/behavioral-model-from-implementation.md` -- 840-line behavioral specification covering tool governance, mode behaviors, agent behaviors, skill workflows, recipe pipelines, and behavioral invariants.

3. **Earlier validation work** on the foundation bundle is documented in `docs/mechanism-modeling/` (files 3-6), including a real comparison of what the model predicted vs what actually happened in a session.

### Phase 4: Plan-to-Model (the current breakthrough)

The key insight: a mechanism plan contains all the same information as a behavioral model, just organized differently. So we asked: **can we generate a behavioral model from a plan, before implementing anything?**

1. **Created plan-to-model recipe** (`recipes/plan-to-behavioral-model.yaml`): Takes a mechanism plan document, LLM-extracts structured JSON of all mechanisms, then synthesizes a behavioral model document.

2. **Smoke-tested it** against the systems-design plan:
   - Generated: `docs/examples/systems-design/behavioral-model-from-plan.md` (v1)
   - Generated: `docs/examples/systems-design/behavioral-model-from-plan-v2.md` (v2, after extraction fixes)

3. **Compared plan-derived vs implementation-derived models** (see `docs/mechanism-modeling/10_plan-vs-implementation-model-comparison.md`):
   - Models are complementary, not duplicative (~35-40% unique content each)
   - Plan-derived model caught a mechanism the implementation model missed (hooks-design-context)
   - Implementation-derived model has data the plan can't provide (transitive dependencies, composition loopholes)
   - Plan-derived model's self-identified limitations are 90% accurate

4. **Compared plan-derived model vs actual implementation** to check fidelity:
   - Found 5 drifts between the model and the implementation
   - 3 were extraction errors in the recipe (fixed in v2): model_role fallback arrays, approval gate semantics, anonymous vs named delegations
   - 2 were genuine plan-vs-implementation divergence (review recipe agent swap, default value flip) -- these are drifts the model correctly surfaces

### Phase 5: Lifecycle Question (where we are now)

The demonstrated lifecycle so far is:

```
Objectives → Plan → Implementation → Behavioral Model (from implementation)
                  → Behavioral Model (from plan)
```

The open question is: **what's the optimal lifecycle?** Three candidates:

**A: Objectives → Plan → Model → Implementation**
The plan is the primary design artifact. The model validates the plan before implementation.

**B: Objectives → Model → Plan → Implementation**
The model is the primary design artifact (behavioral specification). The plan is derived from the model as a construction guide.

**C: Objectives → Model → Implementation**
Skip the plan entirely. The model + mechanism guide provides enough information for an implementer.

Our current thinking leans toward **B or C**. The model answers "what should this look like when it's working?" which is a more natural question after objectives than "what files should I create?" The plan's value is as a construction blueprint, not a design artifact. If the implementer has the mechanism guide, the plan may be derivable or skippable.

Key evidence supporting this: the plan and model contain overlapping information. The plan adds construction details (file paths, YAML wiring) and design rationale. The model adds behavioral scenarios (mechanism chain traces that function as integration tests for the design).

## What Exists in This Repo

### Recipes

| Recipe | Purpose | Status |
|--------|---------|--------|
| `recipes/plan-to-behavioral-model.yaml` | Generate behavioral model from mechanism plan | Working, tested, v2 with extraction fixes |
| `recipes/bundle-behavioral-spec.yaml` | Generate behavioral model from implemented bundle | Working, tested on foundation and systems-design bundles |

### Recipe Scripts (for bundle-behavioral-spec)

| Script | Purpose |
|--------|---------|
| `recipes/scripts/parse_bundle_composition.py` | Deterministic parsing of bundle composition from registry.json |
| `recipes/scripts/analyze_composition_effects.py` | Compute tool availability, delegation necessity, composition loopholes |
| Tests in `recipes/scripts/tests/` | Unit tests for both scripts |

### Documentation

| Directory | Contents |
|-----------|----------|
| `docs/understanding-mechanisms/` | Mechanism reference docs + designing-with-mechanisms guide |
| `docs/mechanism-modeling/` | Research artifacts: behavioral specs, flow analyses, cross-session evidence |
| `docs/mechanism-planning/` | Plan iteration history and evaluation |
| `docs/examples/systems-design/` | Complete example: objectives → plan → model (from both plan and implementation) |

## What To Build Next

1. **Objectives → Model recipe**: Can we go directly from objectives to a behavioral model, skipping the plan? This would validate lifecycle option C.

2. **Model → Plan recipe**: Can we derive a construction plan from a behavioral model + the mechanism guide? This would validate lifecycle option B.

3. **Plan schema**: The mechanism plan format emerged naturally from conversation. Formalizing it as a schema would enable more deterministic extraction and validation.

4. **Drift detection recipe**: Automatically compare a plan-derived model against an implementation-derived model to detect where implementation has drifted from design intent.

5. **Bundle as a proper Amplifier bundle**: This directory needs bundle.md, behavior YAML, and proper bundle structure to be composable in the Amplifier ecosystem.

## Key Design Decisions

1. **The behavioral model IS the primary design artifact.** It describes observable behavior (what triggers what, what the user sees, what mechanisms activate). The plan is a construction blueprint that can be derived from the model.

2. **The behavioral model has an "inventory" section (mechanism definitions) and a "scenarios" section (mechanism chain traces).** The inventory IS the model definition. The scenarios are test cases that validate the model is coherent. They're not examples -- they're traces through the state machine the inventory defines.

3. **Plan-derived and implementation-derived models are complementary, not competing.** Use them at different lifecycle stages: plan-derived for design validation, implementation-derived for runtime verification, comparison for drift detection.

4. **The designing-with-mechanisms guide is central.** It provides the vocabulary of mechanism primitives and their behavioral properties. Both planning and modeling depend on this shared vocabulary.

---

*This document was created on 2026-04-15 from session 7ee82b2d in the amplifier-system-design project.*
