import os
import time
import streamlit as st
from core.agent_manager import (
    load_agents_config,
    get_agent_names,
    get_agent_info,
    check_required_apis,
    load_agent_instance,
)
from core.api_keys import init_api_keys, handle_api_keys_input


# page config
st.set_page_config(page_title="AI Chat Interface", layout="wide")

init_api_keys()

# session state init
for var, default in [
    ("messages", []),
    ("selected_agent_name", None),
    ("agent_instance", None),
    ("api_keys", {}),
]:
    if var not in st.session_state:
        st.session_state[var] = default

# titre
st.title("AI Chat Interface")

# sidebar - configuration
with st.sidebar:
    st.header("Configuration")

    # API keys
    handle_api_keys_input()

    # load config file
    config = load_agents_config(path="config/agents_config.json")
    names = get_agent_names(config)

    if names:
        choice = st.selectbox("Select an agent", names)
        st.session_state.selected_agent_name = choice

        info = get_agent_info(config, choice)
        if info and info.get("description"):
            st.info(info["description"])

        # show missing keys
        if info:
            missing = check_required_apis(info, st.session_state.api_keys)
            if missing:
                st.warning(f"Missing API key(s): {', '.join(missing)}")

        if st.button("Confirm selection"):
            if info:
                missing = check_required_apis(info, st.session_state.api_keys)
                if missing:
                    st.error(f"Cannot load agent, missing: {', '.join(missing)}")
                else:
                    try:
                        inst = load_agent_instance(info, st.session_state.api_keys)
                        st.session_state.agent_instance = inst
                        st.success(f"Loaded agent {choice}")
                    except Exception as e:
                        st.error(f"Error loading agent: {e}")
    else:
        st.warning("No agents in config")

# chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# chat input / response
if st.session_state.agent_instance:
    if prompt := st.chat_input("Ask your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            try:
                resp = st.session_state.agent_instance.chat(prompt)
                for w in str(resp).split():
                    full += w + " "
                    time.sleep(0.05)
                    placeholder.markdown(full + "▌")
                placeholder.markdown(full)
            except Exception:
                placeholder.markdown("Sorry, I encountered an unexpected error during response")
        st.session_state.messages.append({"role": "assistant", "content": full})
elif not names:
    st.info("Please add agents to config")
else:
    st.info("Select and confirm an agent to start chatting")
