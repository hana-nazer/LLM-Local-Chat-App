import streamlit as st
import httpx # For making HTTP requests to FastAPI
import asyncio # For asynchronous operations
import os
import json

# Set Streamlit page configuration
st.set_page_config(page_title="Local LLM Chat", layout="wide")

CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'chat_history.json')

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, 'r') as f:
                history = json.load(f)
                if not isinstance(history, dict):
                    return {} # Return empty dict if not in correct format
                return history
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_chat_history(history):
    try:
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

# Load chat history
chat_history = load_chat_history()

# Initialize session state for active chat
if "active_chat" not in st.session_state:
    st.session_state.active_chat = []

# Initialize session state for model selection
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama2"

# Sidebar for model selection and chat history
with st.sidebar:
    st.title("Settings")

    # Model selection dropdown
    model_options = ["llama2", "mistral"]
    st.session_state.selected_model = st.selectbox(
        "Choose LLM Model:",
        model_options,
        index=model_options.index(st.session_state.get("selected_model", "llama2"))
    )

    st.title("Chat History")

    if st.button("New Chat"):
        st.session_state.active_chat = []
        st.rerun()

    for chat_title in reversed(list(chat_history.keys())):
        if st.button(chat_title, key=chat_title):
            st.session_state.active_chat = chat_history[chat_title]
            st.rerun()

    # Add a spacer to fill the sidebar
    st.markdown("""
        <style>
        div[data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .clear-chat-bottom {
            margin-top: auto;
            margin-bottom: 5px;
        }
        </style>
        <div class='clear-chat-bottom'>
        </div>
    """, unsafe_allow_html=True)

    # Place the clear button at the bottom with margin
    clear = st.button("Clear All Chat History", key="clear_all_chat")
    if clear:
        chat_history = {}
        save_chat_history(chat_history)
        st.session_state.active_chat = []
        st.rerun()


st.title("💬 Local LLM Chat")
st.caption("Powered by Streamlit, FastAPI, and Ollama (LLaMA2, Mistral, etc.)")

# Display active chat messages
for message in st.session_state.active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to send prompt to FastAPI backend
async def send_prompt_to_backend(prompt, model):
    fastapi_url = "http://localhost:8000/chat"
    payload = {"prompt": prompt, "model": model}

    try:
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(fastapi_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        st.error(f"Backend communication error: {e}")
        return None

# Handle user input
if prompt := st.chat_input("Say something to your local LLM..."):
    # Add user message to active chat
    st.session_state.active_chat.append({"role": "user", "content": prompt})

    # If this is the first message, use it as the chat title
    is_new_chat = len(st.session_state.active_chat) == 1
    if is_new_chat:
        chat_title = prompt[:50] # Use first 50 chars as title
    else:
        # Find the title from the first message
        chat_title = st.session_state.active_chat[0]['content'][:50]


    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from backend
    with st.spinner("Thinking..."):
        response_content = asyncio.run(send_prompt_to_backend(prompt, st.session_state.selected_model))

    if response_content:
        # Add assistant response to active chat
        st.session_state.active_chat.append({"role": "assistant", "content": response_content})
        
        # Save updated chat history
        chat_history[chat_title] = st.session_state.active_chat
        save_chat_history(chat_history)

        # Rerun to update the display
        st.rerun()
    else:
        st.error("Failed to get a response from the backend.")
        # remove user message if backend fails
        st.session_state.active_chat.pop()