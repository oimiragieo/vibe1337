# UI Module - User Interfaces for VIBE1337

## Overview

The `ui/` directory contains alternative user interfaces for interacting with the VIBE1337 agent. Currently includes a web-based chat interface and a voice interaction interface.

**Critical Issue:** Both UIs are **standalone implementations** that bypass the core agent infrastructure (ToolRegistry, LLMOrchestrator, MemorySystem). They make direct OpenAI API calls instead of using the unified agent architecture.

## Structure

```
ui/
├── web/                           # Web-based chat interface
│   └── websocket_server/         # FastAPI + WebSocket server
│       ├── main.py               # Server entry point
│       ├── flow.py               # PocketFlow flow definition
│       ├── nodes.py              # Streaming chat node
│       ├── requirements.txt      # Web UI dependencies
│       ├── README.md
│       ├── static/
│       │   └── index.html        # Chat interface
│       ├── docs/
│       │   └── design.md
│       └── utils/
│           ├── __init__.py
│           └── stream_llm.py     # OpenAI streaming utility
│
└── voice/                        # Voice interaction interface
    └── pocketflow_voice/
        ├── main.py               # Voice entry point
        ├── flow.py               # Voice flow definition
        ├── nodes.py              # Audio processing nodes
        ├── requirements.txt      # Voice UI dependencies
        ├── README.md
        ├── docs/
        │   └── design.md
        └── utils/
            ├── __init__.py
            ├── audio_utils.py    # Audio recording/playback
            ├── call_llm.py       # Direct LLM API calls
            ├── speech_to_text.py # STT processing
            └── text_to_speech.py # TTS processing
```

---

## Web UI (`web/websocket_server/`)

### Purpose
Browser-based chat interface with real-time streaming responses.

### Technology Stack
- **FastAPI** - Web framework
- **WebSocket** - Real-time bidirectional communication
- **PocketFlow** - Async flow orchestration
- **OpenAI API** - Direct LLM calls (**bypasses core agent**)

### Components

#### `main.py` - FastAPI Server
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    - Accepts WebSocket connections
    - Manages conversation history
    - Creates and runs streaming flow
```

**Entry Point:**
```bash
cd ui/web/websocket_server
python main.py
# Access: http://localhost:8000
```

#### `flow.py` - Flow Definition
Creates PocketFlow for streaming chat:
```python
def create_streaming_chat_flow():
    - Defines chat processing pipeline
    - Connects nodes
    - Returns executable flow
```

#### `nodes.py` - StreamingChatNode
```python
class StreamingChatNode(AsyncNode):
    async def prep_async(self, shared):
        - Prepares conversation history
        - Gets user message and websocket

    async def exec_async(self, prep_res):
        - Calls stream_llm() for streaming response
        - Sends chunks to websocket
        - Returns full response

    async def post_async(self, shared, prep_res, exec_res):
        - Updates conversation history
```

**Streaming Format:**
```json
{"type": "start", "content": ""}
{"type": "chunk", "content": "token"}
{"type": "end", "content": ""}
```

#### `utils/stream_llm.py` - Streaming Utility
```python
async def stream_llm(messages):
    - Creates AsyncOpenAI client
    - Calls chat completion with stream=True
    - Yields content chunks
```

**Issue:** Makes direct OpenAI calls, doesn't use:
- ToolRegistry
- LLMOrchestrator
- ExecutionEngine
- MemorySystem

#### `static/index.html` - Chat Interface
Modern chat UI with:
- Message display
- User input
- Streaming visualization
- WebSocket connection management

### Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai==1.3.8
pocketflow
```

### Features
- ✅ Real-time streaming responses
- ✅ Conversation history
- ✅ Clean, modern UI
- ❌ No tool access
- ❌ No agent integration
- ❌ No memory persistence

### Limitations
1. **Standalone** - Doesn't use core agent
2. **No tools** - Can't execute filesystem, shell, web search, etc.
3. **Direct API** - Bypasses LLMOrchestrator
4. **No memory** - Session-only, not persistent
5. **OpenAI only** - Can't use Ollama or Anthropic

---

## Voice UI (`voice/pocketflow_voice/`)

### Purpose
Voice-based interaction using speech-to-text and text-to-speech.

### Technology Stack
- **PocketFlow** - Node-based flow orchestration
- **OpenAI Whisper** - Speech-to-text
- **OpenAI TTS** - Text-to-speech
- **sounddevice** - Audio capture
- **scipy** - Audio processing

### Architecture
```
Audio Input
    ↓
RecordAudioNode → audio_utils.record_audio()
    ↓
SpeechToTextNode → STT API
    ↓
QueryLLMNode → call_llm()
    ↓
TextToSpeechNode → TTS API
    ↓
PlayAudioNode → audio_utils.play_audio()
```

### Components

#### `main.py` - Entry Point
```python
def main():
    - Creates voice interaction flow
    - Runs async event loop
    - Processes voice input/output
```

**Run:**
```bash
cd ui/voice/pocketflow_voice
python main.py
```

#### `flow.py` - Voice Flow
```python
def create_voice_flow():
    - Connects audio nodes in sequence
    - Defines voice processing pipeline
```

#### `nodes.py` - Processing Nodes

**RecordAudioNode** - Captures audio from microphone
**SpeechToTextNode** - Converts speech to text
**QueryLLMNode** - Sends text to LLM (**direct API call**)
**TextToSpeechNode** - Converts response to speech
**PlayAudioNode** - Plays audio response

#### `utils/` - Utility Modules

**`audio_utils.py`** - Audio I/O
- `record_audio()` - Capture from microphone
- `play_audio()` - Playback audio
- `save_audio()` - Write audio files

**`speech_to_text.py`** - STT
```python
async def speech_to_text(audio_data):
    - Uses OpenAI Whisper API
    - Converts audio to text
```

**`text_to_speech.py`** - TTS
```python
async def text_to_speech(text):
    - Uses OpenAI TTS API
    - Returns audio data
```

**`call_llm.py`** - LLM Interaction
```python
async def call_llm(message):
    - Direct OpenAI API call
    - Returns text response
```

**Issue:** Bypasses all core agent functionality.

### Dependencies
```
openai
pocketflow
numpy
sounddevice
scipy
soundfile
```

### Features
- ✅ Voice input (STT)
- ✅ Voice output (TTS)
- ✅ End-to-end voice interaction
- ❌ No tool access
- ❌ No agent integration
- ❌ No streaming (waits for full response)
- ❌ Linear flow only

### Limitations
1. **Standalone** - Doesn't use core agent
2. **No tools** - Can't access tools
3. **Direct API** - Bypasses LLMOrchestrator
4. **No streaming** - Waits for complete response
5. **OpenAI only** - Can't use Ollama or Anthropic
6. **No conversation history** - Each interaction is isolated

---

## Integration Issues

### Current Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   CLI Agent     │     │    Web UI        │     │    Voice UI      │
│  (vibe1337.py)  │     │  (FastAPI)       │     │  (PocketFlow)    │
├─────────────────┤     ├──────────────────┤     ├──────────────────┤
│ LLMOrchestrator │     │ OpenAI Direct    │     │ OpenAI Direct    │
│ ToolRegistry    │     │ No Tools         │     │ No Tools         │
│ MemorySystem    │     │ Session Memory   │     │ No Memory        │
│ 4 Tools ✅       │     │ Streaming ✅      │     │ Voice I/O ✅      │
│ No Streaming ❌  │     │ No Tools ❌       │     │ No Tools ❌       │
└─────────────────┘     └──────────────────┘     └──────────────────┘
     Separate              Separate               Separate
```

### Problems
1. **Code Duplication** - 3 separate LLM query implementations
2. **Feature Fragmentation** - Each UI has different capabilities
3. **No Consistency** - Different behavior across UIs
4. **Wasted Potential** - UIs can't access 28 available tools

---

## Recommended Integration

### Unified Architecture
```
┌────────────────────────────────────────────────────────┐
│                   VIBE1337Agent (Core)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │            LLMOrchestrator (Brain)                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │  │
│  │  │ Ollama   │  │ OpenAI   │  │  Anthropic   │   │  │
│  │  └──────────┘  └──────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │     ToolRegistry (28 Tools)                       │  │
│  │  [filesystem, shell, web, python, browser, ...]  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │     MemorySystem (Persistent)                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
             │              │              │
             ↓              ↓              ↓
    ┌───────────────┐ ┌─────────┐ ┌────────────┐
    │  CLI Interface│ │ Web UI  │ │ Voice UI   │
    │   (stdio)     │ │ (WS)    │ │ (audio)    │
    │  Streaming ✅  │ │Stream ✅ │ │ Stream ✅   │
    │  Tools ✅      │ │Tools ✅  │ │ Tools ✅    │
    └───────────────┘ └─────────┘ └────────────┘
```

### Implementation Strategy

#### 1. Create Shared Agent Service

```python
# core/agent_service.py
class AgentService:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.memory = MemorySystem()
        self.execution_engine = ExecutionEngine(self.tool_registry)
        self.orchestrator = LLMOrchestrator({})
        # Wire dependencies

    async def process_streaming(self, user_input):
        """Process with streaming responses"""
        async for chunk in self._process_with_stream(user_input):
            yield chunk

    async def process(self, user_input):
        """Process with full response"""
        return await self.orchestrator.process(user_input)
```

#### 2. Update Web UI

```python
# ui/web/websocket_server/nodes.py
from core.agent_service import AgentService

class StreamingChatNode(AsyncNode):
    def __init__(self):
        self.agent = AgentService()  # Use shared agent

    async def exec_async(self, prep_res):
        messages, websocket = prep_res

        # Use agent's streaming method
        async for chunk in self.agent.process_streaming(messages[-1]):
            await websocket.send_text(json.dumps({
                "type": "chunk",
                "content": chunk
            }))
```

#### 3. Update Voice UI

```python
# ui/voice/pocketflow_voice/nodes.py
from core.agent_service import AgentService

class QueryLLMNode(AsyncNode):
    def __init__(self):
        self.agent = AgentService()

    async def exec_async(self, prep_res):
        text = prep_res
        # Use agent instead of direct API
        result = await self.agent.process(text)
        return result["response"]
```

---

## Migration Path

### Phase 1: Add Streaming to Core
1. Implement `LLMOrchestrator.process_streaming()`
2. Add streaming to all LLM query methods
3. Test with CLI

### Phase 2: Create Shared Service
1. Create `core/agent_service.py`
2. Export unified interface
3. Add streaming support

### Phase 3: Migrate Web UI
1. Import AgentService
2. Replace direct OpenAI calls
3. Test streaming
4. Test tool access

### Phase 4: Migrate Voice UI
1. Import AgentService
2. Replace call_llm()
3. Test voice flow
4. Test tool access

### Phase 5: Cleanup
1. Remove duplicate code
2. Update documentation
3. Add tests
4. Verify all UIs work consistently

---

## Testing

### Web UI
```bash
cd ui/web/websocket_server
python main.py
# Open http://localhost:8000
# Test: "list files in current directory" (should use tools after integration)
```

### Voice UI
```bash
cd ui/voice/pocketflow_voice
python main.py
# Speak: "What files are in the current directory?"
# Should use tools after integration
```

---

## Future Enhancements

### Web UI
1. **Rich output formatting** - Code blocks, tables, images
2. **File upload** - Analyze documents
3. **Tool visualization** - Show which tools were used
4. **Multi-session** - Multiple concurrent conversations
5. **Authentication** - User accounts

### Voice UI
1. **Wake word** - Hands-free activation
2. **Interrupt handling** - Stop mid-response
3. **Multi-language** - Support more languages
4. **Emotion detection** - Sentiment analysis
5. **Voice profiles** - User recognition

### Both
1. **Mobile apps** - iOS/Android clients
2. **Desktop apps** - Electron wrappers
3. **API mode** - REST API for integrations
4. **Plugins** - Custom UI extensions

---

## Dependencies

### Web UI
- fastapi - Web framework
- uvicorn - ASGI server
- openai - API client (will be optional after integration)
- pocketflow - Flow orchestration

### Voice UI
- openai - API client (will be optional after integration)
- pocketflow - Flow orchestration
- numpy - Audio processing
- sounddevice - Audio I/O
- scipy - Audio utilities
- soundfile - Audio formats

---

## Performance

### Web UI
- **WebSocket** - Low latency (~50ms)
- **Streaming** - Immediate token delivery
- **Concurrent** - Multiple clients supported

### Voice UI
- **STT Latency** - ~1-2s
- **LLM Latency** - Variable (depends on response length)
- **TTS Latency** - ~1-2s
- **Total** - 2-4s + LLM time

### Optimization Opportunities
1. **Local STT/TTS** - Reduce API calls
2. **Response caching** - Cache common queries
3. **Connection pooling** - Reuse HTTP connections
4. **Parallel processing** - STT while recording continues

---

## Security

### Web UI
1. **WebSocket authentication** - Add token-based auth
2. **Rate limiting** - Prevent abuse
3. **Input validation** - Sanitize user input
4. **CORS** - Restrict origins

### Voice UI
1. **Audio validation** - Check file formats
2. **Content filtering** - Block harmful requests
3. **Session management** - Timeout inactive sessions

---

## Version History

- v1.0 - Initial standalone implementations
- v1.1 - Added streaming to web UI
- v1.2 - Added voice UI
- v2.0 (target) - Integrated with core agent
