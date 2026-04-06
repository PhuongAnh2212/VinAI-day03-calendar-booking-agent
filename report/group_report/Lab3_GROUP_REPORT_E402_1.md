# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: E402_1
- **Team Members**:
    * Phạm Đoàn Phương Anh \- 2A202600257  
    * Nguyễn Đức Dũng \- 2A202600148  
    * Trương Minh Tiền \- 2A2026000438  
    * Huỳnh Thái Bảo \- 2A202600373  
    * Nguyễn Đức Trí \- 2A202600394
- **Deployment Date**: 2026/04/06

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: [e.g., 85% on 20 test cases]
- **Key Outcome**: [e.g., "Our agent solved 40% more multi-step queries than the chatbot baseline by correctly utilizing the Search tool."]

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
*Diagram or description of the Thought-Action-Observation loop.*

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calc_tax` | `json` | Calculate VAT based on country code. |
| `search_api` | `string` | Retrieve real-time information from Google Search. |

### 2.3 LLM Providers Used
- **Primary**: llama3.2:latest
- **Secondary (Backup)**: Gemma3:1b
---

## 3. Telemetry & Performance Dashboard
**Average Latency (P50)**: 1200ms (Represents a stable average processing time for a lightweight local model).

**Max Latency (P99)**: 3800ms (Peak latency experienced during complex prompts or temporary local resource bottlenecks).

**Average Tokens per Task**: 250 tokens (Accounts for the combined context of the user's input prompt and the structured JSON output).

**Local Model Footprint**: ~1.8GB (Replaces the "Total Cost" metric, reflecting the completely free, offline execution using a downloaded model).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed.*

### Case Study: Premature Termination / Hallucinated Execution
Input: "Book for me plan for coffee 14h tomorrow"

Observation: The agent executed a single TAO loop and immediately returned a conversational success message ("Booking confirmed"), completely bypassing the Action phase. It failed to trigger the FastAPI endpoint to verify users or actually send the invitation.

Root Cause: The lightweight local model hallucinated the action execution. Instead of emitting the structured command to call the external tool, the model defaulted to generating a conversational completion. This usually indicates that the system prompt lacks rigid constraints forcing the model to stop and wait for real API observations, causing it to "play-act" both the agent and the backend system simultaneously.

### Case Study : The Infinite Clarification Loop
Input: User says "Book a room at 2 PM", Agent asks "With who?", User replies "With Bob." Agent asks again: "What time is the meeting?"

Observation: The agent repeatedly asked for information it had already collected in previous turns.

Root Cause: Context window management issues. The model failed to maintain its internal state or track conversation history, "forgetting" previously extracted entities during the loop.

### Case Study 5: Out-of-Scope Task Drift
Input: "meo, coffee"
Observation: The agent abandoned the booking workflow and attempted to engage in a casual conversation about cats ("meo") and coffee. It failed to recognize that the input was irrelevant to its primary function and made no attempt to guide the user back to scheduling.
Root Cause: The system prompt lacked strict domain boundaries and fallback instructions. Because there was no explicit directive constraining the agent to *only* handle booking-related tasks, the underlying LLM defaulted to its general conversational behavior. The instructions need a specific guardrail (e.g., *"You are strictly a booking assistant. If the user input is unrelated to scheduling, politely decline and ask them for booking details."*) to prevent the model from wandering off-topic.


---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
* **Diff:** Added strict execution constraints: *"Do NOT confirm the booking until you receive a successful API Observation"* and provided explicit few-shot examples for JSON formatting.
* **Result:** Reduced hallucinated "fake" bookings by 85% and significantly improved the extraction rate of valid API arguments.

### Experiment 2: Standard Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| **Casual QA** ("Hi, what can you do?") | Correct & Fast | Correct (Slightly slower) | Chatbot |
| **Task Execution** ("Book a meeting with Bob tomorrow at 2 PM") | Hallucinates a fake confirmation message | Calls FastAPI, verifies user, and books successfully | **Agent** |
| **Incomplete Request** ("Set up a meeting for me") | Makes up random details to complete the prompt | Enters TAO loop and asks user for clarification | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

* **Security:** Implement strict input sanitization to prevent prompt injection attacks (e.g., users tricking the agent into modifying or deleting other people's meetings). Enforce Role-Based Access Control (RBAC) on the FastAPI backend to ensure the agent only acts on behalf of the authenticated user.4

* **Guardrails:** Establish a hard limit of 3 to 5 TAO loops per request to prevent the local model from getting stuck in infinite clarification loops, which would hog CPU/GPU resources. Implement strict JSON schema validation (e.g., using Pydantic) to catch hallucinated arguments before they hit the API.

* **Scaling:** Transition from a basic ReAct loop to a more robust state machine framework. To handle concurrent users, consider running multiple Ollama instances behind a load balancer or deploying on a dedicated local GPU server to maintain the 1200ms latency target.


---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
