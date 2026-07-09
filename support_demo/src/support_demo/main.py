#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai.project import human_feedback
from support_demo.crews.support_crew.support_crew import SupportCrew

class SupportState(BaseModel):
    complaint: str = "I can't access the staging database."
    drafted_ticket: str = ""
    final_output: str = ""

class SupportFlow(Flow[SupportState]):

    @start()
    def draft_ticket_step(self):
        print(f"Processing complaint: {self.state.complaint}")
        # Execute the Crew sequentially
        result = SupportCrew().crew().kickoff(inputs={'complaint': self.state.complaint})
        self.state.drafted_ticket = result.raw
        return self.state.drafted_ticket

    # This officially pauses the Flow in the CrewAI AMP Dashboard
    @listen(draft_ticket_step)
    @human_feedback(
        message="Please review the drafted incident ticket. Reply 'approved' to submit, or provide feedback for revision.",
        emit=["approved", "needs_revision"],
        default_outcome="approved"
    )
    def approval_step(self):
        pass

    # Routes the execution based on the human's decision
    @router(approval_step)
    def route_approval(self):
        last_feedback = self.human_feedback_history[-1]
        if last_feedback.outcome == "approved":
            return "submit"
        else:
            return "revise"

    @listen("submit")
    def submit_ticket(self):
        # Simulated Slack Dispatch
        self.state.final_output = f"✅ TICKET APPROVED & DISPATCHED TO SLACK #level-2-escalations\n\n{self.state.drafted_ticket}"
        return self.state.final_output
    
    @listen("revise")
    def revise_ticket(self):
        last_feedback = self.human_feedback_history[-1]
        self.state.final_output = f"❌ TICKET REJECTED. User Feedback: {last_feedback.feedback}\nRouting back to support queue."
        return self.state.final_output

def kickoff():
    flow = SupportFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()