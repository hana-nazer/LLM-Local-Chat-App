# Local LLM Chat Application

A simple, local chat application that lets you interact with large language models (LLMs) running on your machine. The app features a web-based chat UI, model selection, and persistent chat history.

---

## Features

- **Chat with Local LLMs:** Send prompts and receive responses from models like LLaMA2 or Mistral running via Ollama.
- **Model Selection:** Choose which LLM to use from a dropdown in the UI.
- **Persistent Chat History:** Your chat history is saved and automatically reloaded when you revisit the app.
- **Clear Chat:** Easily clear your chat history from the UI.

---

## Project Structure

```
ChatApp/
├── backend/
│   └── backend.py         # FastAPI backend server
├── frontend/
│   ├── frontend.py        # Streamlit frontend app
│   └── chat_history.json  # (auto-generated) Persistent chat history
├── requirements.txt       # Python dependencies
```

---

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) (for running LLMs locally)
- The following Python packages (see `requirements.txt`):
  - fastapi
  - uvicorn
  - httpx
  - streamlit
  - requests

---

## Setup & Usage

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Ollama and Pull Models

Make sure [Ollama](https://ollama.com/) is installed and running.

To use a model (e.g., `llama2` or `mistral`), pull it with:

```bash
ollama pull llama2
ollama pull mistral
```

Check available models with:

```bash
ollama list
```

### 3. Start the Backend

```bash
cd backend
uvicorn backend:app --reload
```
This starts the FastAPI server at `http://localhost:8000`.

### 4. Start the Frontend

In a new terminal:

```bash
cd frontend
streamlit run frontend.py
```
This starts the Streamlit app at `http://localhost:8501`.

---

## How It Works

- The **frontend** (Streamlit) provides a chat interface. You can select the LLM model, enter prompts, and view responses.
- The **backend** (FastAPI) receives prompts from the frontend, forwards them to the Ollama API, and returns the LLM's response.
- **Chat history** is saved in `frontend/chat_history.json` and automatically loaded on app start.

---

## Chat History Persistence

- **How it works:**
  - Every time you send or receive a message, the chat history (all messages) is saved to a file named `chat_history.json` in the `frontend/` directory.
  - When you open or refresh the app, it automatically loads previous messages from this file, so your conversation continues where you left off.
  - If you clear the chat, the file is also cleared.
- **Format:**
  - The file stores a list of message objects, each with a `role` ("user" or "assistant") and `content` (the message text):
    ```json
    [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there!"}
    ]
    ```
- **Implementation:**
  - This is handled in `frontend/frontend.py` using Python's `json` and `os` modules for file I/O.
  - No external database is required; it's simple and local.

---

## Tools & Libraries Used

- **[Streamlit](https://streamlit.io/):** For building the interactive web-based chat UI.
- **[FastAPI](https://fastapi.tiangolo.com/):** For creating the backend API server.
- **[Ollama](https://ollama.com/):** For running LLMs (like LLaMA2, Mistral) locally and serving responses.
- **[httpx](https://www.python-httpx.org/):** For making asynchronous HTTP requests between frontend, backend, and Ollama.
- **[uvicorn](https://www.uvicorn.org/):** For running the FastAPI server.
- **Python Standard Library:** `os`, `json`, and `asyncio` for file handling, data serialization, and async operations.

---

## Customization

- **Add/Remove Models:**  
  Edit the `model_options` list in `frontend/frontend.py` to match the models you have available in Ollama.

- **Change Backend/Frontend Ports:**  
  Adjust the port numbers in `backend/backend.py` and `frontend/frontend.py` if needed.

- **Chat History File:**  
  The chat history is stored in `frontend/chat_history.json` as a list of message objects:
  ```json
  [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
  ```

---

## Troubleshooting

- **Model Not Found:**  
  If you see an error like `model 'mistral' not found`, make sure you have pulled the model with `ollama pull mistral`.

- **Backend Not Running:**  
  If the frontend cannot connect, ensure the FastAPI backend is running on the correct port.

- **Chat History Issues:**  
  If chat history does not persist, check file permissions for `frontend/chat_history.json`.

---

## Security Note

This app is for local/demo use. For production, consider:
- Adding authentication
- Using a database for chat history
- Securing API endpoints

---

## License

MIT (or specify your license here) 