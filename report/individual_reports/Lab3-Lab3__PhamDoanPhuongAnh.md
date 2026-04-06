# REPORT_PHAM_DOAN_PHUONG_ANH

# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Pham Doan Phuong Anh  
- **Student ID**: 2A202600257  
- **Date**: 2026-04-06  

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implemented**:  
  - `agent/react_loop.py` – Core ReAct loop handling (`Thought → Action → Observation`)  
  - `agent/parser.py` – Parsing structured outputs from Ollama  
  - `tools/calendar_tool.py` – Google Calendar API integration  
  - `auth/auth_handler.py` – Authentication handling  
  - `chatbot/rule_based_guard.py` – Rule-based fallback system  

- **Code Highlights**:  
  - Implemented rule-based guardrails to prevent hallucination:
    ```python
    if "booking confirmed" in response and not tool_called:
        return "⚠️ Please confirm details before booking."
    ```
  - Added loop validation to ensure:
    - No skipping `Action`
    - No fake success responses
    - Proper step sequencing  

  - Ensured consistency by enforcing tool usage before final answers  

- **Documentation**:  
  The system follows a ReAct architecture:

  1. User input → LLM (Ollama)  
  2. LLM generates:
     - `Thought`
     - `Action`
     - `Action Input`  
  3. Backend executes tool (Google Calendar API)  
  4. Tool returns `Observation`  
  5. Loop continues until final answer  

  My main contribution was stabilizing the loop by:
  - Enforcing correct structure  
  - Reducing hallucination  
  - Adding fallback and validation logic  

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**:  
  The agent frequently hallucinated successful bookings without calling the calendar tool. It also skipped steps and directly returned final answers.

- **Log Source**:
  ```json
  {
    "thought": "User wants to book a meeting tomorrow at 3PM",
    "action": null,
    "final_answer": "Your meeting has been successfully booked."
  }

- **Diagnosis**:  
  Causes of the issue:
  - Weak prompt constraints  
  - Limitations of local model (Ollama)  
  - No strict enforcement of tool usage  
  - Missing context tracking  

  The model assumed task completion instead of verifying execution.

- **Solution**:
  - Added rule-based validation layer  
  - Enforced tool call before final response  

  Improved prompt instructions:
  > Never confirm booking without calling the tool  

  Added loop guard:
  ```python
  if not action and not is_final_step:
      retry_with_clarification()

* Reduced unnecessary context to improve consistency

**Result:**

* Reduced hallucination
* Improved reliability
* More deterministic agent behavior

---

## II. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning

The **Thought** block provides explicit reasoning steps, helping:

* Break down tasks
* Improve debugging
* Increase transparency

**However**, it does not always improve correctness compared to a simple chatbot.
---

## V. Additional Reflection (Optional)

During this lab, I learned several important practical lessons beyond just implementing the agent:

- **Data Formatting**:  
  I realized the importance of strict data standards when working with external APIs.  
  For example, Google Calendar requires **ISO 8601 format** for date and time.  
  Incorrect formatting can completely break the system even if the logic is correct.

- **System Integration**:  
  I gained a clearer understanding of how different components connect:
  - Frontend (user input)  
  - Backend (API handling)  
  - Agent (reasoning + tool selection)  
  - External services (Google Calendar)  

  Small mismatches (e.g., request/response schema) can cause the entire pipeline to fail.

- **Interface Contract Design**:  
  One key issue in our project was the **lack of a clearly defined contract** between:
  - Backend request format (`POST` body)  
  - Agent input/output structure  

  This led to integration failure at the final stage, even though individual components were working.

- **Time Allocation & Team Coordination**:  
  As the team leader, I learned that:
  - It is not enough to assign tasks — **alignment must be enforced early**  
  - Critical components (like API contracts) must be **validated before final integration**  
  - Delays in one part of the system can block the entire pipeline  

  Although we were unable to fully demo the system due to incomplete integration, this experience highlighted the importance of:
  - Early testing between components  
  - Clear communication and accountability  
  - Setting concrete deadlines for intermediate results  

**Overall Lesson for myself**:  
A system can fail not because of complex algorithms, but because of **small inconsistencies in data format, interface design, and team coordination**.

### 2. Reliability

The ReAct agent performed **worse** than a chatbot when:

* Tasks are simple
* Output format breaks
* Tool calls fail

**Chatbots are:**

* Faster
* More stable
* Less dependent on rigid structure

### 3. Observation

The **Observation** step:

* Grounds the agent in real data
* Reduces hallucination
* Guides the next reasoning step

**Limitation:**  
If the observation is unclear or incomplete, the agent can still fail.

---

## III. Future Improvements (5 Points)

### How would you scale this for a production-level AI agent system?

#### Scalability
* Use asynchronous queues (Celery, Redis)
* Build a modular tool system
* Support multi-agent architecture

#### Safety
* Add a Supervisor LLM to validate outputs
* Enforce policy constraints
* Use structured schema validation (Pydantic, JSON Schema, etc.)

#### Performance
* Integrate vector database (FAISS, Chroma, Pinecone)
* Cache tool responses
* Optimize prompt size and token usage

---

**End of Report**
