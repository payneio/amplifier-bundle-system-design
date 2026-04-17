---
name: system-type-edge-offline
description: "Domain patterns for edge computing and offline-first systems — sync protocols, conflict resolution under partition, local-first architecture, constrained resources, intermittent connectivity, and failure modes. Use when designing or evaluating mobile apps, IoT systems, field-deployed software, or any system that must work without reliable network access."
---

# System Type: Edge & Offline-First

Patterns, failure modes, and anti-patterns for systems that operate under intermittent connectivity and constrained resources.

---

## 1. Offline-First Architecture

The fundamental assumption shift: the network is not a dependency — it is an optimization. An offline-first system is fully functional without connectivity and becomes better when connectivity is available. This is the opposite of how most systems are built, where the server is the source of truth and the client is a thin rendering layer that breaks the moment the network disappears.

### The Offline Spectrum

| Model | Description | Network requirement | Complexity | Example |
|---|---|---|---|---|
| **Online-only** | Server renders everything. Client is a viewport. | Continuous | Lowest | Traditional server-rendered web apps |
| **Offline-tolerant** | Works online, degrades gracefully offline. Shows cached data, queues writes. | Expected, with brief gaps | Low-medium | Gmail offline mode, Google Maps cached areas |
| **Offline-first** | Full functionality offline. Sync when connected. Network enhances, does not enable. | Optional, intermittent | High | Notion mobile, Field Service apps, CouchDB/PouchDB apps |
| **Local-only** | No server component. Data lives entirely on device. | None | Low (no sync) | Local note apps, single-player games, calculators |
| **Local-first** | Local-only experience with optional peer or cloud sync. User owns the data. | Optional, for collaboration | Highest | Automerge-based apps, Obsidian with sync, Linear's local model |

Most teams think they're building "offline-tolerant" but their users need "offline-first." The gap between those two is enormous — it's the difference between showing a spinner with "waiting for connection" and letting the user do their entire job on an airplane.

### Local-First as a Design Principle

Local-first means the device has a complete, usable copy of the data the user needs. Not a cache — a replica. The distinction matters:

- **Cache**: Server is authoritative. Cache is disposable. Stale cache means stale UI. Cache miss means broken feature.
- **Replica**: Device has a full copy. Local writes are first-class, not optimistic guesses. The device can operate indefinitely without the server. Sync is reconciliation between peers, not cache invalidation.

Design consequences of treating the device as a replica:

- The data model must be defined in terms of local operations, not server API calls.
- Every write must succeed locally before any network interaction.
- The UI must never show a loading state for data the user has already seen.
- Conflict resolution is a first-class design concern, not an edge case handler.

### Client-Side Storage

| Technology | Platform | Max storage | Strengths | Weaknesses |
|---|---|---|---|---|
| **SQLite** | iOS, Android, Desktop, WASM | Device storage | Full SQL, ACID transactions, mature tooling, single-file database | No built-in sync, schema migrations need care |
| **IndexedDB** | Web browsers | Varies (typically 50%+ of disk) | Async, transactional, structured data, available in service workers | Terrible API ergonomics (use a wrapper like Dexie.js), no SQL, browser eviction policies |
| **Realm** | iOS, Android, Web (partial) | Device storage | Object-oriented, live objects, built-in sync (MongoDB Atlas), reactive | Vendor lock-in to MongoDB ecosystem, schema constraints |
| **Core Data** | iOS, macOS | Device storage | Deep OS integration, CloudKit sync built-in | Apple-only, complex concurrency model, opaque conflict resolution |
| **OPFS (Origin Private File System)** | Web browsers | Varies | Fast synchronous file access in workers, good for WASM-based SQLite | Limited browser support, no structured query without SQLite on top |
| **MMKV / SharedPreferences / UserDefaults** | Mobile | Small (MB range) | Fast key-value access for config and small state | Not suitable for structured data, no query capability, no transactions |

**Practical guidance**: SQLite is the right default for anything beyond trivial key-value storage. It works everywhere (via WASM for browsers), has decades of battle-testing, and the tooling ecosystem is unmatched. Use a SQLite wrapper with migration support (Drizzle, Prisma with SQLite, Room on Android, GRDB on iOS). IndexedDB is acceptable for web-only applications where WASM SQLite is too heavy.

### Optimistic UI with Background Sync

The user performs an action. The UI updates immediately based on the local write. A background process syncs the change to the server when connectivity permits.

**The contract with the user:**

1. Your action is saved (locally). It will not be lost.
2. It will sync when a connection is available.
3. If there's a conflict, we will tell you (or resolve it automatically, depending on the data type).

**Implementation pattern:**

1. Write to local store. Assign a local operation ID.
2. Add to outbound sync queue (persistent — survives app restart).
3. Update UI from local store (not from the sync response).
4. Background sync process drains the queue when online.
5. On sync success: mark operation as synced, update local metadata (server-assigned IDs, timestamps).
6. On sync conflict: invoke conflict resolution strategy (see section 3).
7. On sync failure (non-conflict): retry with exponential backoff.

**The hard part**: Server-assigned IDs. If the server assigns the canonical ID for a resource, the local store has a temporary local ID until sync completes. Every reference to that resource (foreign keys, UI links, pending operations) must handle both local and server IDs. Solution: use client-generated UUIDs as the canonical ID, or maintain a local-to-server ID mapping table.

### Service Workers and Background Sync

On the web, service workers are the mechanism for offline capability:

- **Cache API**: Store HTTP responses for offline access. Use a cache-first strategy for static assets and a network-first strategy for API responses (falling back to cached).
- **Background Sync API**: Register sync events that fire when connectivity returns. Limited browser support and platform-specific restrictions (Android allows it, iOS Safari does not reliably fire background sync).
- **Periodic Background Sync**: Even more limited. Only available in installed PWAs with high engagement scores. Do not depend on it for critical sync.

The gap between the Background Sync API spec and reality is significant. On iOS, there is no reliable background sync for web apps — period. If your users are on iOS and need offline-first, you need a native app or a hybrid with native sync components.

---

## 2. Sync Protocols

Sync is the hardest part of offline-first systems. Getting data from device to server is easy. Getting data from device to server to other devices, bidirectionally, with conflicts, after arbitrary offline periods, without data loss — that's where the complexity lives.

### Sync Models

**Full sync (snapshot sync)**
On each sync, the server sends the complete current state. The client replaces its local data with the server's version.
- When to use: Small datasets (< 1MB), infrequent changes, when simplicity outweighs efficiency. Initial sync for a new device.
- When to avoid: Large datasets, frequent changes, metered connections. Transferring 50MB of data to sync a 100-byte change is not acceptable.

**Delta sync (state-based)**
Client sends its last-known version identifier. Server computes and sends only the changes since that version.
- When to use: Most CRUD applications. Document sync, contact sync, settings sync.
- Implementation: Maintain a `last_modified` timestamp or monotonic version counter per record. Server query: `WHERE updated_at > :client_last_sync`. Return changed and deleted records.
- Watch for: Deleted records must be tracked (soft deletes with tombstones) or the client will never know something was removed. Tombstones must eventually be garbage-collected, which means clients that haven't synced in longer than the tombstone retention period need a full resync.
- Clock skew: If using timestamps, server clock is authoritative. Never trust the client's clock for ordering. Use server-side `updated_at` assigned on receipt.

**Operation-based sync (event sourcing)**
Instead of syncing state, sync the operations that produced the state. The client sends "user added item X", "user changed field Y to Z". The server applies operations and forwards them to other clients.
- When to use: Collaborative editing, systems where the intent matters (not just the result), when you need undo/redo, when CRDTs are the underlying data model.
- When to avoid: Simple CRUD where state-based sync is sufficient. Operation logs grow without bound — you need compaction or snapshotting.
- The advantage: Operations carry intent. "Set price to $10" and "set price to $12" as operations can be conflict-resolved differently than two state snapshots showing $10 and $12.

### Sync Direction

**Unidirectional (server → client)**
Server is authoritative. Client is a read replica. Changes flow one way.
- When to use: Reference data distribution (product catalogs, price lists, configuration), content delivery, read-heavy mobile apps.
- Simplifies everything: no conflicts, no merge logic, no outbound queue. If you can make your system unidirectional, do it.

**Unidirectional (client → server)**
Client generates data. Server collects it. Data flows from edge to cloud.
- When to use: IoT telemetry, field data collection, sensor readings, analytics events.
- The server never pushes changes back. The client is authoritative for the data it generates.

**Bidirectional**
Both client and server can create and modify data. Changes flow in both directions.
- When to use: Collaborative applications, field service apps where both the field worker and the back office modify records.
- This is where all the hard sync problems live: conflicts, ordering, causality, merge semantics. If you can avoid bidirectional sync, avoid it. Most systems that think they need bidirectional sync actually need unidirectional-down for reference data and unidirectional-up for user-generated data, with a small bidirectional surface for shared mutable state.

### Sync Ordering and Causality

When multiple devices sync changes, the order matters. User A edits a document on their phone, then on their laptop. The phone syncs first. Then the laptop syncs. The laptop's changes should win because they happened later — but "later" is defined by the user's intent, not by which device had connectivity first.

**Vector clocks**: Each device maintains a counter per known device. On each local operation, increment your own counter. On receiving a sync, merge counters (take the max per device). Lets you determine if one version causally follows another or if they're concurrent.

**Hybrid Logical Clocks (HLC)**: Combine physical timestamps with logical counters. More compact than vector clocks. Provide causal ordering and approximate wall-clock time. Preferred for most practical sync systems.

**Lamport timestamps**: Provide total ordering but cannot distinguish causal relationships. Useful as a tiebreaker, not for causality.

**Practical approach**: Use HLCs for ordering within the sync protocol. Fall back to server-assigned sequence numbers for global ordering after sync. Don't trust device clocks — a user can set their phone's clock to 2030 and corrupt your ordering.

### Sync Protocol Design Decisions

**Push vs Pull vs Hybrid**
- Pull: Client polls the server for changes periodically. Simple, predictable, wasteful of battery and bandwidth on mobile.
- Push: Server notifies client of changes via push notification or persistent connection. Efficient but requires infrastructure (push notification services, WebSocket servers) and doesn't work offline.
- Hybrid: Push notification triggers a pull sync. The push says "there are changes," the pull fetches them. This is the standard pattern for mobile apps. The push is a hint, not the data delivery mechanism.

**Batching and pagination**: Sync responses must be paginated. A client that's been offline for six months cannot receive all changes in a single response — the response may be gigabytes. Page by version number or timestamp, with a reasonable page size (1000-5000 records). The client iterates pages until caught up.

**Compression**: Sync payloads should be compressed (gzip, brotli) at the transport layer. For operation-based sync, consider semantic compression: collapse "set field X to A, then to B, then to C" into "set field X to C" before transmission.

**Partial sync and subscriptions**: Not every device needs every record. Let clients subscribe to subsets of data (by project, by region, by assigned user). This reduces sync volume and local storage requirements. The subscription model must be part of the sync protocol — the server must track what each client is subscribed to and only send relevant changes.

---

## 3. Conflict Resolution Strategies

Conflicts are inevitable in offline-first systems. Two devices, both offline, both modifying the same data. When they sync, their changes disagree. The system must decide what to do, and "don't allow this to happen" is not a strategy — it's a denial of the system's fundamental operating conditions.

### When Conflicts Are Acceptable vs Catastrophic

This is the first question. The answer determines your entire conflict resolution architecture.

**Acceptable conflicts** — automatic resolution is fine:
- Two users update their own profile simultaneously → last-writer-wins per field.
- Two users add items to a shared shopping list → union merge (keep both).
- Two users edit different sections of a document → merge non-overlapping changes.
- Counter increments from multiple devices → CRDT counter (sum of increments).

**Catastrophic conflicts** — data integrity is paramount:
- Two doctors modify the same patient's medication dosage offline → user must review and choose.
- Two warehouse workers both reserve the last unit of inventory → one must be rejected.
- Two financial transactions modify the same account balance → must be serialized.
- Two approvers make contradictory approval decisions on the same request → domain logic must arbitrate.

If your domain has catastrophic conflicts, do not reach for automatic resolution. Surface the conflict to the user or the domain logic. Losing a shopping list item is annoying. Doubling a medication dosage is lethal.

### Last-Writer-Wins (LWW)

The simplest strategy. Compare timestamps (or version numbers) on conflicting writes. The most recent one wins. The other is discarded silently.

- **Per-record LWW**: The entire record is replaced by the most recent version. If user A changes the name and user B changes the address, and B's write is later, A's name change is lost even though it didn't conflict with B's change.
- **Per-field LWW**: Track timestamps per field. Merge by taking the most recent value for each field independently. User A's name change and user B's address change both survive. This is almost always what you want over per-record LWW.

**The fundamental limitation**: LWW silently discards data. It trades data loss for simplicity. Use it for low-stakes data where losing a concurrent write is acceptable. Never use it where the discarded write might have been important.

### CRDTs for Automatic Merge

CRDTs (Conflict-free Replicated Data Types) are data structures designed so that concurrent updates always converge to the same state, with no coordination required. They achieve this by constraining the set of allowed operations to those that commute.

**G-Counter (Grow-only Counter)**
Each device maintains its own count. The merged value is the sum of all device counts. Two devices each incrementing independently always converge. Cannot decrement.

**PN-Counter (Positive-Negative Counter)**
Two G-Counters: one for increments, one for decrements. The value is the sum of increments minus the sum of decrements. Supports both increment and decrement.

**G-Set (Grow-only Set)**
Elements can be added but never removed. Merge is union. Two devices adding different elements always converge.

**OR-Set (Observed-Remove Set)**
Elements can be added and removed. Each addition is tagged with a unique ID. A remove operation removes specific tagged additions. "Add wins over concurrent remove" semantic — if one device adds an element while another removes it, the add wins. This is usually the right semantic for user-facing sets (task lists, tag sets, collaborator lists).

**LWW-Register**
A single value with a timestamp. Last write wins. This is the CRDT equivalent of a per-field LWW.

**Text CRDTs (RGA, YATA, Fugue)**
Represent text as a sequence of uniquely identified characters with position metadata. Concurrent insertions and deletions at different positions commute. Concurrent insertions at the same position are ordered deterministically (by device ID tiebreaker).

Libraries: **Yjs** (JavaScript, performance-optimized, widely used), **Automerge** (JavaScript/Rust, richer data model, document-oriented), **Diamond Types** (Rust, high-performance text CRDT).

**CRDT tradeoffs:**
- Memory overhead is real. A 10KB text document may consume 100KB+ of CRDT metadata (character IDs, tombstones for deletions, vector clock data). For large documents, this metadata must be periodically compacted.
- CRDTs guarantee convergence, not user intent. Two users simultaneously replacing the title of a document will converge to one of them — but which one "wins" may not match either user's expectation. CRDTs resolve structural conflicts, not semantic ones.
- Not every data model maps cleanly to available CRDT types. If your domain has complex invariants (e.g., "these two fields must sum to 100"), CRDTs won't enforce them. You need application-level validation after merge.

### Application-Level Merge Rules

When CRDTs are too generic and LWW is too lossy, define merge rules specific to your domain:

- **Field-level merge with domain priority**: "If the status field conflicts, the value closer to 'completed' wins." Define a total ordering on field values and always resolve toward the 'forward' state.
- **Merge with tombstone protection**: "A deleted record cannot be resurrected by a stale offline device." If one device deletes a record and another modifies it, the delete wins. This prevents zombie records but can lose legitimate edits.
- **Additive merge**: "For list fields, take the union of both versions." Works for tags, attachments, comments — anything where both contributions should be preserved.
- **Domain-specific serialization**: "For inventory counts, reject the offline write and force a re-count." When the real-world state has moved on, the offline data is not just conflicting — it's wrong.

### User-Facing Conflict Resolution

When automatic resolution is inappropriate, surface the conflict to the user:

- **Show both versions side by side.** Let the user choose one or manually merge. This is the Git merge conflict model applied to application data.
- **Highlight conflicting fields.** Don't show the entire record as conflicting if only one field differs. Focus the user's attention on the actual disagreement.
- **Provide a default resolution.** "We chose the most recent version. Tap to review the other version." Most users will accept the default. Make it easy to override.
- **Queue conflicts for review.** Don't block the sync process on user resolution. Sync everything, mark conflicts, let the user resolve them asynchronously from a conflict queue.
- **Deadline for resolution.** If a conflict isn't resolved within N days, auto-resolve with the default strategy and notify the user. Unresolved conflicts that accumulate forever are a data integrity risk.

---

## 4. Constrained Resources

Edge devices are not servers. A server has 64GB of RAM, NVMe storage, and unlimited power. A mobile phone has 3-6GB of RAM (shared with every other app), flash storage with write amplification concerns, and a battery that the user expects to last all day. An IoT sensor may have 256KB of RAM and a coin-cell battery that must last years. Designing for constrained resources is not optimization — it's a fundamentally different set of engineering constraints.

### CPU and Processing Budgets

**Mobile OS background restrictions:**
- **iOS**: Background execution is heavily restricted. Apps get approximately 30 seconds of background time after entering the background. Background App Refresh is discretionary — the OS decides when (and if) to grant it. Background fetch is not guaranteed to fire. Long-running background tasks require specific entitlements (location, audio, VoIP, Bluetooth).
- **Android**: Doze mode and App Standby progressively restrict background activity. Jobs scheduled via WorkManager are batched by the OS to minimize wake-ups. Foreground services require a persistent notification. Android 12+ restricts foreground service launch from the background.

**Practical impact on sync:**
- You cannot assume your sync process will complete in the background. Design sync to be resumable — if the OS kills your process mid-sync, the next sync picks up where it left off.
- Batch operations aggressively. One sync session that processes 500 changes is better than 500 individual sync requests.
- Use OS-provided scheduling primitives (WorkManager on Android, BGTaskScheduler on iOS) instead of custom timers. The OS will defer your work, but it won't kill it unexpectedly.

**CPU-intensive operations at the edge:**
- Compression, encryption, and diff computation consume meaningful CPU. On a low-end Android device, compressing a 1MB payload takes noticeable time and drains battery.
- Move expensive computation off the main thread. Always. On mobile, blocking the main thread for >16ms causes visible frame drops. For sync, do all serialization, compression, and diffing on a background thread or worker.

### Memory Constraints

**Mobile memory pressure:**
- The OS can terminate background apps at any time to reclaim memory. On iOS, there is no warning — your process simply stops.
- Large in-memory data structures (full CRDT document state, large sync payloads) can trigger memory pressure and cause the OS to kill your app.
- Use streaming parsers for large sync responses. Don't deserialize a 50MB JSON payload into memory. Parse it incrementally and write records to local storage as they arrive.
- For CRDT-based systems, keep the in-memory working set small. Load document sections on demand. Persist CRDT state to disk and only hydrate the active portion.

**IoT memory constraints:**
- Devices with 64-256KB of RAM cannot hold complex data structures. Use fixed-size ring buffers for telemetry. Pre-allocate memory at boot. Avoid dynamic allocation in steady state.
- Protocol choice matters. MQTT is designed for constrained devices. HTTP with JSON is not — the parsing overhead alone may exceed available memory.

### Storage Quotas and Eviction

**Browser storage:**
- IndexedDB storage is subject to browser eviction policies. Under storage pressure, the browser may delete your data without warning (unless the user has granted persistent storage via `navigator.storage.persist()`). Always request persistent storage for offline-first web apps.
- Storage quotas vary by browser: Chrome grants up to 80% of total disk space per origin. Safari is more restrictive and may evict after 7 days of inactivity for non-installed web apps.

**Mobile storage:**
- Users with 32GB phones filled with photos and apps have very little free space. Your app's data must be a good citizen.
- Implement storage budgets: define a maximum local storage size per data type. When the budget is exceeded, evict the least-recently-used data, not the oldest data (the oldest data might be the most important).
- Separate "essential" data (user's own records, unsynced changes) from "cached" data (other users' data, reference data that can be re-downloaded). Never evict unsynced changes.

**Eviction strategies:**
- **LRU (Least Recently Used)**: Evict data the user hasn't accessed recently. Good default for cached data.
- **Priority-based**: Assign priority tiers. Evict low-priority data before high-priority data regardless of recency. Unsynced changes are never evictable.
- **TTL-based**: Data expires after a defined period. Simple for reference data that is periodically refreshed via sync.
- **Size-bounded with watermarks**: When storage exceeds the high watermark (e.g., 80% of budget), evict until reaching the low watermark (e.g., 60%). Prevents thrashing by creating headroom.

### Battery and Power

Battery drain from sync is one of the top reasons users uninstall apps.

**Radio power states**: The cellular radio has three states: idle (low power), connected (high power), and tail (intermediate — stays powered after transmission in case more data follows, typically 10-30 seconds). Each transition from idle to connected costs energy. Chatty sync (many small requests) is dramatically worse for battery than batched sync (fewer large requests) because of the radio tail.

**Practical battery conservation:**
- Batch outbound sync. Queue changes and send them in a single burst, not individually.
- Use push notifications to trigger sync instead of polling. Polling every 30 seconds keeps the radio in the connected/tail state permanently.
- Respect battery level. Throttle or skip non-critical sync when battery is below 20%. Never perform a full sync on low battery.
- Compress payloads. Less data transmitted means less radio time means less battery consumed.
- Defer non-urgent sync to when the device is charging and on Wi-Fi (WorkManager constraints on Android, BGProcessingTask on iOS).

### Data Compression and Transfer Optimization

- **Delta encoding**: Don't send the full record — send the diff. For structured data, send only changed fields. For text, send operational transforms or CRDT operations instead of full content.
- **Binary protocols**: Protobuf, MessagePack, or CBOR instead of JSON. A typical protobuf payload is 3-10x smaller than equivalent JSON. On metered connections, this matters.
- **Columnar compression**: For tabular data (sensor readings, log entries), columnar encoding (all timestamps together, all values together) compresses dramatically better than row-oriented encoding because adjacent values in a column tend to be similar.
- **Image and media optimization**: Sync thumbnails first, full resolution on demand. Never auto-sync original-resolution photos over cellular without explicit user consent.

---

## 5. Edge Computing Patterns

Edge computing is a spectrum from "device with local cache" to "autonomous compute node that operates independently for weeks." The right position on this spectrum depends on latency requirements, connectivity reliability, data volume, and regulatory constraints.

### Edge Node Roles

**Edge as cache**
The edge node holds a subset of cloud data for fast local access. All writes go to the cloud. The edge is a read replica with expiration policies.
- When to use: CDN-style content delivery, API response caching at the edge, read-heavy applications where latency matters but data freshness tolerance is seconds to minutes.
- The simplest edge pattern. No conflict resolution needed. Cache invalidation is the only hard problem (and it's still hard).

**Edge as compute**
The edge node processes data locally — filtering, aggregating, transforming — before sending results to the cloud. Raw data stays at the edge; derived data goes up.
- When to use: IoT data reduction (a sensor generating 1000 readings/second sends 1 summary/minute to the cloud), privacy-sensitive processing (PII is processed at the edge and only anonymized results go to the cloud), latency-sensitive computation (real-time anomaly detection on a factory floor).
- The key decision: what computation runs at the edge vs the cloud. Push computation to the edge when: the data volume is too large to send raw, latency to the cloud is too high for the use case, or regulatory requirements demand local processing.

**Edge as autonomous unit**
The edge node makes decisions independently. It has its own business logic, its own data store, and operates without cloud connectivity for extended periods. It syncs with the cloud when convenient.
- When to use: Field-deployed systems (military, mining, maritime), retail point-of-sale (must work during internet outages), medical devices in rural clinics, autonomous vehicles.
- The most complex edge pattern. Requires full offline-first architecture, local decision-making authority, and eventual reconciliation with cloud state.

### Hierarchical Edge Topologies

Real-world edge deployments are rarely flat (device ↔ cloud). They're hierarchical:

```
Device → Gateway → Regional Edge → Cloud
```

- **Device**: Sensor, mobile app, embedded system. Minimal compute. May not have direct internet access.
- **Gateway**: Aggregates data from many devices. Runs on more capable hardware (Raspberry Pi, industrial PC, edge server). Has local storage and processing capability. May connect to the internet intermittently.
- **Regional Edge**: Data center-lite at the network edge (cell tower, ISP facility, factory server room). Significant compute and storage. Reliable connectivity to the cloud but may still need to operate during cloud outages.
- **Cloud**: Full data center. Unlimited compute and storage. Global coordination and analytics.

Each layer in the hierarchy serves as a sync boundary. Devices sync with their gateway. Gateways sync with the regional edge. Regional edges sync with the cloud. This reduces the blast radius of connectivity failures — a device losing connectivity doesn't affect cloud sync if the gateway is still connected.

**Practical considerations:**
- Each layer must be able to operate independently for its expected offline duration. A gateway that only works when connected to the regional edge is not an edge node — it's a proxy.
- Data transformation happens at each layer. Devices send raw readings. Gateways aggregate to minute-level summaries. Regional edges compute hourly statistics. The cloud stores everything but primarily works with pre-aggregated data.
- Deployment and updates must cascade through the hierarchy. You can't SSH into 10,000 field devices. Push updates to gateways; gateways push to devices during their next local sync.

### Edge ML Inference

Running machine learning models at the edge avoids the latency and connectivity requirements of cloud inference.

- **Model formats**: TensorFlow Lite (mobile/embedded), Core ML (Apple devices), ONNX Runtime (cross-platform), TensorRT (NVIDIA edge devices). Models must be quantized and optimized for the target hardware.
- **Model updates**: Ship new models via the sync mechanism. The device downloads the model, validates it (checksum, test inference), and hot-swaps it. Never leave the device without a working model during an update — keep the previous model as a fallback.
- **Resource budgets**: Edge inference competes with the application for CPU, memory, and battery. Set inference frequency limits. A classification model running on every camera frame at 30fps will drain the battery in an hour. Run inference at 1-5fps and interpolate between results.
- **Fallback behavior**: Define what the system does when the model's confidence is low or when inference fails. Degrade to rule-based heuristics, queue the input for cloud inference later, or surface uncertainty to the user. Never silently act on low-confidence predictions.

### Edge-to-Cloud Data Flow

**Data gravity**: Data accumulates at the edge faster than it can be uploaded. A single camera generates 1-5 Mbps of video. A fleet of 1000 vehicles generates terabytes per day. You cannot upload all of it.

**Strategies:**
- **Filter at the edge**: Only send interesting data. A security camera sends frames only when motion is detected. A vehicle sends telemetry only during anomalous events. Define "interesting" at the edge — this is where edge ML inference earns its value.
- **Aggregate at the edge**: Send summaries instead of raw data. Temperature readings every second become min/max/average per minute. This is lossy but practical.
- **Tiered upload**: Send metadata immediately (event detected, summary statistics). Upload raw data later when on Wi-Fi or when specifically requested from the cloud.
- **Edge data retention**: Keep raw data at the edge for a defined retention period (7 days, 30 days) for local query and forensic analysis. Evict after retention expires or when storage is full.

---

## 6. Connectivity Patterns

Connectivity is not binary. It's not "online" or "offline." It's a spectrum that changes continuously, and your system must handle every point on that spectrum gracefully.

### Connection State Machine

```
    ┌──────────┐
    │  ONLINE  │ ← Full connectivity, low latency, high bandwidth
    └────┬─────┘
         │ degradation detected (high latency, packet loss)
         ▼
    ┌──────────────┐
    │   DEGRADED   │ ← Partial connectivity: high latency, intermittent drops, low bandwidth
    └──────┬───────┘
           │ connection lost
           ▼
    ┌──────────────────┐
    │  TRANSITIONING   │ ← Brief window: might recover, might not. Don't panic yet.
    └──────┬───────────┘
           │ timeout exceeded
           ▼
    ┌──────────┐
    │ OFFLINE  │ ← No connectivity. Operate locally.
    └──────────┘
```

**Why four states, not two:**
- **ONLINE → OFFLINE** with no intermediate state causes thrashing. A momentary network glitch triggers offline mode, queues operations, then connectivity returns 2 seconds later and triggers a sync storm. The TRANSITIONING state absorbs brief interruptions (3-10 second window before committing to OFFLINE).
- **DEGRADED** is operationally distinct from both ONLINE and OFFLINE. On a degraded connection, you can sync — but slowly. Send critical data only. Defer large payloads. Don't attempt full sync. Don't show "you're offline" to the user — show "sync may be delayed."

**Detection mechanisms:**
- **Network reachability APIs** (e.g., `navigator.onLine`, iOS `NWPathMonitor`, Android `ConnectivityManager`): Tell you if a network interface is available, not if the server is reachable. A device connected to a captive portal Wi-Fi has a network interface but no server connectivity. Never use reachability alone.
- **Application-level heartbeat**: Periodic lightweight request to your server (HEAD request, ping endpoint). If it succeeds, you're online. If it fails or times out, you're degraded or offline. This is the only reliable signal.
- **Adaptive timeout**: Short heartbeat interval (15s) when online to detect degradation quickly. Longer interval (60s+) when offline to conserve battery. Increase interval progressively the longer you've been offline.

### Queue-and-Retry for Writes

Every write that occurs offline must be queued and retried when connectivity returns.

**Queue requirements:**
- **Persistent**: The queue must survive app restarts and device reboots. Use SQLite or a file-backed queue. In-memory queues lose data on crash.
- **Ordered**: Operations must be replayed in the order they were performed. An "update" before the "create" was synced will fail.
- **Idempotent replay**: The server must handle duplicate submissions (client retries after timeout, but the first attempt actually succeeded). Use client-generated idempotency keys on every queued operation.
- **Bounded**: Set a maximum queue size. When the queue is full, the user must be informed that new actions cannot be saved until sync clears some space. This is rare but must be handled — a field worker offline for a week generating thousands of operations can fill any queue.

**Retry strategy:**
- Exponential backoff with jitter: 1s, 2s, 4s, 8s, ... capped at 5 minutes. Jitter prevents thundering herd when many devices regain connectivity simultaneously.
- Distinguish retriable from non-retriable errors. A 500 is retriable. A 409 (conflict) needs conflict resolution. A 422 (validation error) means the operation cannot succeed as-is and should be flagged for user review.
- Batch retry: When connectivity returns, don't send queued operations one at a time. Batch them into a single sync request. This reduces round-trips and radio wake-ups.

### Priority-Based Sync

Not all data is equally urgent. Define sync priorities:

| Priority | Examples | Sync behavior |
|---|---|---|
| **Critical** | Financial transactions, safety alerts, medication changes | Sync immediately on any connectivity, retry aggressively |
| **High** | User-facing data changes, shared state updates | Sync on stable connection, retry with standard backoff |
| **Normal** | Background data, reference data updates | Sync when convenient, batch with other operations |
| **Low** | Analytics events, usage telemetry, log uploads | Sync only on Wi-Fi + charging, drop if queue is full |

The sync queue should be a priority queue, not FIFO. When connectivity is intermittent, ensure critical operations go first. A 30-second connectivity window should sync the medication change, not yesterday's telemetry logs.

### Bandwidth-Aware Behavior

Detect and adapt to available bandwidth:

- **Connection type detection**: Distinguish Wi-Fi from cellular (4G/5G/3G). Many mobile APIs expose connection type. Use it to decide sync aggressiveness.
- **Adaptive payload size**: On low bandwidth, send smaller sync pages (100 records instead of 1000). On high bandwidth, send larger pages.
- **Progressive data loading**: Sync metadata first, then content. A field service app syncs work order headers (100 bytes each) before syncing attached photos (5MB each). The user can start working immediately with headers while photos load in the background.
- **User-controlled sync**: Let the user decide. "Sync photos only on Wi-Fi" is a setting, not an engineering decision. Provide sensible defaults but respect user preference.

### Mesh Networking Between Edge Devices

When cloud connectivity is unavailable, devices can sync with each other directly:

- **Bluetooth Low Energy (BLE)**: Short range (10-30m), low bandwidth (1-2 Mbps theoretical, much less in practice), good battery characteristics. Suitable for small data exchange between nearby devices.
- **Wi-Fi Direct / Wi-Fi Aware**: Medium range, higher bandwidth (50+ Mbps). Devices form an ad-hoc network without an access point. Suitable for larger data exchange.
- **Local network (mDNS/Bonjour)**: When devices are on the same LAN (even without internet access), they can discover and sync with each other via mDNS service discovery.

**Mesh sync considerations:**
- Trust model: Which devices are trusted to provide data? In a peer-to-peer sync, a compromised device can inject bad data into the mesh. Use signed operations or certificate-based device authentication.
- Conflict amplification: Peer-to-peer sync can create complex multi-way conflicts that are harder to resolve than simple client-server conflicts. Prefer a gossip protocol with causal ordering (vector clocks) to maintain convergence.
- Topology changes: Devices enter and leave the mesh constantly. The sync protocol must handle partial connectivity gracefully — not every device can reach every other device.

---

## 7. Security at the Edge

Every device you deploy is a device you don't physically control. It's in someone's pocket, on someone's factory floor, in someone's home. The threat model expands from "protect the server" to "protect the server, the device, the data at rest on the device, the data in transit, and the sync protocol — from the device's own user, from other users on the same network, and from anyone who picks up the device."

### Authentication Without Server Contact

The user must be able to authenticate and use the app offline. But the server is the authority on identity. This creates a fundamental tension.

**Cached tokens:**
- On successful online authentication, cache a token (JWT, opaque session token) locally with an expiration time.
- While offline, the cached token authorizes local operations. The device trusts the token until it expires.
- Token lifetime is a tradeoff: long-lived tokens (30 days) mean the user rarely hits an auth wall offline, but a revoked user retains access for up to 30 days. Short-lived tokens (1 hour) mean better revocation but frequent auth failures for offline users.
- Practical approach: Use a refresh token (long-lived, stored securely) and an access token (short-lived). When the access token expires, attempt a refresh. If offline, extend the access token's validity locally for a defined grace period (24-72 hours). Log this extension so the server can audit it post-sync.

**Certificate-based authentication:**
- Issue a client certificate per device during enrollment. The certificate proves device identity without contacting a server.
- Revocation checking (CRL, OCSP) requires server contact. For offline operation, use short-lived certificates (days to weeks) and renew them during sync windows. An expired certificate means the device must connect to re-authenticate.
- Stronger than cached tokens for device identity. Commonly used in IoT and enterprise MDM deployments.

**Biometric / PIN as local gate:**
- Use device biometrics (fingerprint, face) or a PIN to unlock the app locally. This doesn't authenticate the user to the server — it authenticates the user to the device.
- Pair with cached credentials: biometric unlocks the keychain, keychain provides the cached auth token.
- Defense in depth: even if someone steals the cached token file, they can't use the app without biometric authentication.

### Authorization Decisions with Stale Data

Offline authorization is inherently stale. The user's permissions may have changed on the server since the last sync.

**Strategies:**
- **Cache permissions with data**: When syncing, include the user's current permission set. Enforce locally based on cached permissions. Accept that permissions may be stale by up to one sync interval.
- **Permissive offline, strict on sync**: Allow broader actions offline. Validate all offline actions against current permissions when syncing. Reject unauthorized actions at sync time and notify the user.
- **Conservative offline, graceful upgrade**: Restrict offline capabilities to a safe subset. When connectivity returns, upgrade to full permissions. This prevents unauthorized offline actions but reduces offline utility.

The right choice depends on risk tolerance. A field service app might use permissive-offline (let the worker do their job, sort out permissions later). A medical records app might use conservative-offline (only allow read access to existing records, no new prescriptions without server validation).

### Secure Local Storage

Data at rest on the device is vulnerable to physical access, malware, and forensic extraction.

**Mobile platform security:**
- **iOS Keychain**: Hardware-backed secure storage for credentials and small secrets. Encrypted at rest, access-controlled by the app's entitlements. Use for auth tokens, encryption keys, and certificates. Not suitable for bulk data.
- **Android Keystore**: Hardware-backed key storage (on devices with TEE/Strongbox). Generates and stores cryptographic keys that cannot be extracted. Use for encrypting local databases.
- **Encrypted databases**: SQLCipher (encrypted SQLite), Realm encryption. Encrypt the entire local database at rest using a key stored in the platform keychain/keystore.

**Key management:**
- Never hardcode encryption keys. Derive them from platform-secured storage or user credentials.
- Key rotation: When you rotate encryption keys (e.g., after a suspected compromise), you must re-encrypt the local database. This is expensive on large databases — design for it being a background operation.
- Data wipe capability: Implement remote wipe. On the next sync (or via push notification), the device erases all local data and requires re-authentication. This is essential for enterprise deployments where devices are lost or employees are terminated.

### Device Attestation

How does the server know the device is legitimate and not a modified client?

- **Platform attestation APIs**: Android SafetyNet/Play Integrity, iOS DeviceCheck/App Attest. These cryptographically attest that the app is running on a genuine device, unmodified, from the official app store.
- **Limitations**: Attestation proves the device and app binary are genuine at a point in time. It does not prove the device hasn't been modified since attestation, and it does not prevent a genuine device from being used maliciously.
- **When to require it**: Financial transactions, healthcare data access, any scenario where a modified client could cause real harm. Don't require it for every request — attestation calls add latency and have rate limits.

### The Expanded Attack Surface

Distributed edge deployments expand the attack surface compared to a centralized server:

- **Physical access to devices**: An attacker with physical access to a device can extract storage, intercept network traffic, and modify the application. Assume physical compromise is possible. Encrypt everything at rest. Use certificate pinning to prevent MITM. Don't store secrets that can be reused on other devices.
- **Sync protocol as attack vector**: A compromised device can inject malicious data through the sync protocol. Validate all synced data on the server with the same rigor as API input validation. A client claiming to be device A sending data for device B should be rejected.
- **Side-channel through sync patterns**: Sync timing and volume can reveal information. An observer monitoring network traffic can infer activity patterns (e.g., "a medical app syncing at 2 AM means a patient event occurred"). Use constant-rate sync or padding to mitigate if side-channel leakage is a concern.
- **Offline replay attacks**: A device that's been offline records a valid transaction. The user then performs the same transaction online (via a different device). The offline device syncs and replays the transaction. Idempotency keys prevent literal replays, but semantic replays (two identical but intentional transactions) need domain-level deduplication.

---

## 8. Common Failure Modes

These are not edge cases — they are the normal operating conditions of offline-first systems. Every system that runs at the edge will encounter all of these.

### Sync Conflicts After Long Offline Periods

**What happens**: A device is offline for days or weeks. During that time, other devices have synced hundreds of changes. When the long-offline device finally syncs, it has a massive batch of outbound changes that conflict with the current server state.

**Why it's hard**: The offline device's local state has diverged significantly from the server's state. Individual conflicts might be resolvable, but the cumulative effect of many small conflicts can produce a state that makes no sense. A field worker who reassigned 50 tasks offline, while the dispatcher also reassigned those same 50 tasks, creates a combinatorial conflict nightmare.

**Mitigation**: Set a maximum offline duration per data type. If the device has been offline longer than the threshold, flag the entire sync as "stale" and require manual review rather than attempting automatic resolution. Warn the user ("You've been offline for 14 days — some of your changes may conflict with updates from the team.") before syncing.

### Storage Exhaustion on Device

**What happens**: The device runs out of local storage. The sync queue can't accept new operations. Local writes fail. The app becomes unusable.

**Why it's hard**: You can't predict device storage — the user's photo library, other apps, and OS updates all compete for space. Your app may have plenty of allocated storage one day and hit quota the next.

**Mitigation**: Monitor local storage usage proactively. Warn when approaching limits (80% of budget). Implement progressive eviction of cached (re-downloadable) data before the user hits the wall. Never lose unsynced data — that is always the highest priority for retention. If storage is critically low, offer the user a "sync now to free space" action that uploads unsynced data and then evicts the synced copies.

### Split-Brain Between Edge Nodes

**What happens**: Two edge nodes (gateways, regional servers) that normally sync with each other lose connectivity between them. Each continues to accept writes and make decisions independently. When connectivity is restored, their states have diverged.

**Why it's hard**: This is the CAP theorem in practice. During the partition, each node chose availability over consistency. Now you must reconcile two potentially contradictory sets of decisions. Inventory was allocated on both nodes. Appointments were booked in the same slot by both nodes. Work orders were assigned to different workers by each node.

**Mitigation**: Design for partition from the start. Use CRDTs or domain-specific merge rules for data that both nodes can modify. For data where split-brain is catastrophic (inventory, booking), pre-allocate partitioned budgets — each node gets a quota it can allocate independently, and quotas are reconciled and rebalanced when connectivity returns.

### Stale Cached Data Causing Wrong Decisions

**What happens**: An edge device makes a decision based on locally cached data that is no longer accurate. A field worker dispatches to a location that was reassigned two hours ago. A medical device administers a dose based on a patient record that was updated at the hospital.

**Why it's hard**: The device doesn't know its data is stale. From its perspective, the data is the latest it has. The user trusts the device and acts on what they see.

**Mitigation**: Display data freshness prominently. "Last synced: 3 hours ago" is essential context for the user. For critical decisions, require a sync check before acting — "This record is 6 hours old. Sync before proceeding?" For safety-critical domains, enforce a maximum data age beyond which certain operations are blocked until a fresh sync is completed.

### Battery Drain from Aggressive Sync

**What happens**: The sync mechanism is too aggressive — polling too frequently, retrying too fast, keeping the radio active. Users complain about battery drain and uninstall the app.

**Why it's hard**: Sync frequency is a direct tradeoff with data freshness. Product managers want "real-time sync." Users want "all-day battery." You can't have both.

**Mitigation**: Measure sync energy impact explicitly (Android Battery Historian, iOS Energy Log). Set a sync energy budget. Use push notifications to trigger sync instead of polling. Respect OS-level battery saving modes. Provide user-visible sync frequency controls ("Real-time / Hourly / Manual only"). Default to the least aggressive option that still meets the product's core use case.

### Data Loss from Failed Sync Recovery

**What happens**: A sync attempt partially succeeds — some records sync, some fail. The recovery logic has a bug. On retry, the already-synced records are re-sent (duplicates), while the failed records are dropped from the queue (data loss). Or worse: the recovery logic interprets a partial failure as a complete success and clears the entire queue.

**Why it's hard**: Sync recovery is the most complex and least-tested code path. It handles the combination of partial success, network failure, timeout, and server error — states that are difficult to reproduce in testing.

**Mitigation**: Use a transactional outbox pattern. Queue entries are only removed after server-side confirmation. Implement sync reconciliation: after each sync session, compare the local outbox with the server's received operations. Flag discrepancies. Test sync failure recovery explicitly — kill the network mid-sync, corrupt responses, simulate server timeouts — and verify that no queued operations are lost.

### Version Skew Between App and Server API

**What happens**: The server API is updated. Some devices have the new app version (which speaks the new API). Other devices are running the old app version (which speaks the old API). During the transition, both versions are syncing simultaneously.

**Why it's hard**: You don't control when users update their apps. On mobile, some users disable auto-update. Enterprise devices may be on managed update cycles weeks behind the latest release. You must support at least two API versions simultaneously, sometimes more.

**Mitigation**: Version the sync API explicitly (`/sync/v2`, `/sync/v3`). The server must support all API versions that are still in use by active devices. Track the distribution of client versions — monitor what percentage of sync traffic comes from each version. Define a deprecation policy: support old versions for N months after the new version is released, with a forced-update prompt for clients on deprecated versions. Design sync payload schemas to be backward-compatible — add fields, don't remove or rename them.

---

## 9. Anti-Patterns

**"Server-required architecture with offline bolted on."** The system was designed assuming always-on connectivity. Offline support was added as an afterthought by caching API responses and queuing failed requests. The result: every feature works slightly differently offline, some features don't work at all, conflict handling is inconsistent, and the sync logic is scattered across dozens of ad-hoc retry wrappers. Offline-first is an architecture, not a feature flag. Retrofitting it is as expensive as rebuilding.

**"Sync everything always."** Every record synced to every device regardless of whether the device needs it. A mobile app for a field technician downloads the complete customer database of 2 million records. Storage fills up. Sync takes 30 minutes on 3G. Battery drains. The technician only ever needs their 50 assigned work orders. Sync what the device needs, not what the server has. Use subscription-based sync with explicit scoping.

**"Conflict avoidance instead of conflict resolution."** Designing around the assumption that conflicts won't happen — by locking records during offline access, or by restricting each record to a single editor. This cripples the offline experience. If two field workers can't independently update the same work order offline, one of them must wait for connectivity. The result is "offline-first in theory, online-required in practice." Embrace conflicts. Design resolution strategies. Users can handle "your change conflicted with Sarah's — here's what happened" far better than they can handle "you can't edit this because someone else might be editing it."

**"Treating edge as thin client."** Using the edge device as a rendering layer that calls APIs for every interaction. When the API is unreachable, the device is a brick. Edge devices must have local state, local business logic, and local decision-making authority proportional to their expected offline duration. A field device that must be online to look up a customer name has failed at edge computing.

**"Ignoring the sync queue as a persistence concern."** Storing the outbound sync queue in memory, in localStorage with no error handling, or in a way that doesn't survive app restarts. The sync queue is the most important data structure in an offline-first app — it contains the user's unsaved work. Treat it with the same care as a database write-ahead log. It must be persistent, crash-safe, and bounded.

**"Timestamps as the source of truth for ordering."** Relying on device clocks to order operations. Device clocks are wrong. Users change them. Time zones cause confusion. A device set to a future date will produce operations that "win" every LWW conflict for years. Use logical clocks (HLC, vector clocks) for ordering. Use server-assigned timestamps only after sync.

**"Full resync as the error recovery strategy."** When sync fails or gets confused, delete all local data and re-download everything. This is the "rm -rf and re-clone" of offline-first systems. It works, but it's expensive (bandwidth, time, battery), it loses unsynced local data if the outbox wasn't flushed first, and it trains users to distrust the app's offline capability. Invest in incremental sync recovery. Full resync is the last resort, not the first response.

**"Optimistic UI without a reconciliation path."** Showing the user an optimistic update and then having no plan for what happens when the server disagrees. The UI said "saved!" but the server rejects the write 20 minutes later. Now the user's local state and the server state have diverged, and the user doesn't know. Every optimistic update needs a reconciliation path: what happens if the server rejects it, what the user sees, and how local state is corrected.

**"Testing only the happy path of sync."** Testing sync with two devices, both online, making small non-conflicting changes. The real failure modes are: ten devices, three of them offline for different durations, all modifying overlapping data, one running an old app version, one with a nearly full disk, and one that loses connectivity mid-sync. If your sync tests don't include failure injection, they don't test sync.

**"One-size-fits-all sync frequency."** Syncing all data types at the same frequency. Critical safety alerts synced on the same schedule as usage telemetry. Background photos synced with the same urgency as work order status updates. Different data has different urgency, different size, and different conflict sensitivity. Use tiered sync priorities and let each data type define its own sync characteristics.
