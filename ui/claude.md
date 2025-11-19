# ui/ - VIBE1337 User Interfaces

## Overview
Contains user interface implementations for VIBE1337. **Important**: These are **STANDALONE APPLICATIONS** that are **NOT CONNECTED** to the main VIBE1337 agent (vibe1337.py).

## Status
- **Integration with main agent**: ⚠️ **0%** - Not connected
- **Standalone functionality**: ✅ Potentially working (not tested)
- **Framework**: PocketFlow (workflow orchestration)
- **Recommendation**: Either integrate or document as separate projects

## Directory Structure

```
ui/
├── voice/                      # ⚠️ STANDALONE - Voice chat interface
│   └── pocketflow_voice/       # OpenAI STT/TTS with PocketFlow
└── web/                        # ⚠️ STANDALONE - Web interface
    └── websocket_server/       # FastAPI + WebSocket
```

---

## ⚠️ voice/pocketflow_voice/ (STANDALONE)

**Status**: **NOT CONNECTED TO MAIN AGENT**
- Standalone voice chat application
- Uses PocketFlow for workflow orchestration
- Uses OpenAI for STT (Speech-to-Text) and TTS (Text-to-Speech)
- **NOT imported or referenced** by vibe1337.py

### Files

**Main Application**:
- `main.py` (27 LOC) - Entry point
- `flow.py` (25 LOC) - PocketFlow workflow definition
- `nodes.py` (unknown LOC) - Workflow nodes
- `requirements.txt` (52 bytes) - Dependencies

**Utilities** (utils/):
- `audio_utils.py` (4,910 bytes) - Audio processing
- `call_llm.py` (583 bytes) - LLM API calls
- `speech_to_text.py` (1,971 bytes) - OpenAI STT
- `text_to_speech.py` (1,515 bytes) - OpenAI TTS
- `tts_output.mp3` (65,664 bytes) - Sample audio output

**Documentation**:
- `README.md` (4,153 bytes) - Setup and usage
- `docs/design.md` (9,064 bytes) - Architecture design

### Architecture

**Workflow** (PocketFlow-based):
```
1. CaptureAudioNode      → Record user speech
2. SpeechToTextNode      → Convert to text (OpenAI Whisper)
3. QueryLLMNode          → Get LLM response
4. TextToSpeechNode      → Convert to speech (OpenAI TTS)
   └─► Loop back to 1 (next turn)
```

**Code** (flow.py:1-25):
```python
from pocketflow import Flow
from nodes import CaptureAudioNode, SpeechToTextNode, QueryLLMNode, TextToSpeechNode

def create_voice_chat_flow() -> Flow:
    capture_audio = CaptureAudioNode()
    speech_to_text = SpeechToTextNode()
    query_llm = QueryLLMNode()
    text_to_speech = TextToSpeechNode()

    # Define transitions
    capture_audio >> speech_to_text
    speech_to_text >> query_llm
    query_llm >> text_to_speech
    text_to_speech - "next_turn" >> capture_audio

    return Flow(start=capture_audio)
```

### Dependencies
```
pocketflow
openai
sounddevice
numpy
scipy
```

### Key Issue
**QueryLLMNode likely calls OpenAI directly**, NOT the VIBE1337 LLMOrchestrator!

This means:
- ❌ No multi-provider support (Ollama, Anthropic)
- ❌ No tool calling
- ❌ No memory system integration
- ❌ No VIBE1337 execution engine
- ✅ Just basic OpenAI chat

### To Integrate with Main Agent
1. Import VIBE1337Agent from vibe1337.py
2. Modify QueryLLMNode to call agent.process(user_input)
3. Handle async properly
4. Share memory system
5. Test end-to-end

---

## ⚠️ web/websocket_server/ (STANDALONE)

**Status**: **NOT CONNECTED TO MAIN AGENT**
- Standalone FastAPI web server
- WebSocket for real-time communication
- Uses PocketFlow for workflow
- **NOT imported or referenced** by vibe1337.py

### Files

**Main Application**:
- `main.py` (40 LOC) - FastAPI server + WebSocket endpoint
- `flow.py` (6 LOC) - PocketFlow workflow
- `nodes.py` (unknown LOC) - Streaming chat node
- `requirements.txt` (68 bytes) - Dependencies

**Static Assets**:
- `static/index.html` (7,288 bytes) - Chat interface
- `assets/banner.png` (684,587 bytes) - VIBE1337 banner

**Utilities** (utils/):
- `stream_llm.py` (732 bytes) - LLM streaming
- `__init__.py` (53 bytes)

**Documentation**:
- `README.md` (1,740 bytes) - Setup and usage
- `docs/design.md` (3,036 bytes) - Architecture design

### Architecture

**FastAPI Server** (main.py:1-40):
```python
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from flow import create_streaming_chat_flow

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_chat_interface():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    shared_store = {
        "websocket": websocket,
        "conversation_history": []
    }
    while True:
        data = await websocket.receive_text()
        shared_store["user_message"] = message.get("content", "")
        flow = create_streaming_chat_flow()
        await flow.run_async(shared_store)
```

**Workflow** (flow.py:1-6):
```python
from pocketflow import AsyncFlow
from nodes import StreamingChatNode

def create_streaming_chat_flow():
    return AsyncFlow(start=StreamingChatNode())
```

### Dependencies
```
fastapi
uvicorn
pocketflow
websockets
```

### Key Issue
**StreamingChatNode likely calls LLM directly**, NOT VIBE1337!

This means:
- ❌ No VIBE1337 orchestrator
- ❌ No tool calling
- ❌ No multi-provider support
- ❌ No security hardening
- ❌ Separate conversation history (not shared with main agent)

### To Integrate with Main Agent
1. Import VIBE1337Agent from vibe1337.py
2. Create agent instance in WebSocket handler
3. Call agent.process(user_message)
4. Stream response back over WebSocket
5. Share memory system
6. Handle errors gracefully

---

## Integration Challenges

### Why They're Disconnected

1. **Different frameworks**: Main agent is direct async/await, UIs use PocketFlow
2. **Different entry points**: Each has its own main.py
3. **Different dependencies**: UIs have additional requirements
4. **No shared state**: Separate memory, conversation history
5. **Not imported**: Grep confirms zero references to vibe1337.py

### Integration Approaches

**Option 1: Minimal Integration**
```python
# In voice/web nodes
from vibe1337 import VIBE1337Agent

class QueryLLMNode:
    def __init__(self):
        self.agent = VIBE1337Agent(config)

    async def execute(self, shared):
        result = await self.agent.process(shared["user_message"])
        shared["llm_response"] = result["response"]
```

**Option 2: Shared Service**
```python
# Run VIBE1337 as a service
# UIs call it via HTTP/WebSocket
# Requires: Adding API endpoints to VIBE1337

# In vibe1337.py
from fastapi import FastAPI
app = FastAPI()

@app.post("/query")
async def query(text: str):
    return await agent.process(text)

# UIs call: requests.post("http://localhost:8080/query", ...)
```

**Option 3: Merge Codebases**
```python
# Merge UI code into vibe1337.py
# Add FastAPI routes alongside CLI
# Unified memory and configuration
```

**Recommendation**: Option 1 (minimal integration) is fastest

---

## PocketFlow Framework

**What is PocketFlow?**
- Lightweight workflow orchestration framework
- Node-based execution flow
- Supports sync and async operations
- State sharing via `shared` dict

**Why it's used here**:
- Clean separation of concerns
- Easy to visualize workflow
- Handles state transitions
- Async support for IO-bound operations

**Example**:
```python
from pocketflow import Flow, Node

class MyNode(Node):
    async def execute(self, shared):
        shared["result"] = "processed"
        return "next_action"

node1 = MyNode()
node2 = AnotherNode()

# Define transitions
node1 >> node2  # Default transition
node1 - "error" >> error_handler  # Conditional transition

flow = Flow(start=node1)
flow.run(shared_state)
```

---

## Running the UIs

### Voice Chat
```bash
cd ui/voice/pocketflow_voice
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python main.py
```

**Expected behavior**:
1. Captures audio from microphone
2. Sends to OpenAI Whisper (STT)
3. Calls LLM (likely OpenAI, not VIBE1337)
4. Converts response to speech (TTS)
5. Plays audio
6. Loops

### Web Chat
```bash
cd ui/web/websocket_server
pip install -r requirements.txt
python main.py
```

**Then open**: http://localhost:8000

**Expected behavior**:
1. Shows chat interface
2. WebSocket connection
3. User types message
4. Calls LLM (likely OpenAI, not VIBE1337)
5. Streams response back
6. Updates UI

---

## Documentation Review

### voice/pocketflow_voice/README.md
- Setup instructions
- OpenAI API key requirement
- How to run
- **No mention of VIBE1337 integration**

### web/websocket_server/README.md
- FastAPI setup
- WebSocket protocol
- How to run
- **No mention of VIBE1337 integration**

**Conclusion**: Documentation confirms these are standalone apps

---

## Recommendations

### Immediate
1. **Document clearly**: Add "STANDALONE - Not integrated with main agent" to READMEs
2. **Decision needed**: Integrate or separate repository?
3. **Update main README**: Don't claim "Advanced UI" if not connected

### Short-term (if integrating)
1. Import VIBE1337Agent in LLM nodes
2. Call agent.process() instead of direct OpenAI
3. Share memory system
4. Test end-to-end
5. Update documentation

### Short-term (if separating)
1. Move to separate repositories
2. Remove from main codebase
3. Link in main README as "Related Projects"
4. Maintain independently

### Long-term
1. Unified architecture (if integrated)
2. Shared configuration
3. Consistent tool usage
4. Real-time streaming support in main agent
5. Multi-modal support (text + voice + web)

---

## Code Statistics

### voice/pocketflow_voice/
- **Files**: ~10 Python files + assets
- **LOC**: ~500 (estimated)
- **Integration**: 0%
- **Dependencies**: pocketflow, openai, sounddevice, numpy, scipy
- **Status**: Standalone

### web/websocket_server/
- **Files**: ~6 Python files + HTML/assets
- **LOC**: ~300 (estimated)
- **Integration**: 0%
- **Dependencies**: fastapi, uvicorn, pocketflow, websockets
- **Status**: Standalone

**Total**: ~800 LOC of UI code not connected to main agent

---

## For AI Assistants

**When working with UI code**:

✅ **DO**:
- Treat as separate applications
- Test standalone before integrating
- Check for conflicts with main agent
- Document integration approach

❌ **DON'T**:
- Assume they work with main VIBE1337 agent
- Modify without testing standalone
- Break standalone functionality when integrating
- Skip documentation updates

**Key understanding**: These are PocketFlow apps that call LLMs directly, bypassing VIBE1337's orchestrator, tools, and security.

---

## Summary

The `ui/` directory contains:
- ⚠️ **voice/pocketflow_voice/**: Standalone voice chat (~500 LOC)
- ⚠️ **web/websocket_server/**: Standalone web chat (~300 LOC)
- ✅ **Both potentially functional**: But not tested
- ❌ **Zero integration**: Not connected to main VIBE1337 agent

**Integration level**: 0%

**What they do**: Call OpenAI directly for chat, with voice/web interfaces

**What they don't do**:
- Use VIBE1337 orchestrator
- Call VIBE1337 tools
- Share VIBE1337 memory
- Support multi-provider LLMs
- Apply security hardening

**Recommendation**:
1. Short-term: Document as standalone
2. Long-term: Integrate via minimal approach (import VIBE1337Agent)
3. Alternative: Move to separate repos

**Codebase reduction opportunity**: Moving to separate repos would cut ~800 LOC with clear separation of concerns.
