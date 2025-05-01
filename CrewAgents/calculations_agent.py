from typing import Callable, List
from crewai.tools import tool
from CrewAgents.crew_agent import CrewAIAgent


class CalculationAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-1.5-pro"):
        super().__init__(model)

    def _create_tools(self) -> List:
        @tool("calculate")
        def calculate_tool(operator: str, a: float, b: float) -> float:
            """
            Perform a basic arithmetic operation between two numbers.

            This tool supports four operations: addition, subtraction, multiplication, and division.
            
            Parameters:
            - operator (str): The type of operation to perform. It must be one of:
                - "add": to compute a + b
                - "subtract": to compute a - b
                - "multiply": to compute a * b
                - "divide": to compute a / b (division by zero is not allowed)
            
            - a (float): The first number in the operation.
            - b (float): The second number in the operation.

            Returns:
            - float: The result of the calculation.

            Examples:
            - To compute 5 + 2:
                operator="add", a=5, b=2
            - To compute 10 / 5:
                operator="divide", a=10, b=5

            Only use this tool for basic numerical calculations between two values.
            """
            # If you want to ensure the llm used the tool:
            print("Calculator used")
            return self._calculate(operator, a, b)

        return [calculate_tool]

    @staticmethod
    def _calculate(operator: str, a: float, b: float) -> float:
        operations: dict[str, Callable[[float, float], float]] = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else CalculationAgent._raise_zero_division()
        }

        if operator not in operations:
            raise ValueError(f"Unsupported operator: '{operator}'. Expected one of {list(operations.keys())}.")
        return operations[operator](a, b)

    @staticmethod
    def _raise_zero_division():
        raise ZeroDivisionError("Cannot divide by zero.")


def main():
    calculation_agent = CalculationAgent()
    result = calculation_agent.chat("Combien font 23049/123495849")  
    print(result)


if __name__ == "__main__":
    main()
