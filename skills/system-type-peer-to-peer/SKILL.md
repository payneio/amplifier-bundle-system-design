---
name: system-type-peer-to-peer
description: "Domain patterns for peer-to-peer system architecture — network topologies, NAT traversal, peer discovery, data distribution, consistency without central authority, identity and trust, and incentive mechanisms. Use when designing or evaluating a decentralized, peer-to-peer, or mesh-networked system."
---

# System Type: Peer-to-Peer (P2P)

Patterns, failure modes, and anti-patterns for decentralized peer-to-peer systems.

---

## Network Topologies

### Unstructured (Gossip / Flood)
**When to use.** Systems where any peer can hold any data and queries are exploratory — file sharing (early Gnutella), social feeds, informal mesh networks. When simplicity and resilience to churn matter more than lookup efficiency.
**When to avoid.** Systems that need efficient key-based lookups. Large networks where flooding creates unacceptable bandwidth overhead. When query latency must be predictable.
**Key decisions.** TTL (time-to-live) on forwarded messages, fanout degree (how many peers each node forwards to), duplicate message suppression, supernode election for partial structure.

### Structured (DHT)
**When to use.** Efficient key-value lookups in a decentralized network — content-addressable storage, distributed hash tables (Kademlia, Chord, Pastry). When you need O(log n) lookups instead of flooding.
**When to avoid.** When keyword search or range queries are needed (DHTs only do exact key lookup). When the network has extremely high churn (DHT routing tables become stale faster than they can repair). Very small networks where the DHT overhead exceeds the benefit.
**Key decisions.** Hash function and key space design, replication factor (k-bucket size in Kademlia), routing table refresh strategy, handling network partitions and merges, iterative vs recursive lookup.

### Hybrid (Super-Peer / Tracker-Assisted)
**When to use.** When pure decentralization is a goal but some coordination is practical — BitTorrent (trackers + DHT), Skype's original architecture, many production P2P systems. Super-peers handle discovery and coordination; regular peers handle data transfer.
**When to avoid.** When the super-peers become single points of failure that negate the decentralization benefit. When regulatory requirements demand fully decentralized operation.
**Key decisions.** Super-peer election and rotation, fallback when super-peers fail, load balancing across super-peers, preventing super-peer capture or censorship, graceful degradation to pure P2P when coordination layer fails.

### Mesh (Full / Partial)
**When to use.** Local-area networks, IoT device clusters, real-time collaboration with small groups. When peers need direct, low-latency communication and the group size is bounded.
**When to avoid.** Large networks — full mesh is O(n^2) connections. Wide-area networks where direct connections between all peers are impossible.
**Key decisions.** Mesh density (full vs partial), relay selection for peers that can't connect directly, mesh topology maintenance, partition detection and healing.

## NAT Traversal and Connectivity

### STUN (Session Traversal Utilities for NAT)
**When to use.** Discovering your public IP and port mapping when behind a NAT. The first step in establishing direct peer connections. Works for most consumer NATs (cone NATs).
**When to avoid.** Symmetric NATs, which assign different external ports per destination — STUN alone can't traverse these. Enterprise firewalls that block UDP entirely.
**The hard part.** STUN servers must be publicly reachable. You need fallback for the ~8-15% of networks where STUN fails.

### TURN (Traversal Using Relays around NAT)
**When to use.** Fallback when direct connection is impossible — symmetric NATs, restrictive firewalls, corporate networks. All traffic relays through a TURN server.
**When to avoid.** As a primary strategy — TURN servers are expensive (they relay all traffic) and add latency. Use only when STUN and hole punching fail.
**Key decisions.** TURN server provisioning and cost (bandwidth is proportional to usage), geographic distribution for latency, credential rotation, capacity planning for peak concurrent relayed connections.

### ICE (Interactive Connectivity Establishment)
**When to use.** The standard framework for trying multiple connectivity methods in order — direct connection, STUN, TURN — and selecting the best one. Used by WebRTC. The right default for any new P2P connection system.
**When to avoid.** Systems where you control both endpoints and the network (e.g., data center to data center) — ICE's complexity isn't needed.
**Key decisions.** Candidate gathering timeout (waiting too long delays connection; too short misses viable paths), aggressive vs regular nomination, trickle ICE for faster initial connection, handling ICE restart on network change.

### Hole Punching (UDP and TCP)
**When to use.** Establishing direct connections through NATs by coordinating simultaneous outbound connections from both peers. Works for most cone-type NATs. Essential for keeping TURN costs down.
**When to avoid.** Can't rely on it exclusively — success rate varies by NAT type (works ~80% of the time for UDP, ~60% for TCP in practice).
**The hard part.** Requires a rendezvous server to coordinate the punch. Timing is critical — both sides must send within a narrow window. TCP hole punching is less reliable than UDP due to the three-way handshake. Some NAT devices randomize port mappings, defeating the technique.

## Peer Discovery

### Bootstrap Nodes
**When to use.** The initial entry point for new peers joining the network. Every P2P system needs at least one discovery mechanism for the first connection. Bootstrap nodes are well-known, stable peers that provide initial routing information.
**When to avoid.** As the only discovery mechanism — bootstrap nodes are centralized points that can be blocked or taken down.
**Key decisions.** Number and geographic distribution of bootstrap nodes, hardcoded vs DNS-based discovery, fallback when all bootstrap nodes are unreachable, rate limiting to prevent abuse.

### mDNS / Local Discovery
**When to use.** Finding peers on the same local network without any server infrastructure. LAN gaming, local file sharing, IoT device pairing. Works even when the internet is unavailable.
**When to avoid.** Cross-network discovery. Networks where multicast is disabled (many enterprise networks, most cloud VPCs).
**Key decisions.** Service type naming, conflict resolution when multiple instances exist, discovery refresh interval, privacy implications of announcing presence on the local network.

### DHT-Based Discovery
**When to use.** Decentralized discovery once the peer has joined the network. Peers publish their addresses under known keys; other peers look them up. Combines with bootstrap nodes — bootstrap gets you into the DHT, DHT handles ongoing discovery.
**When to avoid.** When the DHT itself is not yet bootstrapped (chicken-and-egg problem). Very small or ephemeral networks where DHT maintenance overhead exceeds the benefit.
**Key decisions.** Key design for peer records, record TTL and refresh, Sybil resistance in the DHT, handling peers behind NAT (store relay addresses, not direct addresses).

### Peer Exchange (PEX)
**When to use.** Peers share their known peer lists with each other. Reduces load on bootstrap nodes and trackers. BitTorrent uses this extensively — once connected to a few peers, you learn about more through gossip.
**When to avoid.** When peer identity is sensitive (PEX reveals who knows whom). When Sybil attacks are a concern (a malicious peer can flood the network with fake peer addresses).
**Key decisions.** Rate limiting peer exchange, validation of received addresses, preference for recently-seen peers, mixing PEX with other discovery mechanisms for resilience.

## Data Distribution

### Content-Addressable Storage (CAS)
**When to use.** When data integrity is paramount — files are addressed by the hash of their content. IPFS, Git, Nix, Docker image layers. Enables deduplication, caching, and verification without trusting the source.
**When to avoid.** Mutable data that changes frequently — each change produces a new address, requiring indirection (naming systems, mutable pointers) to track the latest version.
**Key decisions.** Hash algorithm (SHA-256 is standard; avoid MD5/SHA-1), chunk size for large files, Merkle tree structure (determines parallel verification and partial downloads), garbage collection of unreferenced content.

### BitTorrent-Style Swarming
**When to use.** Distributing large files to many recipients simultaneously. Each downloader becomes an uploader, distributing the bandwidth cost across the swarm. Scales better with more peers.
**When to avoid.** Small files (the coordination overhead exceeds the benefit). Real-time streaming where pieces must arrive in order. When upload bandwidth is extremely constrained on most peers.
**Key decisions.** Piece size (too small increases metadata overhead; too large reduces parallelism), piece selection strategy (rarest-first to maximize availability), choking/unchoking algorithm for fairness, endgame mode for the last few pieces.

### Gossip Protocols (Epidemic Dissemination)
**When to use.** Disseminating updates across a large, loosely-connected network where guaranteed delivery isn't critical — membership lists, configuration updates, eventually-consistent state. Simple, robust, and tolerant of failures.
**When to avoid.** When strong consistency or ordering guarantees are needed. When message volume is high (gossip amplifies each message by the fanout factor).
**Key decisions.** Fanout degree, push vs pull vs push-pull, message deduplication, crashing vs byzantine fault assumption, convergence time estimation, protocol period.

### Pub/Sub over P2P (GossipSub, FloodSub)
**When to use.** Topic-based message distribution without a central broker — decentralized social feeds, blockchain transaction propagation, collaborative editing. GossipSub (used by libp2p/Ethereum) adds mesh structure to reduce bandwidth.
**When to avoid.** When message ordering is critical (P2P pub/sub is typically unordered or partially ordered). When message loss is unacceptable without additional reliability layers.
**Key decisions.** Topic design and subscription management, mesh degree (D parameter in GossipSub), message validation before forwarding, score-based peer selection for reliability, flood publish for high-priority messages.

## Consistency Without Central Authority

### Conflict-Free Replicated Data Types (CRDTs)
**When to use.** Concurrent editing without coordination — collaborative documents, shared counters, distributed sets. CRDTs guarantee convergence regardless of message ordering or network partitions.
**When to avoid.** When the data model doesn't map to known CRDT types. When the metadata overhead (vector clocks, tombstones) exceeds the data size. When "last writer wins" is actually acceptable.
**Key decisions.** CRDT type selection (G-Counter, PN-Counter, LWW-Register, OR-Set, RGA for sequences), compaction strategy for metadata growth, tombstone garbage collection, integration with persistence layer.

### Vector Clocks and Causal Ordering
**When to use.** Tracking causality between events in a distributed system — knowing that event A happened before event B, or that they're concurrent. Essential for conflict detection in eventually-consistent systems.
**When to avoid.** When the number of peers is very large (vector clocks grow linearly with participants). When wall-clock ordering is sufficient (i.e., last-writer-wins is acceptable).
**Key decisions.** Clock pruning for large participant sets, dotted version vectors for better scalability, integration with merge functions, clock synchronization on peer join/leave.

### Merkle Trees for Synchronization
**When to use.** Efficiently determining what data differs between two peers. Instead of comparing every record, compare tree hashes top-down — only descend into subtrees that differ. Used by Cassandra, Dynamo, IPFS.
**When to avoid.** When the dataset is small enough that full comparison is cheap. When data changes so rapidly that the tree is constantly being rebuilt.
**Key decisions.** Tree depth and branching factor, rebuild frequency vs incremental updates, hash function choice, key space partitioning.

### Blockchain and Distributed Ledgers
**When to use.** When you need a tamper-evident, append-only log agreed upon by mutually untrusting parties. Financial transactions, provenance tracking, governance voting where auditability and censorship resistance are primary requirements.
**When to avoid.** Almost always. If participants can trust a single party (or a small federation), a database is simpler, faster, and cheaper. If data needs to be mutable or deletable. If transaction throughput matters more than decentralization.
**Key decisions.** Consensus mechanism (PoW is energy-expensive, PoS has different trust assumptions, PBFT works for permissioned networks), block size and time, smart contract language and VM, on-chain vs off-chain data, finality guarantees.

## Identity, Trust, and Security

### Cryptographic Identity
**When to use.** Every P2P system. Peers are identified by their public key (or a hash of it). No central authority issues identities — peers generate their own key pairs. This is the foundation of P2P authentication.
**When to avoid.** Never — if your P2P system doesn't use cryptographic identity, it has no authentication.
**Key decisions.** Key algorithm (Ed25519 is the modern default), key derivation and storage, key rotation mechanism, human-readable identifiers (mapping long keys to names — hard problem), multi-device identity.

### Web of Trust
**When to use.** Building trust without a central certificate authority. Peers vouch for each other, creating a graph of trust relationships. PGP's model. Useful in communities where social connections are meaningful.
**When to avoid.** Systems where users don't know each other. Large-scale systems where the trust graph becomes unwieldy. When the consequences of misplaced trust are severe (financial, safety).
**Key decisions.** Trust transitivity depth (how far trust propagates through the graph), revocation propagation, bootstrapping trust for new identities, handling key compromise in the trust graph.

### Sybil Resistance
**When to use.** Any P2P system where a single entity could gain disproportionate influence by creating many fake identities. Sybil attacks undermine voting, reputation, DHT routing, and fair resource allocation.
**When to avoid.** Closed networks with authenticated membership (the Sybil problem doesn't exist if identities are verified out-of-band).
**Key decisions.** Proof-of-work (computational cost per identity), proof-of-stake (economic cost), social verification (vouching), puzzle-based admission, rate-limiting identity creation, the tradeoff between openness and Sybil resistance.

### Encrypted Transport
**When to use.** Always. All peer-to-peer communication should be encrypted in transit — even on trusted networks, because P2P networks are inherently adversarial (you're connecting to strangers).
**When to avoid.** Never. Unencrypted P2P traffic is trivially observable, modifiable, and injectable by any network intermediary.
**Key decisions.** Noise Protocol Framework (used by libp2p, WireGuard — lightweight, modern), TLS 1.3 for TCP connections, DTLS for UDP, forward secrecy (ephemeral key exchange), peer authentication during handshake.

## Incentive Mechanisms

### Tit-for-Tat
**When to use.** Encouraging reciprocal resource contribution — peers that upload get better download speeds. BitTorrent's choking algorithm is the canonical example. Simple, effective, and self-enforcing.
**When to avoid.** When new peers can't bootstrap (they have nothing to offer yet). When the resource being shared isn't divisible (you can't partially share a database query result).
**Key decisions.** Optimistic unchoking (giving new peers a chance), detection of free-riding, handling asymmetric bandwidth (peers with slow upload), interaction with super-seeding.

### Token / Credit Systems
**When to use.** When tit-for-tat is too coarse — you want fine-grained accounting of resource contribution and consumption. Filecoin's storage market, bandwidth credits, compute tokens.
**When to avoid.** When the accounting infrastructure is more complex than the system it's incentivizing. When the token introduces speculation and financialization that distracts from the system's purpose.
**Key decisions.** On-chain vs off-chain accounting, double-spend prevention, price discovery mechanism, inflation/deflation policy, handling disputes.

### Reputation Systems
**When to use.** Peer quality varies and users benefit from knowing which peers are reliable — marketplace trust scores, content quality ratings, service reliability metrics.
**When to avoid.** When reputation can be trivially gamed (Sybil attacks to boost reputation). When reputation creates lock-in that prevents new participants from competing.
**Key decisions.** Local vs global reputation (local is more Sybil-resistant but less portable), decay over time, bootstrapping reputation for newcomers, handling reputation manipulation, privacy implications.

## Common Failure Modes

- **Eclipse attack.** An adversary controls all of a target peer's connections, isolating it from the honest network. The target sees only the adversary's version of reality. Mitigation: diverse peer selection (geographic, network, identity-based), minimum connection count, out-of-band verification of network state.
- **Sybil flooding.** A single entity creates thousands of identities to dominate the network — controlling DHT routing, outvoting honest peers, or monopolizing resources. Mitigation: proof-of-work/stake for identity creation, social verification, rate limiting, anomaly detection on peer behavior.
- **NAT traversal failure cascade.** STUN fails, hole punching fails, TURN servers are overloaded — peers can't connect. As connections fail, the network fragments, and remaining peers bear more relay load, causing further failures. Mitigation: diverse connectivity strategies, TURN capacity planning with headroom, graceful degradation to reduced functionality.
- **DHT routing table poisoning.** Malicious peers insert themselves at strategic positions in the DHT to intercept or drop lookups for specific keys. Mitigation: redundant lookups via disjoint paths, peer validation, signed DHT records, Sybil-resistant peer admission.
- **Free-rider collapse.** Too many peers consume resources without contributing. Upload bandwidth concentrates on a few generous peers who eventually leave or throttle. The network degrades as the ratio of consumers to contributors grows. Mitigation: tit-for-tat reciprocity, reputation systems, minimum contribution requirements.
- **Partition and merge.** Network partitions create independent sub-networks that diverge. When the partition heals, reconciling divergent state is complex and may involve data loss or conflicts. Mitigation: CRDTs for automatic merge, conflict detection and resolution policies, partition-aware consistency models.
- **Bootstrap node failure.** If hardcoded bootstrap nodes go down, new peers cannot join the network. The existing network continues to function but cannot grow. Mitigation: multiple bootstrap mechanisms (DNS-based discovery, hardcoded lists, mDNS, peer exchange), community-operated bootstrap nodes.
- **Message amplification.** Gossip and flooding protocols amplify every message by the fanout factor. Under high message rates, bandwidth consumption grows multiplicatively. Mitigation: message deduplication, adaptive fanout, eager push for critical messages + lazy pull for bulk, rate limiting at the protocol level.

## Anti-Patterns

- **P2P for the aesthetic.** Choosing peer-to-peer architecture because decentralization sounds good, not because the system requirements demand it. P2P adds complexity in NAT traversal, consistency, discovery, and security. Use it when centralization is the actual problem — censorship resistance, bandwidth distribution, offline-first operation — not as a default.
- **Trusting peer-provided data.** Accepting data from peers without verification. Every piece of data received from a peer must be validated — hash verification for content-addressed data, signature verification for attributed data, schema validation for structured data.
- **Ignoring churn.** Designing for a stable peer set when real P2P networks have constant join/leave. Routing tables go stale, stored data becomes unavailable, and overlay structure degrades. Design for churn as the normal case, not the exception.
- **Centralized bottleneck in disguise.** A "P2P" system where all peers depend on a single tracker, relay, or coordination server. When that server goes down, the network fails. If you need coordination, federate it across multiple independent operators.
- **No incentive design.** Assuming peers will altruistically contribute resources. Without explicit incentive mechanisms (reciprocity, reputation, tokens), rational peers will free-ride and the network will degrade to a client-server model where a few peers serve everyone else.
- **Unbounded resource consumption.** Letting peers store unlimited data, relay unlimited bandwidth, or maintain unlimited connections. Every shared resource needs quotas, eviction policies, and backpressure to prevent abuse and ensure fairness.
- **Rolling your own crypto.** Inventing custom encryption, key exchange, or signature schemes instead of using established libraries and protocols (libsodium, Noise framework, TLS). Cryptographic protocols are extremely hard to get right — subtle flaws are undetectable until exploited.
- **Global state assumption.** Designing protocols that require every peer to have the same view of the network. In P2P systems, each peer has a local, partial, and potentially stale view. Protocols must be correct under partial knowledge and eventual consistency.
- **Hardcoded peer limits.** Designing for a fixed network size. P2P systems must handle 10 peers and 10,000 peers with the same protocol. Algorithms with O(n) per-peer costs (full mesh, full broadcast) break at scale.
