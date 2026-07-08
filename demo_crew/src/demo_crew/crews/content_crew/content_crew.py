from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai import LLM

@CrewBase
class ContentCrew():
    """Content Strategy Hierarchical Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # The Manager and Specialists will all share this model
        self.gemini_llm = LLM(
            model="gemini/gemini-2.5-flash",
            temperature=0.3
        )

    # AMP Payload Interceptor: Protects against the v1.15.2 'inputs.id' crash
    @before_kickoff
    def sanitize_inputs(self, inputs):
        if isinstance(inputs, dict) and 'id' in inputs:
            inputs.pop('id')
        return inputs

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=self.gemini_llm,
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            llm=self.gemini_llm,
            verbose=True
        )

    @task
    def master_task(self) -> Task:
        return Task(
            config=self.tasks_config['master_task']
        )

    @crew
    def crew(self) -> Crew:
        # The Manager Agent is dynamically injected to orchestrate the swarm
        manager = Agent(
            role="Content Strategy Manager",
            goal="Orchestrate the research and writing process to deliver a perfect brief.",
            backstory="You are a veteran IT Operations Manager who delegates tasks strictly and reviews outputs critically before declaring a task complete.",
            llm=self.gemini_llm,
            allow_delegation=True,
            verbose=True
        )

        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            verbose=True
        )