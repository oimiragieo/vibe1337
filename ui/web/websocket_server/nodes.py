import asyncio
import json
import sys
from pathlib import Path
from pocketflow import AsyncNode

# Add parent directories to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from core.agent_service import AgentService


class StreamingChatNode(AsyncNode):
    def __init__(self):
        super().__init__()
        # Initialize shared agent service
        self.agent = AgentService({})

    async def prep_async(self, shared):
        user_message = shared.get("user_message", "")
        websocket = shared.get("websocket")

        return user_message, websocket

    async def exec_async(self, prep_res):
        user_message, websocket = prep_res

        await websocket.send_text(json.dumps({"type": "start", "content": ""}))

        full_response = ""

        # Use AgentService streaming instead of direct OpenAI
        async for chunk in self.agent.process_streaming(user_message):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")

            # Send different types of updates
            if chunk_type == "planning":
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "content": content
                }))
            elif chunk_type == "tool_execution":
                await websocket.send_text(json.dumps({
                    "type": "tool",
                    "content": f"🛠️ {chunk.get('tool_name', 'tool')}: {content}"
                }))
            elif chunk_type == "chunk":
                full_response += content
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": content
                }))
            elif chunk_type == "end":
                if not full_response:
                    full_response = content

        await websocket.send_text(json.dumps({"type": "end", "content": ""}))

        return full_response, websocket

    async def post_async(self, shared, prep_res, exec_res):
        full_response, websocket = exec_res

        # Store in shared state for future reference if needed
        shared["last_response"] = full_response 