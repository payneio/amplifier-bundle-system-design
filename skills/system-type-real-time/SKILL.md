---
name: system-type-real-time
description: "Domain patterns for real-time and collaborative systems — persistent connections, state synchronization, conflict resolution, presence, fan-out, and failure modes. Use when designing or evaluating chat systems, collaborative editors, live dashboards, gaming backends, or any system with bidirectional real-time communication."
---

# System Type: Real-Time & Collaborative

Patterns, failure modes, and anti-patterns for systems with persistent connections and real-time state synchronization.

---

## Connection Patterns

### WebSocket
**What it is.** Full-duplex, persistent TCP connection upgraded from HTTP. Both sides can send frames at any time.
**When to use.** Bidirectional communication with low latency — chat, collaborative editing, multiplayer games, live trading. When the server needs to push AND the client needs to push back frequently.
**When to avoid.** Unidirectional server-to-client updates (SSE is simpler). Infrequent updates where polling is adequate. Environments where intermediaries (corporate proxies, older load balancers) silently kill long-lived connections.
**Key decisions.** Binary vs text frames, subprotocol negotiation, per-message compression (permessage-deflate has CPU cost), ping/pong interval tuning.

### Server-Sent Events (SSE)
**What it is.** Unidirectional server-to-client stream over a standard HTTP response. Built-in reconnection with `Last-Event-ID`. Works through HTTP/2 multiplexing natively.
**When to use.** Live dashboards, notification feeds, stock tickers — anything where the server pushes and the client only needs HTTP requests for writes. When you want automatic reconnection semantics for free.
**When to avoid.** Bidirectional real-time communication. Binary data. When you need more than ~6 concurrent connections per domain in HTTP/1.1 browsers (HTTP/2 eliminates this).

### Long Polling
**What it is.** Client sends a request; server holds it open until there's data or a timeout, then responds. Client immediately sends the next request.
**When to use.** Fallback when WebSocket and SSE aren't available. Environments with aggressive proxies. When connection frequency is low enough that the overhead is acceptable.
**When to avoid.** High-frequency updates (each message requires a full HTTP round-trip). The per-request overhead is substantial compared to persistent connections.

### WebTransport
**What it is.** Multiplexed, bidirectional transport built on HTTP/3 (QUIC). Supports both reliable streams and unreliable datagrams. No head-of-line blocking.
**When to use.** Latency-sensitive applications where packet loss shouldn't stall unrelated streams — gaming, live media, telemetry. When you need unreliable delivery (datagrams) alongside reliable streams.
**When to avoid.** Browser support is still limited. When WebSocket meets your latency requirements. When you don't control the server infrastructure to support HTTP/3.

### Connection Lifecycle
Every persistent connection follows the same pattern: **establish → authenticate → maintain → recover**.

- **Establish.** Negotiate the connection (WebSocket upgrade, SSE stream open). Set initial parameters. The handshake is your one chance to reject bad clients cheaply.
- **Authenticate.** Pass a short-lived token during handshake (query param or first message). Never rely on cookies alone — CSRF is harder to prevent on WebSocket upgrades. Re-validate tokens periodically for long-lived connections.
- **Heartbeat.** Both sides send pings at a regular interval. If a pong is missed, the connection is considered dead. Tune the interval: too fast wastes bandwidth; too slow means minutes of stale "online" state. 30 seconds is a common default; 15 seconds for presence-critical systems.
- **Reconnect.** Exponential backoff with jitter. Include the last-seen sequence number so the server can resume without replaying the entire state. Cap the backoff (e.g., 60 seconds) — waiting 10 minutes to reconnect is indistinguishable from being offline.

### Connection Multiplexing
Multiple logical channels over a single physical connection. Avoids the cost of many TCP handshakes and TLS negotiations. Implement with message framing that includes a channel ID. Watch for: head-of-line blocking in WebSocket (a single TCP stream), priority inversion between channels, complexity of flow control per logical channel.

## State Synchronization

### Server-Authoritative State
**What it is.** The server owns the truth. Clients send intents; the server validates, applies, and broadcasts the result.
**When to use.** Any system where correctness matters more than perceived latency — financial systems, competitive games, inventory management. When cheating or inconsistency is unacceptable.
**The cost.** Every action has at least one round-trip of latency before the user sees the result.

### Optimistic Updates with Server Reconciliation
**What it is.** Client applies changes locally before server confirmation. If the server rejects or modifies the change, the client rolls back or reconciles.
**When to use.** Collaborative editing, chat message sending, any UI where perceived latency matters. The user sees their action instantly; corrections arrive later.
**The hard part.** Rolling back user-visible state is jarring. Design for reconciliation (merge the server's response into local state) rather than rollback (undo and redo). The client must maintain a queue of unconfirmed changes and be able to rebase them onto server state.

### Client Prediction
**What it is.** Client simulates the outcome of actions locally and reconciles when the server's authoritative state arrives. Common in games (client-side prediction with server reconciliation).
**When to use.** Real-time games, cursor tracking, any interaction where the round-trip latency is perceptible and the outcome is usually predictable.
**Watch for.** Mispredictions cause visual corrections ("rubber-banding"). The prediction logic must match server logic exactly, or divergence accumulates.

### Operational Transformation (OT)
**What it is.** Transforms concurrent operations against each other so they can be applied in any order and converge to the same state. Requires a central server to determine operation ordering.
**When to use.** Text-based collaborative editing (Google Docs uses OT). When you have a reliable central server and need character-level collaboration.
**When to avoid.** Decentralized systems (OT requires a single ordering authority). Complex data structures beyond text — OT transform functions become combinatorially complex as operation types grow.

### CRDTs (Conflict-Free Replicated Data Types)
**What it is.** Data structures where concurrent updates always converge without coordination. No central server needed for correctness — peers can sync directly.
**When to use.** Offline-capable collaboration, peer-to-peer systems, any system where nodes must work independently and sync later. Text editing (Yjs, Automerge), shared counters, sets, maps.
**When to avoid.** When server-authoritative state is simpler and sufficient. CRDTs have memory overhead (they carry metadata for conflict resolution) and some types (text sequences) are significantly more complex to implement correctly than OT. When your data model doesn't map cleanly to available CRDT types.

### Versioning and Ordering
**Sequence numbers.** Simple monotonic counter per stream. Sufficient for single-server systems. Clients can detect gaps and request retransmission.
**Vector clocks.** Track causal ordering across multiple nodes. Each node maintains a counter per known node. Expensive to compare at scale — the vector grows with the number of participants.
**Hybrid logical clocks.** Combine physical timestamps with logical counters. More compact than vector clocks, provide causal ordering, and approximate wall-clock time. Good for distributed collaborative systems.
**Lamport timestamps.** Provide total ordering but not causal ordering. Sufficient when you just need a tiebreaker, not true causality tracking.

## Conflict Resolution

### Last-Writer-Wins (LWW)
**What it is.** Most recent write (by timestamp or version number) wins. Previous concurrent writes are silently discarded.
**When to use.** User profile updates, settings, any field where the most recent intent is what matters and losing a concurrent write is acceptable.
**When to avoid.** Anything additive (counters, lists, collaborative text). Losing a write silently is data loss — LWW just makes it someone else's problem.

### Application-Level Merge Strategies
**When conflicts are acceptable.** Most collaborative systems — two users editing different paragraphs, updating different fields. Present both versions and let the user choose, or merge automatically when the changes are non-overlapping.
**When conflicts are catastrophic.** Financial transactions, inventory reservation, anything where "both writes happen" means real-world harm. Use pessimistic locking, serializable transactions, or compare-and-swap operations. Accept the latency cost.

### CRDT Conflict Resolution
- **G-Counter / PN-Counter.** Grow-only and positive-negative counters. Each node increments its own slot. Sum of all slots is the value. No conflicts possible by construction.
- **G-Set / OR-Set.** Grow-only set (add-only) and observed-remove set (add and remove). OR-Set handles the "add wins over concurrent remove" semantic, which is the right default for most applications.
- **LWW-Register.** Last-writer-wins register using timestamps. Simple but lossy — use when losing concurrent writes is tolerable.
- **Text CRDTs (RGA, YATA).** Represent text as a sequence of uniquely identified characters with ordering metadata. Insertions and deletions commute. Libraries like Yjs and Automerge implement these. Memory overhead is real — a 10KB document may use 100KB+ of CRDT metadata.

## Presence and Awareness

### Online/Offline Detection
**Heartbeat-based presence.** Client sends periodic heartbeats. Server marks client as offline after missing N consecutive heartbeats. Simple and reliable. Tune the timeout: too aggressive and flaky connections cause presence flickering; too lenient and stale presence lingers for minutes.
**The fundamental tradeoff.** Fast detection (5-10s timeout) vs stable presence (30-60s timeout). Chat applications typically use 15-30 seconds. Collaborative editors can tolerate 30-60 seconds because the cursor position already conveys activity.

### Cursor Positions and Selection
Broadcast cursor position on change, throttled to ~10-20 updates per second per user. Include a user identifier and color. Don't broadcast every keystroke position — batch and throttle. For remote cursors, interpolate between received positions to smooth movement.

### Typing Indicators
Send a "started typing" event. Clear after a timeout (3-5 seconds of inactivity) or an explicit "stopped typing" event. Don't send continuous "is typing" events — send transitions. Rate-limit outbound typing events to avoid flooding channels with many participants.

### Thundering Herd on Reconnection
When a server restarts or a network partition heals, all clients reconnect simultaneously. Every client sends presence updates, subscribes to channels, and requests state catch-up — at the same instant.
**Mitigations:**
- **Jittered reconnect delay.** Clients wait a random interval (0 to N seconds) before reconnecting. Spreads the thundering herd across a time window.
- **Gradual presence broadcast.** After a server restart, don't broadcast all presence updates immediately. Batch and stagger.
- **Connection rate limiting.** Accept connections at a controlled rate. Return "retry later" with a backoff hint for excess connections.
- **Stale presence TTL.** Don't immediately mark everyone as offline when a server restarts. Assume recent presence is still valid for a short window while clients reconnect.

## Fan-Out Patterns

### Per-Connection Fan-Out
**What it is.** For each message, iterate over all connected clients and deliver individually.
**When to use.** Small-scale systems, prototypes, rooms with fewer than ~100 participants.
**When it breaks.** Delivery time grows linearly with connection count. A room with 10,000 members means 10,000 individual sends per message. CPU and memory on the connection server become the bottleneck.

### Channel-Based Routing
**What it is.** Clients subscribe to named channels (rooms, topics). Messages published to a channel are delivered to all subscribers. The pub/sub layer handles fan-out.
**When to use.** Chat rooms, topic-based feeds, any system with natural groupings of interested clients.
**Implementation.** In-process subscriber lists for single-server. Redis Pub/Sub, NATS, or Kafka for multi-server. The pub/sub layer must deliver to every server that has subscribers for the channel; each server then fans out to its local connections.

### Presence-Aware Delivery
**What it is.** Only deliver to clients that are currently online. Queue or drop messages for offline clients based on policy.
**When to use.** Systems where offline delivery is handled separately (push notifications, email fallback) or where messages are ephemeral (typing indicators, cursor positions).
**The decision.** What happens to messages for offline users? Options: drop silently (ephemeral data), queue for delivery on reconnect (chat messages), persist and let client pull on reconnect (channel history).

### The N-Squared Problem
In a room with N participants, each participant's state change (cursor move, typing indicator) must be sent to N-1 others. That's O(N) messages per event, and if all N participants are active, that's O(N²) messages per second. At ~50 participants, this dominates bandwidth.
**Mitigations:**
- **Throttle per-user broadcasts.** Limit cursor updates to 5-10 per second per user regardless of actual movement frequency.
- **Viewport-aware fan-out.** Only send updates relevant to what each client is viewing. A user viewing page 1 doesn't need cursor positions from page 47.
- **Aggregated updates.** Batch multiple small updates into a single message per delivery interval (e.g., every 50ms). Reduces message count at the cost of slight latency.
- **Tiered presence.** Full presence for focused collaborators; degraded presence (online/offline only) for observers.

### Scaling Fan-Out

**Pub/Sub backing.** Use Redis Pub/Sub, NATS, or Kafka to distribute messages across connection servers. Each connection server subscribes to channels that its local clients care about. Watch for: Redis Pub/Sub is fire-and-forget (no persistence, no replay); Kafka provides persistence but adds latency; NATS JetStream provides a middle ground.

**Connection affinity.** Route clients in the same channel to the same connection server when possible. Reduces cross-server fan-out. Watch for: uneven distribution when some channels are much larger than others, rebalancing during deploys.

**Sharded channels.** For very large channels (thousands of subscribers), shard across multiple servers. Each shard handles fan-out for a subset of subscribers. A message published to the channel is forwarded to all shards. Watch for: ordering guarantees across shards, shard rebalancing.

## Reconnection and Rehydration

### Resumable Connections
Assign each connection a session ID and track the last-delivered sequence number. On reconnect, the client sends its session ID and last-seen sequence number. The server replays missed messages from a buffer.
**Buffer sizing.** Too small and clients that were offline for a minute get a full resync. Too large and the server holds too much state per connection. A sliding window of 5-10 minutes of messages is typical. Use a ring buffer per channel, not per connection.

### State Catch-Up After Disconnect
**Delta sync.** Client sends its last-known version. Server computes and sends only the changes since that version. Efficient but requires the server to maintain a change log.
**Full sync.** Client discards local state and downloads everything. Simple but expensive. Acceptable for small state (a chat room's last 50 messages); unacceptable for large state (a collaborative document).
**Hybrid.** Attempt delta sync. If the client's version is too old (outside the change log window), fall back to full sync. This is the pragmatic approach for most systems.

### Offline Queue
Client queues actions performed while disconnected. On reconnect, the queue is replayed against the server.
**The hard part.** Actions in the queue may conflict with changes made by other users while this client was offline. Each queued action must be validated and potentially transformed or rejected by the server. This is where OT and CRDTs earn their complexity budget — they provide principled answers to "what happens when I replay my offline edits against a state that has moved on."

## Scaling Persistent Connections

### Connection Servers vs Application Servers
Separate the concern of holding connections from the concern of processing business logic. Connection servers are I/O-bound (thousands of idle connections, occasional message forwarding). Application servers are CPU-bound (message validation, persistence, business rules). Scaling them independently is the key to cost-efficient real-time systems.

### Sticky Sessions and Their Downsides
Persistent connections are inherently sticky — they're bound to the server that accepted the upgrade. This creates problems:
- **Uneven load.** Some servers accumulate more connections over time, especially for popular channels.
- **Deploys require draining.** You can't just kill a server — you must drain connections gracefully, giving clients time to reconnect elsewhere.
- **Server failure is localized.** When a connection server dies, all its clients disconnect simultaneously, creating a localized thundering herd on the remaining servers.
- **No mid-connection rebalancing.** Unlike HTTP requests, you can't redistribute persistent connections without client cooperation.

### Connection Migration During Deploys
**Graceful drain.** Stop accepting new connections. Send a "please reconnect" control message to existing clients with a jittered delay. Wait for connections to close. Shut down.
**Blue/green for WebSocket.** Route new connections to the new deployment. Drain old connections over minutes, not seconds. The overlap period means both old and new servers must handle the same channels.
**The deploy budget.** If you have 100,000 connections and each reconnection takes 100ms of server time, draining all connections simultaneously requires 10,000 seconds of CPU-time. Stagger over 2-5 minutes minimum.

### Backpressure for Slow Consumers
A client on a poor network connection can't receive messages as fast as they're produced. Without backpressure, the server buffers messages per-connection, memory grows, and the server eventually OOMs.
**Strategies:**
- **Per-connection send buffer with a cap.** If the buffer is full, drop messages (with a "you missed N messages, resync" notification) or disconnect the client.
- **Priority-based dropping.** Drop ephemeral messages (cursor positions, typing indicators) before durable messages (chat content). Not all messages are equal.
- **Adaptive rate.** Reduce update frequency for slow consumers. Send aggregated updates instead of individual events.

### Memory Per Connection at Scale
Each WebSocket connection costs memory: TCP buffers (~4-8KB), TLS state (~20-50KB), application-level state (subscriptions, session data). At 100,000 connections, that's 2-6GB of overhead before any message buffering. Budget for it. Monitor RSS per connection server. A "small" memory leak of 1KB per connection per hour becomes 100MB/hour at scale.

## Common Failure Modes

- **Connection storm on deploy.** Server restart disconnects all clients. They all reconnect simultaneously, overwhelming the new server before it's warmed up. Mitigation: jittered reconnect with exponential backoff, connection rate limiting on the server, pre-warming the new server before draining the old one.
- **Slow consumer backpressure.** A client on a degraded network stops reading. The server buffers outbound messages. Multiply by thousands of slow clients and the server runs out of memory. Mitigation: per-connection buffer limits, drop policy for ephemeral messages, disconnect chronically slow consumers.
- **Split-brain in presence.** Two servers disagree about who is online — one thinks the user connected, the other hasn't received the disconnect. Mitigation: presence TTL with heartbeat renewal, criss-cross presence queries during ambiguity, accept that presence is eventually consistent and design the UI accordingly.
- **Message ordering across shards.** Messages published to different shards of a channel arrive at clients in different orders. Mitigation: include a causal ordering field (sequence number or timestamp) and let the client reorder. Accept that total ordering across shards is expensive and usually unnecessary.
- **Thundering herd on network partition heal.** A network partition between data centers heals. Thousands of connections that were in "reconnecting" state all succeed at once. Both data centers flood each other with state sync. Mitigation: jittered reconnection, rate-limited sync, partition-aware message deduplication.
- **Memory leaks from abandoned connections.** Client process crashes without sending a close frame. The server holds the connection open until the next heartbeat timeout. If heartbeats are infrequent or the cleanup path has bugs, connections accumulate. Mitigation: aggressive heartbeat timeouts (30s), periodic connection audits, process-level memory monitoring with alerts.
- **Fan-out amplification.** A single message to a large channel generates thousands of outbound messages. If the channel has 50,000 subscribers across 100 servers, one inbound message becomes 50,000 outbound messages. Mitigation: sharded fan-out, hierarchical pub/sub (edge servers aggregate), rate limiting per-channel publish.
- **Stale state after long disconnect.** Client reconnects after being offline for hours. The delta sync window has expired. The client has a deeply stale local state and applies offline changes against it. Mitigation: version-aware reconnection that detects when delta sync is impossible and forces full resync, discard offline queue when the gap is too large.

## Anti-Patterns

- **Polling in a WebSocket.** Opening a WebSocket and then having the client poll for updates on it every N seconds. You have a persistent connection — use server push. If you're polling, you didn't need WebSocket.
- **Unbounded per-connection buffers.** Buffering all messages for every slow client without limits. One degraded mobile client on a busy channel can consume gigabytes of server memory. Always cap buffers and have a drop or disconnect policy.
- **Presence as ground truth.** Treating presence state as strongly consistent. Presence is inherently best-effort — network delays, heartbeat windows, and race conditions mean presence will occasionally be wrong. Design the application to tolerate showing a user as online for 30 seconds after they left. Never make authorization decisions based on presence.
- **Synchronous persistence in the message path.** Writing every message to a database before delivering to subscribers. This puts database latency in the critical path of every real-time message. Deliver first, persist asynchronously. Accept the small window of potential message loss or use a write-ahead log.
- **Global ordering for everything.** Requiring total ordering across all messages in the system. Total ordering requires a single sequencer — a bottleneck by design. Most applications only need ordering within a channel or conversation. Identify where ordering actually matters and scope it narrowly.
- **Reconnecting without backoff.** Client immediately retries on disconnect, in a tight loop. Multiplied across thousands of clients hitting a struggling server, this turns a transient failure into a permanent one. Always use exponential backoff with jitter. Always.
- **Treating WebSocket connections as cheap.** Opening a connection per feature (one for chat, one for notifications, one for presence). Each connection has TLS, TCP, and memory overhead. Multiplex logical channels over a single connection. One connection per client, not per feature.
- **CRDTs for everything.** Reaching for CRDTs because they sound elegant when server-authoritative state with simple last-writer-wins would suffice. CRDTs have real memory and complexity costs. Use them when you need offline-capable collaboration or decentralized sync. Use simpler models when you don't.
- **Ignoring the deploy problem.** Designing the real-time system without a plan for zero-downtime deploys. Persistent connections make deploys fundamentally harder than stateless HTTP services. If you haven't designed graceful drain and reconnection, your first deploy under load will teach you why you should have.
