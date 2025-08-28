from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from pydantic import BaseModel
import json, os, asyncio
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

@app.get("/")
async def root():
    return {"message": "WebSocket server is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("connection open")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                prompt_data = json.loads(data)
                prompt = prompt_data.get("prompt", "")

                if not prompt:
                    await websocket.send_json({
                        "prompt": "",
                        "response": "",
                        "error": "No prompt provided"
                    })
                    continue

                # Call Gemini safely (run blocking in thread)
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)

                # Ensure safe string response
                reply_text = getattr(response, "text", None)
                if not reply_text:
                    reply_text = str(response)

                await websocket.send_json({
                    "prompt": prompt,
                    "response": reply_text,
                    "error": None
                })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "prompt": "",
                    "response": "",
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "prompt": "",
                    "response": "",
                    "error": str(e)
                })

    except WebSocketDisconnect:
        print("connection closed")
    except Exception as e:
        print("connection closed", e)
        await websocket.close()
