import streamlit as st
import time
import json
import importlib
import os
import asyncio

st.set_page_config(page_title="AI Chat Interface", layout="wide")

def load_agent_config():
    """Load the agent configuration from JSON file"""
    try:
        with open('agents_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Configuration file 'agents_config.json' not found!")
        return {"agents": []}
    except json.JSONDecodeError:
        st.error("Invalid JSON in configuration file!")
        return {"agents": []}

def load_agent(module_path, class_name):
    """Dynamically load an agent class from the specified module"""
    try:
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        return agent_class()
    except Exception as e:
        st.error(f"Error loading agent: {str(e)}")
        return None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

if "agent_instance" not in st.session_state:
    st.session_state.agent_instance = None

st.title("AI Chat Interface")

agent_config = load_agent_config()

with st.sidebar:
    st.header("Configuration")
    
    agents = [agent["name"] for agent in agent_config["agents"]]
    
    selected_agent_name = st.selectbox("Select an agent", agents)

    selected_agent_info = next((agent for agent in agent_config["agents"] if agent["name"] == selected_agent_name), None)
    if selected_agent_info:
        st.info(selected_agent_info["description"])
    
    if st.button("Confirm selection"):
        if selected_agent_info:
            agent_instance = load_agent(selected_agent_info["module_path"], selected_agent_info["class_name"])
            if agent_instance:
                st.session_state.selected_agent = selected_agent_name
                st.session_state.agent_instance = agent_instance
                st.success(f"Agent {selected_agent_name} loaded successfully!")
                
                if st.checkbox("Reset chat history with the new agent"):
                    agent_instance.clear_chat()
                    st.session_state.messages = []

def get_agent_response(query, agent_instance) -> str:
    """Get the response from the agent from a query
    
    Args:
        query (str): The query to send to the agent
        agent_instance (Agent): The agent instance to send the query to

    Returns:
        str: The response from the agent
    """

    if agent_instance and hasattr(agent_instance, 'chat'):
        chat_method = getattr(agent_instance, 'chat')
        
        if asyncio.iscoroutinefunction(chat_method):
            return asyncio.run(chat_method(query))
        else:
            return chat_method(query)  
    
    return "Error: The agent does not have a 'chat' method"


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.selected_agent and st.session_state.agent_instance:
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
    
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            agent_response = get_agent_response(prompt, st.session_state.agent_instance)

            # This is just for a typing effect
            try:
                for chunk in str(agent_response).split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

            except Exception as e:
                print(f'Error: {e}')
                message_placeholder.markdown("Sorry, I encountered an unexpected error displaying your request, please try again")
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    st.info("Please select an agent in the sidebar to start.")
