from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import google.generativeai as genai
import os
import json

# Initialize FastAPI app
app = FastAPI(title="Gemini API with FastAPI")

# Configure Gemini API (replace with your actual API key)
genai.configure(api_key="AIzaSyA9ZsXKBRcwNxFPazY4Cfe7f2lBbZeaHrI")

# Define request model for HTTP
class UserPrompt(BaseModel):
    prompt: str

# Root endpoint
@app.get("/")
async def root():
    return {"message": "WebSocket server is running"}

# HTTP endpoint to handle user prompts
@app.post("/generate")
async def generate_response(user_prompt: UserPrompt):
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response from Gemini
        response = model.generate_content(user_prompt.prompt)
        
        # Return the response
        return {
            "prompt": user_prompt.prompt,
            "response": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# WebSocket endpoint for Gemini API interaction
@app.websocket("/ws/generate")
async def websocket_gemini_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive prompt from client
            data = await websocket.receive_text()
            try:
                prompt_data = json.loads(data)
                prompt = prompt_data.get("prompt", "")
                
                if not prompt:
                    await websocket.send_json({"error": "No prompt provided"})
                    continue
                
                # Initialize Gemini model
                model = genai.GenerativeModel('gemini-pro')
                
                # Generate response
                response = model.generate_content(prompt)
                
                # Send response back to client
                await websocket.send_json({
                    "prompt": prompt,
                    "response": response.text
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                await websocket.send_json({"error": f"Error generating response: {str(e)}"})
                
    except WebSocketDisconnect:
        print("Client disconnected from /ws/generate")
    except Exception as e:
        print(f"WebSocket error in /ws/generate: {str(e)}")
        await websocket.close()

# WebSocket endpoint for echoing messages
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("connection open")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
            await websocket.send_text(f"Vesper: {data}")
    except WebSocketDisconnect:
        print("connection closed")
    except Exception as e:
        print("connection closed", e)
        await websocket.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}