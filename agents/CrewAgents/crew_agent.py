import core.sqlite_patch as sqlite_patch

from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from crewai.tools import tool
from litellm import AuthenticationError, BadRequestError


from typing import List

#This class is an abstraction of the CrewAi agents framework 
class CrewAIAgent:
    def __init__(self, model = "gemini/gemini-2.0-flash-lite"):

        # Dummy Instructions
        self.role = "Ai assistant that provides relevant information from the web"
        self.goal = "To provide insightful and relevant responses based on user queries."
        self.instructions = "Respond concisely and accurately. If unsure, clarify with the user."
        self.knowledge = "The agent has general knowledge about the world up to 2021, excluding highly specialized or personal knowledge."

        #Load Api Keys from env
        load_dotenv()
    
        # Create Tools
        self.tools = self._create_tools()

        # Create Agent
        self.agent = self._create_crewai_agent(model)

        # Create generic task for the agent
        self.task = Task(
            description=("Answer the user's query comprehensively, using tools when necessary. "
                         "This is the conversation history: {history}"
                         "This is the user's latest query: {query}"),
            expected_output="A clear, well-formatted answer, incorporating tool results when appropriate.",
            agent=self.agent
        )

        # Initialize messages
        self.messages = []

        # Create crew with agents and tasks
        self.crew = Crew(
            agents=[self.agent],
            tasks=[self.task],
            verbose=False
        )


    def _create_tools(self) -> List:
        """
        Create tools for the crew AI agent
        Returns a List of tools
        """
        return []
    
    def _create_crewai_agent(self, model):
        """
        Create a CrewAI agent with the specified configuration

        Args : 
            model (str): the llm to use

        Returns :
            CrewAI Agent
        """

        return Agent(
            role= self.role,
            goal = "\n".join([self.goal, self.instructions]),
            backstory= self.knowledge,
            tools= self.tools,
            verbose = False,
            llm = model
        )
    
    def chat(self, message: str) -> str:
        """
        Send a message with optional document support.

        Parameters:
        - message (str): The user's message.
        - doc (list[str], optional): List of documents paths.

        Returns:
        - str: Agent's response.
        """
        try :
            response = self.crew.kickoff(inputs={"query":message, "history":self.messages})

            self.messages.append({"role":"user", "content":message})
            self.messages.append({"role":"assistant", "content": str(response)})
            return response
        
        except Exception as e:
            return self.handle_chat_exception(e)


    def handle_chat_exception(self, e: Exception) -> str:
        """
        Map low‑level LLM exceptions into friendly strings.
        """
        msg = str(e)

        if isinstance(e, AuthenticationError) or "API key not valid" in msg:
            return "❌ Authentication failed: your API key is invalid. Please check it in the sidebar."
        if isinstance(e, BadRequestError) or "API key expired" in msg:
            return "❌ Your API key has expired. Please renew it in the sidebar."
        if '"code": 503' in msg:
            return "Sorry, servers are a little busy, you might want to try again in a few minutes (or more...)"
        return f"⚠️ An unexpected error occurred: {msg}"
        
    def clear_chat(self)-> bool:
        """
        Reset the conversation context

        Returns 
            bool: True if successful
        """
        try:
            self.messages = []

            self.crew = Crew(
                agents = [self.agent],
                tasks = [self.task],
                verbose = False
            )
            return True
        except Exception as e:
            print(f"Error clearing chat: {e}")
            return False
        