---
name: "provider-privacy-analysis"
description: "Perform deep privacy, data governance, and model training policy analysis for AI inference providers, developer platforms, and LLM gateways."
---

# AI Provider Privacy & Data Governance Analysis

Perform fast, schematic, and high-density privacy audits of AI model providers, developer platforms, and LLM gateways. Avoid conversational prose and narrative filler; focus strictly on preliminary eligibility (inference & free tier), third-party gateway routing risks, paywalled privacy controls, actionable opt-out steps, and before/after privacy states.

---

## Preliminary Pre-Check (Before Deep Audit)

Always establish these 2 fundamental operational facts first:
1. **Inference Capability & Provider Archetype**:
   - First-Party Model Developer/Host (trains and runs proprietary weights directly).
   - Dedicated Inference Cloud (hosts open-weight models on owned hardware).
   - Intermediary Gateway / Proxy Router (aggregates and forwards requests to external third-party hosts).
2. **Free Tier Availability**:
   - Permanent Free Tier (zero-cost permanent quotas or rate-limited access).
   - Recurring Developer Quota (monthly/daily free refresh).
   - One-Time Promotional Credits (temporary trial balance).
   - Paid Only (no free inference).

---

## Core Investigation Dimensions

Audit and extract the following technical and legal parameters:

1. **Third-Party Gateway & Passthrough Exposure**:
   - Does the platform route requests to external third-party providers (e.g. Together, Fireworks, AWS Bedrock, Cerebras, Groq)?
   - Are payloads subjected to disparate third-party Terms of Service and Privacy Policies outside user visibility and control?
2. **Paywalled Privacy Discrimination (Free vs Paid Tiers)**:
   - Are privacy controls (Zero Data Retention, training opt-out toggles, non-logging guarantees, DPAs) reserved exclusively for paid or Enterprise plans?
   - Are free-tier users used as training data by default with no self-serve opt-out?
3. **Request Payload Training**:
   - Default stance on utilizing prompts, completions, attachments, and code for model training, fine-tuning, or alignment.
4. **Data Retention & ZDR**:
   - Ephemeral memory vs persistent disk storage, retention duration (e.g. 30 days abuse logging vs indefinite), and strict ZDR availability.
5. **Jurisdiction & Legal Sovereignty**:
   - Incorporated entity, compute cluster locations, GDPR compliance, and vulnerability to foreign surveillance laws (US CLOUD Act, PRC CSL/PIPL).

---

## Standard Output Format

Always format the report strictly using this concise, schematic template:

```markdown
# Provider Privacy Audit: <Provider Name>

## 1. Preliminary Classification & Free Tier

- **Provider Archetype**: [First-Party Model Builder / Dedicated Inference Host / Intermediary Gateway]
- **Direct Model Inference**: [Yes / No (Passthrough only)]
- **Free Tier Availability**: [Permanent Free Tier / Recurring Quota / One-Time Trial / Paid Only]
- **Gateway Passthrough Risk**: [Direct (No third parties) / Multi-Hop (Forwards to external providers)]

---

## 2. Quick Privacy Matrix

| Dimension | Default Free/Cloud State | Hardened / Paid / Local State |
| :--- | :--- | :--- |
| **Model Training on Payloads** | [ON / OFF / Allowed by default] | [Disabled / Blocked / Local] |
| **Privacy Options Paywalled?** | [Yes (Paid/Enterprise only) / No] | [Available / Local execution] |
| **Gateway Third-Party Risk** | [Direct / Forwarded to 3rd parties] | [Direct / Isolated] |
| **Payload Data Retention** | [Indefinite / 30 Days / Ephemeral] | [0 Days / Local execution] |
| **Zero Data Retention (ZDR)** | [Unavailable on Free / Enterprise] | [100% Achieved via Local / Paid] |
| **Data Residency & Jurisdiction** | [Country / Cloud Host] | [Local Hardware / Sovereign] |

**Privacy Verdict**: [Safe / Moderate Caution / High Exposure / Critical]

---

## 3. Gateway Passthrough & Upstream Provider Analysis

- **Routing Architecture**: [Explain if data stays on provider servers or routes externally]
- **Upstream Terms Risk**: [If gateway: lists third-party providers and unmanageable terms risk]

---

## 4. Tier Discrimination & Paywalled Privacy Controls

- **Free Tier Privacy Restrictions**: [Explain if free users are trained on / cannot opt out]
- **Paid / Enterprise Protections**: [Features unlocked on paid tiers: ZDR, no-training guarantees, DPAs]
- **Self-Hosted / Local Weights Alternative**: [Availability of GGUF/MLX/ONNX open weights to bypass cloud tiers]

---

## 5. Step-by-Step Full Opt-Out & Hardening Action Plan

1. **[Step 1: UI / Account Action]**: [Exact toggle, URL, or settings page to disable data sharing]
2. **[Step 2: API / Gateway Action]**: [Headers, request parameters, or OmniRoute filter to use]
3. **[Step 3: Web / Cookie Action]**: [Cookie rejection, GPC signal, analytics opt-out]
4. **[Step 4: Sovereign Alternative]**: [Local deployment method to eliminate cloud exposure completely]

---

## 6. Before vs. After Opt-Out Comparison

| Metric | Default Setup | After Applying Hardening & Opt-Outs |
| :--- | :--- | :--- |
| **Prompt/Code Privacy** | [Exposed / Trained on] | [100% Private / Not logged] |
| **Model Training Risk** | [Active] | [Eliminated] |
| **Third-Party Terms Exposure** | [Exposed to upstream policies] | [Zero exposure] |
| **Cloud Surveillance / CLOUD Act** | [Subject to foreign law] | [Zero exposure (Local/Airgapped)] |
```
