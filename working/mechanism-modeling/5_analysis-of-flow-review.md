Two Changes, Not One

Change 1: Fix the synthesizer prompt (cheap, high impact)

The current synthesis step takes component descriptions at face value and generates an idealized narrative. Adding analysis rules to the prompt would
catch all 4 gaps we identified:


 Rule                                                             What it catches
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Tool availability determines behavior more than prose            delegate(explorer) before planning (can't write, must delegate)
 Skills matching mode name are loaded first                       load_skill("writing-plans") on write-plan entry
 When recipes is safe, LLM CAN launch pipelines from within mode  The SDD-inside-write-plan loophole
 Blocked tools force delegation patterns                          Parallel plan-writer calls, git-ops for commits


Plus tagging steps as [STRUCTURAL] (enforced by tool restrictions), [CONVENTIONAL] (described in prose, not enforced), or [INFERRED] (synthesizer's best
guess).

Change 2: Add a deterministic composition effects analysis step (moderate cost, targeted)

A pure Python script (no LLM) that computes from the already-parsed manifest:

 • Tool availability matrix per mode
 • Delegation necessity map (which operations MUST use delegation because direct tools are blocked)
 • Composition loopholes (safe tools that enable launching capabilities the mode seemingly prohibits)
 • Skill-mode associations by name matching

This gets fed to the synthesizer alongside the component descriptions.

What about session mining?

Zen-architect says: build it as a separate recipe, not a step in this one. Different lifecycle (accumulates over time), different consumers (validation,
anti-pattern detection), optional dependency. The behavioral spec recipe can reference session evidence if it exists, ignore it if it doesn't.

This is the right call. The two prompt/script changes alone would have caught every inaccuracy we found, without the complexity of session parsing.