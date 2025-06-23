import streamlit as st
import httpx # For making HTTP requests to FastAPI
import asyncio # For asynchronous operations
import os
import json

# Set Streamlit page configuration
st.set_page_config(page_title="Local LLM Chat", layout="centered")

CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'chat_history.json')

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_chat_history(messages):
    try:
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(messages, f)
    except Exception:
        pass

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Model selection dropdown
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama2"

model_options = ["llama2", "mistral"]
st.session_state.selected_model = st.selectbox(
    "Choose LLM Model:",
    model_options,
    index=model_options.index(st.session_state.selected_model)
)

st.title("💬 Local LLM Chat")
st.caption("Powered by Streamlit, FastAPI, and Ollama (LLaMA2, Mistral, etc.)")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to send prompt to FastAPI backend
async def send_prompt_to_backend(prompt):
    fastapi_url = "http://localhost:8000/chat"
    payload = {"prompt": prompt, "model": st.session_state.selected_model}  # Use selected model

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(fastapi_url, json=payload, timeout=600) # Increased timeout
            response.raise_for_status()
            data = response.json()
            if "response" in data:
                return data["response"]
            elif "error" in data:
                st.error(f"Backend error: {data['error']}")
                return None
            else:
                st.error("Unexpected backend response format.")
                return None
    except httpx.RequestError as e:
        st.error(f"Could not connect to FastAPI backend: {e}")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"FastAPI backend returned an error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# React to user input
if prompt := st.chat_input("Say something to your local LLM..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_history(st.session_state.messages)

    # Get response from backend
    with st.spinner("Thinking..."):
        # Run the async function
        response_content = asyncio.run(send_prompt_to_backend(prompt))

    if response_content:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response_content)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        save_chat_history(st.session_state.messages)

# Optional: Clear chat history button
if st.button("Clear Chat"):
    st.session_state.messages = []
    save_chat_history(st.session_state.messages)
    st.rerun()