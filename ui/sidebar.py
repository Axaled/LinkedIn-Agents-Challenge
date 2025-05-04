import streamlit as st

def display_sidebar(agent_config, agents):
    st.sidebar.header("Configuration")
    if agents:
        agent_name = st.sidebar.selectbox("Select an agent", agents)
        st.session_state.selected_agent_name = agent_name
        selected_info = next((a for a in agent_config["agents"] if a["name"] == agent_name), None)
        if selected_info:
            st.sidebar.info(selected_info.get("description", ""))
