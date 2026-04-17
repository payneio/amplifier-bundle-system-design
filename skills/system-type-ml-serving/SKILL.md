---
name: system-type-ml-serving
description: "Domain patterns for ML/AI serving and training systems — model serving, feature stores, training pipelines, experiment tracking, A/B testing, GPU scheduling, and failure modes. Use when designing or evaluating machine learning infrastructure, model serving platforms, or AI-powered product features."
---

# System Type: ML/AI Serving & Training

Patterns, failure modes, and anti-patterns for machine learning infrastructure and model serving systems.

---

## Model Serving Patterns

### Online Inference (Real-Time)
**What it is.** Model receives a request, runs inference synchronously, returns a prediction. The model sits in the request path — latency matters as much as accuracy.
**When to use.** User-facing predictions where the result must be immediate: search ranking, recommendation, fraud scoring at transaction time, autocomplete.
**When to avoid.** When predictions can be precomputed. When the model is too large to meet latency budgets. When the cost per prediction doesn't justify real-time serving.
**Key concerns.** Tail latency (P99, not just P50) dominates user experience. Model loading time creates cold start problems. Memory footprint determines how many models fit per node. Timeouts must be set aggressively — a slow prediction is worse than a fallback.

### Batch Inference
**What it is.** Run predictions over a large dataset on a schedule (hourly, daily). Write results to a store; serve precomputed predictions at request time.
**When to use.** Recommendations that refresh periodically. Risk scoring where real-time freshness isn't required. Any case where the input space is bounded and enumerable.
**When to avoid.** When input features change faster than the batch interval. When the input space is too large to precompute (e.g., arbitrary user queries). When staleness directly harms the user.
**Key concerns.** Batch jobs that overrun their schedule. Incomplete batches that leave stale predictions for some entities. The join between precomputed predictions and request-time serving (cache misses for new entities). Monitoring must cover prediction freshness, not just job success.

### Streaming Inference
**What it is.** Model consumes events from a stream (Kafka, Kinesis), produces predictions continuously. Sits between batch and real-time — lower latency than batch, lower cost than synchronous serving.
**When to use.** Event-driven predictions: fraud detection on transaction streams, anomaly detection on telemetry, real-time feature updates feeding downstream models.
**When to avoid.** When you need sub-100ms request-response latency. When the prediction consumer expects synchronous responses.
**Key concerns.** Consumer lag means predictions fall behind reality. Backpressure from slow models causes event queue growth. Exactly-once semantics for predictions that trigger side effects (e.g., blocking a transaction). Reprocessing on model update — do you recompute predictions for the backlog or only apply the new model forward?

### Model-as-a-Service vs. Embedded Models
**Model-as-a-service.** Centralized inference endpoint. Clear ownership, independent scaling, versioning decoupled from application deploys. But: network latency, one more service to operate, coupling on availability.
**Embedded models.** Model ships inside the application binary or container. No network hop. But: every application deploy includes the model, model updates require app redeployment, resource isolation is harder (the model competes with the app for memory and CPU).
**The real question:** How often does the model change independently of the application? If weekly or more, service extraction pays off. If quarterly, embedding avoids operational overhead.

## Feature Engineering

### Feature Stores
**What it is.** A system that manages feature computation, storage, and serving for ML models. Separates feature engineering from model training and serving.
**Online store.** Low-latency key-value lookups at serving time. Backed by Redis, DynamoDB, or similar. Optimized for point lookups by entity ID.
**Offline store.** Historical feature values for training. Backed by a data warehouse, object storage, or lakehouse. Optimized for bulk reads with time-range filters.
**When to use.** Multiple models share features. Feature engineering is a bottleneck. Training-serving skew is a known problem. The organization has enough ML workloads to justify the infrastructure.
**When to avoid.** Single model, single team, simple features. The overhead of operating a feature store exceeds the pain it solves. You don't yet have a training-serving skew problem.

### Feature Freshness and Staleness
Features have different freshness requirements. User profile features may tolerate hours of staleness. Transaction features (current cart, session behavior) may need sub-second freshness. Mixing stale and fresh features in a single model is normal — but the staleness bounds must be explicit, monitored, and tested.
**The critical failure:** A feature pipeline silently falls behind. The model receives stale features but no one notices because predictions are still "reasonable." Quality degrades gradually. By the time it's caught, you've been serving degraded predictions for days.

### Training-Serving Skew
The most insidious ML infrastructure bug. The features used in training differ from those used in serving — different code paths, different data sources, different timing.
**Common causes:** Feature engineering code duplicated between training (Python/Spark) and serving (Java/Go). Different aggregation windows. Features joined at different time granularities. Backfill data that doesn't match production feature computation.
**Mitigation:** Use the same feature computation code for training and serving. Log features at serving time and use those logged features for training. Continuously compare training feature distributions against serving feature distributions.

### Point-in-Time Correctness
**What it is.** When constructing training data, ensure each training example uses only features that were available at the time the label was observed. No future data leakage.
**Why it matters.** Without point-in-time joins, the model sees features that wouldn't exist in production at prediction time. Training metrics look artificially good. Production performance is worse. This is data leakage — the most common source of "the model worked in the notebook but not in production."
**How to enforce.** Feature stores with timestamp-aware retrieval. Event-time-based joins rather than processing-time joins. Simulation environments that replay historical data in order.

## Training Pipeline Patterns

### Training DAGs
**What it is.** Training isn't a single script — it's a DAG of data preparation, feature computation, training, evaluation, validation, and registration steps. Orchestrated by Airflow, Kubeflow Pipelines, or similar.
**Key decisions.** Granularity of steps (too coarse: can't retry failures; too fine: orchestration overhead). Caching intermediate outputs to avoid recomputation. Parameterization for hyperparameter sweeps. Idempotency — rerunning a step with the same inputs should produce the same outputs.
**Operational reality.** Training DAGs are some of the most brittle pipelines in any organization. They depend on data availability, GPU scheduling, library versions, and random seeds. Expect failures. Design for retryability.

### Reproducibility
**What it is.** Given the same inputs, produce the same model. Sounds simple; it's not.
**What must be pinned:** Training data (immutable snapshots, not mutable tables). Code (git commit SHA). Dependencies (lock files, container images by digest). Random seeds. Hardware (GPU type affects floating point behavior). Library versions (cuDNN, NCCL).
**What you'll actually get:** Approximate reproducibility. Bit-exact reproduction across different GPU types is often impossible. Settle for "same data + same code + same hardware = same metrics within acceptable tolerance."

### Experiment Tracking and Model Registry
**Experiment tracking.** Log hyperparameters, metrics, artifacts, and code versions for every training run. Without this, you're guessing which run produced a given model. Tools: MLflow, Weights & Biases, Neptune.
**Model registry.** A versioned catalog of production-ready models with metadata: who trained it, what data, what metrics, approval status. The bridge between "a model exists" and "a model is deployed."
**The gap:** Experiment tracking is for researchers iterating. The model registry is for engineers deploying. Most failures happen in the handoff between these two worlds.

### Distributed Training
**When to use.** Model or dataset doesn't fit on a single GPU. Training time on one GPU exceeds acceptable iteration speed.
**Data parallelism.** Replicate the model across GPUs, split the data. Gradients are aggregated. Scales well but communication overhead grows with model size.
**Model parallelism.** Split the model across GPUs. Necessary for very large models. Complex to implement and debug. Pipeline parallelism (splitting by layers) is the most common form.
**Key concerns.** Communication bandwidth between GPUs (NVLink vs. PCIe vs. network). Gradient synchronization overhead. Batch size scaling and learning rate adjustment. Fault tolerance — a single GPU failure kills a multi-GPU job.

### GPU Scheduling and Preemption
Training jobs compete for GPU resources. Schedulers must balance utilization, fairness, and priority.
**Preemption.** Lower-priority training jobs can be preempted by higher-priority jobs (e.g., production retraining preempts research experiments). Requires checkpointing — jobs must save state frequently enough that preemption doesn't lose significant work.
**Gang scheduling.** Multi-GPU jobs need all their GPUs simultaneously. Partial allocation is useless. This creates fragmentation: a 4-GPU job can't start even though 3 GPUs are free.
**Bin packing.** Small jobs fill gaps left by large jobs. Efficient utilization requires a mix of job sizes.

## Model Versioning and Rollout

### Canary Deployments for Models
**What it is.** Route a small percentage of traffic to the new model. Compare metrics against the current model. Gradually increase traffic if metrics are acceptable.
**How it differs from software canary.** Software canaries look for errors and latency. Model canaries must also compare prediction quality — which may take days of observation to assess statistically. You can catch a crash in minutes; you can't catch a 0.5% conversion rate drop in minutes.
**Key decisions.** What percentage to start with. What metrics to compare. How long to bake. What constitutes a rollback trigger. Whether canary traffic is random or stratified.

### Shadow Mode
**What it is.** Run the new model on production traffic, log its predictions, but don't serve them to users. Compare offline against the current model's predictions.
**When to use.** High-risk model changes. First deployment of a new model type. When you need prediction-level comparison without user impact.
**Limitations.** Shadow mode can't measure user behavioral metrics (click-through, conversion) because the user never sees the shadow predictions. Good for catching gross errors; insufficient for measuring subtle quality differences.

### Champion/Challenger Pattern
**What it is.** The current production model is the champion. New models are challengers. Challengers must beat the champion on defined metrics to be promoted.
**How to implement.** Automated evaluation pipeline that tests challengers against holdout data and (optionally) live traffic. Promotion criteria are explicit and automated — not "the data scientist thinks it's better."
**The gap between offline and online metrics.** A model can improve offline AUC by 2% and decrease online conversion by 1%. Offline metrics measure prediction accuracy; online metrics measure business impact. They are correlated but not identical. Always validate online.

### Model Rollback
Model rollback is harder than software rollback. The new model may have already influenced user behavior (recommendations changed what users clicked, which changed the data, which changed the features). Rolling back the model doesn't roll back the data distribution shift it caused.
**Requirements.** Previous model versions must remain deployable (artifacts retained, not garbage collected). Feature pipelines must be compatible with older model versions. Rollback must be a one-command operation, not a multi-day retrain.

## A/B Testing and Experimentation

### Statistical Rigor
**Sample size.** Underpowered experiments are noise. Calculate required sample size before starting, based on minimum detectable effect and baseline metric variance. Running an experiment "until it looks significant" guarantees false positives.
**Duration.** Run for complete business cycles (at least one full week to capture day-of-week effects). Avoid starting or ending experiments during anomalous periods (holidays, outages, marketing campaigns).
**Multiple comparisons.** Testing 10 metrics simultaneously means one will be "significant" by chance at p=0.05. Apply corrections (Bonferroni, Benjamini-Hochberg) or pre-register a primary metric. The more metrics you test, the more likely you are to find noise and call it signal.
**Sequential testing.** If you check experiment results daily and stop when significant, your false positive rate is much higher than 5%. Use sequential testing methods (always-valid p-values) or commit to a fixed duration upfront.

### Feature Flags for Model Routing
Models are routed via feature flags, not deployment topology. This decouples model deployment from model activation. Deploy the new model to all servers; activate it for 5% of traffic via a flag. Roll back by flipping the flag, not redeploying.
**Key requirements.** Consistent assignment — a user should see the same model variant for the duration of an experiment. Flag evaluation must be fast (microseconds, not milliseconds). Flag state must be auditable (who changed what, when).

### Guardrail Metrics
**What they are.** Metrics that must not degrade, regardless of whether the primary metric improves. Revenue, latency, error rate, user complaints, safety metrics.
**Why they matter.** A model that improves click-through rate by 5% but increases page load time by 200ms is not a win. Guardrails prevent optimizing one metric at the expense of the system.
**Implementation.** Guardrail violations trigger automatic experiment shutdown. Guardrails are defined at the platform level, not per-experiment. Every experiment inherits the same set.

### Interaction Between ML and Product Experiments
Running a product A/B test and an ML A/B test simultaneously on the same users creates interaction effects. If the product change alters user behavior, it changes the data the ML model sees, confounding both experiments.
**Mitigation.** Experiment isolation layers that ensure users are in at most one experiment per surface. Or: multi-armed bandit approaches that adapt to interactions. Or: accept the interaction and use multi-factor analysis — but this requires much larger sample sizes.

## GPU and Compute Management

### GPU Scheduling
**Time-slicing.** Multiple processes share a GPU by time-sharing. Simple but unpredictable latency — a training job's burst can starve an inference job's request.
**Multi-Instance GPU (MIG).** Physically partition a GPU into isolated instances (A100, H100). Each partition gets guaranteed compute and memory. Good for inference workloads that don't need a full GPU. Bad for workloads that need burst access to full GPU memory.
**Multi-Process Service (MPS).** Multiple CUDA processes share a GPU with better concurrency than time-slicing. Lower isolation than MIG. Suitable for many small inference requests.
**The tradeoff:** Isolation vs. utilization. MIG gives isolation but wastes capacity on bursty workloads. Time-slicing maximizes utilization but gives no guarantees. Match the scheduling strategy to the workload's latency sensitivity.

### Spot/Preemptible Instances for Training
Training workloads are often fault-tolerant and can resume from checkpoints. Spot instances cost 60-90% less than on-demand.
**Requirements.** Frequent checkpointing (every 15-30 minutes for long jobs). Graceful handling of termination notices. Job orchestration that restarts preempted jobs automatically. Checkpoints stored on durable storage (S3, GCS), not local disk.
**When spot doesn't work.** Jobs shorter than the minimum billing increment. Jobs that can't checkpoint (some distributed training frameworks). Time-critical retraining where interruption delays a production model update.

### Model Optimization for Serving Cost
**Quantization.** Reduce precision from FP32 to FP16, INT8, or INT4. Reduces memory footprint and increases throughput. Quality impact is model-dependent — always validate on your evaluation set. Post-training quantization is easy; quantization-aware training recovers more quality.
**Distillation.** Train a smaller "student" model to mimic a larger "teacher" model. The student is cheaper to serve. The quality gap depends on the task complexity and student capacity.
**Pruning.** Remove weights or neurons that contribute little to output quality. Structured pruning (removing entire channels) is hardware-friendly. Unstructured pruning (zeroing individual weights) requires sparse computation support.
**The cost equation.** Serving cost = (instances × price per instance) / (throughput per instance). Optimization reduces the denominator. But: engineer time spent optimizing has a cost too. Optimize when serving cost is a top-3 expense, not when it's a rounding error.

### Autoscaling Inference Endpoints
**Why it's harder than web service autoscaling.** Model loading takes seconds to minutes (downloading weights, GPU memory allocation, warmup). Scaling up is slow. Scaling down risks dropping in-flight requests. GPU instances are expensive — over-provisioning is costly.
**Scaling signals.** Request queue depth (best leading indicator). GPU utilization (lagging — high utilization means you're already slow). Prediction latency P99 (too lagging for proactive scaling).
**Minimum instances.** Always keep enough warm instances to handle baseline traffic. A scale-to-zero strategy for inference endpoints means the first request after idle waits for model loading — acceptable for dev, not for production.
**Scale-down cooldown.** Set long cooldown periods. GPU instances are expensive to keep but more expensive to repeatedly start and stop (loading model weights each time).

## LLM-Specific Patterns

### Prompt Management and Versioning
Prompts are code. They determine model behavior, affect output quality, and change over time. Treat them accordingly.
**Version control.** Store prompts in version control, not in application config or databases. Track which prompt version produced which outputs. Enable rollback to previous prompt versions.
**Parameterization.** Separate prompt templates from variable inputs. Template: "Summarize the following article in {style} for {audience}." Variables are injected at runtime.
**Evaluation.** Every prompt change requires evaluation against a test suite of inputs and expected outputs. "It seemed better when I tried a few examples" is not evaluation.

### RAG (Retrieval-Augmented Generation)
**What it is.** Retrieve relevant documents from a knowledge base, inject them into the prompt context, and have the LLM generate a response grounded in those documents. Reduces hallucination and enables knowledge that wasn't in training data.
**Architecture.** Document ingestion pipeline → chunking → embedding → vector store. At query time: embed query → retrieve top-k chunks → construct prompt with context → generate response.
**Key decisions.** Chunk size (too small: lost context; too large: noise and wasted tokens). Embedding model selection (quality vs. cost vs. latency). Retrieval strategy (vector similarity, hybrid with keyword search, reranking). Number of retrieved chunks (more context vs. longer prompts vs. distraction).
**Failure modes.** Retrieved chunks are irrelevant (retrieval quality problem). Retrieved chunks are relevant but the LLM ignores them (prompt engineering problem). Retrieved chunks are outdated (ingestion pipeline lag). Chunk boundaries split critical information.

### Token Budget Management
LLMs bill by token. Every wasted token is wasted money. At scale, prompt engineering is cost engineering.
**Input optimization.** Strip unnecessary context. Compress verbose inputs. Use shorter system prompts for high-volume, low-complexity tasks. Cache and reuse common prompt prefixes where the API supports it.
**Output optimization.** Constrain output length with max_tokens. Use structured output formats (JSON) to avoid verbose prose when you need data. Stop sequences to prevent rambling.
**Budget allocation.** For a 128K context window, allocate deliberately: system prompt (fixed cost), retrieved context (variable), user input (variable), output budget (reserved). Monitor actual token usage per request and alert on drift.

### Rate Limiting and Cost Control
**Per-user rate limits.** Prevent individual users from consuming disproportionate resources. Implement at the application layer, not just the LLM provider layer.
**Cost ceilings.** Set daily and monthly spend limits. Alert at 50%, 80%, and 95% of budget. Automatically degrade (switch to smaller models, reduce context, disable features) before hitting hard limits.
**Tiered model routing.** Route simple requests to cheaper, faster models. Route complex requests to expensive, capable models. Classification of request complexity is itself a modeling problem — start with heuristics (input length, task type), graduate to a classifier.

### Caching Strategies for LLM Calls
**Exact match caching.** Cache the response for identical (prompt, parameters) pairs. Hit rate is low for user-generated input but high for system-generated prompts (e.g., classification of a fixed set of categories).
**Semantic caching.** Embed the prompt, return a cached response if a sufficiently similar prompt was previously seen. Risky — "sufficiently similar" is hard to define, and cache hits on semantically different prompts produce wrong answers. Use only when the cost of an occasional wrong cached response is low.
**Component caching.** Cache intermediate results: embeddings, retrieved documents, extracted entities. Cheaper to recompute the final LLM call than to redo the entire pipeline.

### LLM Evaluation Frameworks
**Beyond accuracy.** LLM outputs are open-ended. Traditional accuracy metrics are insufficient.
**Dimensions to evaluate.** Factual correctness (does it hallucinate?). Instruction following (does it do what was asked?). Safety (does it produce harmful content?). Consistency (does it give the same answer to the same question?). Latency and cost. Format compliance (valid JSON, correct schema).
**Evaluation methods.** Human evaluation (gold standard, expensive, slow). LLM-as-judge (use a stronger model to evaluate a weaker model's output — cheaper, scalable, but circular if both models share the same biases). Automated metrics (BLEU, ROUGE for summarization — crude but fast). Task-specific assertions (regex matching, schema validation, keyword presence).
**Regression testing.** Maintain a dataset of (input, expected_output) pairs. Run it on every prompt change, model change, or dependency update. Alert on regressions. This is your CI/CD for prompts.

## Common Failure Modes

- **Training-serving skew.** Features are computed differently in training and serving. The model sees a different world in production than it trained on. Silent, gradual quality degradation. Mitigation: shared feature computation code, feature logging at serving time, distribution monitoring.
- **Model degradation over time.** The world changes but the model doesn't. User behavior shifts, product changes alter the data distribution, seasonality effects the model wasn't trained on. Mitigation: scheduled retraining, performance monitoring dashboards, drift detection on input features and output predictions.
- **Data drift without detection.** Input feature distributions shift — a new user cohort, a changed upstream data source, a schema migration that alters feature semantics. If you're not monitoring feature distributions in production, you won't know until prediction quality has already degraded. Mitigation: statistical tests on feature distributions (KL divergence, PSI), alerting on drift magnitude.
- **GPU memory leaks.** CUDA memory that isn't freed between inference requests. Memory usage creeps up until OOM. More common with dynamic computation graphs, custom CUDA kernels, and long-running serving processes. Mitigation: memory monitoring per request, periodic process restarts, memory profiling in staging.
- **Cold start latency for large models.** Loading a multi-gigabyte model from disk to GPU memory takes 30 seconds to several minutes. First request after a scale-up event or container restart is painfully slow. Mitigation: pre-warmed instance pools, model weight caching on local NVMe, minimum instance counts, readiness probes that wait for model loading.
- **Silent prediction quality regression.** The model serves predictions, latency is fine, no errors — but prediction quality has dropped. No one notices because there's no quality monitoring in production, only latency and error rate dashboards. Mitigation: online evaluation metrics (logged predictions vs. eventual outcomes), A/B testing infrastructure, human evaluation sampling.
- **Cascading failures from model timeouts.** A model inference endpoint slows down. Callers queue up and exhaust connection pools. Upstream services start failing. A slow model is worse than a down model — at least a down model triggers fallback logic immediately. Mitigation: aggressive timeouts (fail fast), circuit breakers, graceful degradation (return default predictions or disable the ML feature).
- **Feature store outages.** The online feature store goes down. Every model that depends on it starts making predictions with missing features. Some frameworks silently fill missing features with zeros or defaults — the model produces plausible but wrong predictions. Mitigation: feature store as a critical-path dependency with its own SLO, fallback feature values that are explicitly chosen (not implicit defaults), monitoring on feature availability rate.
- **Checkpoint corruption.** A training job's checkpoint is corrupted (incomplete write, storage issue). The job fails on restart and must begin from scratch — wasting hours or days of GPU time. Mitigation: write checkpoints atomically (write to temp, rename), verify checksums after writing, retain multiple checkpoint generations.
- **Feedback loop amplification.** The model influences the data it's trained on. A recommendation model promotes certain items; users interact with those items; the model is retrained on that interaction data; the model becomes even more confident in those items. Diversity collapses. Mitigation: exploration strategies (epsilon-greedy, Thompson sampling), monitoring diversity and coverage metrics, holdout sets not influenced by the model.

## Anti-Patterns

- **Notebook-to-production pipeline.** Treating Jupyter notebooks as production artifacts. Notebooks have hidden state, implicit execution order, and no testing infrastructure. Use notebooks for exploration; extract production code into tested, versioned modules.
- **The offline-metric trap.** Optimizing exclusively for offline metrics (AUC, F1, RMSE) without validating online impact. A model that improves AUC by 3% on a test set can degrade the user experience. Offline metrics are necessary but not sufficient — they filter bad models but don't guarantee good ones.
- **Feature store as first investment.** Building a feature store before you have more than two models or a demonstrated training-serving skew problem. The infrastructure cost and operational burden of a feature store is substantial. Earn the right to build one by outgrowing simpler approaches.
- **Retraining without monitoring.** Automatically retraining models on a schedule without validating that new data is clean and the new model is better. Auto-retraining on corrupted data produces a corrupted model, deployed automatically. Every retraining pipeline needs a validation gate.
- **GPU hoarding.** Teams reserve GPU capacity "in case they need it" while actual utilization is 15%. GPUs cost $1-3/hour each. An idle GPU cluster is a cash incinerator. Centralize GPU scheduling, enforce utilization monitoring, reclaim idle allocations.
- **One model to rule them all.** Forcing a single model architecture to serve all use cases. The ranking model shouldn't also be the spam classifier. Different problems have different accuracy/latency/cost tradeoffs and different data distributions.
- **Ignoring model serving cost at training time.** Researchers train the largest model possible, then hand it to engineers who can't serve it within latency or cost budgets. Include serving constraints (latency budget, memory limit, cost per prediction) in the model development process from the start.
- **Shadow mode forever.** Running a new model in shadow mode indefinitely because no one defined the promotion criteria or owns the decision to go live. Shadow mode is a validation step, not a permanent state. Define exit criteria before entering shadow mode.
- **Treating ML infrastructure as a data science problem.** ML infrastructure is software engineering. Reliability, observability, deployment automation, and incident response are engineering problems. Staffing an ML platform team entirely with data scientists produces research-grade infrastructure with research-grade reliability.
- **Prompt engineering by vibes.** Changing LLM prompts based on gut feel and a handful of manual tests. Without systematic evaluation against a test suite, every prompt change is a coin flip that might improve the tested case and regress ten others.
