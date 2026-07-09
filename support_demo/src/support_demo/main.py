#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.human_feedback import human_feedback
from crewai import Agent, Task, Crew, LLM  # Added imports for the dynamic agent

from support_demo.crews.content_crew.content_crew import SupportCrew

class SupportState(BaseModel):
    complaint: str = "I can't access the staging database."
    drafted_ticket: str = ""
    final_output: str = ""

class SupportFlow(Flow[SupportState]):

    @start()
    def draft_ticket_step(self):
        print(f"Processing complaint: {self.state.complaint}")
        
        # 1. Execute the primary Investigation & Drafting Crew
        result = SupportCrew().crew().kickoff(inputs={'complaint': self.state.complaint})
        
        self.state.drafted_ticket = result.raw
        return self.state.drafted_ticket

    # 2. Simplified HITL Pause - strict button clicks only
    @listen(draft_ticket_step)
    @human_feedback(
        message="Please review the drafted incident ticket.",
        emit=["approved", "rejected"],
        llm="gemini/gemini-2.5-flash"  # CRITICAL: Stops the OpenAI default fallback
    )
    def approval_step(self, previous_output):
        # Renders the ticket on the screen for the human
        return self.state.drafted_ticket

    # 3. The Router 
    @router(approval_step)
    def route_approval(self):
        last_feedback = self.human_feedback_history[-1]
        if last_feedback.outcome == "approved":
            return "approved"
        else:
            return "rejected"

    # 4. Success Route: Spin up the Dispatch Agent
    @listen("approved")
    def dispatch_to_slack(self):
        print("Ticket approved. Spinning up Dispatch Agent...")
        
        # Instantiate a dynamic agent specifically for the Slack formatting task
        dispatcher = Agent(
            role="Slack Communications Specialist",
            goal="Format the approved IT ticket for Slack and prepare it for dispatch.",
            backstory="You are an expert at taking raw markdown tickets and formatting them with appropriate Slack emojis, urgency tags, and clean formatting for engineering teams.",
            llm=LLM(model="gemini/gemini-2.5-flash", temperature=0.1)
        )
        
        dispatch_task = Task(
            description=f"Format this approved ticket for a Slack channel alert:\n\n{self.state.drafted_ticket}",
            expected_output="A Slack-formatted alert message starting with an urgency emoji.",
            agent=dispatcher
        )
        
        # Execute this mini-crew on the fly
        slack_crew = Crew(agents=[dispatcher], tasks=[dispatch_task])
        slack_formatted_message = slack_crew.kickoff().raw
        
        # (In a real environment, the requests.post() to the Slack Webhook goes here)
        
        self.state.final_output = f"✅ SUCCESSFULLY DISPATCHED TO SLACK #level-2-escalations:\n\n{slack_formatted_message}"
        return self.state.final_output
    
    # 5. Rejection Route
    @listen("rejected")
    def reject_ticket(self):
        self.state.final_output = "❌ TICKET REJECTED BY HUMAN. Workflow terminated."
        return self.state.final_output

def kickoff():
    flow = SupportFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()