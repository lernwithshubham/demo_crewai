from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai import LLM
from crewai.tools import tool

# 1. Native Python Tool (Simulating the MCP for AMP stability)
@tool("SOP Knowledge Base Tool")
def query_sop(query: str) -> str:
    """Queries the internal IT SOP knowledge base for resolution steps."""
    return "SOP for Staging DB Access: 1. Verify user role in IAM. 2. Request temporary bypass token. 3. Enforce MFA rotation."

# 2. Crew Assembly
@CrewBase
class SupportCrew():
    """IT Support Sequential Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.llm = LLM(model="gemini/gemini-2.5-flash", temperature=0.2)

    @before_kickoff
    def sanitize_inputs(self, inputs):
        if isinstance(inputs, dict) and 'id' in inputs:
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
        return Task(
            config=self.tasks_config['lookup_sop_task']
        )

    @task
    def draft_ticket_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_ticket_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )