from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx # For making HTTP requests to Ollama
import asyncio # For asynchronous operations

app = FastAPI()

# Configure CORS to allow communication from your Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Adjust this if your Streamlit runs on a different port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    model: str = "llama2" # Default to llama2, can be changed by frontend

@app.post("/chat")
async def chat_with_ollama(request: PromptRequest):
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False # Set to False for non-streaming response
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=payload, timeout=600) # Increased timeout
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            ollama_response = response.json()
            return {"response": ollama_response["response"]}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting Ollama: {e}"}
    except httpx.HTTPStatusError as e:
        return {"error": f"Ollama API returned an error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)