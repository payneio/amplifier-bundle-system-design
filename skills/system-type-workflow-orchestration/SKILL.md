---
name: system-type-workflow-orchestration
description: "Domain patterns for workflow orchestration systems — long-running processes, state machines, saga coordination, human-in-the-loop gates, retry and timeout hierarchies, and failure modes. Use when designing or evaluating workflow engines, job orchestrators, or multi-step business process systems."
---

# System Type: Workflow Orchestration

Patterns, failure modes, and anti-patterns for long-running workflow and process orchestration systems.

---

## Core Patterns

### Orchestration vs Choreography

**Orchestration.** A central coordinator owns the workflow definition and explicitly directs each step. The coordinator calls services, waits for results, handles failures, and decides what happens next. The entire flow is visible in one place.
**When to use.** Complex multi-step processes (5+ steps). Flows with conditional branching, retries, timeouts, or compensation logic. When you need a single place to understand what the process does. When you need to answer "where is this order in the pipeline?" without querying every service.
**When to avoid.** Simple event reactions (service A publishes, service B reacts). When the coordinator becomes a bottleneck or single point of failure you can't tolerate. When teams owning individual steps need to evolve independently without touching the orchestrator.

**Choreography.** Each service listens for events and decides what to do next. No central coordinator. The process is emergent from the event chain.
**When to use.** Loosely coupled domains where services genuinely don't need to know about each other. Simple fan-out patterns (order placed → send email, update analytics, reserve inventory). When the number of steps is small (≤3) and failure handling is straightforward.
**When to avoid.** When you catch yourself drawing the event flow on a whiteboard and it takes more than 60 seconds to explain. When debugging requires tracing events across 6 services to figure out why an order is stuck. When compensation logic is non-trivial — choreographed compensation is a nightmare to reason about.

**The honest tradeoff.** Choreography feels elegant and decoupled until something goes wrong. Orchestration feels heavy and centralized until you need to debug a production incident at 2am. Most teams that start with choreography for complex flows end up building an ad-hoc orchestrator anyway — they just don't call it that, and it's worse than a purpose-built one.

### State Machines

**What it is.** Model workflow as a finite set of states with explicit transitions between them. Each transition has a trigger (event, condition, timeout) and may have side effects.
**When to use.** Workflows with well-defined states and transitions: order processing, approval flows, document lifecycle, account provisioning. When you need to enforce that certain transitions are illegal (e.g., can't ship before payment). When auditors ask "what are all the possible states this entity can be in?"
**When to avoid.** Workflows where the number of states explodes combinatorially (parallel execution with many branches). Purely sequential pipelines where a state machine adds ceremony without value.
**Key discipline.** Every state machine needs an explicit terminal state and a timeout for every non-terminal state. A state machine without timeouts is a state machine that accumulates orphaned instances forever.

### DAG-Based Workflows

**What it is.** Model workflow as a directed acyclic graph where nodes are tasks and edges are dependencies. Tasks with no unmet dependencies can execute in parallel.
**When to use.** Data pipelines, build systems, ETL jobs, ML training pipelines — anywhere the work is a dependency graph with parallelism opportunities. When tasks are largely independent and the critical path optimization matters.
**When to avoid.** Workflows with cycles (approval → rejection → resubmission). Workflows where the graph shape depends on runtime results (conditional branching makes DAGs awkward). Long-running workflows with human interaction — DAG engines are typically designed for batch, not for processes that pause for days.
**Key systems.** Airflow, Prefect, Dagster, Argo Workflows. Each has different opinions about dynamic DAGs, task isolation, and scheduling.

### Step Functions / Serverless Workflows

**What it is.** Define workflow as a JSON/YAML state machine executed by a managed service (AWS Step Functions, Azure Logic Apps, Google Cloud Workflows). Each step invokes a Lambda/function, waits for a callback, or branches on conditions.
**When to use.** Cloud-native architectures where you want the provider to handle state persistence, retries, and execution history. Workflows with moderate complexity (10–50 steps). When operational burden of running a workflow engine is higher than the vendor lock-in cost.
**When to avoid.** When you need to test workflows locally without cloud emulators. When workflow logic is complex enough that JSON state machine definitions become unreadable (and they become unreadable fast). When you need sub-second latency for step transitions. When you're not already committed to that cloud provider.
**The real cost.** Step Functions are cheap per transition but expensive in developer time when debugging. The execution history UI is good for happy paths and terrible for understanding why step 17 of 40 failed on the third retry.

### Durable Execution (Temporal, Durable Task Framework)

**What it is.** Write workflow logic as normal code (functions, loops, conditionals). The runtime persists execution state so that if the process crashes, it replays the code from the beginning, skipping activities that already completed (using their recorded results). The code is the workflow definition.
**When to use.** Complex workflows that are hard to express as state machines or DAGs. Workflows with deeply nested conditionals, loops with variable iteration counts, or error handling that needs the full power of a programming language. When you want developers to write workflows in the same language they write everything else.
**When to avoid.** Simple linear workflows where a state machine is sufficient. When the team can't internalize the deterministic replay constraint (this is harder than it sounds). When the operational cost of running a Temporal cluster is disproportionate to the workflow complexity.
**The critical constraint.** Workflow code must be deterministic. Every execution, including replays, must make the same decisions given the same activity results. Non-deterministic operations (random numbers, current time, UUIDs, reading environment variables) must go through the SDK's deterministic APIs. Violating this breaks replay and corrupts workflow state. See: Workflow Versioning, Non-Deterministic Replay.


## Durability and State

### The Durable Execution Model

The central insight of durable execution: separate the workflow's decisions from its side effects. Decisions (if/else, loops, which activity to call next) are deterministic and replayable. Side effects (calling an API, writing to a database, sending an email) are recorded as events so they're not repeated on replay.

**Event history.** Every workflow maintains an ordered event history: activity scheduled, activity completed (with result), timer started, timer fired, signal received. On replay, the runtime feeds recorded results back to the workflow code instead of re-executing activities.

**Checkpointing.** After each event, the workflow's state is implicitly checkpointed. If the worker crashes, a new worker picks up the workflow from the last event and replays forward. No explicit serialization of workflow state is needed — the code itself is the state machine, and the event history is the checkpoint.

### Event Sourcing for Workflow State

Workflow engines are, at their core, event-sourced systems. The event history is the source of truth; current state is derived by replay. This gives you:
- **Full audit trail.** Every decision and side effect is recorded.
- **Time travel.** Replay the workflow to any point in its history for debugging.
- **State reconstruction.** No need to serialize complex in-memory state — just replay events.

**The cost.** Event histories grow. A workflow that runs 10,000 loop iterations has 10,000+ events. Replay becomes slow. Mitigation: periodic snapshots (called "continue-as-new" in Temporal) that truncate history and start a fresh execution with carried-over state.

### Workflow Versioning and Replay Determinism

Workflow code must produce the same sequence of commands (schedule activity, start timer, etc.) when replayed with the same event history. This is the determinism contract.

**What breaks determinism:**
- Adding or removing an activity call in existing workflow code
- Changing the order of activity calls
- Using `time.now()`, `random()`, `uuid()` directly instead of through the SDK
- Reading configuration or environment variables that change between deployments
- Conditional logic that depends on anything other than activity results or signals

**What's safe:**
- Changing activity implementation (the activity is a separate function)
- Adding new workflow definitions (existing workflows don't use them)
- Changing activity retry policies (policies are evaluated at schedule time, not replay time — but check your SDK)
- Adding new signal handlers (signals not yet received don't affect replay)


## Timeout Hierarchies

Timeouts in workflow systems are not a single value. They form a hierarchy, and misconfiguring any level causes cascading failures.

### The Four Timeout Layers

**Schedule-to-start timeout.** How long a task can wait in the queue before a worker picks it up. Detects: worker pool exhaustion, deployment gaps, task routing misconfiguration. If this fires, it means no worker was available — retrying the same activity immediately is pointless.

**Start-to-close timeout.** How long a single activity attempt can run once a worker picks it up. This is the "execution timeout" most people think of. Set it to the maximum expected duration of the activity plus margin. Too short: legitimate work gets killed. Too long: stuck activities hold resources.

**Schedule-to-close timeout.** End-to-end timeout for the activity including all retries. This is the overall budget. If schedule-to-close is 60s and start-to-close is 30s, you get at most 2 attempts. This timeout is what the workflow cares about — "I need this done within X, including retries."

**Workflow execution timeout.** How long the entire workflow can run. The backstop. Set this to the maximum business-acceptable duration. Without it, broken workflows run forever.

### Heartbeating

For long-running activities (minutes to hours), heartbeating lets the activity report progress. If the runtime doesn't receive a heartbeat within the heartbeat timeout, it considers the activity failed and can retry on a different worker.

**When to use.** Any activity longer than 60 seconds. File processing, ML training, batch imports, external API polling.
**What to report.** Progress information in the heartbeat details (e.g., "processed 4500 of 10000 records"). On retry, the new attempt can read the last heartbeat's details and resume from where the previous attempt left off rather than starting over.
**The cascade when heartbeating is missing.** A worker dies mid-activity. Without heartbeating, the runtime doesn't know until the start-to-close timeout expires (potentially minutes or hours later). The workflow is stuck for that entire duration. With heartbeating at 30-second intervals, detection happens within 30 seconds.

### Timeout Misconfiguration Patterns

- **No schedule-to-start timeout.** Activities queue silently when workers are down. Nobody notices until the workflow timeout fires (or never fires, if that's also missing).
- **Start-to-close shorter than actual work.** Activity gets killed repeatedly. Retries burn through the schedule-to-close budget. Workflow fails with a timeout error that looks like the activity is broken when it's just slow.
- **Workflow timeout missing entirely.** Broken workflows accumulate forever. Discovered months later when someone notices 50,000 open workflow executions consuming cluster resources.
- **All timeouts set to the same value.** Eliminates the hierarchy's diagnostic value. When everything times out at 30s, you can't distinguish "worker pool exhausted" from "activity is slow" from "workflow is stuck."


## Compensation and Rollback

### The Saga Pattern

A saga is a sequence of local transactions where each step has a compensating action that semantically undoes it. If step N fails, compensating actions for steps N-1 through 1 are executed in reverse order.

**Orchestrated saga.** A central coordinator manages the sequence and triggers compensations. The coordinator knows the full compensation chain. Easier to reason about, test, and monitor.

**Choreographed saga.** Each service listens for failure events and triggers its own compensation. No central coordinator. The compensation chain is distributed across services. Harder to ensure all compensations run, harder to debug when they don't.

**Use orchestrated sagas.** In almost every case. Choreographed sagas are a foot-gun for anything beyond trivial flows.

### Forward Recovery vs Backward Recovery

**Backward recovery (compensation).** Undo what was done. Cancel the payment, release the reservation, delete the provisioned resource. This is the classic saga approach.

**Forward recovery (retry/resume).** Don't undo — keep trying to move forward. Retry the failed step, wait for an external dependency to recover, use a fallback. Often cheaper than compensation when the failure is transient.

**The decision framework:** Can the failure be retried? → Forward recovery. Is the failure permanent and the partial state harmful? → Backward recovery. Is the failure permanent but the partial state acceptable? → Mark as failed and alert a human.

### When Compensation Is Harder Than the Forward Action

This happens more often than anyone admits during design reviews:

- **Sent an email.** You cannot unsend it. Compensation: send a correction email (which may confuse the user more).
- **Charged a credit card.** Refund is not instant, incurs processing fees, and may take days to appear.
- **Published an event.** Downstream consumers already acted on it. Compensation: publish a reversal event, hope all consumers handle it.
- **Provisioned infrastructure.** Teardown may fail, leave orphaned resources, or have dependencies that prevent deletion.
- **Updated a third-party system.** The third-party API may not support "undo" or may have rate limits on corrections.

**The design implication.** Order your saga steps so that hard-to-compensate actions happen last. Validate and reserve early; commit late. If you must do something irrevocable mid-saga, that's where you put the human approval gate.


## Human-in-the-Loop

### Approval Gates

**What it is.** The workflow pauses at a defined point and waits for a human to approve, reject, or modify before continuing.

**Implementation patterns:**
- **Signal-based.** Workflow waits for an external signal (Temporal signal, Step Functions callback). Human action is delivered as a signal from a UI or API.
- **Task-based.** Create a task in an external system (Jira ticket, approval queue in a UI). Poll or receive webhook when the task is resolved.
- **Callback-based.** Generate a unique callback URL. Include it in an email or Slack message. Human clicks approve/reject, which calls the URL, which signals the workflow.

### SLA Timers on Human Steps

Every human step needs a timeout. Humans forget, go on vacation, leave the company, or simply don't check their email.

**Escalation ladder:**
1. Initial notification to the approver.
2. Reminder after X hours/days.
3. Escalation to the approver's manager or a backup approver after Y hours/days.
4. Auto-approve, auto-reject, or route to a fallback handler after Z hours/days.

**The values of X, Y, and Z depend on business context** but they must exist. A workflow waiting for human approval with no timeout will wait forever. You will discover this when someone asks why 200 orders are stuck in "pending approval" and the approver left the company 3 months ago.

### Notification Fatigue

The fastest way to make approval gates useless is to send too many notifications. If an approver gets 50 approval requests per day, they'll either approve everything without reading (security theater) or ignore them all (workflow stall).

**Mitigations:**
- Batch notifications: "You have 7 pending approvals" once daily, not 7 separate emails.
- Risk-based routing: auto-approve low-risk items, require human review only for high-risk.
- Approval delegation: let approvers delegate to others when they're unavailable.
- Dashboard over email: a queue UI the approver checks proactively, not a flood of emails they learn to ignore.

### Audit Trails

Every human decision in a workflow must be recorded: who approved, when, what they saw at the time, and any comments. This is non-negotiable for regulated industries and a best practice everywhere else.

**Record:** The actor (authenticated identity, not just a name). The timestamp. The workflow state at the time of the decision. The decision itself. Any freeform comments. The IP address and client (for security-sensitive approvals).


## Retry Strategies

### Per-Activity Retry Policies

Each activity should have its own retry policy. A database write and an HTTP call to a flaky third-party API have completely different failure modes and need different retry behavior.

**Policy parameters:**
- **Initial interval.** How long to wait before the first retry. Start small for transient failures (100ms–1s).
- **Backoff coefficient.** Multiplier for each subsequent retry. 2.0 is standard. Higher values back off faster (good for rate limits).
- **Maximum interval.** Cap on the backoff. Without this, exponential backoff eventually produces multi-hour waits.
- **Maximum attempts.** Hard limit on retry count. Prevents infinite retry loops.
- **Non-retryable error types.** Errors that should immediately fail without retrying: validation errors, permission denied, not found. Retrying a 400 Bad Request is pointless.

### Exponential Backoff with Jitter

Always add jitter. Without it, all workflows that failed at the same time retry at the same time, causing retry storms.

**Full jitter formula:** `sleep = random_between(0, min(max_interval, initial_interval * backoff^attempt))`

**Equal jitter formula:** `temp = min(max_interval, initial_interval * backoff^attempt); sleep = temp/2 + random_between(0, temp/2)`

Full jitter gives better distribution. Equal jitter gives a minimum wait floor. Either is dramatically better than no jitter.

### Retry vs Skip vs Fail-Workflow Decisions

Not every activity failure should retry. Not every activity failure should kill the workflow.

- **Retry.** Transient failures: network timeouts, 503s, database connection errors, rate limit responses with retry-after headers. The activity is expected to succeed if tried again.
- **Skip (with default/fallback).** Non-critical enrichment steps: geocoding an address, fetching a user's profile photo, calling a recommendation engine. The workflow can proceed with degraded data.
- **Fail workflow.** Business logic violations: insufficient funds, item out of stock, user account suspended. No amount of retrying will fix the fundamental problem.
- **Pause and alert.** Unexpected errors that might be transient but might indicate a systemic problem. The workflow pauses, an operator investigates, and manually resumes or fails the workflow.

### Poison Pill Detection

A poison pill is an input that consistently causes an activity to fail in a way that looks retryable but will never succeed. Example: a malformed record that causes a serialization error that happens to return a 500 (retryable) instead of a 400 (non-retryable).

**Detection:** Track the failure reason across retries. If the same error message repeats across all attempts, it's likely a poison pill, not a transient failure.
**Mitigation:** After max retries, route the input to a dead-letter queue or failed-items table for manual inspection. Don't let it block other workflows.


## Workflow Versioning

### The Problem

You have 10,000 running workflow instances using version 1 of your workflow code. You need to deploy version 2, which adds a new step between steps 3 and 4. What happens to the in-flight instances?

### Strategies

**Version-aware patching (Temporal's approach).** Use version markers in workflow code. When replaying, the runtime checks the version marker and executes the old code path for old executions and the new code path for new ones. The workflow code accumulates version branches over time.

```
if workflow.get_version("add-fraud-check", DEFAULT, 1) == 1:
    await workflow.execute_activity(fraud_check, ...)
```

**Pros:** In-flight workflows continue without interruption. No migration needed.
**Cons:** Version branches accumulate. After 20 changes, the workflow code is unreadable. Requires discipline to eventually clean up old branches after all old executions complete.

**Workflow ID-based routing.** Run old and new worker versions simultaneously. Route existing workflow IDs to old workers and new workflow IDs to new workers. Old workers are decommissioned after all old executions complete.
**Pros:** Clean code — no version branches. Each version is a clean snapshot.
**Cons:** Operational complexity of running multiple worker versions simultaneously. Resource cost doubles during the transition.

**Terminate and restart.** Terminate in-flight workflows and restart them on the new version, potentially providing the new execution with state extracted from the old one's history.
**Pros:** Simple. No version branching. No dual-running workers.
**Cons:** Only works if workflows can be safely restarted. Doesn't work for workflows mid-way through non-idempotent operations. Requires building the state extraction and re-initialization logic.

**Continue-as-new.** At a safe checkpoint, the workflow completes and starts a new execution with carried-over state, now running the new code version.
**Pros:** Natural truncation of event history. Clean version transitions.
**Cons:** Only works at defined checkpoints. Workflows between checkpoints must finish on the old version first.

### The Practical Advice

Use version-aware patching for small, frequent changes. Use workflow ID-based routing for major rewrites. Use continue-as-new for long-running workflows that naturally have checkpoint boundaries (e.g., end-of-day processing). Plan your versioning strategy before your first deployment, not after your first broken replay.


## Common Failure Modes

- **Non-deterministic replay.** Workflow code uses a non-deterministic operation (system clock, random number, network call) directly instead of through the SDK. On replay, the code takes a different path than the original execution. The runtime detects a mismatch and fails the workflow with a non-determinism error. Every in-flight workflow using that code is now broken. This is the single most common and most devastating failure mode in durable execution systems.

- **Timer drift.** Timer-based workflows assume wall-clock precision, but timer resolution depends on the workflow engine's polling interval and worker availability. A "fire in exactly 60 seconds" timer might fire at 62 seconds or 300 seconds if the worker pool is busy. Design for "at least X" semantics, never "exactly X."

- **Orphaned workflows.** Workflows that are waiting for a signal, callback, or event that will never arrive. Causes: the external system was decommissioned, the callback URL was lost, the human approver left the company. Mitigation: every waiting state needs a timeout. Run periodic queries for workflows stuck in a waiting state beyond their expected duration.

- **Resource exhaustion from fan-out.** A workflow fans out to 10,000 child workflows or activities simultaneously. The worker pool, the database, and the downstream services all collapse under the sudden load. Mitigation: batch fan-out with concurrency limits. Process 100 at a time, not 10,000.

- **Infinite retry loops.** An activity fails with an error that looks transient but is actually permanent. The retry policy keeps retrying. Schedule-to-close timeout is missing or set to days. The workflow burns compute retrying an operation that will never succeed. Mitigation: non-retryable error classification, maximum attempt limits, schedule-to-close timeouts, poison pill detection.

- **Workflow state bloat.** Long-running workflows accumulate events in their history. A workflow that processes a queue by looping accumulates events per iteration. After 100,000 iterations, replay takes minutes and the event history consumes significant storage. Mitigation: continue-as-new to periodically reset history. Design workflows to complete and restart rather than run indefinitely.

- **Worker deployment coordination failures.** Deploying new worker code while old workflows are still replaying. The new code is not backward-compatible with old event histories. Result: non-determinism errors across all in-flight workflows. Mitigation: versioning strategy (see Workflow Versioning). Rolling deployments with version-aware patching. Never deploy breaking workflow changes without a versioning mechanism.

- **Cascading child workflow failures.** A parent workflow starts 100 child workflows. Child workflow 47 fails. The parent's error handling logic cancels all remaining children and triggers compensation. But some children have already completed and produced side effects. The compensation logic doesn't account for partially-completed fan-out. Mitigation: design compensation to be idempotent. Track which children completed and what they did. Compensate only completed children.

- **Signal loss.** Signals sent to a workflow that is currently in the middle of replaying or transitioning state. Depending on the engine, the signal may be buffered, dropped, or cause unexpected behavior. Mitigation: use signals only through the engine's SDK. Validate signal delivery with idempotency keys. Design for at-least-once signal delivery.

- **Scheduled workflow pile-up.** Cron-scheduled workflows that take longer to execute than the cron interval. The 1:00 PM run is still going when the 2:00 PM run starts. Now you have two instances processing the same data. Mitigation: overlap policies (skip if previous is still running), distributed locks, or making the processing idempotent.


## Anti-Patterns

- **The God Workflow.** A single workflow that orchestrates the entire business process from order placement through fulfillment through invoicing through customer notification through analytics update. It has 200 steps, 40 branch conditions, and nobody understands it. Break workflows at domain boundaries. A workflow should map to one bounded context, not one business process end-to-end.

- **Synchronous HTTP disguised as workflow.** Using a workflow engine to make three sequential HTTP calls that take 200ms each. The workflow overhead (state persistence, event history, replay capability) adds latency and complexity for a process that should just be three HTTP calls in a service method. Use workflow engines for processes that need durability, not for request-response coordination.

- **Activities with business logic.** Putting conditional logic, state manipulation, and decision-making inside activities instead of the workflow function. Activities should be side effects: call an API, write to a database, send a message. Decisions belong in the workflow function where they are deterministic and replayable.

- **Polling in a loop without backoff.** Workflow checks an external condition in a tight loop: start activity to check condition, condition not met, immediately start activity again. This hammers the external system and generates enormous event histories. Use timers between polls. Back off if the condition is expected to take time.

- **Missing idempotency in activities.** Activity calls an external API. The call succeeds but the worker crashes before recording the result. On retry, the activity calls the API again. Now you've charged the customer twice, created two shipments, or sent two emails. Every activity that produces side effects must be idempotent — use idempotency keys, check-before-write patterns, or at-most-once delivery mechanisms.

- **Workflows that never complete.** Designing workflows as infinite loops that process items from a queue forever. The event history grows unboundedly, replay slows down, and the workflow becomes a ticking time bomb. Use continue-as-new to reset periodically, or design as a workflow-per-item triggered by an external scheduler.

- **Hardcoded timeouts.** Embedding timeout values directly in workflow code without considering that different environments (dev, staging, production) have different performance characteristics and different SLAs. Timeouts should be configurable, not constants. A 5-second timeout that works in production will flake constantly in a slow CI environment.

- **Testing only the happy path.** Writing tests that verify the workflow completes when all activities succeed. Never testing: activity failures, partial compensation, timeout scenarios, signal delivery during replay, concurrent signals, workflow cancellation mid-execution. Workflow failure modes are combinatorial. If you only test the happy path, you will discover the unhappy paths in production.

- **Treating the workflow engine as a job queue.** Using Temporal or Step Functions when all you need is "run this function asynchronously and retry if it fails." A job queue (SQS + Lambda, Celery, Sidekiq, BullMQ) is simpler, cheaper, and operationally lighter. Workflow engines earn their complexity when you need multi-step coordination, conditional branching, long-running state, or human interaction. If your "workflow" is one step, you don't need a workflow engine.
