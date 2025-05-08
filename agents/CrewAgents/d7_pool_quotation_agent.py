from typing import List
from crewai.tools import tool
from agents.CrewAgents.crew_agent import CrewAIAgent
from core.script_engine.script import Script
from core.script_engine.step import Step
from core.script_engine.validator import Range, Regex


class PoolQuotationAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-2.0-flash-lite"):
        self.role = "Pool price estimator"
        self.goal = "To calculate the estimated price for a pool based on its dimensions."
        self.knowledge = (
            "You are a pool price estimator. You calculate the price based on the length and width of the pool "
        )
        super().__init__(model)

    def get_script(self):
        """
        Defines the steps of the script for the pool quote process.
        """
        return Script(steps=[
            Step("What is the length of your pool (in meters)?", "length", float, validators=[Range(1, 15)]),
            Step("What is the width of your pool (in meters)?", "width", float, validators=[Range(1, 10)]),
            Step("Please provide your email address:", "email", str, validators=[Regex(r".+@.+\..+")]),
        ])
    

    def _create_tools(self) -> List:
        @tool("calculate_price")
        def price_calculation_tool(length: float, width: float) -> float:
            """
            Tool to calculate the estimated price of a pool based on its length and width.

            Parameters:
            - length (float): the length of the pool in meters.
            - width (float): the width of the pool in meters.

            Returns:
            - float: the estimated price of the pool.
            """
            return self._calculate_pool_price(length, width)

        return [price_calculation_tool]

    def _calculate_pool_price(self, length: float, width: float) -> float:
        """
        Calculates the price of the pool based on its length and width.

        Parameters:
        - length (float): the length of the pool.
        - width (float): the width of the pool.

        Returns:
        - float: the estimated price of the pool.
        """

        return length * width * 520 # I chose a random value but you can implement your own business logic there
