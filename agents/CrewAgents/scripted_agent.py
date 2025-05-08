from crewai import CrewAIAgent
from crewai.tools import tool
from core.script_engine.script import Script
from abc import ABC, abstractmethod

class ScriptedAgent(CrewAIAgent, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script = self.get_script()
        self.goal = "Collect each user input in order, then transition to open conversation."
        self.tools = self._create_tools()

    @abstractmethod
    def get_script(self) -> Script:
        """
        Must return a Script instance with a defined step list.
        """
        raise NotImplementedError

    def _create_tools(self):
        @tool
        def assign_value(value: str) -> str:
            """
            Store the user's response under a given variable name.

            Args:
                var_name (str): The key under which to save the response.
                value (str): The raw user reply to store.

            Returns:
                str: Confirmation message of the form "Assigned: var_name = value".

            Example:
                assign_value("name", "John")
                # Returns: "Assigned: name = John"
            """
            self.script.assign(value)
            return f"Assigned: {value}"

        @tool
        def next_step() -> str:
            """
            Advance to the next scripted question.

            Returns:
                str: The next prompt if steps remain, otherwise:
                    "🎉 All inputs collected. Resume free chat."

            Example:
                next_step()
                # Returns: "What's the length of the pool?"
            """
            return self.script.next_prompt()

        return [assign_value, next_step]

    @property
    def instructions(self) -> str:
        return (
            "You are a scripted assistant.\n" 
            "On the first chat with the user always call next_step() to learn the first instructions"
            "On each turn:\n"
            "1. Call next_step() to retrieve and pose the next question (beginning with the first step).\n"
            "2. After you understand the user's answer, call assign_value(value), then next_step().\n"
            "3. Do not generate any free‐form text while steps remain—only invoke these tools. "
            "When next_step() returns “🎉 All inputs collected. Resume free chat.”, "
            "resume open‐domain conversation without using these tools."
        )
