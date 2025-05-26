from crewai import Crew, Task, Process
from agents.CrewAgents.crew_agent import CrewAIAgent
from agents.CrewAgents.d1_calculations_agent import CalculationAgent
from agents.CrewAgents.d3_webpage_agent import WebPageAgent
from agents.CrewAgents.d10_manager_agent import ManagerAgent  

class TestCrew(CrewAIAgent):
    def __init__(self, model="gemini/gemini-1.5-pro"):
        super().__init__(model)
        self.manager_agent = self.create_manager_agent()
        self.agents = self.load_agents()
        self.tasks = self.define_tasks()
        self.crew = self.create_crew()

    def create_manager_agent(self):
        return ManagerAgent().agent

    def load_agents(self):
        calc = CalculationAgent().agent
        web = WebPageAgent().agent
        return [calc, web]

    def define_tasks(self):
        composite_task = Task(
            description=(
                "Analyze the project requirements and perform necessary actions, which may include "
                "calculations and web content summarization."
            ),
            expected_output="A comprehensive report based on calculations and/or web content.",
            agent=self.manager_agent
        )
        return [composite_task]

    def create_crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            manager_agent=self.manager_agent,
            process=Process.hierarchical,
            verbose=False
        )
