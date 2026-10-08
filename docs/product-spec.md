# ClaimPilot
## AI Claims Intelligence & Triage Platform

## 1. Product Vision

ClaimPilot is an AI-powered claims intelligence platform for motor insurance companies.

Its purpose is to reduce the time required to process motor insurance claims by automatically analyzing claim documents, insurance policy information, vehicle damage evidence, repair estimates and historical claim information.

ClaimPilot does NOT replace the surveyor or insurer.

The system prepares a structured pre-survey assessment and recommends how the claim should be routed.

Final consequential decisions remain with an authorized human surveyor or insurer employee.

---

## 2. Primary User

The primary user is an insurance claims employee or motor insurance surveyor.

Secondary users:

- Claims processing teams
- Insurance operations teams
- Surveyors
- Garages
- Customers

---

## 3. Core Problem

Motor insurance claims involve multiple parties:

Customer
Garage
Surveyor
Insurance company

Claims can be delayed because information is incomplete, documents must be manually reviewed, damage must be assessed, repair estimates must be checked, and claims must be manually routed.

ClaimPilot aims to reduce this operational workload.

---

## 4. Core Workflow

1. A new motor insurance claim is created.
2. Claim documents are uploaded.
3. Vehicle damage photographs are uploaded.
4. Accident information is entered.
5. ClaimPilot analyzes the policy.
6. ClaimPilot validates documents.
7. ClaimPilot analyzes vehicle damage.
8. ClaimPilot analyzes the garage repair estimate.
9. ClaimPilot checks for anomalies.
10. ClaimPilot generates a pre-survey claim report.
11. ClaimPilot assigns a triage recommendation:
    - Fast-track
    - Remote survey
    - Physical survey
12. A surveyor reviews the AI-generated report.
13. The surveyor makes the final decision:
    - Approve
    - Request more information
    - Physical inspection

---

## 5. AI Agents

### Orchestrator Agent

Coordinates all other agents.

### Policy Agent

Reads the insurance policy and extracts:

- Policy number
- Vehicle information
- IDV
- Coverage
- Deductible
- Add-ons
- Exclusions
- Relevant conditions

The Policy Agent must provide evidence from the source document whenever possible.

### Document Agent

Checks whether required claim documents are present and extracts relevant information.

### Damage Agent

Analyzes vehicle photographs and identifies:

- Vehicle
- Damaged parts
- Damage severity
- Confidence

The system must clearly label computer-vision outputs as AI assessments rather than definitive surveyor conclusions.

### Estimate Agent

Analyzes the garage repair estimate and compares it with the AI damage assessment.

### Fraud/Anomaly Agent

Identifies suspicious inconsistencies or anomalies.

It must NEVER definitively state that fraud has occurred.

Instead it should output:

- Low concern
- Review recommended
- Investigation recommended

with reasons.

### Triage Agent

Combines outputs from all agents and recommends:

- Fast-track
- Remote survey
- Physical survey

The recommendation is advisory only.

---

## 6. Human-in-the-loop

Human approval is mandatory for consequential decisions.

The system must never autonomously:

- reject a claim
- approve a final settlement
- declare fraud
- make a legally binding coverage decision

The surveyor remains the final decision-maker.

---

## 7. Claim Output

Every analyzed claim should generate:

### Claim Summary

- Claim ID
- Policy number
- Vehicle
- Claim type
- Reported loss
- Estimated damage

### Document Status

- Documents received
- Missing documents
- Document confidence

### Damage Assessment

- Damaged components
- Severity
- Confidence

### Estimate Analysis

- Garage estimate
- AI estimated range
- Variance

### Anomaly Analysis

- Risk indicators
- Reasons
- Recommended review level

### Triage

- Recommended route
- Reason
- Confidence

### Surveyor Action

- Approve
- Request more information
- Physical inspection

---

## 8. Important Product Principle

ClaimPilot is not an insurance chatbot.

It is an agentic workflow automation and claims intelligence platform.

The AI should perform actions and coordinate information between different stages of the claim.

---

## 9. Hackathon MVP

The MVP will use simulated insurance data.

It does not require integration with a real insurance company's internal systems.

The demo will use:

- Sample insurance policy
- Sample vehicle documents
- Sample accident description
- Sample vehicle photographs
- Sample garage repair estimate
- Sample previous claim

The system should demonstrate at least two different claims:

### Claim A

Low-complexity claim.

Recommended route:

Remote survey / fast-track.

### Claim B

High-complexity claim with anomalies.

Recommended route:

Physical survey.

This demonstrates intelligent claim triage.

---

## 10. Technology Direction

Frontend:

Streamlit

Backend:

Python / FastAPI

Database:

SQLite

RAG:

Vector database + embeddings

LLM:

Configurable API provider

Computer Vision:

Vision-capable AI model/API

PDF processing:

PyMuPDF or equivalent

Agent orchestration:

Python-based orchestration or LangGraph

---

## 11. Design Principle

The system must be explainable.

Whenever possible, AI outputs should show:

- Evidence
- Source
- Reason
- Confidence

The system should never present an uncertain AI assessment as a confirmed fact.