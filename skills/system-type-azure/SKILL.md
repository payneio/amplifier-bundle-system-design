---
name: system-type-azure
description: "Domain patterns for Azure cloud architecture — compute selection, managed services, identity (Entra ID), networking, data platform, messaging, deployment, cost management, and operational patterns. Use when designing or evaluating a system deployed on Microsoft Azure."
---

# System Type: Azure

Patterns, failure modes, and anti-patterns for systems built on Microsoft Azure.

---

## Compute

### Azure App Service
**When to use.** Web applications, REST APIs, and backend services where you want managed infrastructure with zero Kubernetes overhead. Supports .NET, Java, Node.js, Python, Go. Built-in autoscaling, deployment slots, and custom domains with managed TLS.
**When to avoid.** Workloads that need GPU, custom networking at the host level, or containers with sidecar patterns. When per-second billing matters (App Service charges per plan, not per request). Workloads that need sub-second cold start.
**Key decisions.** Plan tier (Free/Basic for dev, Standard/Premium for production — Premium required for VNet integration and deployment slots), Linux vs Windows, scaling rules (CPU, memory, HTTP queue length, custom metrics), always-on setting (prevents cold starts on Standard+), deployment slot swap strategy.

### Azure Functions
**When to use.** Event-driven, short-lived compute — HTTP triggers, queue processors, timer-based jobs, event hub consumers. Consumption plan gives true pay-per-execution. Ideal for glue logic, webhooks, and lightweight APIs.
**When to avoid.** Long-running processes (Consumption plan has a 5/10-minute timeout). Workloads with sustained high throughput (Consumption plan cold starts add latency; Premium or Dedicated plan negates the cost advantage). Complex orchestration (use Durable Functions or Container Apps instead).
**Key decisions.** Hosting plan (Consumption for sporadic traffic, Premium for VNet and pre-warmed instances, Dedicated for predictable load), runtime version, trigger binding selection, Durable Functions for orchestration/fan-out, function app isolation boundaries (one app per domain concern).

### Azure Container Apps
**When to use.** Containerized microservices and APIs when you want Kubernetes-like capabilities (scaling, Dapr, service discovery, revisions) without managing a cluster. Built on Kubernetes but abstracts it away. Supports scale-to-zero.
**When to avoid.** When you need full Kubernetes control (custom operators, CRDs, node-level config). Workloads requiring GPU. When the team has deep Kubernetes expertise and the abstraction layer gets in the way.
**Key decisions.** Environment design (shared environments for related services, separate for isolation), Dapr sidecar usage (service invocation, state, pub/sub), scaling rules (HTTP concurrency, KEDA scalers for queues/events), revision management, ingress configuration (internal vs external).

### Azure Kubernetes Service (AKS)
**When to use.** Complex containerized workloads that need full Kubernetes control — custom operators, advanced scheduling, node pools with specific hardware (GPU, high-memory), tight integration with the Kubernetes ecosystem. When the team has Kubernetes expertise.
**When to avoid.** Simple web apps or APIs (App Service or Container Apps are simpler). Small teams without Kubernetes experience — the operational burden is significant. When the Kubernetes features you'd use are already available in Container Apps.
**Key decisions.** Node pool strategy (system vs user pools, spot instances for batch), networking model (kubenet vs Azure CNI — CNI required for VNet pod-level networking), cluster autoscaler vs KEDA, managed identity for pod identity (Workload Identity), upgrade strategy (blue-green node pools vs rolling), monitoring (Container Insights, Prometheus).

### Azure Virtual Machines
**When to use.** Workloads that need full OS control — legacy applications, license-constrained software (BYOL), custom kernel requirements, GPU workloads not supported by higher-level services. Lift-and-shift migrations.
**When to avoid.** Greenfield applications where managed services exist. Any workload where you'd be building infrastructure that Azure already provides (load balancing, auto-restart, scaling, patching).
**Key decisions.** VM series selection (B-series for burstable, D-series general purpose, E-series memory, N-series GPU), managed disks (Premium SSD for production), availability sets vs availability zones, VM Scale Sets for autoscaling, Azure Bastion for secure access (no public SSH), image management (Azure Image Builder, Shared Image Gallery).

## Identity and Access

### Microsoft Entra ID (Azure AD)
**When to use.** Always. Entra ID is the identity control plane for Azure. Every Azure workload should authenticate via Entra ID — user authentication, service-to-service, and resource access. It's not optional; it's the foundation.
**When to avoid.** Never for Azure workloads. For non-Azure external systems that can't speak OIDC/SAML, use Entra ID as the authority and bridge with appropriate protocols.
**Key decisions.** Tenant architecture (single vs multi-tenant), app registration model (one per service vs shared), permission model (delegated vs application permissions), Conditional Access policies, token lifetime and caching, B2C vs B2B for external identities.

### Managed Identity
**When to use.** Any Azure resource that needs to call another Azure resource or Entra ID-protected API. Managed Identity eliminates stored credentials — Azure handles the certificate rotation and token acquisition. System-assigned for single-resource lifecycle, user-assigned for shared identity across resources.
**When to avoid.** Never, when the alternative is storing secrets. If an Azure service supports Managed Identity, use it. The only exception is when calling third-party APIs that don't support Entra ID tokens.
**Key decisions.** System-assigned vs user-assigned (user-assigned enables shared identity and survives resource recreation), RBAC role assignments (least privilege — never Contributor when Reader suffices), DefaultAzureCredential chain for code that runs both locally and in Azure.

### Azure RBAC
**When to use.** All authorization decisions for Azure resource access. RBAC controls who can do what to which resources. Assign roles at the narrowest scope possible — resource, resource group, subscription.
**When to avoid.** Application-level authorization (RBAC controls Azure resources, not your app's business logic — use application-level roles or Entra ID app roles for that).
**Key decisions.** Custom roles vs built-in roles (prefer built-in), role assignment scope (resource group is the common sweet spot), PIM (Privileged Identity Management) for just-in-time elevation, deny assignments for guardrails, regular access reviews.

### Key Vault
**When to use.** Storing secrets, certificates, and encryption keys that can't use Managed Identity (third-party API keys, connection strings for non-Azure services, TLS certificates). Central secret management with audit logging.
**When to avoid.** Secrets that could be eliminated by using Managed Identity instead. High-throughput crypto operations that need HSM-level performance (use Managed HSM or Dedicated HSM).
**Key decisions.** Vault-per-environment (dev/staging/prod), access policy model (RBAC is preferred over vault access policies), secret rotation strategy, soft-delete and purge protection (enable both in production — data loss prevention), network restrictions (private endpoint for production vaults).

## Networking

### Virtual Network (VNet)
**When to use.** All production workloads. VNet is the network isolation boundary in Azure. Every VM, AKS cluster, App Service (with VNet integration), and database (with private endpoint) should be inside a VNet.
**When to avoid.** Only for quick prototypes or development environments where network isolation isn't needed yet.
**Key decisions.** Address space planning (don't overlap with on-premises or other VNets — use RFC 1918 ranges, plan for growth), subnet strategy (separate subnets per workload tier, delegate subnets for PaaS services), NSG (Network Security Group) rules per subnet, VNet peering vs VPN for cross-VNet connectivity.

### Private Endpoints
**When to use.** Accessing PaaS services (Storage, SQL, Cosmos DB, Key Vault, Service Bus) over private IP addresses within your VNet. Eliminates public internet exposure for data-plane operations. Required for compliance in most enterprise environments.
**When to avoid.** Development environments where the DNS complexity isn't justified. Services that don't support private endpoints.
**Key decisions.** Private DNS zone integration (Azure-managed DNS zones for automatic resolution), DNS forwarding for hybrid networks, private endpoint per service per VNet, NSG support on private endpoints (recently added), approval workflow for cross-tenant connections.

### Azure Front Door / Application Gateway
**When to use.** Front Door for global HTTP load balancing, WAF, and CDN with anycast routing — multi-region applications. Application Gateway for regional L7 load balancing, WAF, and SSL termination within a single region.
**When to avoid.** Front Door is overkill for single-region applications. Application Gateway is unnecessary if App Service or Container Apps built-in routing suffices.
**Key decisions.** Front Door tier (Standard for CDN + routing, Premium for WAF + Private Link origins), WAF rule sets (Microsoft-managed + custom rules), caching rules, origin health probes, URL rewriting and routing rules.

### Azure DNS and Traffic Manager
**When to use.** Azure DNS for hosting DNS zones. Traffic Manager for DNS-based global traffic routing (geographic, weighted, priority, performance). Traffic Manager is L4 (DNS-level), not L7 — use Front Door for L7 global routing.
**When to avoid.** Traffic Manager when you need L7 features (path-based routing, SSL termination, WAF). Front Door has superseded Traffic Manager for most HTTP workloads.
**Key decisions.** DNS TTL values (low TTLs for failover speed, higher for caching), Traffic Manager routing method, health probe configuration, nested profiles for complex routing.

## Data Platform

### Azure SQL Database
**When to use.** Relational workloads that need full SQL Server compatibility. Managed service with built-in HA, backups, patching. Serverless tier for intermittent workloads (auto-pause to save cost). Hyperscale for databases exceeding 4 TB.
**When to avoid.** Non-relational workloads. When you need multi-model capabilities (consider Cosmos DB). When PostgreSQL-specific features are needed (use Azure Database for PostgreSQL Flexible Server).
**Key decisions.** Purchasing model (DTU for simple, vCore for granular control), service tier (General Purpose vs Business Critical vs Hyperscale), elastic pools for multi-tenant SaaS (share resources across databases), geo-replication for DR, Managed Instance for SQL Server features not in SQL Database.

### Azure Cosmos DB
**When to use.** Globally distributed, multi-model database for low-latency reads and writes at any scale. Multi-region writes, tunable consistency (five levels from strong to eventual), sub-10ms reads. Document, key-value, graph, and column-family workloads.
**When to avoid.** Simple relational workloads (SQL Database is cheaper and simpler). When strong consistency across all operations is non-negotiable (Cosmos DB's strong consistency has higher latency and RU cost). When the cost model doesn't fit (RU-based pricing is hard to predict for complex query patterns).
**Key decisions.** API selection (NoSQL for documents, PostgreSQL for relational, MongoDB for compatibility, Cassandra for wide-column, Gremlin for graph, Table for key-value), consistency level (session consistency is the sweet spot for most apps), partition key design (this is THE critical decision — bad partition keys cause hot partitions and throttling), RU provisioning (autoscale vs manual), global distribution topology.

### Azure Storage (Blob, Table, Queue, Files)
**When to use.** Blob Storage for unstructured data (images, videos, backups, data lake). Table Storage for simple key-value (cheaper than Cosmos DB for basic lookups). Queue Storage for simple message queuing. Files for SMB/NFS file shares.
**When to avoid.** Table Storage when you need indexing, querying, or global distribution (use Cosmos DB). Queue Storage when you need advanced messaging features (use Service Bus). Blob Storage when you need a POSIX filesystem (use Azure NetApp Files or Azure Managed Lustre).
**Key decisions.** Storage account redundancy (LRS for dev, ZRS for production, GRS/GZRS for DR), access tier (Hot/Cool/Cold/Archive — lifecycle management policies to auto-tier), private endpoints, immutability policies for compliance, blob versioning and soft delete.

### Azure Database for PostgreSQL Flexible Server
**When to use.** PostgreSQL workloads on Azure. Full PostgreSQL compatibility with managed infrastructure. Better price-performance than Cosmos DB for relational patterns. Supports extensions (PostGIS, pgvector for AI workloads, Citus for distributed).
**When to avoid.** When you need multi-region writes (Cosmos DB). When SQL Server compatibility is required (Azure SQL). When the workload is non-relational.
**Key decisions.** Compute tier (Burstable for dev, General Purpose for most, Memory Optimized for analytics), high availability (zone-redundant with automatic failover), read replicas for read scaling, pgvector for AI/vector search, connection pooling (PgBouncer built-in).

## Messaging and Events

### Azure Service Bus
**When to use.** Enterprise messaging with guaranteed delivery, ordering, transactions, and dead-lettering. Queues for point-to-point, topics for pub/sub. When message processing requires at-least-once or exactly-once semantics.
**When to avoid.** High-throughput event streaming (use Event Hubs). Simple fire-and-forget notifications (use Event Grid). When the messaging features exceed what you need (Storage Queues are cheaper for simple queueing).
**Key decisions.** Standard vs Premium tier (Premium for VNet integration, JMS support, and predictable performance), queue vs topic, session support for ordered processing per logical group, dead-letter queue monitoring and alerting, duplicate detection window.

### Azure Event Hubs
**When to use.** High-throughput event streaming — telemetry ingestion, log aggregation, event sourcing, real-time analytics. Kafka-compatible API available. Millions of events per second. Capture to Storage or Data Lake for batch processing.
**When to avoid.** Command-style messaging that needs guaranteed processing and dead-lettering (use Service Bus). Low-volume messaging where the throughput unit minimums make it expensive.
**Key decisions.** Throughput units (Standard) vs Processing Units (Premium) vs Capacity Units (Dedicated), partition count (determines max consumer parallelism — can't be changed after creation), consumer group design, checkpoint storage (Blob Storage), retention period, Schema Registry for Avro/JSON schema governance.

### Azure Event Grid
**When to use.** Reactive event routing — responding to Azure resource events (blob created, resource provisioned) or custom events. Push-based delivery with filtering, retry, and dead-lettering. Event-driven architectures where producers don't know consumers.
**When to avoid.** High-throughput streaming (use Event Hubs). Ordered processing or transactions (use Service Bus). When consumers need to pull at their own pace (Event Grid pushes to endpoints).
**Key decisions.** System topics (Azure resource events) vs custom topics, event schema (Event Grid schema vs CloudEvents), subscription filtering (subject, event type, advanced filters), dead-letter destination, delivery retry policy, private endpoints for security.

## Deployment and Infrastructure

### Azure Resource Manager (ARM) / Bicep
**When to use.** All Azure infrastructure should be defined as code. Bicep is the Azure-native IaC language — compiles to ARM templates, simpler syntax, modules for reuse. First-party, always up-to-date with Azure API changes.
**When to avoid.** Multi-cloud infrastructure (use Terraform for cloud-agnostic IaC). When the team already has deep Terraform expertise and the Azure provider coverage is sufficient.
**Key decisions.** Bicep vs Terraform (Bicep for Azure-only, Terraform for multi-cloud or when the team knows it), module structure (per-resource-type modules, per-workload compositions), parameter files per environment, deployment scopes (resource group, subscription, management group), what-if validation before deployment.

### Azure DevOps / GitHub Actions
**When to use.** CI/CD pipelines for building, testing, and deploying Azure workloads. Azure DevOps for enterprises already in the Microsoft ecosystem with Boards/Repos/Artifacts. GitHub Actions for teams on GitHub with simpler pipeline needs.
**When to avoid.** Neither is wrong; choose based on where your code lives and what your team knows. Don't use both for the same project.
**Key decisions.** Pipeline-as-code (YAML in both), environment approvals and gates, service connection security (federated credentials with Managed Identity, not stored secrets), artifact management, deployment strategy (rolling, blue-green, canary), variable groups and secret management.

### Deployment Strategies on Azure
**Deployment slots (App Service, Functions).** Zero-downtime deployments via slot swap. Deploy to staging slot, warm it up, swap to production. Swap is a DNS-level pointer change — instant. Auto-swap for CI/CD automation. Slot-specific settings for connection strings that differ per environment.
**Blue-green with Traffic Manager or Front Door.** Route traffic between two identical environments. Deploy to the inactive environment, validate, shift traffic. More complex than slots but works for any compute type.
**Canary with Azure Front Door.** Weighted routing to send a percentage of traffic to the new version. Monitor error rates and latency before increasing. Roll back by shifting weight to zero.

## Monitoring and Operations

### Azure Monitor, Log Analytics, Application Insights
**When to use.** Always. Azure Monitor is the unified observability platform. Application Insights for application telemetry (traces, metrics, exceptions, dependencies), Log Analytics for centralized log querying (KQL), Monitor for alerts, dashboards, and autoscale rules.
**When to avoid.** Never for Azure workloads. Complement with Grafana or third-party tools if needed, but Azure Monitor should be the foundation.
**Key decisions.** Log Analytics workspace design (one per environment or one shared with RBAC), data retention (default 30 days, extend for compliance, archive for long-term), sampling rate for Application Insights (balance cost vs fidelity), alert rule design (metric alerts for speed, log alerts for complex conditions), action groups for notification routing.

### Azure Policy
**When to use.** Governance at scale — enforce tagging, restrict VM sizes, require encryption, deny public endpoints, audit compliance. Policies apply across subscriptions via management groups. Shift-left by evaluating in CI/CD pipelines.
**When to avoid.** Application-level business rules (Policy is for infrastructure governance).
**Key decisions.** Audit vs Deny effect (start with Audit to understand impact, graduate to Deny), initiative grouping (bundle related policies), exemptions for legitimate exceptions, custom policies for org-specific rules, remediation tasks for existing non-compliant resources.

## Cost Management

### Reserved Instances and Savings Plans
**When to use.** Predictable workloads that will run for 1-3 years. Reserved Instances for specific VM sizes in specific regions (up to 72% savings). Savings Plans for flexible commitment across VM families, regions, and services (up to 65% savings).
**When to avoid.** Variable or experimental workloads. Short-lived projects. When you can't predict the compute footprint for 1+ year.
**Key decisions.** Reservation scope (shared vs single subscription), reservation vs savings plan (reservations save more but are less flexible), coverage analysis using Azure Advisor recommendations, exchange and cancellation policies.

### Spot VMs
**When to use.** Fault-tolerant, interruptible workloads — batch processing, CI/CD agents, dev/test environments, training jobs. Up to 90% discount. Azure can evict with 30 seconds notice.
**When to avoid.** Production services that need availability. Stateful workloads that can't checkpoint and resume. When eviction would cause user-visible impact.
**Key decisions.** Eviction policy (deallocate vs delete), max price setting, combining with on-demand VMs in Scale Sets for availability, checkpointing strategy for long-running jobs.

### Cost Monitoring
**What it costs.** Azure costs are notoriously easy to surprise on — idle resources, premium tiers left on after testing, storage growing silently, egress charges.
**Key strategies.** Azure Cost Management budgets with alerts, daily cost anomaly review, resource tagging for cost attribution (enforce via Policy), Azure Advisor cost recommendations, regular rightsizing review, dev/test subscriptions with auto-shutdown, Cost Management exports for custom analysis.

## Common Failure Modes

- **Subscription limits and throttling.** Azure has per-subscription limits on resources (VMs, public IPs, Storage accounts) and per-resource API rate limits. Hitting these causes deployment failures or runtime throttling. Mitigation: review Azure subscription limits before design, request quota increases proactively, distribute across multiple subscriptions for large deployments, implement retry with backoff for API calls.
- **Region outage without multi-region.** Deploying everything to a single region. When that region has issues, the entire application is down. Mitigation: active-passive or active-active multi-region for critical workloads, geo-redundant storage, cross-region read replicas, Front Door or Traffic Manager for global routing.
- **Private endpoint DNS misconfiguration.** Private endpoints work via DNS resolution. If DNS zones aren't linked to the right VNets, or DNS forwarding isn't configured for hybrid networks, services resolve to public IPs and either fail (if public access is disabled) or bypass network isolation. Mitigation: centralized private DNS zone management, DNS resolution testing as part of deployment validation, conditional forwarders for on-premises resolution.
- **Managed Identity not propagated.** Deploying a resource with Managed Identity but forgetting to assign RBAC roles on the target resources. The identity exists but has no permissions. Fails at runtime with opaque 403 errors. Mitigation: include RBAC role assignments in IaC alongside the resource deployment, test authentication during deployment validation, use DefaultAzureCredential for local development fallback.
- **Cosmos DB hot partition.** Choosing a partition key with low cardinality or skewed distribution. One logical partition handles most requests, hitting the per-partition RU limit while overall provisioned RUs are underutilized. Mitigation: analyze access patterns before choosing partition key, use synthetic partition keys if natural keys are skewed, monitor per-partition metrics.
- **Storage account transaction throttling.** Azure Storage has per-account and per-partition throughput limits. High-frequency writes to sequentially-named blobs (timestamps, incrementing IDs) concentrate on one partition. Mitigation: add random prefixes to blob names, distribute across multiple storage accounts, use append blobs for log-style writes.
- **App Service plan overcommitment.** Running too many apps on a single App Service plan. CPU and memory are shared — one noisy app degrades all others. Mitigation: monitor per-app resource consumption, separate high-traffic apps into dedicated plans, use per-app scaling on Premium plans.
- **Stale deployment slot configuration.** Deployment slots have slot-specific and non-slot-specific settings. Swapping with wrong setting classification causes production to use staging connection strings or vice versa. Mitigation: explicitly classify every app setting, validate configuration after swap, use staging slot for smoke testing before swap.

## Anti-Patterns

- **Portal-only infrastructure.** Creating and configuring resources through the Azure Portal without IaC. Environments drift, disaster recovery is impossible, and changes are unauditable. Everything in production should be deployable from code.
- **Overprivileged identities.** Assigning Owner or Contributor at the subscription level because it's easier. Every identity should have the minimum role at the narrowest scope. Use PIM for elevated access with time-bound activation.
- **Secrets in app settings.** Storing database passwords, API keys, and connection strings directly in App Service or Function App configuration. Use Key Vault references — they look like app settings but resolve from Key Vault at runtime.
- **Public endpoints on data services.** Leaving SQL Database, Cosmos DB, or Storage accounts accessible from the public internet. Use private endpoints and disable public network access for anything holding real data.
- **Single subscription for everything.** Running dev, staging, production, and shared services in one subscription. No blast radius isolation, RBAC becomes unwieldy, and you'll hit subscription-level quotas. Use a subscription-per-environment or landing zone model.
- **Ignoring Azure Advisor.** Azure Advisor provides free, actionable recommendations for cost, security, reliability, and performance. Ignoring it means leaving money on the table and missing known issues. Review weekly.
- **Lift-and-shift without rearchitecting.** Moving on-premises VMs directly to Azure without evaluating managed alternatives. You get cloud costs without cloud benefits. Evaluate PaaS options for each workload — even partial modernization (database to managed, compute to App Service) reduces operational burden.
- **Not tagging resources.** Resources without tags can't be attributed to teams, projects, or cost centers. Enforce tagging via Azure Policy — at minimum: environment, team, project, and cost center.
- **DIY orchestration over Durable Functions.** Building custom state machines with queues and databases for multi-step workflows when Durable Functions handles the orchestration, checkpointing, and retry for you. Use the managed abstraction unless its constraints don't fit.
