---
name: design-review-methodology
description: "Use when the /design-review mode is active. 6-step design review methodology -- understand the design, evaluate against codebase, adversarial analysis, tradeoff validation, synthesis, and action items. Governs conversation flow, delegation patterns, and user validation checkpoints."
---

# Design Review Methodology

Companion skill for the `/design-review` mode. The mode gates tools; this skill governs behavior.

## Core Rule

**You handle the CONVERSATION. Agents handle the ANALYSIS.**

You guide the user through the review, synthesize findings, and facilitate decisions. For deep analysis work, delegate to `system-design-intelligence:design-critic` or use the `adversarial-review` skill.

## Step Flow

### Step 1: Understand the Design

Before any critique:
1. Read the design document or referenced files thoroughly.
2. Identify the stated goals, constraints, and tradeoffs.
3. If a codebase exists, survey the relevant parts.
4. Note what the design explicitly addresses and what it is silent on.

Ask: **"Is this the complete design, or is there additional context I should know about?"**

### Step 2: Evaluate Against the Codebase

If reviewing an existing system or a design that modifies one:
- Use `read_file`, `grep`, and `LSP` to examine the actual code
- Compare the design's claims against reality
- Identify gaps between the design document and the implementation

### Step 3: Adversarial Analysis

Delegate the deep adversarial review rather than doing it inline:

**Option A -- Delegate to the design-critic agent:**
```
delegate(
  agent="system-design-intelligence:design-critic",
  instruction="Review this design: [design content or file path]. System context: [relevant codebase findings from Step 2]",
  context_depth="recent",
  context_scope="agents"
)
```

**Option B -- Use the adversarial-review skill (spawns 5 parallel agents):**
```
load_skill(skill_name="adversarial-review")
```

Choose Option A when you have accumulated codebase context to pass along. Choose Option B for a quick parallel review when the design is self-contained.

### Step 4: Tradeoff Validation

After the adversarial analysis returns, load the tradeoff-analysis skill if the review reveals unclear tradeoffs:
```
load_skill(skill_name="tradeoff-analysis")
```

Verify:
- Are the stated tradeoffs actually what the design achieves?
- Are there unstated tradeoffs the designers may not have recognized?
- Does the design optimize for what the team actually needs?

### Step 5: Synthesize and Recommend

Present findings to the user:

**Assessment Summary:**
- Overall health: [strong / has concerns / needs significant revision]
- Critical risks: [list]
- Tradeoff alignment: [does the design achieve what it claims?]

**Recommendation:** One of:
- **Proceed** -- risks are acceptable, design is sound
- **Proceed with modifications** -- [specific changes needed]
- **Reconsider** -- [fundamental issue that requires rethinking]

Ask: **"Do these findings match your intuition? Are there aspects of the design I should look at more closely?"**

### Step 6: Capture Action Items

If the user wants to proceed with modifications, produce a clear action list:
1. What to change (specific, not vague)
2. Why (linked to a specific risk or finding)
3. Priority (must-do vs should-do vs nice-to-do)
