---
name: system-type-web-service
description: "Domain patterns for web service architecture — API design (REST/GraphQL/gRPC), scaling, data layer, observability, failure modes, and anti-patterns. Use when designing or evaluating a web service, API, or request/response system."
---

# System Type: Web Service

Patterns, failure modes, and anti-patterns for request/response web services.

---

## API Patterns

### REST
**When to use.** Public APIs, browser-facing services, CRUD-heavy domains, when discoverability and cacheability matter.
**When to avoid.** Highly relational data with many nested queries (N+1 fetches). Real-time bidirectional communication. High-throughput internal service-to-service calls where payload efficiency matters.
**Key decisions.** Resource naming, versioning strategy (URL vs header), pagination approach, error format.

### GraphQL
**When to use.** Multiple client types needing different data shapes from the same backend. Complex, nested data relationships. When frontend teams need to iterate independently from backend.
**When to avoid.** Simple CRUD APIs. Server-to-server communication. When caching at the HTTP layer is important (GraphQL's POST-based model breaks HTTP caching). When the team doesn't have GraphQL operational expertise.
**Key decisions.** Schema-first vs code-first, query complexity limits, N+1 resolution strategy (DataLoader pattern), authorization model.

### gRPC
**When to use.** Internal service-to-service communication. When payload size and serialization speed matter. When you want strongly-typed contracts with code generation. Streaming use cases.
**When to avoid.** Browser clients (requires grpc-web proxy). When human readability of requests matters for debugging. When the team lacks protobuf experience. Public APIs (tooling ecosystem is smaller).
**Key decisions.** Proto file organization, backward compatibility discipline, deadline propagation, load balancing (L7 required for HTTP/2).

## Scaling Patterns

**Horizontal scaling.** Add more instances behind a load balancer. Requires stateless services (or externalized state). The default approach for web services. Watch for: session affinity requirements, connection pool exhaustion at the database, cache consistency across instances.

**Vertical scaling.** Bigger machines. Simpler than horizontal but has a ceiling. Right for: databases, in-memory workloads, and when horizontal scaling's coordination cost exceeds the performance benefit.

**Autoscaling.** Scale instance count based on metrics (CPU, request rate, queue depth). Essential for variable load. Watch for: cold start latency, scaling lag, minimum instance counts for availability, cost runaway from misconfigured scaling policies.

**CDN and edge caching.** Serve static and cacheable dynamic content from edge locations. Dramatically reduces latency and origin load. Watch for: cache invalidation complexity, cache poisoning, TTL tuning, varying content by headers (accept-language, authorization).

**Read replicas.** Offload read traffic from the primary database. Watch for: replication lag causing stale reads, read-after-write consistency requirements, connection routing complexity.

## Data Layer Patterns

**RDBMS (PostgreSQL, MySQL).** Default choice for structured, relational data. Strong consistency, ACID transactions, mature tooling. Scales vertically well; horizontal scaling requires sharding (hard) or read replicas (easier).

**Document stores (MongoDB, DynamoDB).** When data is naturally document-shaped, schema varies per record, or you need horizontal scaling without sharding complexity. Watch for: lack of joins, transaction limitations across documents, query patterns that don't match the data model.

**Key-value stores (Redis, Memcached).** Caching, session storage, rate limiting, leaderboards. Extremely fast for simple access patterns. Watch for: data loss on restart (unless configured for persistence), memory limits, using it as a primary datastore when it's a cache.

**Search engines (Elasticsearch, OpenSearch).** Full-text search, log aggregation, analytics on semi-structured data. Watch for: operational complexity, eventual consistency, write amplification, cluster sizing that's hard to change later.

## Observability

**Structured logging.** JSON logs with consistent fields (request_id, user_id, service, timestamp, level). Enable correlation across services. Avoid: unstructured log lines, logging sensitive data, excessive log volume without sampling.

**Distributed tracing.** Propagate trace IDs across service boundaries to reconstruct request paths. Essential when requests span multiple services. Use OpenTelemetry for vendor-neutral instrumentation.

**Metrics.** RED method for services (Rate, Errors, Duration). USE method for resources (Utilization, Saturation, Errors). Define SLOs before choosing what to measure.

**SLOs and SLIs.** Define service level objectives in terms of measurable indicators (latency P99 < 200ms, error rate < 0.1%). SLOs drive alerting, capacity planning, and error budgets. Without SLOs, you're guessing about reliability.

## Common Failure Modes

- **Cascading failures.** One slow service causes callers to queue up, exhausting their resources. Mitigation: timeouts, circuit breakers, bulkheads.
- **Connection pool exhaustion.** Database or HTTP connection pools fill up under load. Mitigation: pool sizing, connection timeouts, backpressure.
- **Thundering herd.** Cache expiry causes all instances to hit the backend simultaneously. Mitigation: jittered TTLs, request coalescing, cache warming.
- **Retry storms.** Clients retry failed requests, multiplying load on an already-stressed system. Mitigation: exponential backoff with jitter, retry budgets, circuit breakers.
- **Memory leaks.** Gradual memory growth leading to OOM kills. Mitigation: memory limits, health checks, regular restarts (if you can't find the leak).
- **Dependency failures.** External services go down. Mitigation: timeouts, fallbacks, graceful degradation, feature flags.

## Anti-Patterns

- **Distributed monolith.** Microservices that must deploy together, share databases, or make synchronous calls in long chains. You got the complexity of distribution without the benefits.
- **God service.** One service that does everything. Split by domain boundary, not by arbitrary size targets.
- **Chatty interfaces.** Many small API calls where one well-designed call would do. Increases latency, error surface, and complexity.
- **Shared mutable state.** Multiple services writing to the same database tables. Define ownership or accept the coupling.
- **Premature microservices.** Splitting into services before understanding domain boundaries. Start with a well-structured monolith; extract services when you have evidence they need independent scaling or deployment.
- **Ignoring cold starts.** Assuming services are always warm. New deployments, autoscaling events, and restarts all serve cold traffic.
