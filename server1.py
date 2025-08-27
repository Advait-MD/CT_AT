from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv

app = FastAPI()

api_key = os.getenv("API_KEY") 

@app.get("/")
async def root():
    return {"message": "WebSocket server is running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("connection open")
    try:
        while True:
            # Receive JSON message from client
            data = await websocket.receive_text()
            try:
                prompt_data = json.loads(data)
                prompt = prompt_data.get("prompt", "")

                if not prompt:
                    await websocket.send_json({"error": "No prompt provided"})
                    continue

                # Call Gemini
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)

                # Send response
                await websocket.send_json({
                    "prompt": prompt,
                    "response": response.text
                })
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        print("connection closed")
    except Exception as e:
        print("connection closed", e)
        await websocket.close()