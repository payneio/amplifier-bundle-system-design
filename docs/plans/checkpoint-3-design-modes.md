# Checkpoint 3: Structured Design Workflow via /design Mode — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add two interactive modes (`/design` and `/design-review`) to the system-design-intelligence bundle, giving users a structured 8-phase design workflow that blocks writes and enforces rigorous systems thinking before artifact creation.

**Architecture:** Two markdown mode files with YAML frontmatter define tool policies and inject process guidance into the agent's system prompt. The modes infrastructure (hooks-mode for enforcement + tool-mode for programmatic transitions) is wired into the existing behavior YAML. The `/design` mode follows the superpowers hybrid pattern: conversation happens in-mode, artifact creation is delegated to an agent. `/design-review` is a lighter read-only evaluation mode.

**Tech Stack:** Amplifier modes system (markdown + YAML frontmatter), hooks-mode module, tool-mode module, existing behavior YAML composition.

---

### Task 1: Wire hooks-mode and tool-mode into behavior YAML

**Files:**
- Modify: `behaviors/system-design.yaml`

**Step 1: Read the current file**

Read `behaviors/system-design.yaml`. It currently has 20 lines: a `bundle:` header, a `tools:` section with `tool-skills`, and a `context:` section.

**Step 2: Add modes infrastructure**

Replace the entire contents of `behaviors/system-design.yaml` with:

```yaml
bundle:
  name: system-design-behavior
  version: 0.1.0
  description: |
    System design methodology behavior.
    Loads design principles, structured output template, and standing orders
    into the root session context. Provides /design and /design-review modes.

# Explicit dependency on the modes behavior for namespace resolution
# (modes:context/modes-instructions.md needs the "modes" namespace registered)
# NOTE: Include the behavior, NOT the full bundle — the full bundle transitively
# includes foundation, which overrides session.orchestrator to loop-streaming.
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=behaviors/modes.yaml

# Mode hook to discover system-design modes (design, design-review)
# TODO: When published to git, replace absolute path with:
#   "@system-design-intelligence:modes"
# or a git+https:// URL. The @namespace syntax does not resolve at mount time.
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - "/data/labs/amplifier-system-design/modes"

# Mode tool for programmatic mode transitions (agents can request mode changes)
# Skills tool for discoverable design knowledge
tools:
  - module: tool-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/tool-mode
    config:
      gate_policy: "warn"
  - module: tool-skills
    source: git+https://github.com/microsoft/amplifier-module-tool-skills@main
    config:
      skills:
        - "/data/labs/amplifier-system-design/skills"

context:
  include:
    - system-design-intelligence:context/system-design-principles.md
    - system-design-intelligence:context/structured-design-template.md
    - system-design-intelligence:context/instructions.md
```

This adds three new sections to the existing YAML:
1. `includes:` — pulls in the modes behavior bundle for namespace resolution
2. `hooks:` — hooks-mode module with `search_paths` pointing at our `modes/` directory (absolute path, same pattern as the skills fix from Checkpoint 2)
3. `tools:` — adds tool-mode before the existing tool-skills entry

The `context:` section is unchanged.

**Step 3: Verify YAML is valid**

Run: `python3 -c "import yaml; yaml.safe_load(open('behaviors/system-design.yaml')); print('YAML valid')"`

Expected: `YAML valid`

**Step 4: Commit**

```bash
git add behaviors/system-design.yaml && git commit -m "feat: wire hooks-mode and tool-mode into behavior YAML for /design modes"
```

---

### Task 2: Create the /design mode

**Files:**
- Create: `modes/design.md`

**Step 1: Create the modes directory**

```bash
mkdir -p modes
```

**Step 2: Create `modes/design.md`**

Write the following content to `modes/design.md`. This follows the exact structural pattern of `related-projects/amplifier-bundle-superpowers/modes/brainstorm.md` — same sections in the same order, but with system-design-specific content in each section.

```markdown
---
mode:
  name: design
  description: Structured system design exploration — model the system, explore alternatives, analyze tradeoffs, validate design section-by-section
  shortcut: design

  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - delegate
      - recipes
      - todo
    warn:
      - bash

  default_action: block
  allowed_transitions: [design-review, brainstorm, write-plan, debug]
  allow_clear: false
---

DESIGN MODE: You facilitate structured system design through collaborative dialogue.

<CRITICAL>
THE HYBRID PATTERN: You handle the CONVERSATION. Agents handle the ARTIFACTS.

Your role: Model the system, ask questions, explore alternatives, analyze tradeoffs, present design sections, get user validation. This is interactive dialogue between you and the user.

Agent's role: When it's time to CREATE THE DESIGN DOCUMENT, you MUST delegate to `foundation:zen-architect`. The architect agent writes the artifact. You do not write files.

This gives the best of both worlds: interactive back-and-forth systems thinking (which requires YOU) + focused, clean document creation (which requires a DEDICATED AGENT with write tools).

You CANNOT write files in this mode. write_file and edit_file are blocked. The architect agent has its own filesystem tools and will handle document creation.
</CRITICAL>

<HARD-GATE>
Do NOT delegate document creation, invoke any implementation tool, or take any
implementation action until you have presented the design section-by-section and
the user has approved each section. This applies to EVERY design regardless of
perceived simplicity. No shortcuts. No "this is straightforward enough to skip."
</HARD-GATE>

When entering design mode, create this todo checklist immediately:
- [ ] Understand context (codebase, constraints, existing systems)
- [ ] Model the system (goals, constraints, actors, interfaces, feedback loops, failure modes)
- [ ] Ask clarifying questions (one at a time)
- [ ] Explore 3+ alternatives with tradeoffs
- [ ] Evaluate against fixed frame (load tradeoff-analysis skill)
- [ ] Present design in sections (validate each with user)
- [ ] Adversarial review (load adversarial-review skill)
- [ ] Delegate artifact creation to architect agent

## The Process

Follow these phases in order. Do not skip phases. Do not compress multiple phases into one message.

Before starting Phase 1, check for relevant skills: `load_skill(search="design")` and `load_skill(search="system-type")`. Load any that match the problem domain.

### Phase 1: Understand Context

Before asking a single question:
- Check the current project state (files, docs, recent commits)
- Read any referenced documents, existing designs, or architecture artifacts
- Survey the codebase structure if one exists
- Understand what already exists and what constraints are inherited

Then state what you understand about the project context. Be specific about what you found.

### Phase 2: Model the System

This is the key differentiator from generic brainstorming. Before exploring solutions, produce an explicit system map:

- **Goals**: What must this system accomplish? What does success look like?
- **Constraints**: What is fixed? (budget, timeline, team size, existing systems, regulations)
- **Actors**: Who and what interacts with this system? (users, services, operators, external systems)
- **Interfaces**: Where are the boundaries? What crosses them? What are the contracts?
- **Feedback loops**: Where does output become input? Where can behavior amplify or dampen?
- **Failure modes**: What breaks? What happens when it breaks? What is the blast radius?

Present the system map to the user. Ask: "Does this map capture the system correctly? What am I missing?"

Do NOT proceed to solutions until the system map is validated. A weak designer jumps to answers. A strong designer first builds a map.

@system-design-intelligence:context/system-design-principles.md

### Phase 3: Ask Questions One at a Time

Refine understanding through focused questioning:
- Ask ONE question per message. Not two. Not three. ONE.
- Prefer multiple-choice questions when possible — easier to answer
- Open-ended questions are fine when the space is genuinely open
- Focus on: unknown constraints, scale expectations, team capabilities, integration points, non-functional requirements
- If a topic needs more exploration, break it into multiple questions across messages

Do NOT bundle questions. Do NOT present a "questionnaire." One question, wait for answer, next question.

NEVER bundle questions. NEVER present a "questionnaire." If you catch yourself writing "Also," or "Additionally," before a second question — STOP. Delete it. One question. Wait.

### Phase 4: Explore 3+ Alternatives

Once you understand the system:
- Generate at least 3 candidate architectures:
  1. **Simplest viable** — minimum design that meets core requirements
  2. **Most scalable** — optimized for growth in usage, data, or team size
  3. **Most robust** — optimized for reliability, failure tolerance, and operational simplicity
- Present each with its tradeoffs: what it optimizes for, what it sacrifices
- Lead with your recommended option and explain why
- Apply YAGNI ruthlessly — remove unnecessary complexity from all alternatives
- Wait for the user to choose or refine before proceeding

Do NOT present alternatives as a formal matrix dump. Present them conversationally, one at a time, with clear reasoning.

### Phase 5: Evaluate Against Fixed Frame

Once an approach is chosen, evaluate it rigorously:

Load the tradeoff-analysis skill: `load_skill(skill_name="tradeoff-analysis")`

Apply the 8-dimension comparison frame:
- Latency, Complexity, Reliability, Cost, Security, Scalability, Reversibility, Organizational fit

For every dimension, answer: what does this design optimize for, and what does it sacrifice?

Present the evaluation to the user. This is where hidden costs and second-order effects surface.

### Phase 6: Present Design Section-by-Section

Present the design using the structured template, one section at a time:

@system-design-intelligence:context/structured-design-template.md

- Present each section in 200-300 words
- After EACH section, ask: "Does this look right so far?"
- Cover every template section that is relevant (not every section needs equal depth — calibrate to the problem)
- Be ready to go back and revise if something doesn't make sense
- Do NOT dump the entire design in one message

### Phase 7: Adversarial Review

Before finalizing, stress-test the design:

Load the adversarial-review skill: `load_skill(skill_name="adversarial-review")`

If the skill is available, follow its multi-perspective review process. If not, conduct the review yourself from these 5 perspectives:
1. **SRE**: What breaks at 3am? What's the on-call experience?
2. **Security reviewer**: What's the attack surface? What data is exposed?
3. **Staff engineer**: Does this compose well? What's the maintenance burden in 2 years?
4. **Finance owner**: What are the cost drivers? What scales linearly vs. superlinearly?
5. **Operator**: How do you deploy, monitor, rollback, and debug this?

Present findings to the user. Address any critical risks before proceeding.

### Phase 8: Delegate Artifact Creation

When the user has validated all sections and adversarial review is addressed, DELEGATE to the architect agent to create the artifact:

```
delegate(
  agent="foundation:zen-architect",
  instruction="Write the design document for: [topic]. Save to docs/plans/YYYY-MM-DD-<topic>-design.md. Use the structured design template with these sections: problem framing, explicit assumptions, system boundaries, components and responsibilities, data and control flows, risks and failure modes, tradeoffs, recommended design, simplest credible alternative, migration plan, success metrics. Here is the complete validated design: [include all validated sections from the conversation]",
  context_depth="recent",
  context_scope="conversation"
)
```

This delegation is MANDATORY. You discussed and validated the design with the user. Now the agent writes the document. Do NOT attempt to write it yourself.

## After the Design

When the architect agent has saved the document:

```
Design saved to `docs/plans/YYYY-MM-DD-<topic>-design.md`.

Ready to evaluate this design? Use /design-review.
Ready to create an implementation plan? Use /write-plan.
```

## Scope Assessment

Calibrate depth based on the scope of what's being designed:

- **Single-subsystem** — streamlined process; focused system map, lighter failure mode analysis
- **Multi-subsystem** — thorough dependency mapping required; trace all integration points and data flows before exploring alternatives
- **Greenfield system** — emphasis on interface design and boundary placement; establish contracts before internals; extra scrutiny on reversibility

## Anti-Rationalization Table

| Your Excuse | Why It's Wrong |
|-------------|---------------|
| "I already know the right architecture" | Then the system modeling phase will be fast. That's not a reason to skip it. Unexamined assumptions are where designs fail. |
| "Let me just sketch the high-level approach" | Sketches skip constraint discovery, tradeoff analysis, and failure mode identification. Follow the phases. |
| "The user seems to know what they want" | Users know their requirements. They don't always know their constraints. The system map surfaces what they haven't considered. |
| "This is a standard web service / event system / CRUD app" | Every system has unique constraints, failure modes, and organizational context. "Standard" architectures applied without analysis produce standard problems. |
| "Three alternatives is overkill for this" | The simplest-viable alternative takes 2 sentences. If you can't articulate 3 options, you haven't explored the design space. |
| "I'll present the whole design at once" | Dumping 1000 words without checkpoints means rework when section 3 invalidates section 1. Present in sections. |
| "The tradeoff analysis is obvious" | If it's obvious, writing it down takes 30 seconds. If it's not obvious (likely), you just saved the project from a hidden cost. |
| "Adversarial review is too heavyweight" | Skipping adversarial review means the SRE finds your failure modes at 3am instead of now. 5 minutes of review prevents 5 hours of incident response. |
| "I can just write the design doc myself" | You CANNOT. write_file is blocked. Delegate to foundation:zen-architect. This is the architecture. |
| "Delegation breaks the flow" | YOU own the conversation flow. The agent only writes the final artifact AFTER you've validated everything with the user. The flow is preserved. |

Every design goes through this process. A single-endpoint API, a distributed system — all of them. "Simple" systems are where unexamined assumptions cause the most costly failures. The design can be short, but you MUST model, explore, evaluate, and validate.

## Do NOT:
- Write implementation code
- Create or modify source files
- Make commits
- Skip the system modeling phase (Phase 2)
- Skip the questioning phase
- Present the entire design in one message
- Ask multiple questions per message
- Skip tradeoff analysis ("it's obvious")
- Skip adversarial review ("it's overkill")
- Write the design document yourself (MUST delegate)
- Run git push, git merge, gh pr create, or any deployment/release commands

## Key Principles

- **Model before solving** — Build the system map before exploring solutions
- **One question at a time** — Don't overwhelm with multiple questions
- **Multiple choice preferred** — Easier to answer than open-ended when possible
- **3+ alternatives always** — Explore the design space before converging
- **Fixed frame evaluation** — Use the 8-dimension tradeoff frame, not ad hoc analysis
- **Incremental validation** — Present design in sections, validate each
- **Adversarial review** — Stress-test from 5 perspectives before finalizing
- **Delegate the artifact** — You own the conversation, the agent owns the document
- **YAGNI ruthlessly** — Remove unnecessary complexity from all designs
- **Simplicity as constraint** — Prefer the simplest design whose failure modes are acceptable

## Announcement

When entering this mode, announce:
"I'm entering design mode for structured system design. I'll start by modeling the system — mapping goals, constraints, actors, interfaces, and failure modes. Then I'll ask questions one at a time, explore at least 3 architectural alternatives, evaluate tradeoffs against a fixed frame, and present the design in sections for your validation. Once we've validated everything and stress-tested it, I'll delegate to a specialist agent to write the design document."

## Transitions

**Done when:** Design document saved to `docs/plans/`

**Golden path:** `/design-review` or `/write-plan`
- Tell user: "Design complete and saved to [path]. Use `/design-review` for a multi-perspective evaluation, or `/write-plan` to create an implementation plan."
- Use `mode(operation='set', name='design-review')` or `mode(operation='set', name='write-plan')` to transition. The first call will be denied (gate policy); call again to confirm.

**Dynamic transitions:**
- If the design needs brainstorming on a sub-problem -> use `mode(operation='set', name='brainstorm')` for free-form exploration, then return to /design
- If bug mentioned -> use `mode(operation='set', name='debug')` because systematic debugging has its own process
- If user already has a validated design -> suggest `/design-review` for evaluation or `/write-plan` to skip directly to implementation planning

**Skill connection:** Skills loaded during the process (tradeoff-analysis, adversarial-review, system-type-*) tell you WHAT to analyze. This mode enforces HOW. They complement each other.
```

**Step 3: Verify the file exists and frontmatter is valid**

Run:
```bash
python3 -c "
import yaml
content = open('modes/design.md').read()
parts = content.split('---', 2)
fm = yaml.safe_load(parts[1])
print(f'Mode name: {fm[\"mode\"][\"name\"]}')
print(f'Tools safe: {len(fm[\"mode\"][\"tools\"][\"safe\"])} tools')
print(f'Default action: {fm[\"mode\"][\"default_action\"]}')
print(f'Transitions: {fm[\"mode\"][\"allowed_transitions\"]}')
print(f'Allow clear: {fm[\"mode\"][\"allow_clear\"]}')
print('VALID')
"
```

Expected:
```
Mode name: design
Tools safe: 12 tools
Default action: block
Transitions: ['design-review', 'brainstorm', 'write-plan', 'debug']
Allow clear: False
VALID
```

**Step 4: Verify line count is in the expected range**

Run: `wc -l modes/design.md`

Expected: approximately 200-230 lines (matching brainstorm.md's 202 lines with extra phases)

**Step 5: Commit**

```bash
git add modes/design.md && git commit -m "feat: /design mode — 8-phase structured system design workflow"
```

---

### Task 3: Create the /design-review mode

**Files:**
- Create: `modes/design-review.md`

**Step 1: Create `modes/design-review.md`**

Write the following content to `modes/design-review.md`:

```markdown
---
mode:
  name: design-review
  description: Evaluate an existing design or proposed change against the codebase — multi-perspective review for integrity, constraints, failure modes, and DX
  shortcut: design-review

  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - load_skill
      - LSP
      - python_check
      - delegate
      - recipes
      - todo
    warn:
      - bash

  default_action: block
  allowed_transitions: [design, brainstorm, write-plan, execute-plan, debug]
  allow_clear: true
---

DESIGN-REVIEW MODE: You evaluate existing designs against the codebase and design principles.

Your role:
- READ the design document or proposal
- SURVEY the codebase for context, constraints, and existing patterns
- EVALUATE against the review checklist
- PRODUCE findings: strengths, concerns, risks, recommendations

You CANNOT write files in this mode. write_file and edit_file are blocked. This is evaluation, not creation.

## Review Checklist

Evaluate each design against these dimensions:

| Dimension | Key Questions |
|-----------|--------------|
| **Design integrity** | Are the components coherent? Do responsibilities overlap? Are boundaries clean? |
| **Constraint satisfaction** | Does the design respect stated constraints (budget, timeline, team, existing systems)? Are there unstated constraints it violates? |
| **Failure modes addressed** | Are failure modes identified? Is blast radius bounded? Are recovery paths defined? What breaks at 3am? |
| **Developer experience** | Can the team build and maintain this? Is the cognitive load manageable? Are the abstractions learnable? |
| **Implementation viability** | Can this actually be built with available resources? Are there hidden dependencies or prerequisites? What's the riskiest part to implement? |
| **Simplicity assessment** | Is there unnecessary complexity? Could a simpler design achieve the same goals with acceptable risk? What would you remove? |
| **Consistency** | Does this align with existing codebase patterns? Does it introduce new paradigms that conflict with established conventions? |

## The Process

### Step 1: Understand the Design

- Read the design document thoroughly
- Identify the stated goals, constraints, and tradeoffs
- Note what the design explicitly optimizes for and sacrifices

### Step 2: Survey the Codebase

- Examine the relevant parts of the codebase
- Understand existing patterns, conventions, and architectural decisions
- Identify integration points where the design meets existing code
- Look for constraints the design may not account for

### Step 3: Evaluate Against Checklist

Work through each dimension of the review checklist. For each:
- State the assessment (strong / adequate / concern / critical risk)
- Provide specific evidence from the design or codebase
- Be concrete — "the retry logic doesn't handle partial failures in the batch processor at `src/batch/processor.py:45`" not "failure handling could be improved"

Load relevant skills for deeper analysis:
- `load_skill(skill_name="tradeoff-analysis")` for tradeoff evaluation
- `load_skill(skill_name="adversarial-review")` for multi-perspective stress testing
- `load_skill(search="system-type")` for domain-specific patterns

### Step 4: Produce Findings

Present a structured review:

**Strengths**: What this design does well. Be specific.

**Concerns**: Issues that should be addressed but aren't blocking. Include severity and suggested remediation.

**Risks**: Critical issues that could cause failure. Include likelihood, impact, and mitigation options.

**Recommendations**: Concrete next steps — what to change, what to investigate, what to accept.

## Announcement

When entering this mode, announce:
"I'm entering design-review mode to evaluate this design. I'll read the design document, survey the relevant codebase, evaluate against a structured checklist (integrity, constraints, failure modes, DX, viability, simplicity, consistency), and produce findings with specific evidence."

## Transitions

**Done when:** Review findings presented to user.

**If redesign needed:** `/design`
- Tell user: "This design has [critical risks / significant concerns]. I recommend entering `/design` mode to address [specific issues]."
- Use `mode(operation='set', name='design')` to transition.

**If design approved:** `/write-plan` or `/execute-plan`
- Tell user: "Design looks solid. Use `/write-plan` to create an implementation plan, or `/execute-plan` if you already have one."
- Use `mode(operation='set', name='write-plan')` to transition.

**If needs brainstorming:** `/brainstorm`
- Tell user: "Some aspects need more exploration before a full redesign. Use `/brainstorm` to explore [specific area]."
```

**Step 2: Verify the file exists and frontmatter is valid**

Run:
```bash
python3 -c "
import yaml
content = open('modes/design-review.md').read()
parts = content.split('---', 2)
fm = yaml.safe_load(parts[1])
print(f'Mode name: {fm[\"mode\"][\"name\"]}')
print(f'Tools safe: {len(fm[\"mode\"][\"tools\"][\"safe\"])} tools')
print(f'Default action: {fm[\"mode\"][\"default_action\"]}')
print(f'Transitions: {fm[\"mode\"][\"allowed_transitions\"]}')
print(f'Allow clear: {fm[\"mode\"][\"allow_clear\"]}')
print('VALID')
"
```

Expected:
```
Mode name: design-review
Tools safe: 12 tools
Default action: block
Transitions: ['design', 'brainstorm', 'write-plan', 'execute-plan', 'debug']
Allow clear: True
VALID
```

**Step 3: Verify line count**

Run: `wc -l modes/design-review.md`

Expected: approximately 100-120 lines

**Step 4: Commit**

```bash
git add modes/design-review.md && git commit -m "feat: /design-review mode — multi-perspective design evaluation"
```

---

### Task 4: Verify modes are discoverable and functional

**Files:**
- None (verification only)

**Step 1: List modes to verify discovery**

Run:
```bash
python3 -c "
import os
modes_dir = '/data/labs/amplifier-system-design/modes'
files = os.listdir(modes_dir)
print(f'Modes directory contents: {files}')
for f in sorted(files):
    if f.endswith('.md'):
        path = os.path.join(modes_dir, f)
        with open(path) as fh:
            content = fh.read()
        # Check frontmatter
        if content.startswith('---'):
            import yaml
            parts = content.split('---', 2)
            fm = yaml.safe_load(parts[1])
            name = fm.get('mode', {}).get('name', 'MISSING')
            desc = fm.get('mode', {}).get('description', 'MISSING')[:60]
            default = fm.get('mode', {}).get('default_action', 'MISSING')
            transitions = fm.get('mode', {}).get('allowed_transitions', [])
            print(f'  {name}: {desc}... (default_action={default}, transitions={transitions})')
        else:
            print(f'  {f}: NO FRONTMATTER')
print('All modes valid')
"
```

Expected:
```
Modes directory contents: ['design.md', 'design-review.md']
  design: Structured system design exploration — model the system, e... (default_action=block, transitions=['design-review', 'brainstorm', 'write-plan', 'debug'])
  design-review: Evaluate an existing design or proposed change against the c... (default_action=block, transitions=['design', 'brainstorm', 'write-plan', 'execute-plan', 'debug'])
All modes valid
```

**Step 2: Verify behavior YAML references are correct**

Run:
```bash
python3 -c "
import yaml
with open('behaviors/system-design.yaml') as f:
    config = yaml.safe_load(f)

# Check includes
includes = config.get('includes', [])
print(f'Includes: {len(includes)} entries')
for inc in includes:
    print(f'  - {inc.get(\"bundle\", \"MISSING\")}')

# Check hooks
hooks = config.get('hooks', [])
print(f'Hooks: {len(hooks)} entries')
for hook in hooks:
    print(f'  - {hook[\"module\"]}: search_paths={hook.get(\"config\", {}).get(\"search_paths\", [])}')

# Check tools
tools = config.get('tools', [])
print(f'Tools: {len(tools)} entries')
for tool in tools:
    print(f'  - {tool[\"module\"]}')

# Check context
ctx = config.get('context', {}).get('include', [])
print(f'Context includes: {len(ctx)} entries')

print('Behavior YAML structure valid')
"
```

Expected:
```
Includes: 1 entries
  - git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=behaviors/modes.yaml
Hooks: 1 entries
  - hooks-mode: search_paths=['/data/labs/amplifier-system-design/modes']
Tools: 2 entries
  - tool-mode
  - tool-skills
Context includes: 3 entries
Behavior YAML structure valid
```

**Step 3: Verify cross-references in design.md**

The design mode body should contain @mentions to our context files. Verify they point to real files:

Run:
```bash
grep -n '@system-design-intelligence:' modes/design.md
ls -la context/system-design-principles.md context/structured-design-template.md
```

Expected: grep shows 2 @mention lines; ls shows both files exist.

**Step 4: Verify mode tool policies**

Run:
```bash
python3 -c "
import yaml

for mode_file in ['modes/design.md', 'modes/design-review.md']:
    with open(mode_file) as f:
        content = f.read()
    parts = content.split('---', 2)
    fm = yaml.safe_load(parts[1])
    mode = fm['mode']
    safe = set(mode['tools']['safe'])
    warn = set(mode['tools'].get('warn', []))
    
    # Verify write tools are NOT in safe or warn (they'll be blocked by default_action)
    blocked = {'write_file', 'edit_file', 'apply_patch'}
    in_safe = blocked & safe
    in_warn = blocked & warn
    
    if in_safe or in_warn:
        print(f'ERROR: {mode_file} allows write tools: safe={in_safe}, warn={in_warn}')
    else:
        print(f'{mode[\"name\"]}: write tools correctly blocked (default_action={mode[\"default_action\"]})')
    
    # Verify delegate IS in safe (needed for hybrid pattern)
    if 'delegate' in safe:
        print(f'{mode[\"name\"]}: delegate correctly in safe tools')
    else:
        print(f'ERROR: {mode_file} missing delegate in safe tools')
"
```

Expected:
```
design: write tools correctly blocked (default_action=block)
design: delegate correctly in safe tools
design-review: write tools correctly blocked (default_action=block)
design-review: delegate correctly in safe tools
```

---

### Task 5: Final commit and structure verification

**Files:**
- None (verification + commit only)

**Step 1: Verify clean git status**

Run: `git status`

Expected: Clean working tree (all changes committed in Tasks 1-3).

If there are uncommitted changes, stage and commit them:
```bash
git add -A && git commit -m "chore: checkpoint 3 cleanup"
```

**Step 2: Verify full bundle structure**

Run:
```bash
echo "=== Bundle Structure ==="
find . -not -path './related-projects/*' -not -path './.git/*' -not -path './docs/*' -type f | sort
echo ""
echo "=== Modes ==="
ls -la modes/
echo ""
echo "=== Git Log (Checkpoint 3) ==="
git log --oneline -5
```

Expected output should show:
- `./behaviors/system-design.yaml` (modified)
- `./bundle.md` (unchanged)
- `./context/instructions.md`, `./context/structured-design-template.md`, `./context/system-design-principles.md` (unchanged)
- `./modes/design-review.md` (new)
- `./modes/design.md` (new)
- `./skills/*/SKILL.md` files (unchanged from Checkpoint 2)
- 3 new commits for Checkpoint 3

**Step 3: Commit the plan document**

```bash
git add docs/plans/checkpoint-3-design-modes.md && git commit -m "docs: checkpoint 3 implementation plan"
```
