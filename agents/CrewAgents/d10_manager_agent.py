from agents.CrewAgents.crew_agent import CrewAIAgent

class ManagerAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-1.5-pro"):
        self.role = "Project Manager"
        self.goal = "Efficiently manage the crew and ensure high-quality task completion"
        self.backstory = (
            "You're an experienced project manager, skilled in overseeing complex projects "
            "and guiding teams to success. Your role is to coordinate the efforts of the crew members, "
            "ensuring that each task is completed on time and to the highest standard."
        )
        super().__init__(model)
        self.allow_delegation = True
