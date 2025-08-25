from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

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