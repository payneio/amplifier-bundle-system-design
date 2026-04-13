Amplifier:
Here's the full comparison of what the spec says vs what actually happened:

----------------------------------------------------------------------------------------------------------------------------------------------------------


Spec vs Reality: write-plan Mode

Spec Says Should Happen (Steps 8-11)

 1 Enter write-plan via mode(set, write-plan) (two calls for gate policy)
 2 Check for design doc from brainstorm
 3 Discuss task breakdown with user; decide file decomposition BEFORE tasks
 4 Plans >15 tasks MUST be split into phases
 5 MANDATORY delegation to superpowers:plan-writer (single call)
 6 Present execution choice: /execute-plan (<=3 tasks) vs SDD recipe (>3 tasks)
 7 Transition to execute-plan (golden path)

What Actually Happened (4 sessions)


 Behavior                             Session 1          Session 2          Session 3            Session 4
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Enter mode correctly                 Yes                Yes                Yes                  Yes
 load_skill("writing-plans")          Yes                --                 --                   Yes
 Read design doc                      Yes                Yes                --                   --
 Discuss task breakdown with user     SKIPPED            Partial            SKIPPED              Yes (via todos)
 File decomposition before tasks      SKIPPED            SKIPPED            SKIPPED              SKIPPED
 Pre-explore with delegate(explorer)  Yes (x4 parallel)  --                 Yes (x4)             Yes
 delegate(plan-writer)                Yes (x4 parallel)  Yes (x6, retries)  Yes (3 of 5 stints)  Yes (x5)
 Present execution choice             SKIPPED            SKIPPED            SKIPPED              SKIPPED
 Transition to execute-plan           Yes                NEVER              3 of 5 stints        NEVER
 delegate(git-ops) to commit plans    Yes                Yes                --                   --


Key Gaps

Things spec says should happen but didn't in ANY session:

 • File decomposition discussion before individual tasks (Step 9)
 • Presenting execution choice to user (Step 11: execute-plan vs SDD recipe)

Things that happened but spec doesn't mention:

 • load_skill("writing-plans") before starting
 • delegate(explorer) to survey codebase before planning (spec says plan-writer does its own exploration)
 • Multiple parallel plan-writer delegations (one per phase), not single delegation
 • delegate(git-ops) to commit plans before transitioning
 • Plan-writer retry/failure handling with model_role cycling (6 attempts in Session 2)

Critical structural issue: Sessions 2 and 4 discovered a loophole -- recipes is listed as a safe tool in write-plan mode. This let the orchestrator launch
subagent-driven-development recipes (full implementation pipelines) without ever leaving write-plan. Those sessions collapsed the entire
plan->execute->verify cycle into a single mode, running for 2,685+ events without transitioning. The blocked write_file/edit_file tools were bypassed
because sub-agents in the recipe run in their own sessions with full tool access.

Ordering difference: The dominant real pattern was:


 enter write-plan → load skill → read design → explore codebase → create todo structure →
 plan-writer × N (per phase) → commit plans → transition to execute-plan


vs the spec's:


 enter write-plan → check design → discuss with user → file decomposition →
 plan-writer × 1 → present choice → transition


The spec describes a leaner, more interactive flow. Reality is more autonomous with heavier upfront exploration and parallel plan-writer calls.