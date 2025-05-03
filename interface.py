import streamlit as st
import time
import json
import importlib
import os
import asyncio


st.set_page_config(page_title="AI Chat Interface", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

if "agent_instance" not in st.session_state:
    st.session_state.agent_instance = None

# Dictionary to store API keys
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {}

st.title("AI Chat Interface")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input in sidebar
    with st.expander("API Keys", expanded=True):
        # Gemini API Key
        gemini_key = st.text_input("Gemini API Key", 
                                  type="password", 
                                  value=st.session_state.api_keys.get("GeminiAPIKey", ""),
                                  help="Enter your Gemini API key")
        
        # Tavily API Key
        tavily_key = st.text_input("Tavily API Key (Optional)", 
                                   type="password", 
                                   value=st.session_state.api_keys.get("TavilyAPIKey", ""),
                                   help="Enter your Tavily API key")
        
        # Save API keys to session state
        if gemini_key:
            st.session_state.api_keys["GeminiAPIKey"] = gemini_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            st.success("Gemini API Key set ✓")
        
        if tavily_key:
            st.session_state.api_keys["TavilyAPIKey"] = tavily_key
            os.environ["TAVILY_API_KEY"] = tavily_key
            st.success("Tavily API Key set ✓")

    # Load agent configuration
    try:
        with open('agents_config.json', 'r') as f:
            agent_config = json.load(f)
    except FileNotFoundError:
        st.error("Configuration file 'agents_config.json' not found!")
        agent_config = {"agents": []}
    except json.JSONDecodeError:
        st.error("Invalid JSON in configuration file!")
        agent_config = {"agents": []}
    
    # Agent selection
    agents = [agent["name"] for agent in agent_config["agents"]]
    
    if agents:
        selected_agent_name = st.selectbox("Select an agent", agents)

        selected_agent_info = next((agent for agent in agent_config["agents"] if agent["name"] == selected_agent_name), None)
        if selected_agent_info:
            st.info(selected_agent_info["description"])
            
            # Check if agent requires an API key
            required_api = selected_agent_info.get("requires")
            if required_api:
                api_key_provided = st.session_state.api_keys.get(required_api, "")
                if not api_key_provided:
                    st.warning(f"This agent requires a {required_api}. Please provide it in the API Keys section.")
        
        if st.button("Confirm selection"):
            if selected_agent_info:
                # Check if required API key is provided
                required_api = selected_agent_info.get("requires")
                if required_api and not st.session_state.api_keys.get(required_api):
                    st.error(f"Cannot load agent: {required_api} is required.")
                else:
                    try:
                        module = importlib.import_module(selected_agent_info["module_path"])
                        agent_class = getattr(module, selected_agent_info["class_name"])
                        
                        # Set environment variables for API keys
                        for key_name, key_value in st.session_state.api_keys.items():
                            if key_value:
                                os.environ[key_name.upper()] = key_value

                        agent_instance = agent_class()
                        
                        st.session_state.selected_agent = selected_agent_name
                        st.session_state.agent_instance = agent_instance
                        
                        st.success(f"Agent {selected_agent_name} loaded successfully!")
                    except Exception as e:
                        st.error(f"Error loading agent: {str(e)}")
    else:
        st.warning("No agents available in configuration.")

# Function to get agent response
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

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and response
if st.session_state.selected_agent and st.session_state.agent_instance:
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
    
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            agent_response = get_agent_response(prompt, st.session_state.agent_instance)

            # Typing effect
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
elif not agents:
    st.info("Please check your agent configuration file.")
else:
    st.info("Please select an agent in the sidebar to start.")