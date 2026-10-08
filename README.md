# ClaimPilot

### AI-Powered Motor Insurance Claim Assessment

> **We don't replace the surveyor. We prepare the surveyor.**

ClaimPilot is an insurer-side AI system designed to help surveyors and claims teams assess motor insurance claims faster.

It brings together claim documents, accident descriptions, vehicle damage images, indicative part pricing, cost calculations, investigation indicators, and survey-route recommendations into one consolidated assessment.

---

## 🚗 Problem

Motor insurance claim assessment requires the surveyor to review and combine information from multiple sources:

- Insurance policy documents
- Registration Certificate (RC)
- Driving Licence (DL)
- Accident description
- Vehicle damage images
- Damaged components
- Repair and replacement requirements
- Indicative part prices

This information is often fragmented, requiring significant manual review before the surveyor can make an assessment.

### The result

**Scattered information → Manual review → More assessment effort → Slower claim processing**

ClaimPilot helps organize and analyze this information before it reaches the surveyor.

---

## 💡 Solution

ClaimPilot acts as an intelligent assessment layer between the insurer's existing claim system and the surveyor.

It uses specialized agents for different parts of the assessment workflow:

1. **Document Agent** checks document presence and basic completeness.
2. **Damage Agent** analyzes vehicle images and identifies visible damage.
3. **Pricing Agent** searches public web sources for indicative part prices.
4. **Cost Engine** performs deterministic repair-cost calculations.
5. **Investigation Agent** identifies potential investigation indicators.
6. **Triage Agent** recommends the appropriate survey route.
7. **Claim Agent** orchestrates the complete workflow and combines the results.

The final assessment is presented through a **Surveyor Dashboard** and a **PDF Report**.

---

## 🏗️ System Architecture

```text
┌──────────────────────────────────────────────┐
│                    INPUT                     │
│                                              │
│  Insurance Policy (PDF)                     │
│  Registration Number (RC)                   │
│  Driving Licence (DL)                       │
│  Vehicle Damage Images                      │
│  Accident Description                       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│          FRONTEND — SURVEYOR INTERFACE       │
│                    Streamlit                 │
│                                              │
│  Upload / View Claim Data                   │
│  View AI Assessment                         │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             CLAIM AGENT — ORCHESTRATOR       │
│                                              │
│  Coordinates specialized agents             │
│  Passes data between agents                 │
│  Generates final assessment                 │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 LLM SERVICE                  │
│              Google Gemini                  │
│                                              │
│  Multimodal image + text analysis            │
└──────────────────────┬───────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     Document       Damage       Pricing
      Agent         Agent         Agent
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Cost Engine  │
              │   Python       │
              │                │
              │ Parts          │
              │ Labour         │
              │ Paint          │
              │ Allowances     │
              └───────┬────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
      Investigation          Triage
          Agent               Agent
             │                 │
             └────────┬────────┘
                      ▼
┌──────────────────────────────────────────────┐
│              SURVEYOR ASSESSMENT             │
│                                              │
│  Surveyor Dashboard                         │
│  Preliminary Cost Exposure                  │
│  Investigation Indicators                   │
│  Recommended Survey Route                   │
│                                              │
│  PDF Assessment Report                      │
└──────────────────────────────────────────────┘
