import os
import uuid
import json
import requests
from typing import List

from dotenv import load_dotenv
from msal import PublicClientApplication

from crewai.tools import tool
from agents.CrewAgents.crew_agent import CrewAIAgent


class OutlookAgent(CrewAIAgent):
    def __init__(self, model="gemini/gemini-2.0-flash-lite"):
        load_dotenv()
        os.makedirs("temp_uploads", exist_ok=True)
        self.token_file = "temp_uploads/outlook_token.json"
        self.access_token = None
        self.device_flow_data = None
        self.chat_instantiation = True
        self.role  = "Your custom Outlook-aware assistant",
        self.goal = "Send and manage your emails via Outlook seamlessly.",
        self.instructions = "Always confirm authentication before sending mail, and summarize sent items.",
        self.knowledge = "This agent knows how to interact with Microsoft Graph Mail API."
        super().__init__(model)
        self.tools = self._create_tools()

    def is_identified(self) -> bool:
        if self.access_token:
            return True
        token = self._load_token()
        if token:
            self.access_token = token
            return True
        return False

    def _load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                data = json.load(f)
            return data.get("access_token")
        return None

    def _save_token(self, token):
        with open(self.token_file, "w") as f:
            json.dump({"access_token": token}, f)

    def _start_auth_flow(self) -> str:
        msa_client_id = os.getenv("MSA_CLIENT_ID")
        if not msa_client_id:
            raise ValueError("Missing MSA_CLIENT_ID in environment")

        app = PublicClientApplication(
            client_id=msa_client_id,
            authority="https://login.microsoftonline.com/consumers"
        )
        self.device_flow_data = app.initiate_device_flow(scopes=["https://graph.microsoft.com/Mail.Send"])
        if "user_code" not in self.device_flow_data:
            raise Exception(f"Device flow failed: {self.device_flow_data.get('error_description', 'Unknown error')}")
        self.app = app
        print (self.device_flow_data["message"])
        return self.device_flow_data["message"]

    def _complete_auth_flow(self) -> bool:
        if not self.device_flow_data or not self.app:
            raise Exception("Authentication flow not started. Call `start_authentication` first.")
        result = self.app.acquire_token_by_device_flow(self.device_flow_data)
        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_token(self.access_token)
            return True
        raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")

    def _create_tools(self) -> List:
        @tool("complete_authentication")
        def complete_auth_tool() -> str:
            """
            Completes the Outlook authentication process after user logs in via browser.
            Run this after `start_authentication`.
            """
            if self.is_identified():
                return "✅ Already authenticated."
            try:
                success = self._complete_auth_flow()
                return "🔓 Authentication successful." if success else "❌ Authentication failed."
            except Exception as e:
                return f"❌ Error: {str(e)}"

        @tool("send_personal_email")
        def send_email_tool(subject: str, body: str, recipients: List[str]) -> str:
            """
            Sends an email via the connected Outlook account.

            ⚠️ Please run `complete_authentication()` before using this tool.
            If it returns False, use `start_authentication` and `complete_authentication` first.
            """
            if not self.is_identified():
                return "❗ Not authenticated. Please run  `complete_authentication`."

            url = "https://graph.microsoft.com/v1.0/me/sendMail"
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "Text", "content": body},
                    "toRecipients": [{"emailAddress": {"address": addr}} for addr in recipients]
                },
                "saveToSentItems": True
            }

            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code == 202:
                return f"📨 Email sent to: {', '.join(recipients)}"
            else:
                return f"❌ Failed: {response.status_code} - {response.text}"

        return [complete_auth_tool, send_email_tool]
    
    def chat(self, prompt):
        if self.chat_instantiation:
            self.chat_instantiation = False
            if self.is_identified():
                return super().chat(prompt)
            return "First we need to log you in to your personnal Outlook account \n" + self._start_auth_flow()
        return super().chat(prompt)
