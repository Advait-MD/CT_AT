from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse

app = FastAPI()

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
            print(f"Received from client: {data}")
            await websocket.send_text(f"Echo: {data}")  # reply back
    except Exception as e:
        print("connection closed", e)