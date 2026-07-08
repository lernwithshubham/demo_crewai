#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from demo_crew.crews.content_crew.content_crew import ContentCrew

# 1. Define the State (This maps to the AMP UI Inputs)
class DemoFlowState(BaseModel):
    topic: str = "The future of Agentic AI in enterprise environments"

# 2. Define the Flow
class DemoFlow(Flow[DemoFlowState]):

    @start()
    def run_content_crew(self):
        print(f"Starting the Hierarchical Crew for topic: {self.state.topic}")
        
        # Map the Flow state to the Crew inputs expected by the YAML files
        crew_inputs = {
            'topic': self.state.topic
        }
        
        # Execute the Crew
        result = ContentCrew().crew().kickoff(inputs=crew_inputs)
        return result.raw

# 3. The Entry Point executed by CrewAI AMP
def kickoff():
    demo_flow = DemoFlow()
    demo_flow.kickoff()

if __name__ == "__main__":
    kickoff()