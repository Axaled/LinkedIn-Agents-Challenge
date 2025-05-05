import core.sqlite_patch as sqlite_patch

from CrewAgents.crew_agent import CrewAIAgent

import os
import uuid

from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from typing import List
from crewai.tools import tool


SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file"
]

class GoogleDocsAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-1.5-pro"):

        self.session_id = str(uuid.uuid4())
        super().__init__(model)
        self._init_google_services()

        self.tools = self._create_tools()  
        self.crew = Crew(agents=[self.agent], tasks=[self.task], verbose=False)

    def _init_google_services(self):
        """Initialise docs_service et drive_service avec OAuth2."""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.docs_service = build("docs", "v1", credentials=creds) 
        self.drive_service = build("drive", "v3", credentials=creds)

    def _create_tools(self) -> List:
        @tool("save_conversation")
        def save_conv_tool() -> str:
            doc = self._create_doc()
            self._insert_conversation(doc_id=doc["documentId"])
            return f"Conversation saved to Google Docs (ID: {doc['documentId']})"
        return [save_conv_tool]

    def chat(self, message: str) -> str:
        if message.strip().lower() == "save conversation as document":
            return self.tools[0]()  
        return super().chat(message)

    def _create_doc(self) -> dict:
        """Crée un document vierge dans Drive."""
        
        body = {"title": f"Conversation_{self.session_id}_{datetime.now(timezone.utc).isoformat()}"}
        doc = self.docs_service.documents().create(body=body).execute()  
        return doc

    def _insert_conversation(self, doc_id: str):
        """Insère toute la conversation en un seul batchUpdate."""

        requests = []
        index = 1
        for msg in self.messages:
            text = f"{msg['role'].upper()}: {msg['content']}\n"
            requests.append({
                "insertText": {
                    "location": {"index": index},
                    "text": text
                }
            })
            index += len(text) 

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute() 

    def list_saved_docs(self, folder_id: str, page_size: int = 10):
        """Exemple: liste les fichiers dans un dossier Drive."""
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        res = self.drive_service.files().list(
            q=query, pageSize=page_size, fields="files(id, name)"
        ).execute() 
        return res.get("files", [])
