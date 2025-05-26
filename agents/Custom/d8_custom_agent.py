import os
import re
import io
import sys
import asyncio
import google.generativeai as genai

from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple

class CustomAgent:
    def __init__(self, model="gemini-1.5-flash-002", max_llm_calls=10):
        self.model = model
        self.MAX_LLM_CALLS = max_llm_calls
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("Please set GEMINI_API_KEY in your environment variables or .env file")
        genai.configure(api_key=api_key)
        
        self.genai_model = genai.GenerativeModel(self.model)
        self.chat_session = self.genai_model.start_chat(history=[])
        
        self.tools = self.create_tools()
        self.tool_descriptions = self.get_tool_descriptions()
    
    def create_tools(self) -> List[Dict[str, Any]]:
        """Lists available tools"""
        return [
            self.schedule_meeting_function(),
            self.final_answer_function()
        ]
    

    async def chat(self, prompt: str) -> str:
        return await self.agent_loop(prompt)

    def clear_chat(self) -> bool:
        """Clears chat history"""
        self.chat_session = self.genai_model.start_chat(history=[])
        return True

    def get_tool_descriptions(self) -> str:
        descriptions = []
        for tool in self.tools:
            desc = f"Tool: {tool['name']}\n"
            desc += f"Description: {tool['description']}\n"
            desc += "Parameters:\n"
            for param_name, param_info in tool['parameters']['properties'].items():
                required = "Required" if param_name in tool['parameters'].get('required', []) else "Optional"
                desc += f"- {param_name}: {param_info['description']} ({required}, Type: {param_info['type']})\n"
            descriptions.append(desc)
        return "\n".join(descriptions)

    async def agent_loop(self, prompt: str) -> str:
        """Main chat loop"""
        
        system_instructions = f"""You have access to:<tool_descriptions>
        {self.tool_descriptions}
        </tool_descriptions>

        To solve the task, you must plan forward to proceed in a series of steps, in a cycle of 'Thought:', 'Code:', and 'Observation:' sequences.

        At each step, in the 'Thought:' sequence, you should first explain your reasoning towards solving the task, then the tools that you want to use.
        Then in the 'Code:' sequence, you should write CLEAN Python code without any additional prefixes or syntax markers. Just pure Python code. The code sequence must end with 'End code' sequence.
        During each intermediate step, you can use 'print()' to save whatever important information you will then need.
        These print outputs will then be available in the 'Observation:' field, for using this information as input for the next step.

        In the end you have to return a final answer using the `final_answer` tool.

        Always provide a 'Thought:' and a 'Code:' sequence ending with 'End code' sequence. You MUST provide at least the 'Code:' sequence to move forward.

        IMPORTANT: When writing code, DO NOT include any prefix like 'python' or 'py' at the beginning of your code. Just write clean Python code directly.
        """

        full_prompt = f"{system_instructions}\n\nUser request: {prompt}"

        final_response = ""
        llm_call_count = 0
        current_context = full_prompt
        
        while llm_call_count < self.MAX_LLM_CALLS:
            llm_call_count += 1

            model_response = await self.call_llm(current_context)

            thought, code, remainder = self.extract_response_parts(model_response)
            
            # Building final response
            final_response += f"Thought: {thought}\n\nCode:\n```py\n{code}\n```\n\n"
            
            observation = await self.execute_code(code)
            final_response += f"Observation: {observation}\n\n"
            
            current_context = f"{current_context}\n\nThought: {thought}\n\nCode:\n{code}\nEnd code\n\nObservation: {observation}\n\nContinue with next step:"
            
            if "final_answer" in code:
                break
        
        return final_response

    async def call_llm(self, prompt: str) -> str:
        """Generate content from gemini API"""
        response = self.genai_model.generate_content(prompt)
        return response.text

    def extract_response_parts(self, response: str) -> Tuple[str, str, str]:
        """Extracts the Thoughts and Code parts of the response"""

        thought_match = re.search(r'Thought:(.*?)(?=Code:|$)', response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""
        
        code_pattern = r'Code:(?:\s*```(?:py|python)?\s*)?(.*?)(?:\s*```|/End code|\nEnd code)'
        code_match = re.search(code_pattern, response, re.DOTALL)
        
        if not code_match:
            # Implemented because of the llm hallucination
            code_pattern = r'```(?:py|python)?\s*(.*?)(?:\s*```)'
            code_match = re.search(code_pattern, response, re.DOTALL)
        
        code = ""
        if code_match:
            code = code_match.group(1).strip()

            if code.startswith('thon'):
                #implemented because of recurring llm hallucination
                code = code[4:].strip()
        
        remainder = response
        if code_match:
            end_pos = code_match.end()
            remainder = response[end_pos:].strip()
        
        return thought, code, remainder

    async def execute_code(self, code: str) -> str:
        """Executes the python code"""

        locals_dict = {
            "schedule_meeting": self.schedule_meeting,
            "final_answer": self.final_answer,
            "input": self.mock_input,
            "result": None
        }

        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        
        try:
            code = code.strip()
            
            # Executing code, I implemented this method because it is a simple use case, if you plan on using this agent
            # for more complex uses cases (which I DON'T recomand, it is a demo agent), you will need to restrict access
            exec(code, globals(), locals_dict)
            output = redirected_output.getvalue()
            
            if locals_dict.get("result") is not None:
                output += f"\nResult: {locals_dict['result']}"
            
            return output.strip() if output.strip() else "No output"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout
    
    def mock_input(self, prompt=""):
        """For demo purpose"""
        print(f"[Input prompt: {prompt}]")
        if "attendees" in prompt.lower():
            return "John, Sarah, Michael"
        elif "date" in prompt.lower():
            return "2024-11-02"
        elif "time" in prompt.lower():
            return "14:00"
        elif "topic" in prompt.lower():
            return "Q2 marketing strategy"
        else:
            return "Default mock response"

    #tool
    def schedule_meeting(self, attendees: List[str], date: str, time: str, topic: str) -> str:
        """Mockup method to schedule a meeting for demo purpose"""
        result = f"Meeting scheduled for {date}, at {time}, with attendees: {', '.join(attendees)}, to discuss the topic: {topic}. Attention, you should all bring your coffee mug"
        print(f"[Tool] schedule_meeting called: {result}")
        
        self.last_meeting = {
            "attendees": attendees,
            "date": date,
            "time": time,
            "topic": topic
        }
        
        return result
    
    #tool
    def final_answer(self, answer: str) -> str:
        """ Tool called when the chatbot is able to give a response"""
        print(f"[Tool] final_answer called with: {answer}")
        return answer

    def schedule_meeting_function(self) -> Dict[str, Any]:
        """Json sent to llm to give tool context"""
        return {
            "name": "schedule_meeting",
            "description": "Schedules a meeting with specified attendees at a given time and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of people attending the meeting.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the meeting (e.g., '2024-07-29')",
                    },
                    "time": {
                        "type": "string",
                        "description": "Time of the meeting (e.g., '15:00')",
                    },
                    "topic": {
                        "type": "string",
                        "description": "The subject or topic of the meeting.",
                    },
                },
                "required": ["attendees", "date", "time", "topic"],
            },
        }
    
    def final_answer_function(self) -> Dict[str, Any]:
        """Json sent to llm to give tool context"""
        return {
            "name": "final_answer",
            "description": "Use this to provide the final answer to the user's question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer to provide to the user.",
                    },
                },
                "required": ["answer"],
            },
        }

async def main():
    load_dotenv()
    agent = CustomAgent()
    
    test_prompt = "Please schedule a meeting with John, Sarah, and Michael for the 02/11/2024 at 2pm to discuss the Q2 marketing strategy and tell me if I should bring anything."
    print("Sending prompt to agent:", test_prompt)
    response = await agent.chat(test_prompt)
    print("\nAgent response:")
    print(response)
    
    test_prompt = "Who was involved in the meeting I just planned?"
    print("\nSending prompt to agent:", test_prompt)
    response = await agent.chat(test_prompt)
    print("\nAgent response:")
    print(response)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())