# Enterprise Agentic IT Support Workflow - CrewAI Demo

Welcome to the **Support Demo** project! This is a production-grade, event-driven enterprise workflow that demonstrates how to integrate CrewAI flows with external communication tools (Slack) and implement a secure Human-in-the-Loop (HITL) approval process.

## 🎯 Purpose & Learning Objectives

This demo teaches you how to:
- Build a **Sequential Process Crew** with multiple specialized agents
- Use **CrewAI Flow** to manage state across multiple workflow steps
- Implement **Human-in-the-Loop (HITL)** for ticket approval and authorization
- Dynamically spin up **single-task agents on the fly** (Dispatch Agent)
- Handle **egress/outbound webhooks** to Slack channels
- Build a **custom API trigger script** to bypass third-party ingestion limitations
- Deploy workflows to **CrewAI AMP** (Agentic Management Platform)

## 🏗️ Architecture Overview

The workflow follows a 4-phase process:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: DRAFTING                                           │
│ • SOP Specialist queries knowledge base for resolution steps │
│ • Ticketing Specialist drafts markdown ticket               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: NOTIFICATION                                       │
│ • Flow pushes drafted ticket to Level 1 Slack channel       │
│ • Includes hyperlink to CrewAI AMP dashboard                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: HUMAN-IN-THE-LOOP PAUSE                           │
│ • Workflow execution halts completely                       │
│ • Awaits human approval in CrewAI AMP UI                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: DISPATCH                                           │
│ • Approves: Routes to success, instantiates dynamic         │
│   "Slack Communications Specialist" agent                   │
│ • Rejects: Graceful workflow termination                    │
│ • Final ticket pushed to Level 2 Escalation channel         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
support_demo/
├── src/
│   └── support_demo/
│       ├── __init__.py
│       ├── main.py                    # Flow orchestrator (state management & routing)
│       └── crews/
│           └── content_crew/
│               ├── __init__.py
│               ├── content_crew.py    # Crew logic & tools
│               └── config/
│                   ├── agents.yaml    # Agent definitions
│                   └── tasks.yaml     # Task definitions
├── trigger.py                         # API trigger script for local testing
├── pyproject.toml                     # Project dependencies
├── uv.lock                            # Locked dependencies
└── README.md                          # This file
```

## 🔧 Prerequisites

- **Python**: >=3.10 <3.14
- **UV Package Manager**: For dependency management
- **API Keys**: 
  - Google Gemini API key (for `gemini/gemini-2.5-flash` LLM)
  - CrewAI AMP API key (for deployment)
- **Slack Workspace**: With permission to create Incoming Webhooks
- **CrewAI AMP Account**: For deployment and Human-in-the-Loop management

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lernwithshubham/demo_crewai.git
cd demo_crewai/support_demo
```

### 2. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

Alternatively, using pip:
```bash
pip install uv
```

### 3. Install Dependencies

```bash
uv sync
```

If `requests` is missing (required for `trigger.py`):
```bash
uv add requests
```

### 4. Environment Setup

Create a `.env` file in the `support_demo` root directory with the following variables:

```env
# Google Gemini API
GEMINI_API_KEY=your_google_gemini_api_key_here

# CrewAI AMP Configuration
AMP_API_URL=https://api.crewai.com/flows/run
AMP_API_KEY=your_amp_bearer_token_here
AMP_DASHBOARD_URL=https://app.crewai.com/flows/your-flow-id/hitl

# Slack Webhooks
SLACK_CHANNEL_1_WEBHOOK=https://hooks.slack.com/services/YOUR/CHANNEL/1/WEBHOOK
SLACK_CHANNEL_2_WEBHOOK=https://hooks.slack.com/services/YOUR/CHANNEL/2/WEBHOOK
```

## 🔑 Configuration Guide

### Step 1: Set Up Slack Webhooks

1. Go to your Slack workspace → **Settings & Administration** → **Manage Apps**
2. Search for "Incoming Webhooks" and activate it
3. Click **Create New Webhook**
4. Select **Channel 1** (e.g., `#support-queue`) and create the webhook
5. Copy the webhook URL to `SLACK_CHANNEL_1_WEBHOOK` in `.env`
6. Repeat for **Channel 2** (e.g., `#escalations`) and copy to `SLACK_CHANNEL_2_WEBHOOK`

### Step 2: Configure Agent & Task Definitions

**File**: `src/support_demo/crews/content_crew/config/agents.yaml`

Defines two agents:
- **sop_specialist**: SOP & Knowledge Base Specialist
- **ticketing_specialist**: Incident Ticketing Specialist

**File**: `src/support_demo/crews/content_crew/config/tasks.yaml`

Defines two tasks:
- **lookup_sop_task**: Queries knowledge base
- **draft_ticket_task**: Drafts IT incident ticket

### Step 3: Review Crew Logic

**File**: `src/support_demo/crews/content_crew/content_crew.py`

Key components:
- **SOP Tool**: `@tool("SOP Knowledge Base Tool")` named `query_sop` (returns hardcoded SOP)
- **LLM Initialization**: `LLM(model="gemini/gemini-2.5-flash", temperature=0.2)`
- **Sequential Process**: Defined in `@crew` decorator
- **Sanitization Hook**: `@before_kickoff` removes 'id' key from dynamic inputs

### Step 4: Review Flow Orchestrator

**File**: `src/support_demo/main.py`

Key components:
- **State Management**: `SupportState` tracks `complaint`, `drafted_ticket`, `final_output`
- **@start() draft_ticket_step**: Initiates crew, sends Slack notification
- **@listen() approval_step**: Human-in-the-Loop gate
  - ⚠️ **CRITICAL**: Set `llm="gemini/gemini-2.5-flash"` to prevent OpenAI default
  - Set `emit=["approved", "rejected"]` for UI buttons
- **@router() route_approval**: Routes based on approval outcome
- **@listen("approved") dispatch_to_slack**: Instantiates dynamic agent, formats ticket
- **@listen("rejected")**: Graceful termination

## 🚀 Running the Demo

### Option 1: Local Testing with Trigger Script

1. **Deploy to CrewAI AMP** (see Deployment section below)
2. **Run the trigger script**:
   ```bash
   python trigger.py "I am locked out of the production AWS account."
   ```
3. **Observe Slack Channel 1**: Drafted ticket appears with AMP link
4. **Approve in AMP**:
   - Click the dashboard link in Slack message
   - Log into CrewAI AMP
   - Navigate to **Human-in-the-Loop** tab
   - Click **Approve** button
5. **Observe Slack Channel 2**: Final formatted ticket dispatched

### Option 2: Manual Flow Testing

If running locally without AMP deployment:
```bash
# Run directly with Python
python -m src.support_demo.main
```

## 📤 Deployment to CrewAI AMP

### 1. Prepare Your Project

Ensure all files are committed to a Git repository:
```bash
git add .
git commit -m "Add support_demo workflow"
git push origin main
```

### 2. Create AMP Deployment

1. Go to [CrewAI AMP Dashboard](https://app.crewai.com)
2. Click **Create Flow** → Select **CrewAI**
3. Connect your GitHub repository
4. Select the `support_demo` directory
5. Configure environment variables in AMP:
   - `GEMINI_API_KEY`
   - `SLACK_CHANNEL_1_WEBHOOK`
   - `SLACK_CHANNEL_2_WEBHOOK`
   - `AMP_DASHBOARD_URL` (copy from deployment settings)

### 3. Deploy & Monitor

1. Click **Deploy**
2. Wait for status to show **Online** (green)
3. Copy the **API URL** and **Bearer Token** to `.env`
4. Your flow is now ready to receive requests!

## 📝 How the Trigger Script Works

**File**: `trigger.py`

The `trigger.py` script bridges the gap between Slack and CrewAI AMP:

```bash
# Syntax:
python trigger.py "<Your complaint/ticket description>"

# Example:
python trigger.py "Database query performance degrading on prod"
```

**What it does**:
1. Captures your complaint as a command-line argument
2. Constructs a JSON payload: `{"inputs": {"complaint": "..."}}`
3. Attaches the AMP Bearer Token in headers
4. POSTs to the live AMP API endpoint
5. CrewAI Flow wakes up and begins processing

## 🔄 Workflow Execution Flow

```
User runs trigger.py
        ↓
HTTP POST to AMP API
        ↓
Flow receives complaint
        ↓
SOP Specialist queries knowledge base
        ↓
Ticketing Specialist drafts ticket
        ↓
Notification sent to Slack Channel 1
        ↓
🛑 PAUSE - Waiting for human approval
        ↓
   [User clicks Approve in AMP]
        ↓
Slack Communications Specialist spawned
        ↓
Formats ticket with emojis & urgency tags
        ↓
Final ticket sent to Slack Channel 2
        ↓
✅ Workflow complete
```

## 🛠️ Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'uv'`
**Solution**: Install UV dependencies:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv sync
```

### Issue: `requests` module not found
**Solution**:
```bash
uv add requests
uv sync
```

### Issue: Flow defaults to OpenAI instead of Gemini
**Solution**: Ensure `llm="gemini/gemini-2.5-flash"` is explicitly set in:
- `@human_feedback` decorator in `main.py`
- `LLM()` initialization in `content_crew.py`

### Issue: Slack messages not appearing
**Checklist**:
- ✅ Webhook URLs are valid and not expired
- ✅ Slack channels exist and bot has permission to post
- ✅ Environment variables are set correctly
- ✅ Check AMP logs for webhook errors

### Issue: Human-in-the-Loop approval button not rendering
**Solution**: Ensure `emit=["approved", "rejected"]` is set in `@human_feedback` decorator

## 📚 Key Files Explained

| File | Purpose |
|------|---------|
| `main.py` | Flow orchestrator, state management, routing logic |
| `content_crew.py` | Crew definition, agents, tools, LLM configuration |
| `agents.yaml` | Agent roles, goals, and backstories |
| `tasks.yaml` | Task descriptions and expected outputs |
| `trigger.py` | Local API trigger for testing the workflow |
| `.env` | Environment variables (not committed to git) |

## 🔐 Security Best Practices

1. **Never commit `.env`** to version control
2. **Rotate Slack webhooks** if they're exposed
3. **Use strong AMP API keys** and rotate regularly
4. **Limit Slack bot permissions** to necessary channels only
5. **Audit CrewAI AMP logs** for suspicious activity
6. **Sanitize user inputs** (already done in `content_crew.py` via `@before_kickoff`)

## 📖 Learning Resources

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewai)
- [CrewAI Discord Community](https://discord.com/invite/X4JWnZnxPb)
- [Google Gemini API Docs](https://ai.google.dev/)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

## 🤝 Support & Contributions

Have questions or found an issue? Please:
1. Check this README thoroughly
2. Review the troubleshooting section
3. Open an issue on the [GitHub repository](https://github.com/lernwithshubham/demo_crewai)
4. Join the CrewAI Discord for community support

## 📄 License

This project is provided as-is for educational purposes.

---

**Happy learning! 🚀 Now go build amazing enterprise AI workflows with CrewAI!**
