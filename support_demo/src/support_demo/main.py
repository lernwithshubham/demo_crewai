#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.human_feedback import human_feedback
from support_demo.crews.content_crew.content_crew import SupportCrew

class SupportState(BaseModel):
    complaint: str = "I can't access the staging database."
    drafted_ticket: str = ""
    final_output: str = ""

class SupportFlow(Flow[SupportState]):

    @start()
    def draft_ticket_step(self):
        print(f"Processing complaint: {self.state.complaint}")
        
        # 1. Execute the Crew sequentially
        result = SupportCrew().crew().kickoff(inputs={'complaint': self.state.complaint})
        
        # 2. Save the output to Flow State
        self.state.drafted_ticket = result.raw
        return self.state.drafted_ticket

    # 3. The HITL Pause
    @listen(draft_ticket_step)
    @human_feedback(
        message="Please review the drafted incident ticket. Use the buttons below or type your feedback.",
        emit=["approved", "needs_revision"],
        default_outcome="approved",
        llm="gemini/gemini-2.5-flash"  # CRITICAL: Interprets free-text feedback to map to the emit routes
    )
    def approval_step(self, previous_output):
        # CRITICAL: We must return the ticket here. 
        # The @human_feedback decorator shows THIS return value to the human reviewer in the UI.
        return self.state.drafted_ticket

    # 4. The Flow Router
    @router(approval_step)
    def route_approval(self):
        # Access the history array to see what the human decided
        last_feedback = self.human_feedback_history[-1]
        
        if last_feedback.outcome == "approved":
            return "submit"
        else:
            return "revise"

    # 5a. Success Route
    @listen("submit")
    def submit_ticket(self):
        self.state.final_output = f"✅ TICKET APPROVED & DISPATCHED TO SLACK #level-2-escalations\n\n{self.state.drafted_ticket}"
        return self.state.final_output
    
    # 5b. Rejection Route
    @listen("revise")
    def revise_ticket(self):
        last_feedback = self.human_feedback_history[-1]
        self.state.final_output = f"❌ TICKET REJECTED.\nUser Feedback: {last_feedback.feedback}\nRouting back to support queue for revision."
        return self.state.final_output

def kickoff():
    flow = SupportFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()