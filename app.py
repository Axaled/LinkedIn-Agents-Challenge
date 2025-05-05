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

st.set_page_config(page_title="AI Chat Interface", layout="wide")
init_api_keys()

def init_session_state():
    defaults = {
        "messages": [],
        "selected_agent_name": None,
        "agent_instance": None,
        "api_keys": {},
        "uploaded_files": [],
    }
    for key, default in defaults.items():
        st.session_state.setdefault(key, default)

init_session_state()

def get_current_agent(config):
    name = st.session_state.selected_agent_name
    if not name:
        return {}, False
    info = get_agent_info(config, name) or {}
    return info, info.get("accepts_file_input", False)

def sidebar_agent_selector():
    st.header("Configuration")
    handle_api_keys_input()

    config = load_agents_config(path="config/agents_config.json")
    names = get_agent_names(config)
    if not names:
        st.warning("No agents in config")
        return config

    choice = st.selectbox("Select an agent", names)
    st.session_state.selected_agent_name = choice

    info, _ = get_current_agent(config)
    if info.get("description"):
        st.info(info["description"])

    missing = check_required_apis(info, st.session_state.api_keys)
    if missing:
        st.warning(f"Missing API key(s): {', '.join(missing)}")

    if st.button("Confirm selection"):
        if missing:
            st.error(f"Cannot load agent, missing: {', '.join(missing)}")
        else:
            try:
                inst = load_agent_instance(info, st.session_state.api_keys)
                st.session_state.agent_instance = inst
                st.success(f"Loaded agent {choice}")
            except Exception as e:
                st.error(f"Error loading agent: {e}")

    return config

def file_uploader_panel(config):
    info, accepts_files = get_current_agent(config)
    if not accepts_files:
        return

    st.subheader("Upload Files")
    uploaded = st.file_uploader(
        "Upload PDF files to share with the AI",
        accept_multiple_files=True,
        type=["pdf"]
    )

    if uploaded:
        upload_dir = os.path.abspath("temp_uploads")
        os.makedirs(upload_dir, exist_ok=True)
        new_files = []
        for uploaded_file in uploaded:
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            new_files.append({
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size,
            })
        if new_files:
            st.session_state.uploaded_files = new_files
            st.success(f"Uploaded {len(new_files)} file(s)")

    if st.session_state.uploaded_files:
        st.subheader("Current Files")
        file_name_list = ", ".join([f"`{f['name']}`" for f in st.session_state.uploaded_files])
        st.markdown(f"Working with: {file_name_list}")
        if st.button("Clear files"):
            for file_info in st.session_state.uploaded_files:
                try:
                    os.remove(file_info["path"])
                except Exception:
                    pass
            st.session_state.uploaded_files = []
            st.success("All files cleared")

st.title("AI Chat Interface")

with st.sidebar:
    config = sidebar_agent_selector()

if st.session_state.agent_instance:
    file_uploader_panel(config)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask your question...")
    if prompt:
        info, accepts_files = get_current_agent(config)
        files_param = st.session_state.uploaded_files if accepts_files else None
        file_context = (
            "\n\nUser has uploaded: " + ", ".join([f['name'] for f in st.session_state.uploaded_files])
            if accepts_files and st.session_state.uploaded_files else ""
        )

        user_message = prompt + file_context
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            try:
                resp = (
                    st.session_state.agent_instance.chat(user_message)
                )
                for word in str(resp).split():
                    full += word + " "
                    time.sleep(0.05)
                    placeholder.markdown(full + "▌")
                placeholder.markdown(full)
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {e}"
                placeholder.markdown(error_message)
                full = error_message

        st.session_state.messages.append({"role": "assistant", "content": full})
elif not get_agent_names(load_agents_config(path="config/agents_config.json")):
    st.info("Please add agents to config")
else:
    st.info("Select and confirm an agent to start chatting")
