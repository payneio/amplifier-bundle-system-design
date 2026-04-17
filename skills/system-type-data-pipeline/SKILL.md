---
name: system-type-data-pipeline
description: "Domain patterns for data pipeline architecture — batch processing, stream processing, ETL/ELT, DAG scheduling, data quality, schema evolution, backfill strategies, and failure modes. Use when designing or evaluating data pipelines, ETL systems, or streaming data infrastructure."
---

# System Type: Data Pipeline

Patterns, failure modes, and anti-patterns for batch and streaming data pipelines.

---

## Core Patterns

### Batch Processing
**What it is.** Process bounded datasets on a schedule — hourly, daily, or triggered. Read a full partition, transform, write output. The workhorse of data engineering.
**When to use.** Reporting, analytics, ML feature generation, any workload where latency of minutes to hours is acceptable. When the source data naturally arrives in chunks (file drops, database snapshots, daily exports). When transformations are complex aggregations across the full dataset.
**When to avoid.** When business requirements demand sub-minute freshness. When the dataset grows faster than the batch window can process it — you'll never catch up. When downstream consumers need continuous updates, not periodic dumps.

### Stream Processing
**What it is.** Process unbounded data continuously as it arrives. Events flow through a topology of operators. State is maintained in-stream.
**When to use.** Real-time fraud detection, live dashboards, operational alerting, CDC-based replication, any use case where "the answer must be current." When events have value that decays with time.
**When to avoid.** When you need complex joins across large historical windows — stream state gets expensive. When your team has no operational experience with Flink/Kafka Streams/Spark Streaming (the failure modes are subtle and unforgiving). When the "real-time" requirement is actually "within an hour" — that's batch.

### Micro-Batch
**What it is.** Process small batches at very short intervals (seconds to low minutes). Spark Structured Streaming is the canonical example. Gives near-real-time latency with batch-like programming models.
**When to use.** When you need latency better than batch but the team's skill set is batch-oriented. When exactly-once semantics are easier to reason about in batch units. When sub-second latency is not required.
**When to avoid.** When you need true event-at-a-time processing with sub-second latency. When the micro-batch interval masks timing bugs that will surface under load. When the overhead of repeated job initialization dominates actual processing time.

### ETL vs ELT
**ETL (Extract, Transform, Load).** Transform data before loading into the target. Traditional approach. Use when the target system is expensive (data warehouse with per-query pricing), when you need to filter/clean before storage, or when the target can't handle raw data volumes.
**ELT (Extract, Load, Transform).** Load raw data first, transform in the target system. Modern approach enabled by cheap storage and powerful query engines. Use when storage is cheap, when you want to preserve raw data for reprocessing, when transformations evolve frequently, or when the target system (Snowflake, BigQuery, Databricks) has strong compute for transformations.
**The real tradeoff.** ETL reduces storage cost and query scope at the expense of flexibility — you can't transform what you didn't keep. ELT preserves optionality at the expense of storage cost and potential query performance on raw data. Default to ELT unless you have a specific reason not to.

### Lambda Architecture
**What it is.** Run batch and streaming pipelines in parallel. Batch layer provides complete, accurate results; speed layer provides approximate, real-time results. Merge at query time.
**When to use.** Almost never in new systems. Was a necessary compromise before streaming frameworks matured.
**When to avoid.** In most cases. Maintaining two codepaths that must produce consistent results is an operational nightmare. Logic drift between batch and speed layers is the norm, not the exception. Prefer Kappa architecture unless you have a proven need for both.

### Kappa Architecture
**What it is.** Single streaming pipeline handles both real-time and historical reprocessing. Replay the log to reprocess.
**When to use.** When your source of truth is an immutable log (Kafka). When you want one codebase for both real-time and historical processing. When reprocessing means replaying from an offset, not re-running a different batch job.
**When to avoid.** When reprocessing terabytes by replaying a log is impractically slow. When batch-specific optimizations (partition pruning, columnar scans) are critical to meeting processing SLAs. When the streaming framework can't handle the state size required for historical aggregations.

## DAG Scheduling

**The core abstraction.** A directed acyclic graph of tasks with dependency edges. Task B runs only after Task A succeeds. Airflow, Dagster, Prefect, and Argo Workflows all implement this pattern.

**Temporal dependencies vs data dependencies.** Temporal: "run at 2am." Data: "run when the upstream partition exists." Temporal dependencies are fragile — they break when upstream is late. Data dependencies are robust but harder to implement. Prefer data-aware scheduling (sensors, dataset triggers) over cron-based scheduling wherever possible.

**Idempotent tasks.** Every task must produce the same output when run multiple times with the same inputs. This is non-negotiable. Overwrite the output partition, don't append. Use `INSERT OVERWRITE`, not `INSERT INTO`. Use deterministic file paths based on the logical execution date, not wall-clock time.

**Backfill.** Re-run a DAG for historical date ranges. Requires: idempotent tasks, parameterized execution dates, no hardcoded `datetime.now()`. Airflow's `catchup=True` fills gaps automatically — but test it before relying on it. Backfilling 6 months of daily tasks that each take 20 minutes will saturate your cluster for days. Throttle backfills with pool slots or concurrency limits.

**Catch-up.** When a pipeline is paused or delayed, catch-up runs the missed intervals. Dangerous if tasks are not idempotent or if resource consumption scales linearly with the number of missed intervals. Always set `max_active_runs` to prevent catch-up from consuming all available resources.

**SLA monitoring.** Define expected completion times. Alert when tasks miss their SLA. The SLA should be measured from the data's logical time, not the task's start time. A daily pipeline that completes at 8am but was supposed to finish by 6am has missed its SLA even if the task ran successfully.

**Task granularity.** Too fine-grained: excessive scheduler overhead, noisy DAG visualizations, complex dependency management. Too coarse-grained: long retry cycles (a 4-hour task fails at hour 3, you rerun the whole thing), poor observability into where time is spent. Aim for tasks that take 1–30 minutes. Split anything longer.

## Data Quality

**Schema validation.** Validate that incoming data matches the expected schema before processing. Fail fast on unexpected columns, missing required fields, or type mismatches. A single `null` in a non-nullable join key can silently drop millions of rows.

**Data contracts.** Formalize expectations between producers and consumers. A contract specifies: schema, freshness guarantees, volume expectations, allowed value ranges, and who to contact when it breaks. Without contracts, every schema change is a surprise.

**Assertion-based testing.** Great Expectations, dbt tests, Soda, or custom assertions. Check row counts, null rates, value distributions, referential integrity, and uniqueness constraints. Run assertions after every pipeline step, not just at the end. A pipeline that produces wrong data silently is worse than one that fails loudly.

**Quarantine patterns.** Route records that fail validation to a quarantine table instead of dropping them or failing the pipeline. Quarantine tables must include: the original record, the failure reason, the timestamp, and the pipeline version. Quarantined records are reviewed, fixed, and reprocessed — or explicitly discarded with an audit trail.

**Dead letter handling.** For streaming pipelines, records that can't be deserialized or processed go to a dead letter topic/queue. Same principle as quarantine — never silently drop data. Monitor dead letter depth. An empty dead letter queue means the pipeline is healthy or the dead letter routing is broken — verify which.

**Volume anomaly detection.** Alert when row counts deviate significantly from historical norms. A daily table that normally has 10M rows suddenly has 500K — something is wrong upstream even if the schema is valid. Simple statistical bounds (mean ± 3σ) catch most issues.

## Schema Evolution

**Forward compatibility.** New producers, old consumers. Achieved by: only adding optional fields, never removing fields, never changing field semantics. Old consumers ignore new fields they don't understand.

**Backward compatibility.** Old producers, new consumers. Achieved by: new consumers handle missing fields with defaults. New consumers don't require fields that old producers don't send.

**Full compatibility.** Both forward and backward compatible. The gold standard for long-lived data pipelines. Constrains evolution severely — you can only add optional fields with defaults.

**Schema registries.** Confluent Schema Registry, AWS Glue Schema Registry, or similar. Enforce compatibility rules at write time. Reject schemas that break the compatibility contract. Essential for any pipeline with more than one producer or consumer team.

**Handling schema drift.** When the source schema changes without warning (third-party APIs, vendor data feeds, scraped data): land raw data first (ELT pattern), detect drift by comparing against the last known schema, alert on drift, and adapt transformations. Never assume external schemas are stable.

**Format-level schema support.** Avro embeds the writer's schema with the data — readers use schema resolution to handle differences. Protobuf uses field numbers for forward/backward compatibility. Parquet has a schema per file but no cross-file compatibility enforcement. JSON has no schema unless you add one (JSON Schema). Choose formats with built-in evolution support for long-lived pipelines.

## Exactly-Once vs At-Least-Once Processing

**At-least-once.** The practical default. Messages may be delivered and processed more than once. Achieved by: committing offsets only after successful processing. Safe when consumers are idempotent.

**Exactly-once.** Each record affects downstream state exactly once. In practice, this means at-least-once delivery with idempotent processing and atomic commits. Kafka supports exactly-once via idempotent producers + transactional consumers, but at significant throughput cost.

**Checkpointing.** Periodically save processing state (offsets, window contents, aggregation accumulators) to durable storage. On failure, resume from the last checkpoint. Flink and Spark Structured Streaming both use checkpointing. Watch for: checkpoint interval vs data loss window tradeoff, checkpoint storage becoming a bottleneck, checkpoint size growing unboundedly with state.

**Offset management.** In Kafka-based pipelines, offset commits determine "where you are" in the log. Auto-commit is dangerous — it commits before processing is confirmed. Manual commit after processing + idempotent writes is the safe pattern. Store offsets in the same transaction as the output (e.g., offsets in the same database as the sink) for atomic exactly-once.

**Idempotent writes.** Design sink operations so that writing the same record twice produces the same result. Use UPSERT (INSERT ON CONFLICT UPDATE), not INSERT. Use deterministic output paths, not auto-increment IDs. Deduplication at the sink is your last line of defense.

**Deduplication windows.** In streaming systems, you can't remember every message ID forever. Use a bounded time window for deduplication and accept that duplicates outside the window may slip through. Size the window based on the maximum expected redelivery delay, plus margin.

## Backfill and Reprocessing

**Partition-based reprocessing.** Organize output by time partitions (daily, hourly). To reprocess, overwrite the partition. This is why idempotent writes and deterministic partitioning matter. A well-designed pipeline can reprocess any partition without affecting others.

**Time-travel and immutable staging.** Keep raw/bronze data immutable and versioned. When transformation logic changes, reprocess from the immutable source. Delta Lake, Iceberg, and Hudi support time-travel queries — you can query the data as it existed at any point. This is invaluable for debugging and auditing.

**Blue-green data swaps.** Build the new version of a table in a staging location. Validate it (row counts, schema, spot checks). Swap it in atomically by updating a pointer (Hive metastore partition, symlink, view redefinition). If the new version is bad, swap back. Never overwrite production data in place during large reprocessing jobs.

**Cost of reprocessing.** Reprocessing a year of data costs real money (compute, storage writes, egress). Design pipelines with reprocessing cost in mind. Incremental reprocessing (only changed partitions) is dramatically cheaper than full reprocessing. Track data lineage to know which downstream tables are affected by a reprocessing event.

**Backfill coordination.** When backfilling, downstream pipelines may trigger on intermediate states. Pause downstream consumers or use a "complete" marker (e.g., `_SUCCESS` file, partition metadata flag) that downstream pipelines wait for before processing.

## Storage Layer Patterns

### Data Lake vs Data Warehouse vs Lakehouse
**Data lake.** Cheap storage (S3, GCS, ADLS) with schema-on-read. Stores raw data in open formats. Good for: data exploration, ML training data, keeping everything "just in case." Bad for: governed analytics without additional tooling, ad-hoc queries without a query engine on top.
**Data warehouse.** Structured, schema-on-write storage with integrated query engine (Snowflake, BigQuery, Redshift). Good for: BI, reporting, governed analytics, SQL-centric teams. Bad for: unstructured data, ML workloads that need raw files, cost control when data volumes are very large.
**Lakehouse.** Open table formats (Delta Lake, Iceberg, Hudi) on top of lake storage with warehouse-like features (ACID transactions, schema enforcement, time-travel). The convergence point. Good for: teams that want one platform for both analytics and ML, cost-conscious organizations with large data volumes. Bad for: simple use cases where a warehouse alone suffices — the operational complexity of managing table format compaction, vacuuming, and metadata is real.

### Partitioning Strategies
**Time-based partitioning.** Partition by date or hour. The default for event data. Enables efficient time-range queries and partition-level backfill. Watch for: small file problems with over-partitioning (hourly partitions with low volume), skewed partitions (Black Friday vs a Tuesday in February).
**Key-based partitioning.** Partition by a business key (customer_id, region). Enables efficient point lookups. Watch for: skew (one key has 80% of the data), unbounded partition growth, partition pruning only works when queries filter on the partition key.
**Hive-style partitioning.** `year=2024/month=01/day=15/`. Self-describing directory structure. Widely supported. Watch for: too many partition columns creating deep directory trees with tiny files.

### File Formats
**Parquet.** Columnar, compressed, splittable. The default for analytical workloads. Excellent for read-heavy, column-selective queries. Bad for: append-heavy workloads (each write creates a new file), row-level updates (requires rewriting entire files or using a table format on top).
**Avro.** Row-oriented, schema-embedded, good for write-heavy workloads and schema evolution. The default for Kafka and event serialization. Bad for: analytical queries that scan few columns out of many.
**ORC.** Columnar, heavily optimized for Hive. Similar to Parquet but with tighter Hive ecosystem integration. Use if you're in a Hive-heavy environment; otherwise, Parquet has broader ecosystem support.
**JSON/CSV.** Human-readable but inefficient. No schema enforcement (JSON), ambiguous types (CSV). Acceptable for: landing zones, debugging, small reference data. Never use as the primary format for production analytical pipelines — the storage bloat and parse overhead are substantial.

### Compaction
**The problem.** Streaming pipelines and frequent appends create many small files. Small files kill query performance (high metadata overhead, poor parallelism granularity, excessive file open/close operations).
**The solution.** Periodic compaction jobs that merge small files into larger ones. Target file sizes of 128MB–1GB for Parquet on object storage. Delta Lake and Iceberg have built-in compaction (`OPTIMIZE`, `rewrite_data_files`). Run compaction on a schedule, not on every write. Monitor file counts per partition as a health metric.

## Common Failure Modes

- **Late-arriving data.** Events arrive after the processing window closes. Mitigation: watermarking with allowed lateness, late-data sidecar tables, reprocessing windows that extend beyond the primary window. The question isn't whether data will arrive late — it's how late you're willing to handle.
- **Schema drift.** Upstream changes a column type or adds a required field. Your pipeline breaks or, worse, silently produces wrong results. Mitigation: schema registries, schema-on-read with explicit casting, automated drift detection, data contracts.
- **Partition skew.** One partition has 100x the data of others. Tasks on that partition timeout or OOM while others finish in seconds. Mitigation: salted keys, adaptive query execution (Spark AQE), pre-aggregation of hot keys, repartitioning before expensive operations.
- **Resource exhaustion.** Backfills, catch-ups, or traffic spikes consume all cluster resources, starving production pipelines. Mitigation: resource pools, priority queues, concurrency limits on backfill DAGs, separate clusters for backfill vs real-time workloads.
- **Silent data corruption.** Pipeline succeeds but produces wrong data. Duplicated rows, dropped records, incorrect joins, timezone bugs, encoding errors. The most dangerous failure mode because it's invisible until someone notices the numbers don't add up. Mitigation: row-count assertions, cross-system reconciliation, anomaly detection on output metrics.
- **Clock skew.** Event timestamps disagree with processing time. Events from different sources use different timezones or clock drift. Mitigation: normalize all timestamps to UTC at ingestion, use event time (not processing time) for windowing, validate timestamp ranges (reject events from the year 2085).
- **Zombie tasks.** A task appears to be running but is actually stuck — waiting on a lock, deadlocked, or the worker died without reporting. Mitigation: heartbeat-based liveness checks, task-level timeouts, Airflow's `execution_timeout`, external monitoring of task duration against historical baselines.
- **Upstream dependency failures.** The source API is down, the file didn't land, the database snapshot is incomplete. Mitigation: sensors with timeout, retry with backoff, SLA alerting, fallback to stale data with staleness markers rather than producing nothing.
- **Metadata store corruption.** The Hive metastore, Airflow metadata database, or schema registry becomes inconsistent or unavailable. Mitigation: regular backups, HA configuration, graceful degradation (pipeline pauses rather than producing wrong data).
- **Compaction races.** A query reads files while compaction is rewriting them. Mitigation: use table formats (Delta, Iceberg) that provide snapshot isolation, never compact by manually deleting and rewriting files on raw object storage.

## Anti-Patterns

- **Wall-clock pipelines.** Using `datetime.now()` instead of the logical execution date. Breaks backfill, breaks idempotency, makes every run a unique snowflake. Parameterize everything by logical time.
- **Append-only sinks without dedup.** Inserting into a table without an UPSERT or merge strategy. Every retry, backfill, or reprocessing creates duplicates. Eventually someone runs `SELECT COUNT(DISTINCT id)` and panics.
- **Testing in production.** No staging environment for pipeline changes. "Let's just run it and see." You'll see — you'll see corrupted data in production tables at 3am on a Saturday.
- **Monolith DAG.** One DAG with 500 tasks and cross-dependencies everywhere. Impossible to reason about, impossible to backfill partially, one failure cascades everywhere. Split by domain boundary. Each DAG should have a clear owner and a clear SLA.
- **Implicit contracts.** No documentation of what columns a downstream pipeline depends on. Every upstream change is a game of "who did we break this time?" Formalize contracts. Breaking changes require a migration plan.
- **Overengineered real-time.** Building a Flink pipeline with exactly-once semantics when the dashboard refreshes hourly. The operational cost of streaming infrastructure is significant — don't pay it for latency nobody needs. Ask: "What's the cheapest architecture that meets the actual latency requirement?"
- **No data lineage.** Can't answer "what upstream data feeds into this report?" or "if I change this table, what breaks?" Leads to fear-driven stasis where nobody changes anything because the blast radius is unknown. Instrument lineage from day one, even if it's just a metadata table mapping sources to destinations.
- **Ignoring file sizes.** Writing thousands of 1KB Parquet files to S3. Every query takes forever because the metadata overhead dominates. Coalesce writes, run compaction, monitor file sizes. Target 128MB–1GB per file.
- **ETL in the database.** Running heavyweight transformations as stored procedures in the OLTP database. Competes with production traffic for CPU, memory, and I/O. Extract to a dedicated processing environment.
- **Hardcoded credentials and endpoints.** Source connection strings baked into DAG code. Can't switch environments, can't rotate secrets, and someone will commit them to git. Use a secrets manager and environment-based configuration.
- **Skipping the dead letter queue.** Dropping records that fail parsing or validation. You'll never know what you lost. Every production pipeline needs a dead letter destination and monitoring on its depth.
