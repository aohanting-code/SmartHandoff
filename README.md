# SmartHandoff

An intelligent customer support prototype with mixed-initiative
human escalation.

**Module:** Intelligent Interactive Systems  
**Assignment:** Assignment 2 — Project Report   

## 1. Project Status

SmartHandoff addresses the difficulty customers experience when
trying to reach a human agent through an AI customer service
chatbot.

### Implemented

- Conversational customer support interface.
- Gemini-based intent and interaction-signal classification.
- Local rule-based analysis and fallback.
- Conversation context and repeated-issue tracking.
- User-initiated and system-initiated escalation.
- Capability-gap detection.
- Editable handoff context before confirmation.
- Decision inspector showing analysis and execution states.
- Bounded API retry and output validation.
- Loading feedback, button-state management and issue reset.

### Simulated

- Order, delivery, refund and return records.
- Human-support queue and ticket creation.
- Cancellation of simulated handoff requests.

### Limitations and Future Work

No real customer service agent, payment system or order-management
service is connected. Conversation state is stored in memory and
is lost when the application restarts.

Local rules may misclassify unfamiliar expressions. Frustration
signals represent detected language rather than verified emotional
states. Handoff context is a transcript excerpt, not an
AI-generated summary.

Future development could include real service integration,
more robust intent recognition and evaluation with representative
users.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and state management |
| Flask | Web server and interaction API |
| HTML, CSS, JavaScript | Interface and interaction feedback |
| Google Gemini API | Structured language classification |
| Local rules | Manual-request safeguard and fallback |
| JSON | Fictional customer service records |
| pytest | Automated regression testing |
| Git and GitHub | Version control and development evidence |
| ChatGPT | Development and documentation assistance |

Gemini provides classification signals. Application logic
determines escalation and controls simulated execution.

## 3. Running the Prototype

### Installation

Clone the repository and select the developed branch:

```bash
git clone https://github.com/aohanting-code/SmartHandoff.git
cd SmartHandoff
git switch reliability-improvements
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install flask pytest google-genai python-dotenv
```

### Optional Gemini Configuration

Create a local `.env` file containing:

```env
GEMINI_API_KEY=YOUR_OWN_API_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
```

Use your own API key. Never commit the `.env` file or API
credentials to GitHub.

The prototype can also operate without an API key. To explicitly
enable local-only analysis, add:

```env
SMART_HANDOFF_MODE=local
```

### Start the Application

```bash
python app.py
```

Open:

http://127.0.0.1:5000

### Run Automated Tests

```bash
python -m pytest -q
```

## 4. Inspecting the Interaction

Example messages:

| Input | Interaction to inspect |
|---|---|
| Where is my order? | Normal delivery support |
| I no longer want to keep this item. | Implicit return intention |
| Has it left the warehouse yet? | Context-sensitive delivery query |
| When will I get my money back? | Proactive escalation |
| Can I speak to someone instead? | User-initiated escalation |
| Can you generate a return label for me? | Capability boundary |

Reviewers can decline an escalation offer, edit handoff context,
confirm a simulated request, cancel a request or mark an issue
as resolved.

The decision inspector exposes classification signals, fallback
information, escalation reasons and execution status.

Use fictional information only. Messages and recent conversation
context may be sent to Gemini when external analysis is enabled.

## 5. Development Record

### Stage 1 — Initial Prototype

Established a rule-based customer support interface with
conversation tracking and simulated human escalation.

Commits:

- [Initial implementation](https://github.com/aohanting-code/SmartHandoff/commit/a747cd5)
- [Early iteration](https://github.com/aohanting-code/SmartHandoff/commit/094c978)

### Stage 2 — Gemini Integration

Integrated structured LLM classification to improve recognition
of implicit intentions and context-dependent expressions.

Manual testing covered five core scenarios: implicit return,
contextual delivery queries, implicit human-support requests,
frustration language and repeated unresolved issues.

All five scenarios succeeded at least once. Intermittent API
errors revealed limitations in the original fallback rules.

Commit:
[Gemini integration](https://github.com/aohanting-code/SmartHandoff/commit/f40a6c9)

### Stage 3 — Reliability Improvements

Expanded local recognition rules and introduced one additional
attempt for selected temporary server errors.

Eight regression tests were added to examine implicit requests,
context preservation, refusal recognition, retry behaviour
and fallback.

All 19 automated tests passed in 0.35 seconds during this
development stage. A subsequent live Gemini request correctly
classified an implicit return intention without fallback.

API failure tests used simulated exceptions rather than
controlled live service outages.

Commit:
[Reliability improvements](https://github.com/aohanting-code/SmartHandoff/commit/c60f287)

### Stage 4 — Interaction Refinement

Improved issue-state reset, capability-boundary detection,
immediate message feedback, loading indicators, button states
and conversation layout.

Manual inspection demonstrated editable handoff context,
proactive escalation, user refusal and confirmed simulated
ticket creation.

Commit:
[Final interaction prototype](https://github.com/aohanting-code/SmartHandoff/commit/1fdd3dd)

## 6. AI Assistance and Authorship

ChatGPT assisted with initial implementation, code revisions,
debugging, regression-test design and documentation preparation.

Examples include:

- Diagnosing Gemini API timeout errors.
- Proposing bounded retry and local fallback mechanisms.
- Expanding local recognition patterns.
- Suggesting state-management and interface improvements.

I applied the changes locally, ran automated tests, inspected
terminal outputs and manually tested interaction scenarios in
the browser. Development stages were recorded through Git commits.

AI-generated suggestions were checked against observed system
behaviour. The reported tests are developer verification,
not a formal user study.

Gemini is also used as a runtime component of the prototype.
Its outputs are validated before being used by application logic.

## 7. Additional Files

- `app.py` — Flask application and interaction controller.
- `ai_service.py` — Hybrid classification and fallback.
- `escalation.py` — Escalation decision policy.
- `templates/` — HTML interface.
- `static/` — JavaScript and CSS.
- `data/` — Fictional customer service records.
- `tests/` — Automated regression tests.

The accompanying project report contains the system diagram,
illustrated interaction examples, design rationale and references.
