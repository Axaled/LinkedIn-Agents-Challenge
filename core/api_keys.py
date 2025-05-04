import streamlit as st
import os

def init_api_keys():
    """ Create api_keys dict"""
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

def handle_api_keys_input():
    with st.sidebar.expander("API Keys", expanded=True):
        for api_name in ["Gemini", "Tavily"]:
            key = st.text_input(f"{api_name} API Key", type="password",
                                value=st.session_state.api_keys.get(f"{api_name}APIKey", ""),
                                help=f"Enter your {api_name} API key")
            if key:
                env_var = f"{api_name.upper()}_API_KEY"
                st.session_state.api_keys[f"{api_name}APIKey"] = key
                os.environ[env_var] = key
                st.success(f"{api_name} API Key set ✓")
