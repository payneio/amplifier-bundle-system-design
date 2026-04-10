# Checkpoint 5: Repeatable Design Workflows via Recipes

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add 3 recipe YAML files that orchestrate multi-step design workflows using our bundle's agents.
**Architecture:** Recipes are declarative YAML specs executed by the `recipes` tool. We create one staged recipe with approval gates (architecture-review), one flat recipe with parallel foreach (design-exploration), and one flat sequential recipe (codebase-understanding). All three use our agents (`systems-design:systems-architect`, `systems-design:design-critic`, `systems-design:design-writer`) plus the foundation explorer (`foundation:explorer`).
**Tech Stack:** Amplifier recipe system (YAML), staged mode with approval gates, foreach parallel execution, context accumulation.

---

### Task 1: Create the `recipes/` directory and `recipes/architecture-review.yaml`

**Files:**
- Create: `recipes/architecture-review.yaml`

**Step 1: Create the directory and file**

Create `recipes/architecture-review.yaml` with the following content. This is a **staged** recipe (uses `stages:` not `steps:`) with 3 stages and 2 approval gates, following the pattern from `related-projects/amplifier-bundle-recipes/examples/dependency-upgrade-staged-recipe.yaml`.

```yaml
name: "architecture-review"
description: "Multi-stage architecture review with approval gates between reconnaissance, analysis, and report phases"
version: "1.0.0"
author: "System Design Intelligence"
tags: ["architecture", "review", "system-design", "staged", "approval-gates"]

# Staged architecture review with approval gates.
#
# Three stages with human checkpoints:
# 1. Reconnaissance: Survey codebase, identify boundaries (no approval)
# 2. Multi-Perspective Analysis: Parallel analysis from 5 perspectives, synthesize risks (approval required)
# 3. Report: Produce the final architecture review document (approval required)
#
# Typical runtime: 10-20 minutes (includes approval wait times)
# Required agents: foundation:explorer, systems-design:systems-architect,
#                  systems-design:design-critic, systems-design:design-writer
#
# Usage:
#   Execute recipe with target_path=<path-to-codebase>
#
# Approval workflow:
#   - Recipe pauses at each approval gate
#   - Use recipe approvals tool to see pending approvals
#   - Approve to continue, deny to stop and review manually

context:
  target_path: ""                                    # Required: path to codebase or directory to review
  output_path: "docs/designs/architecture-review.md" # Optional: where to write the final report
  perspectives:
    - "design-integrity"
    - "failure-modes"
    - "scalability"
    - "developer-experience"
    - "simplicity"

stages:
  # Stage 1: Reconnaissance - survey and identify structure (no approval needed)
  - name: "reconnaissance"
    steps:
      - id: "survey-codebase"
        agent: "foundation:explorer"
        prompt: |
          Survey the codebase at {{target_path}}.

          Produce a structured overview:
          1. Directory layout and organization pattern
          2. Key entry points (main files, CLI, API endpoints, event handlers)
          3. Configuration files and their purposes
          4. Dependency manifest (package files, lock files)
          5. Test structure and coverage indicators
          6. Documentation files
          7. Build and deployment configuration

          Focus on facts. List what exists, where it lives, and how it's organized.
          Do NOT analyze architecture yet -- just survey.
        output: "codebase_survey"
        timeout: 600

      - id: "identify-boundaries"
        agent: "systems-design:systems-architect"
        mode: "ANALYZE"
        prompt: |
          Based on this codebase survey: {{codebase_survey}}

          For the codebase at: {{target_path}}

          Identify the system's architectural structure:

          1. **System boundaries**: Where are the service/module/package boundaries?
          2. **Major components**: What are the primary functional units?
          3. **Dependencies**: What external systems, services, or libraries are critical?
          4. **Data flows**: How does data enter, move through, and exit the system?
          5. **Integration points**: Where does this system connect to others?
          6. **Technology choices**: What frameworks, databases, messaging systems are in use?

          Present this as a structured system map. Identify areas of clarity and areas of ambiguity.
          Flag anything that looks unusual or potentially problematic, but do NOT make judgments yet.
        output: "system_map"
        timeout: 600

  # Stage 2: Multi-Perspective Analysis (approval required before proceeding)
  - name: "analysis"
    approval:
      required: true
      prompt: |
        RECONNAISSANCE COMPLETE

        Codebase survey and system map are ready for review.

        Survey: {{codebase_survey}}

        System map: {{system_map}}

        Approve to proceed with multi-perspective analysis (5 perspectives analyzed in parallel).
        Deny to stop and review the reconnaissance findings manually.
    steps:
      - id: "perspective-analysis"
        agent: "systems-design:systems-architect"
        mode: "ASSESS"
        prompt: |
          Analyze the architecture from a **{{perspective}}** perspective.

          System map: {{system_map}}
          Codebase survey: {{codebase_survey}}
          Target: {{target_path}}

          Focus specifically on {{perspective}} concerns:

          For design-integrity: Are boundaries clean? Do abstractions leak? Is coupling appropriate? Do patterns stay consistent?
          For failure-modes: What breaks? What is the blast radius? Are there single points of failure? How does the system degrade?
          For scalability: What grows with usage? Where are the bottlenecks at 10x? What becomes painful first?
          For developer-experience: How hard is it to understand, modify, test, and deploy? Where do developers struggle?
          For simplicity: What is unnecessarily complex? What could be removed? Where is YAGNI violated?

          Provide:
          1. Current state assessment (1-5 rating with justification)
          2. Key findings (3-5 specific items with evidence from the codebase)
          3. Risks identified (severity: critical/high/medium/low)
          4. Improvement recommendations (ordered by impact)
        foreach: "{{perspectives}}"
        as: "perspective"
        parallel: 3
        collect: "perspective_analyses"
        timeout: 600

      - id: "synthesize-risks"
        agent: "systems-design:design-critic"
        prompt: |
          Synthesize these multi-perspective architecture analyses into a unified risk assessment:

          {{perspective_analyses}}

          For the system at: {{target_path}}
          System map: {{system_map}}

          Produce:
          1. **Cross-cutting risks**: Issues that appear across multiple perspectives
          2. **Severity-ranked risk list**: All identified risks ordered by severity (critical first)
          3. **Conflicting recommendations**: Where perspectives disagree and why
          4. **Blind spots**: What wasn't covered or needs deeper investigation
          5. **Top 3 actions**: The highest-impact improvements regardless of perspective

          Be adversarial. Challenge optimistic assessments. Flag risks the individual perspectives may have underweighted.
        output: "risk_assessment"
        timeout: 600

  # Stage 3: Report (approval required before generating)
  - name: "report"
    approval:
      required: true
      prompt: |
        MULTI-PERSPECTIVE ANALYSIS COMPLETE

        Risk assessment ready for review:

        {{risk_assessment}}

        Approve to generate the final architecture review document at {{output_path}}.
        Deny to stop and review the analysis manually.
    steps:
      - id: "write-report"
        agent: "systems-design:design-writer"
        prompt: |
          Write the architecture review document for the system at {{target_path}}.

          Save the document to: {{output_path}}

          Use ALL of the following as source material:
          - Codebase survey: {{codebase_survey}}
          - System map: {{system_map}}
          - Multi-perspective analyses: {{perspective_analyses}}
          - Unified risk assessment: {{risk_assessment}}

          Structure the document as:

          # Architecture Review: [System Name]

          ## Executive Summary
          (2-3 paragraph overview of findings and top recommendations)

          ## System Overview
          (System map, boundaries, major components, technology choices)

          ## Perspective Analyses
          ### Design Integrity
          ### Failure Modes
          ### Scalability
          ### Developer Experience
          ### Simplicity

          ## Risk Assessment
          (Severity-ranked risk table with cross-cutting concerns)

          ## Recommendations
          (Ordered by impact, with effort estimates and dependencies)

          ## Appendix: Codebase Survey
          (Raw survey data for reference)

          Write clearly and concisely. Use tables for structured comparisons.
          Every recommendation must trace back to specific evidence.
        output: "final_report"
        timeout: 600

# Output Summary:
#
# After full execution, you'll have:
# - codebase_survey: Directory structure and key file inventory
# - system_map: Identified boundaries, components, dependencies, data flows
# - perspective_analyses: 5 parallel analyses (design-integrity, failure-modes, scalability, DX, simplicity)
# - risk_assessment: Unified severity-ranked risk assessment with cross-cutting concerns
# - final_report: Complete architecture review document written to output_path
#
# You can stop at any approval gate and work with intermediate results.
```

**Step 2: Validate the recipe**

Run:
```
recipes operation=validate recipe_path=recipes/architecture-review.yaml
```
Expected: Validation passes with no errors.

**Step 3: Commit**

```bash
git add recipes/architecture-review.yaml && git commit -m "feat: architecture-review staged recipe with approval gates and parallel analysis"
```

---

### Task 2: Create `recipes/design-exploration.yaml`

**Files:**
- Create: `recipes/design-exploration.yaml`

**Step 1: Create the file**

Create `recipes/design-exploration.yaml` with the following content. This is a **flat** recipe (uses `steps:`) with foreach parallel, following the pattern from `related-projects/amplifier-bundle-recipes/examples/parallel-analysis-recipe.yaml`.

```yaml
name: "design-exploration"
description: "Explore 3 architectural alternatives in parallel, evaluate against tradeoff framework, and synthesize a recommendation"
version: "1.0.0"
author: "System Design Intelligence"
tags: ["design", "exploration", "parallel", "tradeoff-analysis", "system-design"]

# Flat recipe with parallel foreach for design exploration.
#
# Steps:
# 1. Frame the problem (ANALYZE mode) - goals, constraints, actors, boundaries
# 2. Generate 3 candidate architectures in parallel (DESIGN mode):
#    - simplest-viable, most-scalable, most-robust
# 3. Evaluate all candidates against 8-dimension tradeoff frame
# 4. (Optional) Adversarial review of the recommended design
#
# Typical runtime: 5-15 minutes
# Required agents: systems-design:systems-architect,
#                  systems-design:design-critic
#
# Usage:
#   Execute recipe with design_problem="description of what to design"

context:
  design_problem: ""               # Required: description of the system or feature to design
  constraints: ""                  # Optional: known constraints (budget, timeline, team, tech)
  with_adversarial_review: "true"  # Optional: run adversarial review on recommendation
  archetypes:
    - "simplest-viable"
    - "most-scalable"
    - "most-robust"

steps:
  # Step 1: Frame the problem
  - id: "frame-problem"
    agent: "systems-design:systems-architect"
    mode: "ANALYZE"
    prompt: |
      Frame this design problem for systematic exploration:

      Problem: {{design_problem}}
      Known constraints: {{constraints}}

      Build a system map:
      1. **Goals**: What must this system accomplish? What does success look like?
      2. **Constraints**: What is fixed? (Include both stated constraints and discovered ones)
      3. **Actors**: Who and what interacts with this system?
      4. **Interfaces**: Where are the boundaries? What crosses them?
      5. **Failure modes**: What are the most likely and most dangerous failures?
      6. **Time horizons**: What matters now vs. in 6 months vs. in 3 years?
      7. **Key decisions**: What are the critical architectural choices to make?

      Be thorough. This framing drives all subsequent design exploration.
      Flag ambiguities and assumptions explicitly.
    output: "problem_frame"
    timeout: 600

  # Step 2: Generate 3 candidate architectures in parallel
  - id: "generate-candidates"
    agent: "systems-design:systems-architect"
    mode: "DESIGN"
    prompt: |
      Design a **{{archetype}}** architecture for this problem:

      Problem: {{design_problem}}
      Problem frame: {{problem_frame}}
      Constraints: {{constraints}}

      Design archetype guidance:

      For simplest-viable: Minimum design that meets core requirements. Maximize simplicity.
        Fewest components, fewest moving parts, fewest concepts to understand.
        Accept limitations in scalability and resilience if core function works.

      For most-scalable: Optimized for growth in usage, data volume, and team size.
        Design for 10x-100x current needs. Accept higher initial complexity.
        Focus on horizontal scaling, loose coupling, and independent deployability.

      For most-robust: Optimized for reliability, failure tolerance, and operational simplicity.
        Design for graceful degradation, blast radius containment, and observability.
        Accept higher cost and complexity for resilience guarantees.

      For your {{archetype}} design, provide:
      1. Architecture overview (components, boundaries, data flows)
      2. Key technology choices with rationale
      3. What this design optimizes for
      4. What this design sacrifices
      5. When this design would be the right choice
      6. When this design would be the wrong choice
      7. Rough complexity assessment (components count, integration points, concepts to learn)
    foreach: "{{archetypes}}"
    as: "archetype"
    parallel: 3
    collect: "candidate_designs"
    timeout: 600

  # Step 3: Evaluate all candidates against the 8-dimension tradeoff frame
  - id: "evaluate-tradeoffs"
    agent: "systems-design:systems-architect"
    mode: "ASSESS"
    prompt: |
      Evaluate these 3 candidate architectures against the 8-dimension tradeoff frame:

      Problem: {{design_problem}}
      Problem frame: {{problem_frame}}

      Candidate designs:
      {{candidate_designs}}

      For EACH candidate, rate against all 8 dimensions (1-5 scale with justification):

      | Dimension         | simplest-viable | most-scalable | most-robust |
      |-------------------|-----------------|---------------|-------------|
      | Latency           |                 |               |             |
      | Complexity        |                 |               |             |
      | Reliability       |                 |               |             |
      | Cost              |                 |               |             |
      | Security          |                 |               |             |
      | Scalability       |                 |               |             |
      | Reversibility     |                 |               |             |
      | Organizational fit|                 |               |             |

      Then provide:
      1. **Comparison matrix** with the table above filled in
      2. **Key differentiators**: Where do the designs diverge most?
      3. **Recommendation**: Which design to proceed with and why
      4. **What the recommendation optimizes for** and **what it sacrifices**
      5. **Hybrid opportunities**: Can strengths from different candidates be combined?
      6. **Decision criteria**: What factors would change the recommendation?
    output: "tradeoff_evaluation"
    timeout: 600

  # Step 4: Optional adversarial review of the recommendation
  - id: "adversarial-review"
    agent: "systems-design:design-critic"
    condition: "{{with_adversarial_review}} == 'true'"
    prompt: |
      Review the recommended design from this exploration:

      Problem: {{design_problem}}
      Problem frame: {{problem_frame}}
      All candidates: {{candidate_designs}}
      Tradeoff evaluation and recommendation: {{tradeoff_evaluation}}

      Stress-test the recommended design from 5 adversarial perspectives:
      1. **SRE**: How does this break at 3 AM? What's the on-call burden?
      2. **Security reviewer**: What's the attack surface? Where are the trust boundaries weak?
      3. **Staff engineer**: Is this the right level of complexity? Will the team maintain this in 2 years?
      4. **Finance owner**: What are the cost drivers at scale? Where are the runaway risks?
      5. **Operator**: How do you deploy, monitor, debug, and rollback this?

      For each perspective:
      - Top risks (severity: critical/high/medium/low)
      - Specific failure scenarios
      - Mitigation recommendations

      Conclude with a unified assessment:
      - Should the recommendation stand, be modified, or be reconsidered?
      - Top 3 risks that must be addressed before implementation
    output: "adversarial_review"
    timeout: 600
```

**Step 2: Validate the recipe**

Run:
```
recipes operation=validate recipe_path=recipes/design-exploration.yaml
```
Expected: Validation passes with no errors.

**Step 3: Commit**

```bash
git add recipes/design-exploration.yaml && git commit -m "feat: design-exploration recipe with parallel candidate generation and tradeoff evaluation"
```

---

### Task 3: Create `recipes/codebase-understanding.yaml`

**Files:**
- Create: `recipes/codebase-understanding.yaml`

**Step 1: Create the file**

Create `recipes/codebase-understanding.yaml` with the following content. This is a **flat** recipe with sequential steps, following the pattern from `related-projects/amplifier-bundle-recipes/examples/code-review-recipe.yaml`.

```yaml
name: "codebase-understanding"
description: "Survey codebase structure, identify boundaries and coupling, map flows, and produce an architectural overview"
version: "1.0.0"
author: "System Design Intelligence"
tags: ["codebase", "understanding", "architecture", "survey", "system-design"]

# Flat sequential recipe for building architectural understanding of a codebase.
#
# Steps:
# 1. Survey directory structure, file types, entry points, docs
# 2. Identify module boundaries, coupling patterns, dependency relationships
# 3. Map data flows, control flows, assess complexity distribution
# 4. Produce final architectural overview
#
# Typical runtime: 5-10 minutes
# Required agents: foundation:explorer, systems-design:systems-architect
#
# Usage:
#   Execute recipe with target_path=<path-to-codebase>

context:
  target_path: ""    # Required: path to codebase to understand
  focus_area: ""     # Optional: specific subsystem or directory to focus on

steps:
  # Step 1: Survey the codebase structure
  - id: "survey-structure"
    agent: "foundation:explorer"
    prompt: |
      Survey the codebase at {{target_path}}.

      Focus area: {{focus_area}} (if empty, survey the entire codebase)

      Produce a comprehensive inventory:
      1. **Directory layout**: Top-level structure and what each directory contains
      2. **File types**: Languages, config formats, and their distribution
      3. **Entry points**: Main files, CLI entry points, API routers, event handlers, workers
      4. **Configuration**: Config files, environment setup, feature flags
      5. **Dependencies**: Package manifests, lock files, vendored code
      6. **Documentation**: README files, docs directories, inline doc patterns
      7. **Tests**: Test directory structure, test frameworks in use, approximate coverage
      8. **Build/Deploy**: CI/CD configs, Dockerfiles, deployment scripts
      9. **Notable files**: Anything unusual or worth calling out

      Be thorough and factual. Report what exists, not what should exist.
    output: "structure_survey"
    timeout: 600

  # Step 2: Identify boundaries and coupling
  - id: "identify-boundaries"
    agent: "systems-design:systems-architect"
    mode: "ANALYZE"
    prompt: |
      Analyze the codebase at {{target_path}} to identify architectural boundaries and coupling.

      Structure survey: {{structure_survey}}
      Focus area: {{focus_area}} (if empty, analyze the entire codebase)

      Identify:
      1. **Module boundaries**: Where are the logical separations? Are they enforced or conventional?
      2. **Coupling patterns**: What depends on what? Where is coupling tight vs. loose?
         Use file imports, shared types, and cross-module references as evidence.
      3. **Dependency relationships**: Internal module dependencies (which modules call which).
         External dependency hotspots (which modules rely heavily on external libraries).
      4. **Interface patterns**: How do modules communicate? (function calls, events, shared state, APIs)
      5. **Boundary violations**: Where do modules reach into each other's internals?

      Present as a structured analysis with specific file/directory references as evidence.
      Rate overall boundary health: clean / mostly clean / leaky / entangled.
    output: "boundary_analysis"
    timeout: 600

  # Step 3: Map flows and assess complexity
  - id: "map-flows"
    agent: "systems-design:systems-architect"
    mode: "ASSESS"
    prompt: |
      Map data and control flows in the codebase at {{target_path}}.

      Structure survey: {{structure_survey}}
      Boundary analysis: {{boundary_analysis}}
      Focus area: {{focus_area}} (if empty, map the entire codebase)

      Analyze:
      1. **Data flows**: How does data enter the system? How does it move between components?
         Where is it stored? Where does it exit? Identify the primary data paths.
      2. **Control flows**: What triggers processing? How do requests flow through the system?
         What orchestrates multi-step operations?
      3. **Complexity distribution**: Where is complexity concentrated? Which modules/files
         carry the most logic? Where are the complexity hotspots?
      4. **Architectural patterns in use**: What patterns does the codebase actually use?
         (MVC, event-driven, layered, hexagonal, etc.) Are patterns consistent or mixed?
      5. **State management**: Where is state held? How is it synchronized?
         Where are the consistency boundaries?

      Be specific -- reference actual files, functions, and paths.
    output: "flow_analysis"
    timeout: 600

  # Step 4: Produce the architectural overview
  - id: "architectural-overview"
    agent: "systems-design:systems-architect"
    mode: "ASSESS"
    prompt: |
      Produce a final architectural overview for the codebase at {{target_path}}.

      Synthesize ALL previous analysis:
      - Structure survey: {{structure_survey}}
      - Boundary analysis: {{boundary_analysis}}
      - Flow analysis: {{flow_analysis}}
      Focus area: {{focus_area}} (if empty, cover the entire codebase)

      Write a comprehensive architectural overview:

      ## System Architecture: [Name]

      ### Components
      (List each major component, its responsibility, and its boundaries)

      ### Boundaries and Interfaces
      (How components connect, communication patterns, boundary health)

      ### Data Flows
      (Primary data paths through the system, storage points, transformation points)

      ### Control Flows
      (Request processing, event handling, orchestration patterns)

      ### Architectural Patterns
      (Patterns in use, consistency assessment, pattern fitness)

      ### Coupling Assessment
      (Overall coupling level, tight coupling hotspots, loose coupling examples)

      ### Complexity Hotspots
      (Where complexity concentrates, why, and whether it's warranted)

      ### Architectural Debt
      (Pattern violations, workarounds, boundary erosion, inconsistencies)

      ### Strengths
      (What the architecture does well)

      ### Recommendations
      (Ordered by impact -- what would improve the architecture most)

      Ground every observation in specific evidence from the codebase.
    output: "architectural_overview"
    timeout: 600
```

**Step 2: Validate the recipe**

Run:
```
recipes operation=validate recipe_path=recipes/codebase-understanding.yaml
```
Expected: Validation passes with no errors.

**Step 3: Commit**

```bash
git add recipes/codebase-understanding.yaml && git commit -m "feat: codebase-understanding recipe for architectural survey and analysis"
```

---

### Task 4: Verify all recipes

**Files:**
- Verify: `recipes/architecture-review.yaml`
- Verify: `recipes/design-exploration.yaml`
- Verify: `recipes/codebase-understanding.yaml`

**Step 1: Validate all 3 recipes**

Run each validation:
```
recipes operation=validate recipe_path=recipes/architecture-review.yaml
recipes operation=validate recipe_path=recipes/design-exploration.yaml
recipes operation=validate recipe_path=recipes/codebase-understanding.yaml
```
Expected: All 3 pass validation with no errors.

**Step 2: Verify recipe structure manually**

Check that each recipe follows the correct format:

1. `architecture-review.yaml`:
   - Uses `stages:` (not `steps:`) at the top level
   - Has 3 stages: `reconnaissance`, `analysis`, `report`
   - Stage 2 (`analysis`) has `approval: required: true`
   - Stage 3 (`report`) has `approval: required: true`
   - The foreach step uses `parallel: 3` and `collect: "perspective_analyses"`
   - All agent names are fully qualified (`systems-design:*`, `foundation:explorer`)

2. `design-exploration.yaml`:
   - Uses `steps:` at the top level
   - Has 4 steps: `frame-problem`, `generate-candidates`, `evaluate-tradeoffs`, `adversarial-review`
   - The foreach step (`generate-candidates`) uses `parallel: 3` and `collect: "candidate_designs"`
   - Step 4 (`adversarial-review`) has `condition: "{{with_adversarial_review}} == 'true'"`

3. `codebase-understanding.yaml`:
   - Uses `steps:` at the top level
   - Has 4 sequential steps: `survey-structure`, `identify-boundaries`, `map-flows`, `architectural-overview`
   - No foreach, no conditions, no approval gates
   - Each step's `output` is referenced by subsequent steps

**Step 3: Verify file listing**

Run:
```bash
ls -la recipes/
```
Expected: 3 files:
```
architecture-review.yaml
codebase-understanding.yaml
design-exploration.yaml
```

---

### Task 5: Final commit and structure verification

**Step 1: Check the full bundle structure**

Run:
```bash
find . -type f \( -name "*.md" -o -name "*.yaml" \) | grep -v related-projects | grep -v node_modules | grep -v .git/ | sort
```

Expected output should include all files from checkpoints 1-5:
```
./agents/design-critic.md
./agents/design-writer.md
./agents/systems-architect.md
./behaviors/system-design.yaml
./bundle.md
./context/instructions.md
./context/structured-design-template.md
./context/system-design-principles.md
./docs/plans/checkpoint-1-core-design-content.md
./docs/plans/checkpoint-2-design-skills.md
./docs/plans/checkpoint-3-design-modes.md
./docs/plans/checkpoint-4-design-agents.md
./docs/plans/checkpoint-5-design-recipes.md
./docs/planning/plan.v2.md
./modes/systems-design-review.md
./modes/design.md
./recipes/architecture-review.yaml
./recipes/codebase-understanding.yaml
./recipes/design-exploration.yaml
./skills/adversarial-review/adversarial-review.md
./skills/architecture-primitives/architecture-primitives.md
./skills/system-type-event-driven/system-type-event-driven.md
./skills/system-type-web-service/system-type-web-service.md
./skills/tradeoff-analysis/tradeoff-analysis.md
```

**Step 2: Verify git status is clean**

Run:
```bash
git status
```
Expected: Working directory clean (all recipe files committed in Tasks 1-3).

**Step 3: If anything uncommitted, commit**

If there are uncommitted files:
```bash
git add -A && git commit -m "feat: checkpoint 5 complete - 3 design workflow recipes"
```
