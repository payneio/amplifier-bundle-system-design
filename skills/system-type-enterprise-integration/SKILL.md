---
name: system-type-enterprise-integration
description: "Domain patterns for enterprise integration — legacy modernization, strangler fig, anti-corruption layers, API gateways, canonical data models, event-carried state transfer, and failure modes. Use when designing or evaluating integration between existing enterprise systems, legacy modernization, or multi-system orchestration."
---

# System Type: Enterprise Integration

Patterns, failure modes, and anti-patterns for connecting, modernizing, and orchestrating enterprise systems.

---

## 1. Integration Patterns

Enterprise integration is the art of making systems talk to each other when they were never designed to. Every pattern trades coupling for something — throughput, consistency, simplicity, or debuggability. The right choice depends on what you can afford to lose.

### The Topology Spectrum

| Topology | Description | Coupling | Failure domain | Debuggability | When it works |
|---|---|---|---|---|---|
| **Point-to-point** | Direct connections between each pair of systems. N systems → N×(N-1)/2 connections. | Tightest — every system knows every other system's interface | Localized but unpredictable — one system's outage cascades differently depending on who depends on it | Easy when there are 3 systems, impossible at 15 | Small number of integrations (<5 systems), throwaway prototypes, or when two systems genuinely have a 1:1 relationship that won't grow |
| **Hub-and-spoke (ESB)** | Central bus mediates all communication. Systems only know the bus. | Moderate — systems decouple from each other but couple to the bus | Centralized — the bus is a SPOF for everything | Good — the bus logs everything (in theory) | When you need protocol translation, message transformation, and routing in one place. When governance requires a central integration team. When the number of systems is moderate (10–30) and the integration team has the capacity. |
| **Event mesh / event backbone** | Distributed event infrastructure (Kafka, Pulsar, etc.). Systems publish and subscribe to topics. No central broker logic. | Loosest — producers don't know consumers exist | Distributed — broker failure is partial, consumer failure is isolated | Harder — requires distributed tracing, topic monitoring, consumer lag tracking | When you have many (30+) systems, event-driven architectures, and teams that can own their own consumers. When you need to replay events for recovery or new consumers. |

### Synchronous vs Asynchronous

**Synchronous (request/reply).** System A calls System B and waits for a response. The caller's latency includes the callee's latency. The caller's availability depends on the callee's availability.

When it's right:
- The caller genuinely cannot proceed without the response (validate payment before confirming order).
- Latency requirements are well understood and the callee can meet them.
- The dependency graph is shallow (A calls B, not A calls B calls C calls D).

When it creates coupling nightmares:
- Deep call chains. If A→B→C→D, A's p99 latency is the sum of B, C, and D's p99 latencies, and A's availability is the product of their availabilities.
- Retry storms. If B is slow, A retries. B is slow because C is slow. Now A and B are both retrying against C, making C slower. This is a distributed system death spiral.
- Temporal coupling. Both systems must be running simultaneously. Maintenance windows become a coordination problem across every system in the chain.

**Asynchronous (fire-and-forget / event-driven).** System A publishes a message or event and moves on. System B processes it whenever it can.

When it's right:
- The caller doesn't need an immediate response (order placed → fulfillment can happen later).
- You need to absorb load spikes (queue buffers the burst).
- You want temporal decoupling (System B can be down for maintenance without affecting System A).
- Multiple consumers need to react to the same event.

When it creates coupling nightmares:
- When you need the illusion of synchronous behavior built on async primitives. If the user is staring at a spinner waiting for 6 async hops to complete, you've built a slow synchronous system with worse debuggability.
- When ordering matters and you haven't designed for it. Messages arrive out of order. Events get replayed. Idempotency isn't optional — it's a survival requirement.
- When error handling is an afterthought. A failed async message goes to a dead letter queue. Who monitors it? Who retries it? Who tells the user their order silently failed 3 hours ago?

### Messaging Patterns

**Request/reply.** Caller sends a request message with a correlation ID and reply-to address. Callee sends a response to the reply address with the same correlation ID. This is synchronous semantics over asynchronous transport. Use when you need the decoupling benefits of async but the conversation semantics of sync. Be aware that reply correlation adds complexity — lost replies, timeout management, and orphaned requests all need handling.

**Fire-and-forget.** Caller sends a message and does not expect a response. The simplest async pattern. Use for notifications, audit logging, analytics events, or any action where the caller doesn't care about the outcome. The risk: "fire-and-forget" often becomes "fire-and-pray" when the message is actually important but nobody built monitoring for delivery failures.

**Publish/subscribe.** Publisher emits events to a topic. Zero or more subscribers receive them independently. This is the foundational decoupling pattern in enterprise integration. Each subscriber can process events at its own pace, in its own way, without the publisher knowing or caring. The risk: invisible coupling. Adding a new subscriber is easy. Understanding the full impact of changing an event schema when you have 14 subscribers across 6 teams is hard.

---

## 2. Legacy Modernization

Every legacy system is load-bearing. It exists because it does something the business needs, and it has survived because replacing it is harder than maintaining it. Respect this. The codebase is ugly because it has 15 years of business rules encoded in it, not because the original developers were incompetent.

### Strangler Fig Pattern

The single most important pattern in legacy modernization. Named after the strangler fig vine that grows around a tree, eventually replacing it.

**How it works:**
1. Put a facade (proxy, gateway, load balancer) in front of the legacy system.
2. For each new feature or migration target, build the new implementation behind the facade.
3. Route traffic for that feature to the new implementation.
4. Repeat until no traffic goes to the legacy system.
5. Decommission the legacy system.

**Why it works:** You never have a big-bang cutover. Each migration step is small, reversible, and independently valuable. The legacy system continues running for everything you haven't migrated yet.

**What goes wrong:**
- **The facade becomes permanent.** You route 80% of traffic to the new system and 20% stays on legacy forever because those last features are the hardest to migrate and nobody wants to touch them. The "temporary" facade is now permanent infrastructure that you maintain for years.
- **Data synchronization.** If both old and new systems write to different data stores, you need to keep them in sync during the migration. Dual-write is fragile. Change data capture (CDC) is better but adds infrastructure. Every data sync mechanism is a source of bugs during migration.
- **Feature development on both systems.** Business doesn't stop during migration. New features get added to the legacy system because "the migration isn't ready for that module yet." Now you're maintaining two systems and the migration target keeps moving.
- **Loss of organizational will.** Strangler fig migrations take months to years. Leadership changes. Priorities shift. The migration stalls at 60% complete and you're running two systems indefinitely. The strangler fig only works if someone with authority defends the migration budget quarter after quarter.

**Practical guidance:** Start with the highest-traffic, lowest-complexity endpoints. These give you the fastest return on investment and build organizational confidence. Leave the gnarliest, most business-logic-heavy modules for last — by then you'll understand the domain better and have a proven migration playbook.

### Anti-Corruption Layer (ACL)

**What it is.** A translation layer between your new code and a legacy system's data model. The ACL speaks the legacy system's language on one side and your clean domain model on the other.

**Why it exists.** Legacy systems have legacy models — field names that made sense in 1997, overloaded columns that mean different things depending on a status flag, business rules encoded as stored procedures. If your new code adopts the legacy model, you've imported 20 years of technical debt into your clean architecture. The ACL prevents contamination.

**Where to place it:**
- At the boundary of your new service, wrapping calls to the legacy system.
- In a dedicated adapter service if multiple new services need to talk to the same legacy system.
- NOT in the legacy system itself. You don't modify the legacy system. You insulate from it.

**What it translates:**
- Data model mapping (legacy `CUST_REC.ACCT_TYP_CD` → new `Customer.accountType`).
- Protocol translation (legacy SOAP/XML → new REST/JSON or gRPC/protobuf).
- Semantic translation (legacy uses `status = 7` to mean "active with restrictions" → new model has explicit `isActive` and `restrictions[]`).
- Error translation (legacy returns `RC=-412` → new model returns structured error with code, message, and recovery action).

**The discipline:** The ACL must be a team responsibility, not an afterthought. Someone owns the mapping. When the legacy system changes (and it will — even "frozen" legacy systems get emergency patches), the ACL must be updated. Put integration tests at this boundary. They'll save you at 2am.

### Branch by Abstraction

**What it is.** Introduce an abstraction (interface, adapter, feature flag) in the existing codebase that lets you swap between old and new implementations without forking the codebase.

**How it works:**
1. Identify the seam where old implementation meets the rest of the code.
2. Insert an abstraction layer at that seam (interface, strategy pattern, feature flag).
3. Old implementation now lives behind the abstraction.
4. Build new implementation behind the same abstraction.
5. Toggle between implementations using configuration or feature flags.
6. When new implementation is proven, remove the abstraction and the old code.

**When to use instead of strangler fig:** When the thing you're replacing is a library, module, or internal component rather than an externally-facing service. Strangler fig works at the HTTP/network boundary. Branch by abstraction works at the code boundary.

### Database Decomposition

The hardest part of legacy modernization is the database. Legacy systems almost always have a single shared database that everything reads from and writes to. Decomposing it is surgery on a beating heart.

**Strategies, in order of increasing risk:**

1. **Read replica with new schema.** Create a read replica, build a new schema on top of it with views or materialized views. New services read from the new schema. Writes still go to the legacy database. Low risk, but you're still coupled to the legacy schema and you can't write through the new model.

2. **Change data capture (CDC).** Use CDC (Debezium, AWS DMS, or database-native replication) to stream changes from the legacy database into a new data store. New services own their own data store and get updates via the CDC stream. Medium risk — CDC introduces latency (seconds to minutes) and you must handle the eventually-consistent window.

3. **Dual-write with reconciliation.** New service writes to both old and new databases. Reconciliation job detects and fixes drift. High risk — dual-write without distributed transactions means you WILL have inconsistencies. Only use this as a transitional strategy with tight monitoring and automated reconciliation.

4. **Cut over by domain.** Migrate one bounded context at a time. Move all reads and writes for that context to the new database. Update the legacy system to call the new service for that context's data instead of querying the shared database directly. Highest effort but cleanest result. This is the end state you're working toward.

**The shared database trap:** The legacy database is the single largest source of coupling in most enterprises. Every system that queries it directly is coupled to every other system that writes to it. Schema changes break unknown consumers. Performance problems in one system's queries affect every system on the same instance. Decomposing the shared database is the most important and most difficult step in any legacy modernization. Plan for it to take longer than everything else combined.

### The Big Bang Rewrite

**Almost never appropriate.** The failure rate of big bang rewrites is staggering. Netscape. Borland. Countless internal projects that were cancelled 18 months in with nothing to show.

**Why it fails:**
- The old system has 10 years of implicit requirements encoded in bug fixes, edge cases, and undocumented behaviors. The rewrite team discovers these one at a time, in production.
- The business cannot wait 18 months for the rewrite. Feature development on the old system continues, and the rewrite target keeps moving.
- The team underestimates the scope by 3-10x because the old system looks simple from the outside. The complexity is in the interactions, not the code.

**The rare cases where it's appropriate:**
- The old system is so small that a rewrite is weeks, not months.
- The old system's technology is truly unsupportable (no one on the market knows the language, the vendor is bankrupt, the hardware is end-of-life).
- The domain is well-understood and the requirements can be fully specified up front (this is rarer than people think).
- You can run old and new in parallel for an extended comparison period before cutting over.

Even in these cases, prefer a strangler fig approach. The risk of big bang is not technical — it's organizational. Projects that take 18 months and show no incremental value get cancelled.

---

## 3. API Gateway Patterns

The API gateway is the front door of your integration architecture. Done right, it's an enabling layer that simplifies every team's work. Done wrong, it's a coupling bottleneck that every team hates and no one can change.

### Gateway as Integration Fabric

The gateway isn't just a reverse proxy. In enterprise integration, it's where worlds collide — mobile clients hitting SOAP backends, partner APIs needing authentication you don't control, internal services speaking gRPC while external consumers expect REST.

**Core gateway capabilities for enterprise integration:**

| Capability | What it does | Why it matters for integration |
|---|---|---|
| **Protocol translation** | SOAP↔REST, REST↔gRPC, XML↔JSON | Legacy systems speak SOAP. New services speak gRPC. Clients expect REST/JSON. The gateway translates so no one has to. |
| **Authentication aggregation** | Validates tokens from multiple identity providers, normalizes claims | The legacy system uses SAML. The new system uses OAuth2. Partners use API keys. The gateway normalizes all of them into a single internal auth context. |
| **Rate limiting** | Per-client, per-tenant, per-endpoint throttling | Prevents a misbehaving integration partner from overwhelming a backend that has no rate limiting of its own (which is every legacy system). |
| **Response composition** | Aggregates responses from multiple backends into a single response | The client needs data from 3 backends. Instead of 3 round trips, the gateway composes. But this is where complexity lives — see caveats below. |
| **Schema validation** | Validates request/response payloads against schemas | Catches malformed requests before they hit backends that return cryptic errors. |
| **Circuit breaking** | Stops sending traffic to failing backends | The legacy system is down. Without circuit breaking, every request queues behind it, exhausting gateway connections. |

### Protocol Translation

Protocol translation is the gateway's highest-value integration capability and its biggest maintenance burden.

**SOAP to REST.** The most common enterprise translation. SOAP services have WSDLs that define operations, types, and bindings. Map SOAP operations to REST resources and verbs. Map SOAP faults to HTTP status codes. Decide how to handle SOAP headers (WS-Security, WS-Addressing) — most can be dropped if the gateway handles auth, but some carry business semantics (correlation IDs, routing hints) that must be preserved.

The trap: auto-generating REST APIs from WSDLs produces APIs that are "REST" in name only — RPC-style operations mapped to POST endpoints with no resource modeling. If you're building an API that external consumers will use, invest in designing a real REST API and manually mapping it to the SOAP backend.

**REST to gRPC.** Use gRPC-JSON transcoding (built into Envoy, available as gRPC-gateway in Go). Define your gRPC service with HTTP annotations and let the transcoding layer handle conversion. This works well for new services that want gRPC internally but must expose REST externally. Watch for streaming — gRPC server streaming doesn't map cleanly to REST without SSE or WebSockets.

**The ongoing cost:** Protocol translation means maintaining two interface definitions. The SOAP WSDL changes, you update the gateway mapping. The gRPC proto changes, you regenerate the transcoding config. Every translation layer is a surface area for bugs. Automate the generation of translation configs from source schemas wherever possible.

### Backend for Frontend (BFF)

**What it is.** A dedicated backend service for each frontend type (web, mobile, partner API). Each BFF aggregates, transforms, and optimizes responses for its specific consumer.

**When to use in enterprise integration:**
- Different consumers need radically different views of the same data. The mobile app needs a compressed summary. The partner API needs the full record in a specific XML format. The internal dashboard needs real-time aggregations.
- You want to decouple frontend release cycles from backend service changes. The BFF absorbs backend changes and presents a stable interface to its consumer.
- You have multiple teams building multiple frontends and you want each team to own its API contract.

**When to avoid:**
- You have one or two consumers with similar needs. A single gateway layer with minor per-consumer logic is simpler.
- The BFF teams don't have backend engineering skills. A BFF is a backend service — it needs monitoring, error handling, deployment pipelines, on-call.

### The Gateway as a Coupling Point

The gateway is a SPOF by design. All traffic flows through it. This creates risks:

- **Organizational coupling.** If one team owns the gateway, every integration change requires that team's involvement. The gateway team becomes a bottleneck. Mitigate with self-service configuration: each team pushes their own routing rules, rate limits, and translations through a GitOps pipeline. The gateway team owns the platform, not every route definition.
- **Performance coupling.** The gateway adds latency to every request. If the gateway does heavy transformation (XML parsing, response composition from 3 backends), it can become the performance bottleneck. Keep translation lightweight. Move heavy composition to BFF services or dedicated aggregation services behind the gateway.
- **Blast radius.** A bad configuration change to the gateway takes down everything. Use canary deployments for gateway config changes. Test in staging. Have an instant rollback mechanism. Treat gateway changes with the same rigor as database schema changes.
- **Logic creep.** The gateway starts as routing + auth. Then someone adds a business rule. Then another. Now the gateway has business logic that should be in services, and it's deployed as a monolith that's terrifying to change. The rule: the gateway does transport-level concerns (routing, auth, rate limiting, protocol translation). Business logic goes in services. Enforce this boundary ruthlessly.

---

## 4. Data Integration

Data integration is where enterprise integration projects go to die. Systems agree on APIs relatively easily. Getting them to agree on what data means, who owns it, and how to keep it consistent is where the political and technical challenges converge.

### Canonical Data Model

**What it is.** A shared vocabulary and data model that all systems agree to use for exchanging data. Instead of N×(N-1) point-to-point translations, each system translates between its internal model and the canonical model.

**The appeal:** Reduces translation complexity from O(N²) to O(N). Provides a common language for cross-team communication.

**The reality:** Building consensus on a canonical model is a political exercise disguised as a technical one. Every team believes their model is the right one. The canonical model committee produces either a lowest-common-denominator model that loses important domain nuance, or an everything-and-the-kitchen-sink model that no system fully implements.

**When it works:**
- The domain is well-understood and stable (financial transactions, healthcare records with HL7/FHIR).
- There's a strong central architecture team with organizational authority to enforce adoption.
- The canonical model is versioned and evolved deliberately, not frozen.

**When it fails:**
- When "canonical" means "the ERP vendor's data model." That's not canonical — that's vendor coupling dressed up as architecture.
- When the model is defined once and never updated. The business evolves. The model doesn't. Teams work around it with extension fields, out-of-band data, and side channels.
- When no one enforces compliance. A canonical model that 3 of 12 systems actually implement is worse than no canonical model — it's a false promise of interoperability.

**Practical guidance:** If you can't get organizational buy-in for a full canonical model (you probably can't), focus on canonical models for specific integration contexts — a shared order model for the order processing domain, a shared customer model for customer-facing systems. Domain-scoped canonical models are achievable. Enterprise-wide canonical models are a career hazard.

### Event-Carried State Transfer

**What it is.** Instead of querying a source system for data, each consuming system maintains its own local copy of the data it needs, updated by events from the source. When System A updates a customer record, it publishes a `CustomerUpdated` event containing the full (or relevant subset of) customer data. Systems B, C, and D consume the event and update their local copies.

**Why it matters for enterprise integration:**
- **Eliminates runtime coupling.** System B can serve customer data even when System A is down, because it has its own copy.
- **Eliminates query coupling.** System B doesn't need to understand System A's query interface, pagination, or rate limits.
- **Performance.** Local reads are always faster than network calls.

**The costs:**
- **Eventual consistency.** System B's copy of the customer may be seconds or minutes behind System A's authoritative record. The business must be able to tolerate this staleness window.
- **Storage duplication.** Every consumer stores its own copy. For small datasets, this is trivial. For large datasets, it's significant infrastructure.
- **Schema evolution.** When the event schema changes, every consumer must be updated. This is the same problem as the canonical model — amplified by the number of consumers.
- **Debugging.** "Why does System B show the wrong address for this customer?" Because the event was published 3 minutes ago and System B hasn't processed it yet. Or because System B's event consumer crashed and there's a 10,000-event backlog. Or because the event schema changed and System B is silently dropping fields it doesn't recognize.

### Change Data Capture (CDC)

**What it is.** Capture changes from a database's transaction log (WAL, binlog, redo log) and publish them as events. Unlike application-level events (which require the application to remember to publish), CDC captures every change regardless of which code path wrote it — application code, stored procedures, manual SQL, ETL jobs.

**Key tools:** Debezium (open source, Kafka-based), AWS DMS, Oracle GoldenGate, Striim.

**When it's essential for enterprise integration:**
- The source system cannot be modified to publish events (legacy system, vendor software, regulated system).
- Multiple code paths write to the same database and you can't guarantee they all publish events.
- You need to capture the full change history, including changes made by stored procedures, triggers, or batch jobs.

**The costs:**
- CDC operates at the database level, not the domain level. You get `row inserted in CUSTOMER table` not `customer signed up for premium plan`. Consumers must infer domain semantics from database operations. This is an impedance mismatch that gets worse as the schema becomes more normalized.
- CDC is sensitive to schema changes. Adding a column is usually fine. Renaming a column, changing a type, or splitting a table can break the CDC pipeline and every downstream consumer.
- Transaction log retention. The database must retain its transaction log long enough for CDC to read it. If the CDC consumer falls behind (outage, slow processing), the database may purge the log entries it hasn't read. This requires monitoring and alerting on CDC consumer lag.

### The Shared Database Anti-Pattern (and How to Migrate Away)

**The anti-pattern:** Multiple applications read from and write to the same database, using the database as their integration mechanism. No APIs, no events — just shared tables.

**Why it's so common:** It's the easiest possible integration. No API to design, no messaging infrastructure to run, no serialization to worry about. SQL is a universal query language. The database handles transactions and consistency. It works brilliantly until it doesn't.

**Why it's toxic at scale:**
- **Schema coupling.** Every application is coupled to the physical schema. Renaming a column requires coordinated changes across every application — many of which are owned by different teams, on different release cycles, and some of which are vendor software you can't change at all.
- **Performance coupling.** Application A's slow report query locks tables that Application B needs for real-time transaction processing. A missing index in Application A's code path causes timeouts in Application B.
- **No encapsulation.** Every application can read and write any data. There are no domain boundaries, no validation at the integration layer, no access control beyond database grants (which are typically too coarse). Business rules are duplicated across applications — and they diverge.
- **Change paralysis.** Nobody wants to touch the shared schema because nobody knows the full impact. The DBA becomes the bottleneck for every change. "We'll just add a new table" becomes the default, and the schema accumulates cruft for decades.

**Migration path:**

1. **Inventory.** Catalog every application that reads from or writes to the shared database. Identify which tables each application uses and whether it reads, writes, or both. This is harder than it sounds — don't forget stored procedures, views, triggers, ETL jobs, and reporting tools.
2. **Identify domain boundaries.** Cluster tables into bounded contexts. Customer tables, order tables, inventory tables — which application should own each cluster?
3. **Build APIs over owned data.** For each bounded context, the owning application exposes APIs for the data it owns. Other applications migrate from direct database queries to API calls. This is the hardest step and takes the longest.
4. **Introduce CDC for read-heavy consumers.** Applications that do heavy reporting or analytics on data they don't own should get a CDC feed into their own read-optimized store rather than querying the shared database.
5. **Restrict database access.** As consumers migrate to APIs and CDC, revoke their direct database access. The database credentials are the coupling mechanism — removing them is how you enforce the boundary.
6. **Decompose the database.** Once each bounded context is accessed only through its owning application, you can physically separate the data into distinct databases.

This migration takes years in large enterprises. That's normal. The key is to make progress monotonically — each step reduces coupling, and no step makes things worse.

### Data Mesh Concepts

**Domain-owned data products.** Instead of a central data team owning all data, each domain team owns its data as a product — with an SLA, a schema contract, documentation, and discoverability. Integration consumers treat data products like they treat APIs: call the product, get the data, trust the contract.

**What this means for enterprise integration:**
- The "integration team" doesn't own the data or the transformations. Domain teams own the data, expose it as products, and are accountable for quality.
- Central infrastructure provides the platform (catalog, access control, monitoring), not the data itself.
- Integration becomes API-like: discover the product, understand the contract, build your consumer. The organizational model shifts from centralized ETL to federated data ownership.

**The prerequisite:** Domain teams must be mature enough to own their data products. This requires investment in data engineering skills across teams, not just in a central data team. Many organizations aren't ready for this, and forcing it creates data products that nobody maintains.

---

## 5. Message Translation and Routing

Enterprise integration means connecting systems that were never designed to understand each other. Message translation and routing is where you bridge the impedance mismatch between different domain models, protocols, and data formats.

### Message Transformation

**What it is.** Converting a message from one format/schema to another. This is the daily bread of enterprise integration.

**Levels of transformation:**

- **Structural.** Changing the shape of the data — XML to JSON, flat record to nested object, one schema to another. Mechanical and automatable.
- **Semantic.** Changing the meaning — mapping `status = "A"` to `status = "active"`, converting currencies, translating between code systems (ICD-10 to SNOMED). Requires domain knowledge and is where bugs live.
- **Enrichment.** Adding data from external sources — receiving an order with a customer ID, looking up the customer's address from a customer service, and attaching it to the message before forwarding. Introduces a runtime dependency on the enrichment source.
- **Filtering.** Removing data that the consumer doesn't need or isn't authorized to see. PII stripping, field projection, redaction.

**Where to do it:**
- In the producer: Producer emits the canonical model or consumer-specific format. Couples the producer to its consumers.
- In the consumer: Consumer accepts the producer's format and translates internally. Couples the consumer to the producer's model.
- In a mediator: A dedicated transformation service or integration layer does the translation. Adds infrastructure but isolates both sides. This is the ESB model's core value proposition, and it's the right choice when you have many-to-many integrations with different schemas.

### Content-Based Routing

**What it is.** Inspecting the content of a message to decide where to route it. An order message with `country = "DE"` goes to the EU fulfillment system. An order with `country = "US"` goes to the US fulfillment system.

**When to use:** When the routing decision depends on business data inside the message, not just metadata (topic, header, source system).

**The risk:** The routing logic becomes a hidden business rule. When routing rules are embedded in integration middleware, developers and product managers don't know they exist. Document routing rules as first-class business logic. Version them. Test them. Review them when business rules change.

### Scatter-Gather

**What it is.** Send a request to multiple systems in parallel, collect all responses, and aggregate them into a single response.

**Example:** A price comparison that queries 5 supplier systems simultaneously and returns the best offer.

**Key decisions:**
- **Timeout strategy.** Do you wait for all responses or return after a timeout with whatever you have? Most implementations should use a timeout — one slow supplier shouldn't block the entire response.
- **Partial failure.** If 3 of 5 suppliers respond, is that a success or a failure? Define this up front. Most implementations treat partial results as success with degraded quality.
- **Result aggregation.** How do you combine the responses? Best price? Merge and deduplicate? Union? The aggregation logic is domain-specific and often more complex than the scatter or gather.

### Message Enrichment

**What it is.** Augmenting a message with additional data from external sources before delivering it to the consumer.

**Example:** An order event arrives with `customerId: 12345`. The enricher looks up the customer's shipping address, credit tier, and communication preferences, and attaches them to the order event before forwarding it to the fulfillment system.

**The tradeoff:** Enrichment creates a runtime dependency on the enrichment source. If the customer service is down, enrichment fails, and either the message is delayed (queued for retry) or delivered incomplete. Decide up front which enrichments are required (block until available) and which are optional (deliver without them and let the consumer handle the gap).

### Schema Mapping and Impedance Mismatch

Every pair of systems has a different mental model of the same business entities. The customer system has a `Customer` with addresses, preferences, and communication history. The billing system has an `Account` with payment methods, invoices, and credit terms. They're talking about the same person, but their models serve different purposes.

**Mapping strategies:**
- **Field-level mapping.** Direct mapping between fields. `Customer.email` → `Account.contactEmail`. Works for simple cases, breaks when the cardinality differs (Customer has multiple emails, Account expects one).
- **Structural mapping.** Reshaping data — flattening nested structures, combining fields, splitting records. This is where most mapping complexity lives.
- **Lossy mapping.** Accepting that some data cannot be mapped and will be lost in translation. This is often the right answer — the billing system doesn't need the customer's communication history. Document what's lost so future debuggers don't spend hours looking for data that was intentionally dropped.
- **Versioned mappings.** As schemas evolve on either side, the mapping must evolve too. Treat mappings as versioned artifacts with their own tests and release process.

---

## 6. Organizational Patterns

The architecture of your integration reflects the structure of your organization. This is not a suggestion — it's a law of nature (Conway's law). If you want to change the architecture, you must change the organization, or the organization will route around your architecture.

### Conway's Law as a Design Constraint

**Conway's law, restated for integration:** The interfaces between your systems will mirror the communication structures between the teams that build them. If two teams don't talk to each other, their systems won't integrate well. If a team owns three systems, those systems will be tightly coupled. If an integration is owned by "everyone" (no specific team), it will be owned by no one and will rot.

**Using Conway's law offensively:**
- If you want loosely coupled systems, give each system to a team with clear boundaries and well-defined interfaces to other teams.
- If you want a clean integration layer, create a dedicated integration team — but understand that this team will become a bottleneck unless they build self-service platforms rather than hand-coding integrations.
- If two systems need to be tightly integrated, consider whether the teams should be merged or at least co-located (physically or in communication channels).

**The anti-pattern:** Designing a beautiful decoupled architecture on a whiteboard and then assigning it to an organization that doesn't match. The org structure will win. Always.

### Team Topologies for Integration

Borrowed from the Team Topologies framework (Skelton & Pais), applied to enterprise integration:

**Stream-aligned teams.** Own a business capability end-to-end, including its integrations. The order processing team owns the order service, its API, its event publications, and its integrations with payment and fulfillment. This is the ideal for integration ownership because the team that understands the domain owns the integration logic.

**Platform teams.** Provide the shared integration infrastructure — the message broker, the API gateway, the CDC platform, the schema registry, monitoring and alerting. They don't own integrations; they own the tools that make integrations possible. A well-functioning platform team reduces the cognitive load on stream-aligned teams by providing self-service capabilities.

**Enabling teams.** Help stream-aligned teams adopt integration patterns and tools. A team of integration specialists that pairs with product teams during complex integration projects, teaches patterns, and then moves on. This is how you spread integration expertise without centralizing integration ownership.

**Complicated subsystem teams.** Own specific technically complex integration components — a high-performance message transformation engine, a complex protocol adapter for a legacy mainframe, a real-time data synchronization system. These exist when the technical complexity is too high for a stream-aligned team to handle alongside their domain work.

### API Contracts as Team Contracts

An API between two systems is a contract between two teams. Technical API design (REST, gRPC, event schema) is the easy part. The hard part is the social contract:

- **Who can change the API?** The producer team? Only with consumer approval? Through a review process?
- **What's the deprecation policy?** How much notice do consumers get before a breaking change? Who decides what's breaking?
- **What's the SLA?** Availability, latency, throughput — these aren't just technical specs. They're commitments from one team to another. If the order service promises 99.9% availability to the fulfillment service, that's a commitment that affects on-call staffing, infrastructure investment, and deployment practices.
- **Who debugs integration failures?** When data doesn't flow correctly, whose problem is it? Define this before the first production incident, not during it.

**Practical guidance:** Write integration contracts as documents that both teams sign off on. Not legal documents — living documents in a shared wiki or repository. Include: endpoint/topic definitions, schema versions, SLAs, breaking change policy, escalation contacts, and a decision log of why things are the way they are. The decision log is the most valuable part — six months later, nobody will remember why the order event uses a string for quantity instead of an integer.

### The Integration Team Paradox

Every enterprise eventually creates a "central integration team." This team owns the ESB, the API gateway, the iPaaS platform, or whatever the current integration middleware is. The paradox:

- **If the integration team owns integrations:** They become a bottleneck. Every team that needs an integration files a ticket and waits. The integration team is perpetually understaffed because they scale linearly with the number of integrations. They don't understand the domain context of what they're integrating and make mapping errors. Product teams route around them with direct database connections and ad-hoc file transfers.

- **If the integration team owns the platform:** They build self-service tools that product teams use to build their own integrations. This scales better but requires a higher up-front investment and a cultural shift — product teams must accept responsibility for integration code. The integration team's job becomes platform engineering, documentation, and enablement, not building integrations.

The second model is correct. It's also harder to sell to management because "we're building a platform" sounds less concrete than "we're building the integration." Staff engineers in this space must be prepared to make this argument repeatedly.

---

## 7. Migration Strategies

Every migration strategy is a bet about risk tolerance. The spectrum runs from "safe but slow" to "fast but terrifying."

### Parallel Run

**What it is.** Run both old and new systems simultaneously, processing the same inputs. Compare outputs. When outputs match consistently, cut over to the new system.

**When to use:** High-risk migrations where correctness matters more than speed. Financial calculations, regulatory reporting, billing systems — anything where getting the wrong answer has legal or financial consequences.

**How to implement:**
1. Route all inputs to both systems (fan-out at the entry point or replay from a message queue).
2. Capture outputs from both systems without delivering both to downstream consumers (the old system's output is authoritative; the new system's output is shadowed).
3. Compare outputs. Log differences with full context (input, old output, new output, timestamp).
4. Investigate every difference. Some are bugs in the new system. Some reveal bugs in the old system that nobody knew about. Some are timing differences (new system is faster, data was slightly different at query time).
5. When the comparison shows acceptable parity (define "acceptable" before starting — zero differences? <0.01%? <0.1% and all within rounding tolerance?), cut over.

**The cost:** You're running two systems at full cost. The comparison infrastructure is itself a significant engineering effort. Investigating differences is tedious, domain-specific work that requires people who understand the business logic, not just the code. Budget 2-3x the time you think you need for the comparison phase.

### Canary Migration

**What it is.** Route a small percentage of traffic to the new system while the majority continues to go to the old system. Gradually increase the percentage as confidence grows.

**When to use:** High-traffic systems where you want production validation but can tolerate a small percentage of users experiencing issues. Web services, API endpoints, stateless processing.

**Key decisions:**
- **How to split traffic.** By percentage (random), by customer segment (internal users first, then small customers, then large customers), by geography, by feature flag. Customer-segment routing is usually better than random because it lets you control blast radius and get feedback from known users.
- **What to monitor.** Error rates, latency percentiles (p50, p95, p99), business metrics (conversion rate, order completion rate). The canary should fail if ANY metric degrades beyond threshold, not just if errors increase.
- **Rollback trigger.** Automatic rollback on metric degradation, or manual with an on-call engineer watching dashboards? Automatic is safer. Define the rollback criteria before the canary starts.
- **Stickiness.** Once a user is routed to the new system, do they stay there? For stateless requests, it doesn't matter. For stateful flows (multi-step checkout, session-based operations), users must be sticky to one system or both systems must share state.

### Feature Flags for Migration Routing

**What it is.** Use feature flags to control which system handles each capability. Flag on: new system. Flag off: old system. Each flag controls a specific piece of functionality, not all-or-nothing traffic routing.

**Why this is better than traffic percentage for enterprise migration:**
- You migrate by capability, not by user percentage. "Order creation" moves to the new system while "order search" stays on the old system. This matches how strangler fig works at the routing level.
- You can target flags by environment (staging → production), by tenant (internal → beta → GA), and by capability independently.
- Rollback is instant — flip the flag.

**The discipline:**
- Feature flags for migration must have expiration dates. A flag that exists for 2 years is not a migration tool — it's permanent conditional complexity in your codebase.
- Track flag state in a central system, not in application config files scattered across repos.
- Every flag needs an owner and a retirement plan. After migration, remove the flag AND the old code path. If you don't remove old code paths, you're accumulating dead code that still gets tested, reviewed, and worried about.

### Data Synchronization During Migration

The most technically challenging aspect of any migration. During migration, data exists in both old and new systems and must be consistent (or at least convergently consistent).

**Approaches:**

| Approach | How it works | Risk | When to use |
|---|---|---|---|
| **Write to old, replicate to new** | Old system is authoritative. CDC or ETL replicates to new system. New system is read-only or secondary. | Low — one source of truth | Early migration phases. New system is being validated. |
| **Dual-write** | Application writes to both systems on every write operation. | High — no transactional guarantee across two systems. Failures create drift. | Short transitional periods only. Never as a permanent architecture. |
| **Write to new, backfill old** | New system is authoritative. Changes are replicated back to old system for consumers that haven't migrated. | Medium — reverse replication must preserve old system's constraints and triggers. | Late migration phases. Most consumers have moved to new system. |
| **Event-sourced migration** | All writes go through an event log. Both old and new systems consume from the log. | Medium-low — log is the source of truth. Both systems are derived. | When you can introduce an event log without modifying existing write paths (often not feasible with legacy). |

**The reconciliation imperative:** Regardless of approach, run continuous reconciliation between old and new data stores. Compare record counts, checksums, or full record comparisons on a schedule. Every discrepancy is either a bug in your sync mechanism or a race condition you need to understand. Do NOT wait until cutover to discover that 0.3% of records have drifted — by then it's too late to fix.

### Rollback Planning

Every migration must have a rollback plan. Not "we'll figure it out if we need to" — a tested, documented, practiced rollback plan.

**Rollback categories:**

- **Instant rollback.** Flip a feature flag or routing rule. Only possible if data hasn't diverged. Works for stateless routing changes and read-path migrations.
- **Data rollback.** Restore old system's data from a point-in-time backup or snapshot. Possible if you took a snapshot before migration and the data loss from the migration window is acceptable. Works for short migration windows (minutes to hours).
- **No rollback.** The migration is irreversible because the new system has accepted writes that the old system can't ingest, or the old system's infrastructure has been decommissioned. This is a valid choice for low-risk migrations, but it MUST be an explicit, documented decision, not a surprise discovered at 3am when someone asks "can we roll back?"

**The rollback test:** Before every migration, ask: "If we need to roll back 2 hours after cutover, what exactly do we do?" Write down the steps. Estimate the time. Identify the data loss. If the answer is "we can't," make sure everyone with authority has signed off on that risk.

---

## 8. Common Failure Modes

Enterprise integration failures are rarely technical in isolation. They're sociotechnical — a technical failure exposed by an organizational gap. These are the ones that wake you up at night.

### Integration Point as Single Point of Failure

**The pattern:** System A depends on System B through a synchronous integration. System B goes down. System A can't function. Nobody planned for this because "System B has 99.9% uptime."

**Why it happens:** Teams design integrations for the happy path. The integration works in dev, works in staging, passes acceptance testing. Nobody tests what happens when the downstream system returns 500s for 20 minutes, or takes 30 seconds to respond, or returns garbage data that parses but is semantically wrong.

**Mitigation:** Every synchronous integration needs a degraded mode. What does System A do when System B is unavailable? Queue the request and retry later? Serve stale cached data? Return a degraded response? Fail fast with a clear error? All of these are valid, but the choice must be made during design, not during an outage.

### Data Consistency Across Systems

**The pattern:** Customer updates their address in System A. The update event is published. System B processes it 3 minutes later. System C's consumer is down and processes it 2 hours later. For those 2 hours, three systems disagree about the customer's address.

**Why it's hard:** Distributed consistency is a fundamental computer science problem with no free solution. Strong consistency (distributed transactions, two-phase commit) is slow, fragile, and doesn't scale across enterprise boundaries. Eventual consistency is the pragmatic choice, but "eventual" can mean seconds, minutes, or hours, and the business impact of inconsistency varies by domain.

**Mitigation:** Define consistency requirements per integration, not globally. Some data (account balance, inventory count) needs near-real-time consistency and justifies the cost of synchronous updates or very short replication lag. Other data (customer name, address) can tolerate minutes of staleness. Make the consistency window explicit and monitor it — alert when replication lag exceeds the SLA.

### Schema Evolution Breaking Downstream Consumers

**The pattern:** Team A adds a required field to their event schema. Team A's tests pass. Team B's consumer doesn't know about the new field. Team B's deserialization fails. Team B's processing pipeline stops. Team B discovers this in production because nobody tested cross-team schema changes end-to-end.

**Why it happens:** Schema evolution in a distributed system is a coordination problem disguised as a technical one. Each team controls its own schemas, but consumers of those schemas are in other teams with different release cycles.

**Mitigation:**
- **Schema registry.** Enforce backward and forward compatibility rules at registration time (Confluent Schema Registry, AWS Glue Schema Registry, Apicurio). New schemas that break compatibility are rejected before they reach production.
- **Consumer-driven contract testing.** Each consumer publishes a contract specifying what they expect from the producer's schema. The producer's CI pipeline runs these contracts and fails if a change breaks any consumer. (Pact, Spring Cloud Contract.)
- **Additive-only changes.** The rule: you can add optional fields. You cannot remove fields, rename fields, or change field types. If you need a breaking change, create a new version of the schema and run both versions in parallel during migration.

### Cascading Failures Through Integration Layers

**The pattern:** A database is slow. The service that queries it starts timing out. The gateway's connection pool to that service fills up. Other services routed through the same gateway start failing because the gateway has no available connections. A single slow database takes down 12 services.

**Why it happens:** Enterprise integration layers are shared infrastructure. The gateway, the message broker, the ESB — they serve many systems. A problem in one system's integration path can exhaust shared resources (connections, threads, memory, queue depth) and affect every other system.

**Mitigation:**
- **Bulkhead pattern.** Isolate connection pools per downstream service. The gateway has separate connection pools for each backend. If one backend's pool is exhausted, other backends are unaffected.
- **Circuit breaker.** Stop sending requests to a failing backend. After a threshold of failures, the circuit opens and requests fail fast instead of queuing. Periodically allow a probe request to check if the backend has recovered.
- **Timeout hierarchies.** Set timeouts at every layer, and make inner timeouts shorter than outer timeouts. If the gateway's timeout to the backend is 5 seconds, the client's timeout to the gateway should be >5 seconds. Otherwise, the client gives up but the gateway keeps the request in flight, wasting resources.
- **Backpressure.** When the system is overwhelmed, push back on the caller. Return 429 (Too Many Requests) or 503 (Service Unavailable) with a Retry-After header. This is better than accepting the request and failing slowly.

### Vendor Lock-In Through Deep Integration

**The pattern:** The team adopts an iPaaS (MuleSoft, Boomi, Informatica) or cloud integration service (AWS EventBridge, Azure Logic Apps). Over 3 years, 200 integration flows are built on the platform. The vendor raises prices 40%. You can't migrate because every flow uses proprietary connectors, proprietary transformation languages, and proprietary monitoring.

**Why it happens:** Integration platforms are sticky by design. The initial adoption is easy — pre-built connectors, drag-and-drop UIs, managed infrastructure. The lock-in accumulates gradually. Each new flow adds a small amount of platform-specific logic. After 200 flows, the migration cost exceeds the price increase.

**Mitigation:**
- **Encapsulate vendor-specific logic.** Integration flows should call your services through standard APIs, not through vendor-specific connectors that embed your business logic in the vendor's runtime.
- **Exportable configurations.** If your integration logic is in a vendor-proprietary format, you can't migrate without rewriting. Prefer vendors that store configuration in standard formats or provide export capabilities.
- **Cost modeling.** Before adopting an integration platform, model the cost at 10x your current integration count. That's where you'll be in 3 years. If the cost is unacceptable at scale, the platform is a trap.
- **The honest assessment:** Some vendor lock-in is acceptable. Running your own Kafka cluster and building custom CDC pipelines is expensive too. The question isn't "is there lock-in?" — it's "is the lock-in proportional to the value, and can I negotiate from a position of strength when the contract renews?"

### Migration That Never Completes

**The pattern:** The legacy migration starts with energy and executive sponsorship. The first 60% is migrated in 6 months. The remaining 40% involves the most complex, most regulated, least-documented functionality. Progress slows. Leadership changes. The migration budget is reallocated. The team is left running two systems indefinitely — the worst possible outcome, because now you have the operational cost of both systems and the integration complexity of keeping them in sync.

**Why it happens:** Legacy migrations follow an effort curve where the last 20% takes 80% of the time. Executives who approved the project based on the velocity of the first 60% lose patience. Meanwhile, the team has been building new features on the new system, making the old system even harder to migrate because the delta keeps growing.

**Mitigation:**
- **Migrate the hardest things first** (if politically feasible). This front-loads the risk and gives a more honest velocity estimate.
- **Define "done" before starting.** Is "done" decommissioning the old system? Or is "done" migrating all active users while keeping the old system in read-only mode for historical queries? The second is dramatically easier and may be sufficient.
- **Measure and report coupling reduction, not migration percentage.** "We reduced cross-system dependencies from 47 to 12" is more defensible than "we migrated 73% of endpoints." Coupling reduction has direct operational value even if the migration stalls.
- **Budget for the long tail.** Tell leadership: "The first 80% will take 6 months. The last 20% will take 12 months. Here's why." If they won't fund 18 months, negotiate a partial migration that leaves the system in a stable dual-operation state rather than a fragile half-migrated state.

---

## 9. Anti-Patterns

These are the patterns that feel right in the moment and cause pain for years. Each one is the default path of least resistance, which is why they're so common.

**"Enterprise Service Bus as God Object."** The ESB starts as a routing and transformation layer. Then someone adds business logic ("if the order total is over $10,000, route to the fraud check queue"). Then more. Then more. After 3 years, the ESB contains 500 routing rules, 200 transformation mappings, and an unknowable amount of business logic. No team owns it. Everyone depends on it. Deploying a change requires a change advisory board meeting. The ESB is now the most coupled, least testable, most fragile component in the entire enterprise. Congratulations — you've built a distributed monolith and put it in the middle of everything.

**"Shared Database Integration."** Systems communicate by reading and writing to the same database tables. No APIs, no events, no contracts. This is the fastest integration to build and the most expensive to maintain. See section 4. Every organization that has done this for more than 5 years has at least one table with 200+ columns, 15+ applications reading from it, and a DBA who has PTSD from the last schema migration attempt.

**"Big Bang Rewrite."** "We'll just rewrite it from scratch. How hard can it be? The existing system is only 200,000 lines." See section 2. The rewrite takes 3x longer than estimated, delivers 60% of the features of the old system, introduces new bugs for every old bug it fixes, and the team is so exhausted by the end that they have no energy for the migration itself.

**"Canonical Model That No One Follows."** The architecture team spends 6 months defining a canonical data model. It's published on the wiki. Two teams adopt it. The other ten teams continue using their own models because the canonical model doesn't fit their domain, the adoption path is unclear, and there's no enforcement mechanism. The canonical model becomes a fiction that appears in architecture diagrams but not in production traffic.

**"Integration Through the UI."** System A has no API. System B needs data from System A. Someone writes a script that logs into System A's web UI, scrapes the pages, and extracts the data. This is screen scraping. It breaks every time System A changes their CSS, reorganizes a page, or adds a CAPTCHA. It's fragile, slow, impossible to monitor properly, and it violates every security assumption System A's team made about their web interface. And yet it persists because sometimes it's the only option — the vendor won't provide an API, the legacy system predates the concept of APIs, or the budget for a proper integration doesn't exist. If you must do this, encapsulate it behind a clean API so consumers don't know how the sausage is made, and monitor it aggressively. Plan to replace it, and actually replace it.

**"The Synchronous Chain."** Service A synchronously calls B, which synchronously calls C, which synchronously calls D, which synchronously calls E. The chain's availability is the product of each service's availability (0.999^4 ~ 0.996 — half the nines you thought you had). The chain's latency is the sum of each service's latency. Debugging a timeout requires tracing through 4 services with 4 different log formats in 4 different teams' infrastructure. Break the chain. If A needs data from E, consider caching, event-carried state transfer, or at minimum circuit breakers at every link.

**"The Dual-Write Permanent Architecture."** During migration, you dual-write to old and new systems. The migration "finishes" but dual-write stays because "it's working and we don't want to risk turning off the old system." Now you maintain synchronization code, reconciliation jobs, and twice the infrastructure forever. Every dual-write is a ticking clock. Set a decommission date when you start and treat it as a hard deadline.

**"The Integration That Nobody Owns."** Two teams built an integration 3 years ago. Both team leads have left the company. The integration works (mostly) and neither current team considers it their responsibility. When it breaks — and it will — it becomes an incident without an owner, escalated through management chains until someone is voluntold to fix it. Every integration must have a single owning team recorded in a service catalog. When ownership is unclear, it's a risk — and it should be tracked as one.

**"Governance Without Tooling."** The architecture review board mandates that all integrations use the canonical model, go through the API gateway, and follow the event schema standard. But there's no schema registry, no automated compliance checks, no self-service gateway configuration. Developers can't follow the standards without filing tickets and waiting weeks. So they don't. Governance without tooling is just wishful thinking. If a standard isn't enforceable through automation, it isn't a standard — it's a suggestion.

**"The Migration Bypass."** During a long migration, developers start building integrations that go directly to the legacy system instead of through the new integration layer, because the new layer doesn't support their use case yet. Each bypass is a new dependency on the legacy system — exactly what the migration is trying to eliminate. Every bypass must be tracked, justified, and have a retirement date. If you're accumulating bypasses faster than you're migrating, the migration is going backwards.

---

## Design Checklist

When evaluating or designing enterprise integrations, work through these questions:

### Coupling
- [ ] What is every system coupled to? Map it — database, API, event, file, shared library, shared infrastructure.
- [ ] Can each system be deployed independently? If not, why not?
- [ ] If System X goes down, what else breaks? Is that acceptable?

### Data
- [ ] Who is the source of truth for each data entity?
- [ ] What is the acceptable staleness window for each consumer?
- [ ] How does schema evolution work across system boundaries?
- [ ] Is there a shared database? What's the plan to decompose it?

### Organizational
- [ ] Who owns each integration? (Not "everyone." A specific team.)
- [ ] What's the contract between producer and consumer teams?
- [ ] Does the org structure match the desired integration architecture?
- [ ] Who has authority to enforce integration standards?

### Migration
- [ ] Is there a legacy system being strangled? What's the migration status?
- [ ] What's the rollback plan for the current migration phase?
- [ ] Is data synchronized between old and new? How is drift detected?
- [ ] When is the legacy system scheduled for decommission? Is that date realistic?

### Failure
- [ ] What happens when each integration point is unavailable?
- [ ] Are there circuit breakers? Where?
- [ ] Is there monitoring for integration health (not just uptime — latency, error rate, consumer lag)?
- [ ] When was the last time someone tested the failure mode?
