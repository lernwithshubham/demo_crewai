# Enterprise Agentic IT Support Workflow - CrewAI Demo

A production-grade, event-driven enterprise workflow demonstrating how to build an **automated IT Helpdesk pipeline** using CrewAI, CrewAI Flow, and Slack integration with Human-in-the-Loop (HITL) approval.

**Learn how to build a complete, real-world agentic system from scratch!**

---

## 📚 Table of Contents

1. [Project Overview](#-project-overview)
2. [Phase 1: Project Initialization](#phase-1-project-initialization)
3. [Phase 2: Understanding the Boilerplate](#phase-2-understanding-the-boilerplate)
4. [Phase 3: Architecture & Workflow](#phase-3-architecture--workflow)
5. [Phase 4: Writing the Code](#phase-4-writing-the-code)
6. [Phase 5: Slack Integration](#phase-5-slack-integration-configuration)
7. [Phase 6: Deployment & Environment Variables](#phase-6-deployment-and-environment-variables)
8. [Phase 7: Creating the Trigger Script](#phase-7-creating-the-trigger-script-ingress)
9. [Phase 8: Executing the End-to-End Demo](#phase-8-executing-the-end-to-end-demo)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This project teaches you how to:
- ✅ Build a **Sequential Process Crew** with specialized agents
- ✅ Use **CrewAI Flow** to orchestrate multi-step workflows
- ✅ Implement **Human-in-the-Loop (HITL)** approval gates
- ✅ Dynamically spawn agents on the fly
- ✅ Integrate with **Slack** for notifications and escalations
- ✅ Deploy to **CrewAI AMP** (Agentic Management Platform)

**Real-World Scenario**: An automated IT Helpdesk that drafts tickets, sends them to Slack for review, waits for human approval, then dispatches formatted escalations—all driven by AI agents.

---

## PHASE 1: Project Initialization

This phase sets up your development environment and generates the CrewAI foundation.

### Step 1.1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and create a new **public** repository named `demo_crewai`
2. Initialize with a README and clone it locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/demo_crewai.git
   cd demo_crewai
   ```

### Step 1.2: Launch GitHub Codespace (Optional but Recommended)

1. Click **Code** → **Codespaces** → **Create codespace on main**
2. Wait for the container to load (first-time setup takes ~2 minutes)

### Step 1.3: Install CrewAI CLI

In your terminal (local or Codespace), install the CrewAI CLI:

```bash
pip install crewai
```

### Step 1.4: Generate the CrewAI Flow Template

Create the `support_demo` flow project using the CrewAI CLI:

```bash
crewai create flow support_demo
```

This command generates a complete directory structure:
```
support_demo/
├── src/
│   └── support_demo/
│       ├── __init__.py
│       ├── main.py
│       └── crews/
│           └── support_demo_crew/
│               ├── __init__.py
│               ├── support_demo_crew.py
│               └── config/
│                   ├── agents.yaml
│                   └── tasks.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

### Step 1.5: Navigate into the Project

```bash
cd support_demo
```

### Step 1.6: Add the Requests Library

Since we'll be making outbound API calls to Slack, add the `requests` library:

```bash
uv add requests
uv sync
```

**✓ Phase 1 Complete!** You now have a working CrewAI project structure.

---

## PHASE 2: Understanding the Boilerplate

Before writing custom code, understand what the CLI generated for you.

### Key Generated Files

| File/Folder | Purpose |
|-----------|---------|
| **pyproject.toml** / **uv.lock** | Dependency management using UV package manager |
| **src/support_demo/main.py** | The **Flow orchestrator** — defines the state machine and task routing |
| **src/support_demo/crews/support_demo_crew/support_demo_crew.py** | The **Crew definition** — binds agents, tasks, and tools |
| **src/support_demo/crews/support_demo_crew/config/agents.yaml** | Agent definitions (roles, goals, backstories) |
| **src/support_demo/crews/support_demo_crew/config/tasks.yaml** | Task definitions (descriptions, expected outputs, agent mapping) |

### Understanding UV

The CrewAI CLI uses **UV** for dependency management (faster than pip, compatible with pip). Key commands:

```bash
uv add <package_name>    # Add a new dependency
uv sync                  # Lock and sync dependencies
uv run <script.py>       # Run a Python script with the locked environment
```

> **Note**: In our custom build, we'll rename `support_demo_crew` → `content_crew` to represent an IT Operations department. Don't do this now; we'll handle it in Phase 4.

---

## PHASE 3: Architecture & Workflow

### Real-World Scenario: Automated IT Helpdesk

```
┌──────────────────────────────────────────────────────────────┐
│ USER SUBMITS COMPLAINT (via trigger.py)                      │
│ "I can't access the production AWS account"                  │
└──────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: DRAFTING                                            │
│ • SOP Specialist queries knowledge base                      │
│ • Ticketing Specialist drafts markdown ticket                │
└──────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: NOTIFICATION                                        │
│ • Drafted ticket posted to Level 1 Slack channel             │
│ • Includes clickable link to CrewAI AMP dashboard            │
└──────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: HUMAN-IN-THE-LOOP PAUSE                             │
│ 🛑 Workflow halts. Awaits human approval in AMP UI           │
└──────────────────────────────────────────────────────────────┘
                             ↓
                    [HUMAN CLICKS "APPROVE"]
                             ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: DYNAMIC DISPATCH                                    │
│ • Slack Communications Specialist agent spawned on-the-fly   │
│ • Formats ticket with emojis & urgency tags                  │
│ • Final ticket sent to Level 2 Escalation channel            │
└──────────────────────────────────────────────────────────────┘
                             ↓
                    ✅ WORKFLOW COMPLETE
```

### System Components

1. **trigger.py** — Local Python script that sends complaints to AMP API
2. **SupportFlow** (main.py) — State machine that orchestrates the workflow
3. **SupportCrew** (content_crew.py) — Two agents (SOP Specialist, Ticketing Specialist)
4. **Slack Webhooks** — Channels for notification and escalation
5. **CrewAI AMP** — Hosts the flow and provides the HITL UI

---

## PHASE 4: Writing the Code

Now let's replace the boilerplate with our custom implementation.

### Step 4.1: Rename the Crew Folder (Optional but Recommended)

In `src/support_demo/crews/`, rename `support_demo_crew/` to `content_crew/`:

```bash
mv src/support_demo/crews/support_demo_crew src/support_demo/crews/content_crew
```

Update `src/support_demo/crews/content_crew/__init__.py`:
```python
from .content_crew import ContentCrew

__all__ = ["ContentCrew"]
```

### Step 4.2: Configure Agents (YAML)

Replace the contents of `src/support_demo/crews/content_crew/config/agents.yaml`:

```yaml
sop_specialist:
  role: >
    SOP & Knowledge Base Specialist
  goal: >
    Analyze IT complaints and retrieve the correct Standard Operating Procedure (SOP) steps.
  backstory: >
    You are an expert IT knowledge manager. You map user complaints to exact resolution steps.

ticketing_specialist:
  role: >
    Incident Ticketing Specialist
  goal: >
    Draft a professional, formatted IT incident ticket.
  backstory: >
    You are a meticulous IT support engineer who formats raw technical steps into clear, actionable Markdown tickets for human review.
```

### Step 4.3: Configure Tasks (YAML)

Replace the contents of `src/support_demo/crews/content_crew/config/tasks.yaml`:

```yaml
lookup_sop_task:
  description: >
    Analyze the user complaint: "{complaint}". 
    Use your tools to query the SOP knowledge base and retrieve the relevant resolution steps.
  expected_output: >
    A concise list of the SOP steps required to resolve the issue.
  agent: sop_specialist

draft_ticket_task:
  description: >
    Take the SOP steps found by the SOP Specialist and the original complaint: "{complaint}".
    Draft a formal incident ticket containing: 
    - Issue Summary
    - Affected System
    - Proposed Resolution (SOP Steps)
  expected_output: >
    A perfectly formatted Markdown ticket ready for human review.
  agent: ticketing_specialist
```

> **⚠️ IMPORTANT**: In a Sequential process, explicitly mapping `agent: agent_name` at the bottom of each task is **required** to avoid Pydantic validation errors.

### Step 4.4: Write the Crew Definition

Replace the contents of `src/support_demo/crews/content_crew/content_crew.py`:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool("SOP Knowledge Base Tool")
def query_sop(query: str) -> str:
    """Queries the internal IT database for Standard Operating Procedures."""
    return "SOP: 1. Verify VPN connection. 2. Reset AWS IAM temporary credentials. 3. Clear local cache."

@CrewBase
class SupportCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

    @before_kickoff
    def sanitize_inputs(self, inputs):
        """Remove 'id' key if passed dynamically by Flow."""
        if 'id' in inputs:
            inputs.pop('id')
        return inputs

    @agent
    def sop_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['sop_specialist'],
            tools=[query_sop],
            llm=self.llm,
            verbose=True
        )

    @agent
    def ticketing_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['ticketing_specialist'],
            llm=self.llm,
            verbose=True
        )

    @task
    def lookup_sop_task(self) -> Task:
        return Task(config=self.tasks_config['lookup_sop_task'])

    @task
    def draft_ticket_task(self) -> Task:
        return Task(config=self.tasks_config['draft_ticket_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

**Key Features**:
- `@tool("SOP Knowledge Base Tool")` — Custom tool that agents can call
- `@before_kickoff` hook — Sanitizes inputs (removes 'id' key)
- `LLM(model="gemini-2.5-flash")` — Uses Google Gemini instead of OpenAI
- `Process.sequential` — Agents execute tasks in order

### Step 4.5: Write the Flow Orchestrator (The Core Logic)

Replace the contents of `src/support_demo/main.py`:

```python
#!/usr/bin/env python
import os
import requests
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.human_feedback import human_feedback
from crewai import Agent, Task, Crew, LLM
from support_demo.crews.content_crew.content_crew import SupportCrew

class SupportState(BaseModel):
    """State management for the support workflow."""
    complaint: str = "I can't access the staging database."
    drafted_ticket: str = ""
    final_output: str = ""

class SupportFlow(Flow[SupportState]):
    """Enterprise IT Support Workflow Orchestrator."""

    @start()
    def draft_ticket_step(self):
        """PHASE 1: Initiate crew to draft the ticket."""
        print(f"Processing complaint: {self.state.complaint}")
        result = SupportCrew().crew().kickoff(inputs={'complaint': self.state.complaint})
        self.state.drafted_ticket = result.raw
        self._send_review_notification(self.state.drafted_ticket)
        return self.state.drafted_ticket

    def _send_review_notification(self, ticket_text):
        """PHASE 2: Send drafted ticket to Slack Channel 1."""
        webhook_url = os.environ.get("SLACK_CHANNEL_1_WEBHOOK")
        amp_dashboard_url = os.environ.get("AMP_DASHBOARD_URL", "https://app.crewai.com")
        if not webhook_url:
            print("⚠️ SLACK_CHANNEL_1_WEBHOOK not set")
            return
        slack_payload = {
            "text": f"🚨 *New Incident Drafted*\n\n{ticket_text}\n\n👉 <{amp_dashboard_url}|*CLICK HERE TO APPROVE IN CREWAI AMP*>"
        }
        try:
            requests.post(webhook_url, json=slack_payload)
            print("✅ Notification sent to Slack Channel 1")
        except Exception as e:
            print(f"❌ Failed to send Slack notification: {e}")

    @listen(draft_ticket_step)
    @human_feedback(
        message="Please review the drafted incident ticket.",
        emit=["approved", "rejected"],
        llm="gemini/gemini-2.5-flash"  # ⚠️ CRITICAL: Explicitly set to prevent OpenAI default
    )
    def approval_step(self, previous_output):
        """PHASE 3: HITL Pause - Wait for human approval."""
        return self.state.drafted_ticket

    @router(approval_step)
    def route_approval(self):
        """Router: Determine next step based on approval outcome."""
        last_feedback = self.human_feedback_history[-1]
        if last_feedback.outcome == "approved":
            return "approved"
        else:
            return "rejected"

    @listen("approved")
    def dispatch_to_slack(self):
        """PHASE 4: Dispatch - Spawn dynamic agent & send to Slack Channel 2."""
        print("✅ Ticket approved. Dispatching...")
        
        # Dynamically create a single-task agent for formatting
        dispatcher = Agent(
            role="Slack Communications Specialist",
            goal="Format the approved IT ticket for Slack.",
            backstory="You format markdown tickets with Slack emojis and urgency tags.",
            llm=LLM(model="gemini/gemini-2.5-flash", temperature=0.1)
        )
        
        dispatch_task = Task(
            description=f"Format this approved ticket for a Slack channel alert:\n\n{self.state.drafted_ticket}",
            expected_output="A Slack-formatted alert message starting with an urgency emoji.",
            agent=dispatcher
        )
        
        slack_formatted_message = Crew(
            agents=[dispatcher], 
            tasks=[dispatch_task]
        ).kickoff().raw
        
        self._send_to_channel_2(slack_formatted_message)
        self.state.final_output = f"✅ DISPATCHED TO SLACK:\n{slack_formatted_message}"
        return self.state.final_output

    def _send_to_channel_2(self, message):
        """Send the final formatted ticket to Slack Channel 2."""
        webhook_url = os.environ.get("SLACK_CHANNEL_2_WEBHOOK")
        if not webhook_url:
            print("⚠️ SLACK_CHANNEL_2_WEBHOOK not set")
            return
        payload = {"text": f"✅ *APPROVED INCIDENT TICKET*\n\n{message}"}
        try:
            requests.post(webhook_url, json=payload)
            print("✅ Final ticket sent to Slack Channel 2")
        except Exception as e:
            print(f"❌ Failed to send final Slack message: {e}")

    @listen("rejected")
    def reject_ticket(self):
        """PHASE 4 (Reject path): Graceful termination."""
        self.state.final_output = "❌ TICKET REJECTED IN AMP."
        print(self.state.final_output)
        return self.state.final_output

def kickoff():
    """Start the flow."""
    flow = SupportFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()
```

**Key Features**:
- `@start()` — Entry point of the flow
- `@listen()` — Listens for completion of another step
- `@human_feedback()` — HITL gate with approval buttons
  - ⚠️ **CRITICAL**: `llm="gemini/gemini-2.5-flash"` prevents defaulting to OpenAI
  - `emit=["approved", "rejected"]` renders buttons in AMP UI
- `@router()` — Routes execution based on conditions
- Dynamic agent spawning in `dispatch_to_slack()`

**✓ Phase 4 Complete!** Your custom code is now in place.

---

## PHASE 5: Slack Integration Configuration

You need two Slack Incoming Webhooks: one for draft review, one for escalation.

### Step 5.1: Create Webhook for Channel 1 (Draft Review)

1. Open your Slack workspace
2. Go to **Settings & Administration** → **Manage Apps**
3. Search for **"Incoming WebHooks"** and install it
4. Click **Create New WebHook**
5. Select your IT Helpdesk channel (e.g., `#support-queue`)
6. Copy the WebHook URL and save it (you'll need it soon)

### Step 5.2: Create Webhook for Channel 2 (Escalation)

1. Repeat the above steps
2. Select your Escalation channel (e.g., `#escalations`)
3. Copy the WebHook URL and save it

**You should now have 2 webhook URLs:**
```
https://hooks.slack.com/services/TXXX/BXXX/XXXX  (Channel 1)
https://hooks.slack.com/services/TXXX/BXXX/YYYY  (Channel 2)
```

---

## PHASE 6: Deployment and Environment Variables

### Step 6.1: Push to GitHub

Commit and push your code:

```bash
git add .
git commit -m "Add support_demo workflow implementation"
git push origin main
```

### Step 6.2: Deploy to CrewAI AMP

1. Go to [CrewAI AMP Dashboard](https://app.crewai.com)
2. Click **Create Flow** → **CrewAI**
3. Connect your GitHub repository
4. Select the `support_demo` folder
5. Click **Deploy**
6. Wait for status to show **Online** ✅

### Step 6.3: Set Environment Variables in AMP

1. In the AMP Dashboard (left sidebar), navigate to **Settings** → **Environment Variables**
2. Add the following keys:

| Key | Value |
|-----|-------|
| `SLACK_CHANNEL_1_WEBHOOK` | (Paste Channel 1 WebHook URL) |
| `SLACK_CHANNEL_2_WEBHOOK` | (Paste Channel 2 WebHook URL) |
| `AMP_DASHBOARD_URL` | (Copy from AMP: Human-in-the-Loop tab URL) |
| `GEMINI_API_KEY` | (Your Google Gemini API key) |

3. Click **Save**

**✓ Phase 6 Complete!** Your flow is now live on CrewAI AMP.

---

## PHASE 7: Creating the Trigger Script (Ingress)

The trigger script bridges the gap between your local machine and CrewAI AMP. Slack Workflow Builder cannot natively attach Bearer tokens, so we use Python to solve this.

### Step 7.1: Create trigger.py

In the **root directory** of your project (same level as `pyproject.toml`), create `trigger.py`:

```python
import requests
import sys

# Replace with credentials from your CrewAI AMP Dashboard (left sidebar)
API_URL = "PASTE_AMP_API_URL_HERE"
BEARER_TOKEN = "PASTE_BEARER_TOKEN_HERE"

complaint = sys.argv[1] if len(sys.argv) > 1 else "I cannot connect to the production VPN."

def trigger_amp_flow():
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": {"complaint": complaint}}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print("✅ AMP Flow triggered. Check Slack Channel 1 for the approval link.")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_amp_flow()
```

### Step 7.2: Get Credentials from AMP

1. In the CrewAI AMP Dashboard, navigate to **Deployments** → **Your Flow**
2. Copy the **API URL** and **Bearer Token**
3. Paste them into `trigger.py`:
   ```python
   API_URL = "https://api.crewai.com/flows/run/YOUR_FLOW_ID"
   BEARER_TOKEN = "your_bearer_token_here"
   ```

### Step 7.3: Test the Trigger Script

```bash
python trigger.py "I am locked out of the production AWS account."
```

Expected output:
```
✅ AMP Flow triggered. Check Slack Channel 1 for the approval link.
```

---

## PHASE 8: Executing the End-to-End Demo

Now let's run the complete workflow!

### Step 8.1: Trigger the Workflow

```bash
python trigger.py "My AWS staging credentials are locked out."
```

### Step 8.2: Check Slack Channel 1

Within a few seconds, you should see a message like:

```
🚨 New Incident Drafted

**Issue Summary:**
User cannot access staging database credentials.

**SOP Steps:**
1. Verify VPN connection
2. Reset AWS IAM temporary credentials
3. Clear local cache

👉 CLICK HERE TO APPROVE IN CREWAI AMP
```

### Step 8.3: Approve in CrewAI AMP

1. Click the link in the Slack message
2. Log into CrewAI AMP (if not already logged in)
3. Navigate to the **Human-in-the-Loop** tab
4. Click the **Approve** button

### Step 8.4: Check Slack Channel 2

Within a few more seconds, you should see the final formatted message in Slack Channel 2:

```
✅ APPROVED INCIDENT TICKET

🚨 **URGENT ISSUE DETECTED**
User locked out of AWS staging credentials.

**Immediate Actions Required:**
1. ⚡ Verify VPN connection
2. 🔑 Reset AWS IAM temporary credentials
3. 🧹 Clear local cache

Escalated to Level 2 support team.
```

**✓ Phase 8 Complete!** You've successfully executed a full enterprise agentic workflow! 🎉


## 📖 Learning Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewai)
- [CrewAI Discord Community](https://discord.com/invite/X4JWnZnxPb)
- [Google Gemini API Docs](https://ai.google.dev/)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)



