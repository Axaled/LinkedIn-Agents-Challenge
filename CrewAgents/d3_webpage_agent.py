# Day 3 of the challenge, this agent can read any webpage 

import core.sqlite_patch as sqlite_patch
import requests

from typing import List
from crewai.tools import tool
from CrewAgents.crew_agent import CrewAIAgent
from bs4 import BeautifulSoup
from readability import Document


class WebPageAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-1.5-pro"):

        self.role = "Web content analyzer"
        self.goal = "To fetch, parse, and summarize the main content of any webpage provided."
        self.instructions = (
            "If you see a url in the question,"
            "Always use the query_page tool to retrieve content from the given URL. "
            "Ensure the content is cleaned, readable, and only includes the main article body. "
            "Do not hallucinate or fabricate content. Be accurate and concise."
        )
        self.knowledge = (
            "You can read webpages and summarize them. "
            "You do not have knowledge beyond the retrieved content unless explicitly stated."
        )
        super().__init__(model)

    def _create_tools(self) -> List:
        @tool("query_page")
        def page_query_tool(url: str) -> str:
            """
            Tool to fetch and extract the main readable content from a webpage.

            Parameters:
            - url (str): link to the page to explore
            

            returns:
            - body (str): the body of the queried html page 

            """
            return self._query_page(url)

        return [page_query_tool]
    
    def _query_page(self, url:str):
        html = self._fetch_page(url)
        print(self._extract_main_text(html))
        return self._extract_main_text(html)


    @staticmethod
    def _fetch_page(url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            return f"HTTP error occurred: {e}"
        except requests.exceptions.Timeout:
            return "The request timed out."
        except requests.exceptions.RequestException as e:
            return f"An unexpected error occurred: {e}"

    
    @staticmethod
    def _extract_main_text(html: str) ->str:
        # This method extracts only the relevant context of the document
        doc = Document(html)
        return BeautifulSoup(doc.summary(), "html.parser").get_text(separator="\n")
