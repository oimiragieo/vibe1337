import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from flow import create_streaming_chat_flow

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_chat_interface():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Initialize shared store for this connection
    shared_store = {
        "websocket": websocket,
    }

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Update the current user message
            shared_store["user_message"] = message.get("content", "")

            # Create and run the flow
            flow = create_streaming_chat_flow()
            await flow.run_async(shared_store)

    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 