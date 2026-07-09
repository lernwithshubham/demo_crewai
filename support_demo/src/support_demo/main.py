#!/usr/bin/env python
import os
import requests
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.human_feedback import human_feedback
from crewai import Agent, Task, Crew, LLM

# Imports the Crew from your exact directory structure
from support_demo.crews.content_crew.content_crew import SupportCrew

class SupportState(BaseModel):
    complaint: str = "I can't access the staging database."
    drafted_ticket: str = ""
    final_output: str = ""

class SupportFlow(Flow[SupportState]):

    @start()
    def draft_ticket_step(self):
        print(f"Processing complaint: {self.state.complaint}")
        
        # 1. Execute the primary Investigation Crew
        result = SupportCrew().crew().kickoff(inputs={'complaint': self.state.complaint})
        self.state.drafted_ticket = result.raw
        
        # 2. Push Notification to Slack Channel 1 BEFORE pausing
        self._send_review_notification(self.state.drafted_ticket)
        
        return self.state.drafted_ticket

    def _send_review_notification(self, ticket_text):
        """Sends the drafted ticket to the first Slack channel."""
        webhook_url = os.environ.get("SLACK_CHANNEL_1_WEBHOOK")
        amp_dashboard_url = os.environ.get("AMP_DASHBOARD_URL", "https://app.crewai.com")
        
        if not webhook_url:
            print("Warning: SLACK_CHANNEL_1_WEBHOOK not set.")
            return

        slack_payload = {
            "text": f"🚨 *New Incident Drafted*\n\n{ticket_text}\n\n👉 <{amp_dashboard_url}|*CLICK HERE TO APPROVE IN CREWAI AMP*>"
        }
        requests.post(webhook_url, json=slack_payload)

    # 3. The Flow pauses here for human interaction in the AMP UI
    @listen(draft_ticket_step)
    @human_feedback(
        message="Please review the drafted incident ticket.",
        emit=["approved", "rejected"],
        llm="gemini/gemini-2.5-flash" 
    )
    def approval_step(self, previous_output):
        return self.state.drafted_ticket

    # 4. The Router
    @router(approval_step)
    def route_approval(self):
        last_feedback = self.human_feedback_history[-1]
        if last_feedback.outcome == "approved":
            return "approved"
        else:
            return "rejected"

    # 5. Success Route -> Spin up Dispatch Agent and push to Channel 2
    @listen("approved")
    def dispatch_to_slack(self):
        print("Ticket approved in AMP. Dispatching...")
        
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
        
        slack_formatted_message = Crew(agents=[dispatcher], tasks=[dispatch_task]).kickoff().raw
        
        # Dispatch to Level 2 Channel
        self._send_to_channel_2(slack_formatted_message)
        
        self.state.final_output = f"✅ DISPATCHED TO SLACK:\n{slack_formatted_message}"
        return self.state.final_output

    def _send_to_channel_2(self, message):
        """Sends the final ticket to the second Slack channel."""
        webhook_url = os.environ.get("SLACK_CHANNEL_2_WEBHOOK")
        if not webhook_url:
            print("Warning: SLACK_CHANNEL_2_WEBHOOK not set.")
            return
            
        payload = {"text": f"✅ *APPROVED INCIDENT TICKET*\n\n{message}"}
        requests.post(webhook_url, json=payload)

    @listen("rejected")
    def reject_ticket(self):
        self.state.final_output = "❌ TICKET REJECTED IN AMP."
        return self.state.final_output

def kickoff():
    flow = SupportFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()