---
name: "provider-privacy-analysis"
description: "Perform deep privacy, data governance, and model training policy analysis for AI inference providers, developer platforms, and LLM gateways."
---

# AI Provider Privacy & Data Governance Analysis

Perform deep, rigorous privacy and data governance audits of AI model providers, API platforms, and LLM gateways. The analysis focuses strictly on data sovereignty, payload privacy, model training risks, retention policies, and cross-border legal compliance.

---

## 🔍 Core Audit Methodology

When auditing an AI provider or gateway, retrieve and cross-reference official legal and technical sources:
1. **Terms of Service / Terms of Use** (especially sections on Intellectual Property, User Content, Model Training, and License Grants).
2. **Privacy Policy** (data collection, retention periods, third-party sharing, sub-processors).
3. **Developer / API Terms & Service Agreements** (commercial confidentiality, payload handling vs consumer UI).
4. **Trust Center, Security, & Compliance Docs** (SOC 2 Type II, ISO 27001, HIPAA, GDPR Data Processing Agreements (DPA)).
5. **Platform Settings & Developer Dashboards** (live opt-out toggles, telemetry controls, privacy modes).

---

## 📋 6 Authoritative Privacy Dimensions

Every deep provider privacy analysis must evaluate and report on these 6 dimensions:

### 1. Model Training & Fine-Tuning on Payloads
- **Default Policy**: Does the provider train, fine-tune, distill, evaluate, or align foundation/ML models on user inputs, prompts, completions, code, or attachments? (Default ON vs Default OFF).
- **Opt-Out Mechanism**: Is there an explicit opt-out mechanism? Where is it located (dashboard toggle, HTTP header, account settings, support request)? Does it apply prospectively or retroactively?
- **Licensing & Derivative Rights**: Do the Terms grant the provider a broad, perpetual, royalty-free license to create derivative datasets or share interaction data with third parties and research collaborators?

### 2. Data Retention & Zero Data Retention (ZDR)
- **Payload Retention Window**: How long are raw prompts, completions, embeddings, and files retained on disk? (Ephemeral/in-memory only, 30 days abuse monitoring, 6 months, or indefinitely).
- **Zero Data Retention (ZDR)**: Is strict ZDR available by default, configurable per request/key, or locked behind enterprise contracts?
- **Operational Metadata & Telemetry**: What metadata is permanently logged (token counts, timestamps, IP addresses, client headers, billing records, model IDs)?

### 3. Tier & Surface Differences (Free vs Paid vs API vs Web UI)
- **Consumer Web Playground vs Developer API**: Does the free playground/chat UI train on data while the API provides strict confidentiality?
- **Free Tier vs Paid Tier**: Are free tier users subjected to payload logging and model training as payment-in-kind, while paid/consumption tiers are exempted?
- **Enterprise & VPC Deployments**: Are dedicated instances, VPC deployments, or on-premise container distributions available where the provider has zero data access?

### 4. Infrastructure, Routing & Third-Party Sub-processors
- **Architecture Role**: Is the provider a first-party foundation model developer/host or an intermediary proxy/routing gateway?
- **Upstream & Downstream Processing**: If requests are routed through third-party hosting partners (e.g. Together AI, Fireworks, AWS Bedrock, CoreWeave, Azure, Lambda Labs), do those third parties enforce independent data retention and training terms?
- **Data Leakage in Routing**: Does the gateway log payloads before forwarding, or pass them transparently?

### 5. Legal Jurisdiction, Sovereignty & Regulatory Compliance
- **Corporate Entity & Governing Law**: Where is the legal entity incorporated (e.g., US Delaware/California, EU member state, Canada, Singapore, China)?
- **Data Center & Inference Locations**: Where are physical inference compute clusters and storage located? Can EU users enforce data residency?
- **Regulatory Frameworks & Certifications**: GDPR compliance, EU Standard Contractual Clauses (SCCs), SOC 2 Type II, ISO 27001, HIPAA.
- **Government Access Risk**: Legal vulnerability to foreign government compelled-disclosure orders (e.g., US CLOUD Act / FISA 702, China Cybersecurity Law & PIPL).

### 6. Actionable Privacy Configuration Checklist
- Provide precise, step-by-step instructions to maximize privacy:
  - Specific dashboard URLs and toggle locations.
  - Required API request headers or parameters (e.g., `privacy_mode`, `no-log`).
  - Recommended combos, endpoints, or tier selections.

---

## 📊 Standardized Report Structure

Always format the final provider privacy analysis following this structured template:

```markdown
# Privacy & Data Governance Analysis: <Provider Name>

## 📌 Executive Summary & Privacy Matrix

| Privacy Dimension | Status / Policy | Risk Level |
| :--- | :--- | :--- |
| **Model Training on Payloads** | Default: [OFF / ON / Configurable] | [Safe / Caution / High Risk] |
| **Data Retention Duration** | [Ephemeral / 30 Days / Indefinite] | [Safe / Moderate / Risky] |
| **Zero Data Retention (ZDR)** | [Available / Enterprise Only / None] | [Safe / Moderate / Risky] |
| **Free vs Paid Differences** | [Identical / Free Trains, Paid Doesn't] | [Safe / Warning] |
| **Infrastructure & Routing** | [First-Party Host / Third-Party Gateway] | [Direct / Multi-Hop] |
| **Legal Jurisdiction** | [Country / State / GDPR Status] | [Low / Medium / High Risk] |

**Overall Privacy Verdict**: [🟢 Privacy-First / 🟡 Moderate Caution / 🔴 High Exposure / ⛔ Critical Risk]

---

## 1. Model Training & Data Licensing
- **Training Rights**: [Detailed breakdown from Terms of Service]
- **Opt-Out Mechanism**: [Exact instructions and scope]
- **Derivative Datasets**: [Third-party sharing / research rights]

## 2. Retention Periods & Zero Data Retention (ZDR)
- **Raw Payloads (Prompts/Completions)**: [Storage timeline and abuse monitoring policies]
- **Metadata & Telemetry**: [What is logged and retained]
- **ZDR Availability**: [How to enable zero retention]

## 3. Tier & Platform Comparison
- **Free Tier vs Paid API**: [Key contractual differences]
- **Web UI vs Developer API**: [Playground vs programmatic inference]
- **Enterprise / Private VPC**: [Private deployment options]

## 4. Architecture, Sub-processors & Infrastructure
- **Model Hosting**: [Owned clusters vs third-party cloud infrastructure]
- **Gateway / Proxy Routing**: [Downstream provider data policies]

## 5. Legal Jurisdiction, Sovereignty & Compliance
- **Corporate Entity & Headquarters**: [Entity name, location, applicable law]
- **Data Residency & Cross-Border Transfers**: [Server regions, GDPR compliance, SCCs]
- **Certifications**: [SOC 2, ISO 27001, HIPAA]
- **Foreign Surveillance & Legal Exposure**: [US CLOUD Act, Chinese CSL/PIPL, etc.]

---

## 🛠️ Actionable Privacy Hardening Checklist
1. **[Action Item 1]**: [Exact toggle, URL, or API header to apply]
2. **[Action Item 2]**: [Tier/endpoint recommendation]
3. **[Action Item 3]**: [Gateway / proxy hardening recommendation]
```
