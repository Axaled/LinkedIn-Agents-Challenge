# Day 2 of the challenge, this is an agent that browses the web to find the best 
# potential website to give an answer to a question
import core.sqlite_patch as sqlite_patch

import os
import json

from tavily import TavilyClient
from crewai.tools import tool
from CrewAgents.crew_agent import CrewAIAgent

from typing import List

class TavilySearchAgent(CrewAIAgent):

    def __init__(self, model="gemini/gemini-1.5-pro"):
        super().__init__(model)
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")

        self.tavily_client = TavilyClient(api_key=self.tavily_key)


    def _create_tools(self) -> List:
        
        @tool("Web Search")
        def web_search_wrapper(query:str) -> str:
            """ 
            This function searches the 'query' on the web to return the results
            Takes the query string as a parameter 
            """
            return self.web_search(query)

        return [web_search_wrapper]
    
    def web_search(self, query: str) -> str:
        """ 
        This function searches the 'query' on the web to return the results
        Takes the query string as a parameter 
        """
        response = self.tavily_client.search(query)
        results = json.dumps(response.get('results', []))

        print(f"Web results: for {query}: \n {results}")
        return results
    

def main():
    tavily_agent = TavilySearchAgent()
    query = "best AI agent framework"
    results = tavily_agent.chat(query)

    print("Résultats de la recherche :")
    print(results)

if __name__ =="__main__":
    main()
