# Agentic System Design

## On Agentic Design

Train for structure, not just intelligence.

A stronger systems-thinking agent usually needs five upgrades:

**1. Make it model the system before solving**
Have it produce, internally or explicitly:

* goals
* constraints
* actors
* resources
* interfaces
* feedback loops
* failure modes
* time horizons
* tradeoffs

A weak agent jumps to answers. A stronger one first builds a map.

Useful prompt pattern:
“Before proposing a solution, identify the system boundaries, key components, dependencies, constraints, bottlenecks, and likely second-order effects.”

**2. Force multiscale reasoning**
Architects think at several layers at once:

* principle level: what must be true
* structural level: components and interactions
* operational level: runtime behavior and edge cases
* evolutionary level: how the design changes over time

So require outputs in layers:

* assumptions
* architecture
* critical paths
* failure scenarios
* migration path

This alone improves quality materially.

**3. Train it on tradeoff analysis, not best-practice mimicry**
Most agents overfit to “good sounding patterns.” Real architecture is choosing what to sacrifice.

Have it compare options using a fixed frame:

* latency
* complexity
* reliability
* cost
* security
* scalability
* reversibility
* organizational fit

Prompt it to answer:
“What does this design optimize for, and what does it make worse?”

That question is architecturally catalytic.

**4. Make it reason causally**
Systems thinkers trace propagation:

* if X changes, what downstream breaks?
* what is coupled that appears independent?
* where are delays, hidden state, or nonlinearities?
* what incentives create local optimization and global harm?

Ask for:

* first-order effects
* second-order effects
* unintended consequences
* monitoring signals

**5. Give it architectural primitives**
If you want better architecture, give it reusable abstractions:

* boundaries and ownership
* contracts/interfaces
* source of truth
* sync vs async
* state machines
* queues
* caches
* idempotency
* retries
* backpressure
* consistency models
* observability
* blast radius isolation

An agent that knows many patterns is less useful than one that knows when each pattern is wrong.

---

What to change in practice:

**Use a structured response template**
For any nontrivial problem, make it answer in this order:

1. Problem framing
2. Assumptions
3. System boundaries
4. Components and responsibilities
5. Data/control flows
6. Risks and failure modes
7. Tradeoffs
8. Recommended design
9. Migration or rollout plan
10. Metrics to validate success

This prevents shallow output.

**Create an “architect mode” rubric**
Score every answer on:

* completeness of system map
* explicit assumptions
* tradeoff depth
* edge-case coverage
* operational realism
* simplicity
* reversibility

Then have the agent critique and revise itself against that rubric.

**Teach it to generate alternatives**
Require at least 3 architectures:

* simplest viable
* most scalable
* most robust

Then force a recommendation with reasoning. Good architects explore the design space before converging.

**Add adversarial review**
After it proposes a design, have it switch roles:

* SRE: how does this fail in production?
* security reviewer: what is the abuse path?
* staff engineer: where is the hidden complexity?
* finance owner: what cost curve appears later?
* operator: what becomes painful at 2 a.m.?

This produces much better architecture than a single-pass answer.

**Train it on postmortems and design docs**
Best corpus:

* good architecture decision records
* incident reports
* scaling retrospectives
* migration plans
* failed designs and why they failed

Systems thinking improves a lot when the model sees consequences, not just polished final designs.

**Prefer simulation over rhetoric**
Ask it for:

* sequence diagrams
* dependency graphs
* state transitions
* failure injection scenarios
* capacity stress assumptions

Architecture quality rises when outputs become mechanistic.

---

A strong meta-prompt for this is:

“Act as a systems architect. Do not jump to a solution. First model the system: objectives, boundaries, actors, constraints, dependencies, control flows, feedback loops, and failure modes. Then generate three candidate architectures with explicit tradeoffs. Evaluate them across complexity, reliability, scalability, cost, security, and reversibility. Recommend one, explain why, identify second-order effects, and propose metrics and a migration path.”

---

If you’re building this into the agent itself, I’d add these permanent behaviors:

* always surface assumptions
* distinguish local vs global optimization
* ask what scales with usage, time, and org size
* identify tight coupling
* look for single points of failure
* prefer reversible decisions early
* separate mechanism from policy
* name unknowns and monitoring needs

That is close to the core of architectural judgment.

The deepest shift is this:
Don’t train the agent to answer “what should we build?”
Train it to answer “what system are we actually entering, and how will this decision propagate?”

That produces an architect.

I can turn this into a concrete agent spec or system prompt next.

## On Simplicity

Simplicity is central. Without it, “systems thinking” often degrades into ornate overengineering.

A good architect does not merely see more of the system. They preserve clarity while seeing more of it.

Three distinctions matter:

**1. Simple is not small**
A system can be large yet simple if:

* responsibilities are clear
* interfaces are narrow
* behavior is predictable
* failures are legible

Conversely, a tiny system can be complex if every part depends on hidden context.

So the agent should optimize for **structural simplicity**, not minimal component count.

**2. Simplicity is what remains understandable under change**
The real test is not “does this look elegant now?”
It is:

* can someone modify it safely?
* can someone explain it in one pass?
* can production behavior be predicted?
* can failure be contained?

That is architectural simplicity.

**3. Simplicity is a constraint, not an aesthetic preference**
You should make the agent explicitly ask:

* what is the simplest design that satisfies the real requirements?
* which parts are essential vs speculative?
* what can be deferred?
* where are we adding abstraction before we have evidence?

That prevents premature generalization.

A useful rule for the agent:

**Prefer the simplest design whose failure modes are acceptable.**

Not the simplest possible design.
Not the most scalable imaginable design.
The simplest one that is adequate.

Have it evaluate designs on these simplicity dimensions:

* **Conceptual simplicity**: how many ideas must be held in mind?
* **Interface simplicity**: how many contracts and exceptions exist?
* **Operational simplicity**: how hard is it to deploy, debug, and recover?
* **Evolutionary simplicity**: how hard is it to extend later?
* **Organizational simplicity**: does this match the team’s actual ability?

That last one matters a lot. A design that is “clean” in theory but exceeds team cognition is not simple.

You can bake this into the agent with prompts like:

“Penalize unnecessary abstraction, speculative scalability, and hidden coupling. Prefer designs with fewer concepts, clearer ownership, and more reversible decisions.”

And:

“After proposing a design, explain how to simplify it by 30% without violating the core requirements.”

That is a very strong forcing function.

Another good step is to require two outputs:

* the recommended design
* the **simplest credible alternative**

If those are very far apart, the agent is probably overbuilding.

A compact simplicity rubric:

* Can each component be named in one sentence?
* Can each interface be described briefly and precisely?
* Can the failure path be explained clearly?
* Can the design be drawn without clutter?
* Can a new engineer predict where a change belongs?
* Can a feature be removed without unraveling the system?

If not, it is not simple enough.

The subtle point is this:

**Simplicity is not the opposite of systems thinking.**
It is the discipline that prevents systems thinking from turning into systems theater.

A strong agent should therefore do two things at once:

* widen its view enough to see consequences
* compress its design enough to preserve clarity

That combination is rare, and it is exactly what good architects do.

A very good standing instruction would be:

“Think broadly about the system, but design narrowly. Use the minimum number of concepts, components, and abstractions needed to meet the requirements with acceptable risk.”

That one sentence carries a lot.
