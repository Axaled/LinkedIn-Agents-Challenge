# 🤖 30 AI Agents in 30 Days

Welcome to my public challenge: building and releasing **one AI agent per day** for 30 days.  
Each agent solves a concrete problem using **LLMs + tools** — from email automation to smart task orchestration.

## 🌟 What You'll Find Here

- 🛠️ Daily agent builds with clean, open-source code  
- 📚 Technical explanations and architecture breakdowns  
- 💬 Real-world use cases explained for both non-tech and dev audiences  
- 🧪 Lessons learned along the way  

## 🚀 Why I'm Doing This

AI agents are more than just chatbots, they can **act** autonomously, combine tools, remember context, and evolve with feedback.  
This repo explores what it really means to turn language models into intelligent assistants that do real work.

## 📅 Daily Agents

I'll update this list every day:

| Day | Agent | Description |
|-----|-------|-------------|
| 1   | Calculator Agent | Chat GPT now knows how to make calculations without hallucinations! |
| 2   | Web Search Agent   | Browses the web to find relevant information    |
| 3   | Web Page Fetcher   | Reads the content of any url to answer questions   |
| 4   | File Analyser   | Is able to read files it receives as input  |
| 5   | Google docs Agent  | Is able to perform actions on Google docs, like saving a conversation  |
| 6  | Git Analyser Agent  | Retrieves public git repo to analyze them, will be used in collaboration with other agents  |
| 7  | Pool Quotation Agent  | Is a demo of the new ScriptedAgent I created, he will estimate the cost of your future swimming pool  |
| 8  | Custom Agent | Was made without any framework or wrapper, is a demo agent and is not available through the interface  |
| 9  | Email Agent | Sends email to the person you specify: with Object and Content|


## Installation

Before running the project, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Interface

To launch the interface, use the following command:

```bash
streamlit run interface.py
```

## Configuration

You can provide necessary environment variables at runtime or store them in a `.env` file to avoid entering them manually each time. I will make environment variables modifications possible on the interface really soon.


## 🗺️ License

MIT — use, remix, and build on it freely.

This is a personnal project, feel free to give me feedback and suggestions !

This project is licensed for personal use. Please include a reference to this repository in your work if you use any part of this project.