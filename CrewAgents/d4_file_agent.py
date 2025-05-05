import core.sqlite_patch as sqlite_patch


from CrewAgents.crew_agent import CrewAIAgent

import os


from typing import List
from crewai.tools import tool
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA


class DocumentAnalysisAgent(CrewAIAgent):
    def __init__(self, model: str = "gemini/gemini-1.5-flash-002"):
        self.role = "AI assistant specialized in document analysis"
        self.goal = ("To extract, summarize, and analyze content from documents provided by the user."
                     )
        self.instructions = ("Use the document analysis tool when a document is provided;"
                             " otherwise, answer based on conversational context.")
        self.backstory = "Expert in understanding and processing PDFs and other document formats."

        super().__init__(model)



    def _create_tools(self) -> List:
        @tool("analyze_document")
        def analyze_document_tool(doc_name: str, query: str) -> str:
            """
            Ingest and analyze a document, then answer the user query based on its content.
            Parameters:
            - doc_name (str): The name of the document to be analyzed.
            - query (str): A query for the llm to retrieve the information needed
            Returns:
            - str: Answer to the query, with references to the document.
            """
            return self.analyze_document(doc_name, query)
        
        return [analyze_document_tool]

    def analyze_document(self, filename: str, query: str) -> str:
        """
        filename: nom du PDF (ex. 'doc.pdf').
        """
        try:
            
            # Adds the document name to the root of the project
            base = os.getcwd()
            upload_dir = os.path.join(base, "temp_uploads")
            abs_path = os.path.join(upload_dir, filename)

            if not os.path.isfile(abs_path):
                raise FileNotFoundError(f"[STEP {step}] Fichier non trouvé : {abs_path}")
            
            loader = PyPDFLoader(abs_path)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(docs)

            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            db = FAISS.from_documents(chunks, embeddings)

            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

            step = 6
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=db.as_retriever()
            )
            return qa.run(query)

        except Exception as e:
            msg = f"Error in document analysis : {type(e).__name__} : {e}"
            raise RuntimeError(msg)
