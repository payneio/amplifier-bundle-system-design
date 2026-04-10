# The 5 Adversarial Review Perspectives

Stress-test every design from these five perspectives before committing to it. Each perspective has a driving question and specific evaluation concerns.

---

## 1. SRE -- "How does this fail in production?"

- Failure modes and blast radius
- Single points of failure
- Behavior under partial outages and load (graceful degradation vs cliff-edge failure)
- Recovery procedures and automation potential
- Monitoring, alerting, and SLO needs
- On-call runbook requirements

## 2. Security Reviewer -- "What is the abuse path?"

- Attack surface and untrusted input entry points
- Authentication and authorization boundaries (where are they weakest?)
- Sensitive data protection (at rest, in transit, in logs)
- Lateral movement risk if one component is compromised
- Rate limiting, abuse prevention, and input validation gaps
- Supply chain and third-party dependency risks
- Regulatory or compliance requirements

## 3. Staff Engineer -- "Where is the hidden complexity?"

- Things that look simple but are hard to implement correctly
- Implicit assumptions that break as the system evolves
- Coupling that isn't visible in the architecture
- Testability and debugging difficulty
- Wrong-level abstractions (too concrete or too abstract)
- Technical debt being introduced (intentional vs accidental)

## 4. Finance Owner -- "What cost curve appears later?"

- Variable costs that scale with usage (compute, storage, bandwidth, API calls)
- Superlinear cost growth (growing faster than usage)
- Cost cliffs (tier jumps, reserved capacity thresholds)
- Hidden operational costs (team time, on-call burden, vendor management)
- Vendor lock-in and switching costs
- Cost of the simplest credible alternative (is the additional spend justified?)

## 5. Operator -- "What becomes painful at 2am?"

- Zero-downtime deployment and rollback capability
- Diagnostic speed (are logs, metrics, traces sufficient?)
- Manual intervention during normal operation and incidents
- Health verification after deployment or incident
- Upstream dependency change management
- Configuration manageability and safe defaults
- Missing documentation

---

## Output Structure

After reviewing from all 5 perspectives, produce:

**Critical Risks** -- issues that could cause outages, data loss, security breaches, or cost blowouts. Must be addressed before proceeding.

**Significant Concerns** -- issues that increase operational burden, technical debt, or long-term cost. Should be addressed or explicitly accepted with reasoning.

**Observations** -- minor issues, suggestions, or things to monitor. Not blocking.

**What the Design Gets Right** -- acknowledge what is well-designed. Critics who only find flaws lose credibility.

**Recommended Next Steps** -- top 3-5 actions to take before proceeding, ordered by risk reduction.