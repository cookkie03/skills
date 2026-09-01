---
name: "provider-privacy-analysis"
description: "Perform deep privacy, data governance, and model training policy analysis for AI inference providers, developer platforms, and LLM gateways."
---

# AI Provider Privacy & Data Governance Analysis

Perform fast, schematic, and high-density privacy audits of AI model providers, developer platforms, and LLM gateways. Avoid conversational prose and narrative filler; focus strictly on technical data handling, request-level privacy options, actionable opt-out steps, and before/after privacy posture states.

---

## Core Investigation Checklist

When auditing a provider, extract and verify these 5 core data points:

1. **Request Payload Training**: Default stance on using prompts, completions, attachments, and code for model training, fine-tuning, or alignment.
2. **Opt-Out Paths**: Exact UI toggles, API headers, account forms, or configuration parameters to disable training and logging.
3. **Retention & ZDR**: Ephemeral memory vs persistent logging, retention duration (e.g., 30 days vs indefinite), and Zero Data Retention availability.
4. **Surface & Tier Separation**: Policy differences across Free Web Playground, Paid API, Self-Hosted/Local Weights, and Enterprise VPC.
5. **Infrastructure & Jurisdiction**: Cloud hosting entities, data centers (US vs EU vs PRC), sub-processors, and governing law.

---

## Standard Output Format

Always format the report strictly using this concise, schematic template:

```markdown
# Provider Privacy Audit: <Provider Name>

## 1. Quick Privacy Matrix

| Dimension | Default Cloud State | Hardened / Post Opt-Out State |
| :--- | :--- | :--- |
| **Model Training on Payloads** | [ON / OFF / Allowed] | [Disabled / Not Applicable / Blocked] |
| **Payload Data Retention** | [Indefinite / 30 Days / None] | [0 Days / Ephemeral / Blocked] |
| **Zero Data Retention (ZDR)** | [None / Enterprise Only] | [Achieved via Local / Custom DPA] |
| **Telemetry & Metadata** | [Logged / Shared] | [Minimized / Isolated] |
| **Data Residency & Jurisdiction** | [Country / Cloud Host] | [Local Hardware / Sovereign] |

**Privacy Verdict**: [Safe / Moderate Caution / High Exposure / Critical]

---

## 2. Request Privacy Options

- **Cloud Web / Playground**: [Exact options available on web UI]
- **Developer API**: [API parameters, headers, or terms governing API calls]
- **Local / Edge Deployment**: [Availability of open weights, GGUF/MLX/ONNX formats for local execution]

---

## 3. Step-by-Step Full Opt-Out & Hardening Action Plan

1. **[Step 1: UI / Account Action]**: [Exact toggle, URL, or settings page to disable data sharing]
2. **[Step 2: API / Gateway Action]**: [Headers, request parameters, or OmniRoute filter to use]
3. **[Step 3: Web / Cookie Action]**: [Cookie rejection, GPC signal, analytics opt-out]
4. **[Step 4: Sovereign Alternative]**: [Local deployment method to eliminate cloud exposure completely]

---

## 4. Before vs. After Opt-Out Comparison

| Metric | Default Setup | After Applying Hardening & Opt-Outs |
| :--- | :--- | :--- |
| **Prompt/Code Privacy** | [Exposed / Trained on] | [100% Private / Not logged] |
| **Model Training Risk** | [Active] | [Eliminated] |
| **Cloud Surveillance / CLOUD Act** | [Subject to foreign law] | [Zero exposure (Local/Airgapped)] |
```
