---
name: design-philosophy-domain-driven
description: "Domain-Driven Design as a lens for system architecture — bounded contexts, aggregates, ubiquitous language, context mapping, domain events, and strategic vs tactical patterns. Use when modeling complex business domains, defining service boundaries, or evaluating whether a system's structure reflects its domain."
---

# Design Philosophy: Domain-Driven Design

DDD as a thinking tool for aligning system architecture with business reality.

---

## The Core Insight

Most systems fail not because of bad technology choices but because their structure doesn't match the problem they're solving. Domain-Driven Design is a response to that observation: **the shape of your software should reflect the shape of your business domain**.

This sounds obvious. In practice, it's rare. Most codebases are organized around technical concerns (controllers, services, repositories) rather than domain concepts (orders, shipments, policies). The result is code where you can't find the business logic — it's scattered across layers, buried in translation code, and duplicated in ways that diverge over time.

DDD provides a set of thinking tools for fixing that. Some are strategic (how to draw boundaries), some are tactical (how to model within a boundary), and the community is guilty of conflating the two. The strategic tools are almost universally valuable. The tactical tools are situational.

This skill focuses on applying DDD to real architecture decisions. Not a glossary of Evans-book terminology — a thinking framework for when you're staring at a system that doesn't make sense and need to figure out where the boundaries should be.

---

## 1. Ubiquitous Language

### The Principle

Every bounded context should have a language shared by developers, domain experts, product managers, and the code itself. The same words appear in conversations, user stories, class names, database columns, and API contracts. No translation. No "well, in the code we call it X but the business calls it Y."

This is the most important idea in DDD, and the one most teams skip because it feels soft. It isn't.

### Why It Matters Architecturally

Language mismatches are the leading indicator of boundary problems. When developers need a mental mapping table between business terms and code terms, one of two things is true:

1. **The code is modeling the wrong abstraction.** The business says "policy" and the code says `rule_set` — and over time, the code drifts because the developers don't attend the meetings where "policy" semantics get refined.
2. **You have two bounded contexts pretending to be one.** The word "account" means one thing to the billing team and another to the identity team, but they share a table and both are confused.

### The Practical Discipline

- **If you can't name it in the domain, you don't understand it.** Before writing code, you should be able to explain the concept to a domain expert using the same words that will appear in your code. If you can't, stop and go learn the domain.
- **The code is the source of truth for the language.** If a product manager says "let's add a discount" and your code has `PriceAdjustment`, `Rebate`, `PromoCode`, and `CouponRedemption`, your ubiquitous language has collapsed. Choose one term and make everyone use it.
- **Language boundaries reveal system boundaries.** When you notice that two teams use the same word to mean different things, you've found a bounded context boundary. Don't paper over it with a shared glossary — model it as two separate concepts.
- **Translation layers are technical debt.** Every `toBusinessModel()` / `fromBusinessModel()` adapter is a place where meaning gets lost. Some translation is inevitable (at context boundaries), but translation within a context means the model is wrong.

### What to Watch For

A team that can't agree on what to call something is a team that hasn't agreed on what it does. Naming debates aren't bikeshedding — they're domain modeling. Take them seriously.

---

## 2. Bounded Contexts

### The Principle

A bounded context is a linguistic and model boundary. Within a bounded context, every term has exactly one meaning, and the domain model is internally consistent. Across bounded contexts, the same word can (and often does) mean different things.

This is the single most valuable concept in DDD for working architects. If you take nothing else from the entire philosophy, take this.

### What It Actually Means

"Order" in the **Sales** context means a customer's expression of intent to purchase — it has line items, a customer reference, maybe a discount code. "Order" in the **Fulfillment** context means a set of items to be picked, packed, and shipped — it has warehouse locations, carrier assignments, weight calculations. "Order" in the **Billing** context means a set of charges to collect — it has payment methods, tax calculations, invoice line items.

These are not the same object with different views. They are **fundamentally different models** of different aspects of the business. Forcing them into one `Order` class creates a god object that serves nobody well.

### How Bounded Contexts Map to Architecture

| Bounded Context Boundary | Architectural Manifestation |
|---|---|
| Different meaning of same term | Separate services or modules with explicit contracts |
| Different rate of change | Separate deployable units |
| Different team ownership | Separate repositories or strong module boundaries |
| Different data consistency requirements | Separate databases or schemas |

A bounded context doesn't have to be a microservice. It can be a module within a monolith, a namespace, a separate schema in the same database. The boundary is about **model isolation**, not deployment topology.

### The Litmus Test

For any service or module, ask: **"Does every term in this codebase mean the same thing to everyone who touches it?"** If the answer is no, you have either:
- A bounded context that should be split, or
- A missing ubiquitous language that needs to be established.

### How to Identify Bounded Contexts

1. **Listen for linguistic friction.** When two groups argue about what a word means, they're in different contexts.
2. **Follow the org chart (carefully).** Conway's Law means team boundaries often align with context boundaries. Not always — but it's a useful starting point.
3. **Look at the data model.** When one table is being queried for completely different purposes by different parts of the system, the table is probably straddling a context boundary.
4. **Watch for "if this, then that" branching.** Code that says `if (order.type == SALES) ... else if (order.type == RETURN) ...` is a context boundary screaming to get out.

### The Most Common Mistake

Building one "canonical model" that every service shares. This feels like good engineering — one source of truth! In practice, it creates coupling so tight that no team can change anything without coordinating with every other team. The canonical model becomes the lowest-common-denominator model that satisfies nobody.

Each bounded context owns its own model. Communication between contexts happens through well-defined contracts, not shared objects.

---

## 3. Context Mapping

### The Principle

Bounded contexts don't exist in isolation. They relate to each other — data flows between them, one depends on another, teams negotiate interfaces. Context mapping is the discipline of explicitly documenting these relationships and choosing the right integration pattern for each.

### The Patterns

**Shared Kernel**: Two contexts share a subset of the model. Both teams own it jointly. This is high-coupling — use only when two contexts are so closely related that separate models would be absurd, and the teams trust each other enough to co-own code.

- *When it works*: Two contexts maintained by the same team. A domain concept that genuinely can't be split.
- *When it fails*: Cross-team shared kernels become coordination bottlenecks. One team's urgent change breaks the other.

**Customer-Supplier**: One context (supplier/upstream) provides data or services that another context (customer/downstream) consumes. The supplier accommodates the customer's needs in their API.

- *When it works*: Clear provider/consumer relationships with good-faith negotiation. The supplier team has capacity to serve the customer.
- *When it fails*: When the supplier team is under-resourced or doesn't care about the downstream consumers.

**Conformist**: The downstream context accepts the upstream's model as-is, without trying to translate. "We'll use their data structures because fighting it isn't worth the cost."

- *When it works*: Integrating with a dominant external system (Stripe, Salesforce) where the API is well-designed enough to use directly. Or when the upstream team is so much larger/more powerful that negotiation is impossible.
- *When it fails*: When the upstream model is a poor fit for your domain. You'll spend forever working around their assumptions.

**Anti-Corruption Layer (ACL)**: The downstream context builds a translation layer that converts the upstream's model into its own domain language. The upstream model never leaks into the downstream code.

- *When it works*: Integrating with legacy systems. Interfacing with external APIs whose model doesn't match your domain. Protecting your domain model from instability in upstream systems.
- *When it fails*: When the translation overhead isn't justified because the upstream model is close enough. ACLs are real code that needs maintenance.

**Open Host Service**: The upstream context provides a well-defined, versioned protocol (an API) for any downstream consumer, rather than custom integrations per consumer.

- *When it works*: A context that serves many consumers. Platform services. Internal APIs with multiple clients.
- *When it fails*: When you only have one consumer and the ceremony of a published API isn't justified.

**Published Language**: A shared interchange format (like a standard schema, protocol buffer definition, or industry-standard format) used for communication. Often paired with Open Host Service.

- *When it works*: Industry standards (HL7 for healthcare, FIX for finance). API schemas shared across an organization.
- *When it fails*: When the published language becomes a de facto shared kernel that's hard to evolve.

### Choosing a Pattern

Ask two questions:

1. **How much do you trust (and have leverage over) the upstream team?** High trust + leverage = Customer-Supplier or Shared Kernel. Low trust or no leverage = Conformist or ACL.
2. **How different are the models?** Similar models = Conformist or Shared Kernel. Very different models = ACL.

### The Organizational Reality

Context maps reflect power dynamics between teams. A team that "conforms" to another team's model is organizationally subordinate to them for that integration, whether anyone admits it or not. An anti-corruption layer is an organizational declaration of independence: "We will not let your model dictate our design."

Making these dynamics explicit is one of the most valuable things context mapping does. It turns invisible coupling into a diagram you can argue about.

---

## 4. Aggregates

### The Principle

An aggregate is a cluster of domain objects treated as a single unit for data changes. Every aggregate has a root entity (the aggregate root) that is the only object external code can reference directly. All modifications to the aggregate go through the root.

The aggregate boundary is a **consistency boundary**: everything inside an aggregate is guaranteed to be consistent after a transaction. Everything across aggregates is eventually consistent.

### Why Aggregates Should Be Small

The most common DDD mistake is making aggregates too large. The temptation is to put everything that's "related" into one aggregate. An `Order` aggregate that contains `LineItems`, `ShippingAddress`, `PaymentInfo`, `CustomerPreferences`, and `AuditHistory` is too large because:

- **Concurrency conflicts.** The larger the aggregate, the more likely two users modify it simultaneously. If adding a line item and updating the shipping address both lock the entire `Order`, you have unnecessary contention.
- **Transaction scope.** The aggregate is the transaction boundary. Larger aggregates mean larger transactions, which mean more lock contention, longer database operations, and higher failure rates.
- **Memory overhead.** Loading the entire aggregate into memory when you only need one piece of it wastes resources.

### The Rule: One Transaction = One Aggregate

A single business operation should modify at most one aggregate. If you find yourself needing to update two aggregates in one transaction, you have one of three problems:

1. **The aggregates should be merged.** They're actually one consistency boundary.
2. **The operation should be eventual.** Use a domain event to update the second aggregate asynchronously.
3. **You're over-engineering.** Maybe you don't need aggregates at all for this part of the domain.

### How to Find Aggregate Boundaries

- **What must be immediately consistent?** An `Order` and its `LineItems` must add up correctly at all times — they're one aggregate. An `Order` and the customer's `LoyaltyPoints` can be eventually consistent — they're separate aggregates.
- **What's the invariant?** Aggregates exist to protect business invariants. "Total must equal sum of line items" is an invariant that defines the `Order` aggregate boundary. If there's no invariant to protect, you might not need an aggregate.
- **What's the unit of concurrent access?** If two users typically modify different parts of the data simultaneously, those parts should be separate aggregates.

### Cross-Aggregate References

Aggregates reference each other by identity (ID), not by direct object reference. The `Order` aggregate holds a `customerId`, not a `Customer` object. This enforces the boundary — you can't accidentally reach into another aggregate's internals.

### When You Don't Need Aggregates

If your domain is essentially CRUD — create a record, read it, update some fields, delete it — aggregates add complexity without value. Aggregates exist to enforce business invariants in domains with complex rules. A blog post system doesn't need them. An insurance claims processing system probably does.

---

## 5. Domain Events

### The Principle

A domain event represents something meaningful that happened in the domain. `OrderPlaced`, `PaymentReceived`, `ClaimDenied`, `PolicyRenewed`. These are business-meaningful occurrences, not infrastructure artifacts.

The key distinction: **`OrderPlaced` is a domain event. `RowInserted` is not.** `CustomerUpgraded` is a domain event. `CacheMissed` is not. Domain events are named in the ubiquitous language and would make sense to a domain expert.

### Architectural Roles

Domain events serve three purposes:

1. **Cross-aggregate consistency.** When `Order` is placed, `Inventory` needs to be decremented. These are separate aggregates. `Order` publishes `OrderPlaced`; an event handler updates `Inventory`. This is eventual consistency without coupling.
2. **Cross-context integration.** The Sales context publishes `OrderPlaced`; the Fulfillment context subscribes and creates a shipment. Each context reacts in its own terms, using its own model.
3. **Audit and history.** Domain events form a natural audit log that's meaningful to the business, not just "field X changed from A to B."

### Event Design

Good domain events:

- **Are past tense.** `OrderPlaced`, not `PlaceOrder` (that's a command).
- **Carry enough data to be useful.** The event should contain the information consumers need without requiring a callback to the source. But not the entire aggregate state — just the relevant facts.
- **Are immutable facts.** An event represents something that happened. It can't be retracted, only compensated for (`OrderPlaced` followed by `OrderCancelled`).
- **Are versioned.** Event schemas evolve. Use explicit versioning from day one.

### Event Storming

Event storming is a collaborative workshop technique for discovering domain events, commands, aggregates, and bounded contexts. It's the most effective DDD discovery technique because it's inclusive — domain experts participate directly.

The basic process:
1. **Put domain events on the wall.** Orange sticky notes. "What happened?" Past tense. No filtering — quantity over quality.
2. **Organize chronologically.** Create a timeline of what happens in the business process.
3. **Identify commands.** Blue sticky notes. "What triggered this event?" Commands are the actions users or systems take.
4. **Identify aggregates.** Yellow sticky notes. "What entity processed the command and produced the event?"
5. **Draw boundaries.** Where do the clusters naturally form? Those are your candidate bounded contexts.

Event storming in 2-3 hours will teach you more about the domain than weeks of reading requirements documents.

### Common Mistakes

- **Events as database triggers.** Domain events should be published by domain logic, not by database change-data-capture. CDC events are infrastructure; domain events carry business meaning.
- **Overloading events with commands.** `OrderPlaced` tells you what happened. It doesn't tell the fulfillment system what to do — the fulfillment system decides that based on its own rules. Events inform; commands instruct.
- **Ignoring event ordering.** Within a single aggregate, events have a natural order. Across aggregates, you likely cannot guarantee order. Design consumers to handle out-of-order delivery.

---

## 6. Strategic vs Tactical DDD

### The Split

DDD has two halves, and they're not equally valuable:

**Strategic DDD** — bounded contexts, context mapping, subdomain classification, ubiquitous language. This is always worth doing when you have a complex business domain. It doesn't require any specific code patterns. It's about understanding the problem space and drawing boundaries.

**Tactical DDD** — entities, value objects, aggregates, repositories, factories, domain services, specifications. This is a set of code-level patterns for implementing domain logic within a bounded context. It's optional. Use it when the domain is genuinely complex.

### The Mistake: Tactical Patterns for CRUD Domains

A team reads the Evans book, gets excited, and builds an `OrderAggregate` with an `OrderRepository` and an `OrderFactory` and `LineItemValueObject` for... a system that creates, reads, updates, and deletes orders with no complex business rules.

The result: mountains of boilerplate wrapping what could have been a simple ActiveRecord model. Every query requires navigating repository abstractions. Every field change requires going through the aggregate root. The code is harder to understand, not easier.

**Tactical DDD is for domains where the business rules are complex enough to justify the modeling overhead.** Insurance policy calculations. Trading system risk management. Healthcare claims adjudication. Not a task management app.

### Subdomain Classification

Not all parts of a business domain are equally important or complex. DDD classifies subdomains into three types, and this classification should drive your investment:

**Core Domain**: The thing that gives your business a competitive advantage. This is where you invest your best engineers, apply rigorous domain modeling, and potentially use tactical DDD patterns. A logistics company's route optimization. A trading firm's pricing engine. A healthcare company's claims processing rules.

- *Approach*: Custom-built. Best engineers. Deep domain modeling. This is where DDD tactical patterns may earn their keep.

**Supporting Domain**: Necessary for the business but not differentiating. Your logistics company needs a driver scheduling system, but it doesn't need to be world-class — it just needs to work correctly.

- *Approach*: Build it, but don't over-invest. Simpler architecture. Junior-to-mid-level engineers can own it. CRUD patterns are fine.

**Generic Domain**: Problems that have been solved by others. Authentication. Email sending. Payment processing. File storage.

- *Approach*: Buy it, use open source, or use a SaaS product. Do not build this. Building your own authentication system is almost never a competitive advantage (and is usually a liability).

### The Decision Framework

| Question | If Yes | If No |
|---|---|---|
| Are there complex business rules beyond CRUD? | Consider tactical DDD | Use simpler patterns |
| Do domain experts exist and are they accessible? | Strategic DDD is viable | Focus on data modeling |
| Is this a core domain? | Invest in deep modeling | Keep it simple |
| Will the model evolve significantly? | Tactical patterns help manage change | YAGNI |
| Is the team experienced with DDD? | Full DDD is feasible | Start with strategic only |

---

## 7. When DDD Is Wrong

DDD is not a universal architecture philosophy. It's a tool for a specific class of problems. Applying it to the wrong problem creates worse software, not better.

### Don't Use DDD When:

**The application is fundamentally CRUD.** If the system's job is to accept data, validate some fields, store it, and retrieve it — DDD adds ceremony without value. A content management system, a simple inventory tracker, a settings page. Use a straightforward data-centric architecture. Rails-style MVC. Simple service + repository. Don't fight it.

**The domain has no rich business rules.** DDD's value comes from encoding business rules in domain objects. If the business rules are "this field is required" and "this number must be positive," you don't need a domain model — you need input validation.

**Domain experts don't exist or aren't accessible.** DDD is a collaborative discipline. If you can't sit down with someone who deeply understands the business domain and iterate on the model together, you're guessing. And guessing at domain models produces worse results than not having a domain model.

**The team is too small.** Bounded contexts imply maintenance overhead — separate models, integration contracts, mapping code. A team of two maintaining four bounded contexts is going to spend more time on infrastructure than business logic. For small teams, a well-organized monolith with clear module boundaries is usually better.

**You're building a data pipeline or ETL system.** These systems are about transforming and moving data, not about modeling business behavior. Data engineering patterns (staging, transformation, loading, reconciliation) are more appropriate than domain patterns.

**The domain is well-understood and stable.** DDD's modeling rigor pays off when the domain is complex and evolving. If you're building the 500th e-commerce checkout and the business rules are standard, you don't need event storming to discover what "add to cart" means.

**Applied dogmatically.** "We must have aggregates because we're doing DDD" is the worst reason to have aggregates. Every DDD pattern has a cost. If you can't articulate the specific benefit it provides in your specific context, you shouldn't use it.

### The Honesty Test

Ask yourself: **"Is this domain complex enough that the cost of modeling will be repaid by the clarity of the model?"** If you hesitate, the answer is probably no. Start simple. You can always introduce DDD patterns later when the complexity demands them. You can rarely remove them once the team has committed.

---

## 8. Applying the Philosophy

### Running an Event Storming Session

**Prep (30 min before)**:
- Large wall or whiteboard. Unlimited sticky notes in 4 colors (orange=events, blue=commands, yellow=aggregates, pink=problems/questions).
- Invite domain experts, developers, product managers. 4-8 people. No laptops.
- Timebox to 2-3 hours.

**Phase 1 — Chaotic Exploration (30 min)**:
- Everyone writes domain events (orange stickies, past tense) and puts them on the wall. No discussion yet. Go for volume.
- "OrderPlaced", "PaymentFailed", "InventoryReserved", "ShipmentDispatched", "RefundIssued", "CustomerNotified".

**Phase 2 — Timeline (30 min)**:
- Arrange events chronologically. Left to right. What happens first?
- Gaps become obvious. "Wait, what happens between OrderPlaced and ShipmentDispatched?" Those gaps are where the interesting domain logic lives.

**Phase 3 — Commands and Actors (30 min)**:
- For each event, add the command (blue) that triggered it and the actor (person or system) who issued the command.
- "Customer places order" -> `PlaceOrder` command -> `OrderPlaced` event.

**Phase 4 — Aggregates and Boundaries (30 min)**:
- Group related events and commands around the aggregate (yellow) that handles them.
- Draw boundaries around clusters. These are your candidate bounded contexts.
- Mark pain points (pink stickies): "This is where things get confusing." Those are the interesting design problems.

**Phase 5 — Debrief (15 min)**:
- Name each cluster. These names often become your service or module names.
- Identify the core domain (where the most complex, business-critical logic lives).
- Capture open questions for follow-up.

### Identifying Bounded Contexts in Existing Code

When you inherit a codebase and suspect the boundaries are wrong:

1. **Grep for god objects.** Classes with 50+ methods, tables with 30+ columns. These are likely straddling context boundaries.
2. **Map the vocabulary.** List every important noun in the codebase. For each, ask: "Does this word mean the same thing everywhere it's used?" Where it doesn't, you've found a boundary.
3. **Trace the data flow.** Follow a single business operation from API to database. Count how many "translation" steps there are — DTOs to entities to models to view-models. Excessive translation within what should be one context suggests the model is fractured.
4. **Look at the coupling.** Which modules change together? If changing "Order" always requires changing "Customer" and "Inventory," those modules may be incorrectly separated — or correctly separated with too-tight coupling.
5. **Ask who owns what.** If two teams are both modifying the same files, you have either a missing context boundary (the file is doing two things) or an incorrect one (related things are in different places).

### Refactoring Toward Bounded Contexts Incrementally

You don't rewrite a monolith into bounded contexts overnight. The strangler fig approach:

**Step 1 — Identify one context to extract.** Choose the one with the clearest boundary and the most pain. A subsystem that changes frequently but whose changes always conflict with unrelated work is a good candidate.

**Step 2 — Define the contract.** Before moving any code, define the API between the context being extracted and the rest of the system. This is your anti-corruption layer. It might be a function interface, an event bus, or an HTTP API.

**Step 3 — Duplicate, don't delete.** Create the new context's model alongside the old one. Run both in parallel. The new context gets new functionality; the old code handles existing flows. Gradually migrate callers.

**Step 4 — Strangle the old code.** As consumers migrate to the new context's API, the old code paths get less traffic. When traffic hits zero, delete the old code.

**Step 5 — Repeat.** Each extraction makes the remaining monolith simpler and the next extraction easier.

### Key Principles for Migration

- **Don't extract everything at once.** Extract one bounded context, stabilize, then extract the next. Each extraction teaches you something about the domain that improves the next one.
- **Shared database is the enemy.** Two contexts sharing a database table is the most common form of hidden coupling. Splitting the database is often harder than splitting the code — plan for it explicitly.
- **Events are your migration tool.** Publish domain events from the old system. Build the new context as a subscriber. When the new context is ready, redirect consumers from the old API to the new one.
- **Accept temporary duplication.** During migration, you will have duplicate models, duplicate data, and duplicate logic. This is fine. It's temporary, and the alternative (big-bang rewrite) is worse.

---

## Quick Reference: DDD Decision Checklist

| Situation | Recommendation |
|---|---|
| Complex domain with rich business rules | Strategic + tactical DDD |
| Complex domain, team new to DDD | Strategic DDD only (bounded contexts, ubiquitous language) |
| Multiple teams working on one system | Bounded contexts aligned to team boundaries |
| Integrating with legacy systems | Anti-corruption layer |
| Simple CRUD application | Skip DDD entirely |
| Unsure if domain is complex enough | Start without DDD, introduce it when pain appears |
| Domain experts available and engaged | Event storming -> bounded contexts -> iterative modeling |
| Domain experts unavailable | Data modeling + clean architecture. Revisit DDD when experts appear. |

---

## Further Reading

- **Eric Evans, _Domain-Driven Design_ (2003)**: The original. Dense but essential. Focus on Parts I-III (strategic patterns). Part IV (tactical) is optional for most teams.
- **Vaughn Vernon, _Implementing Domain-Driven Design_ (2013)**: More practical and code-oriented than Evans. Better starting point for developers.
- **Alberto Brandolini, _Introducing EventStorming_ (2021)**: The definitive guide to event storming as a discovery technique.
- **Nick Tune, _Architecture Modernization_ (2024)**: Applies DDD thinking to brownfield modernization — extracting bounded contexts from existing systems.
