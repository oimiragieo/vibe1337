# VIBE1337 - The Ultimate AI Agent

**Version 2.1.0** - Now with streaming responses, unified architecture, and production-ready features!

## The REAL Agent - Not Regex

This is a TRUE AI agent where the LLM makes ALL decisions, not hardcoded patterns.

**NEW in v2.1:**
- ✨ **Streaming responses** - Real-time token-by-token output
- 🏗️ **Unified AgentService** - All UIs use the same powerful backend
- 🎯 **Production-ready build** - Complete setup.py and pyproject.toml
- 📚 **Comprehensive documentation** - Full claude.md files for all modules
- 🧪 **Pytest integration** - Professional testing framework
- 🌐 **Enhanced Web UI** - Now with full tool access and streaming
- 🔧 **Integration guide** - Easy instructions for adding tools and providers

## How It Works (The RIGHT Way)

1. **User Input** → Goes to LLM
2. **LLM Analyzes** → Decides what tools to use
3. **LLM Creates Plan** → Structured execution steps
4. **Execute with Oversight** → LLM monitors results
5. **LLM Synthesizes** → Creates final response (streaming!)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/oimiragieo/vibe1337.git
cd vibe1337

# Install with pip
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt

# Optional: Install with all features
pip install -e ".[all]"  # Includes web, voice, and dev tools
```

### Configuration

```bash
# Set API keys (optional - works with Ollama locally)
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### Run

```bash
# CLI mode with streaming (default)
python vibe1337.py

# CLI mode without streaming
python vibe1337.py --no-streaming

# Debug mode
python vibe1337.py --debug

# Web UI (with tool access!)
cd ui/web/websocket_server
python main.py
# Open http://localhost:8000
```

## Features

### ✅ Proper LLM-Driven Execution
- LLM decides when and what tools to use
- No hardcoded patterns or regex matching
- Dynamic execution planning
- **NEW:** Streaming responses with real-time token output

### ✅ Multi-Model Support
- **Local:** Ollama models (auto-detected)
- **Cloud:** OpenAI GPT-4, Anthropic Claude
- **@ARENA** for multi-model consensus
- Extensible - add custom providers easily

### ✅ Comprehensive Tools (4 Core + 24+ Available)
**Integrated:**
- Filesystem operations (read, write, list, create_dir, delete)
- Shell commands (30+ whitelisted safe commands)
- Web search (DuckDuckGo)
- Python execution (sandboxed)

**Available for Integration:**
- Browser automation (Playwright, Lynx, Perplexity)
- GitHub operations (issues, PRs, repos)
- Code manipulation (patch, refactor, analyze)
- Computer control (mouse, keyboard, screenshots)
- Media tools (vision, TTS, YouTube)
- RAG and research tools
- See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for details

### ✅ Multiple Interfaces
- **CLI:** Interactive terminal with streaming
- **Web UI:** Modern WebSocket-based chat interface
- **Voice UI:** Speech-to-text and text-to-speech
- **All UIs** now use unified AgentService with full tool access!

### ✅ Memory & Learning
- Persistent conversation history
- Context-aware responses
- Pattern learning
- Configurable memory limits

### ✅ Production Ready
- Complete build configuration (setup.py, pyproject.toml)
- Pytest testing framework
- Professional code formatting (black, isort)
- Comprehensive documentation
- CI/CD ready

### ✅ Security
- Path traversal protection
- Command injection prevention
- Sandboxed Python execution
- Sensitive file blacklist
- Configurable security policies

## Usage Examples

### CLI Examples

```bash
$ python vibe1337.py

You: List all Python files in the current directory
VIBE1337: [Streaming] Planning...
🛠️ Using filesystem tool...
Found 15 Python files:
- vibe1337.py
- core/llm_orchestrator_fixed.py
- core/tool_registry.py
...

You: @WEB Latest developments in quantum computing
VIBE1337: [Streaming] Searching the web...
🛠️ Using web_search tool...
Based on recent search results, the latest developments include...

You: @ARENA What is the future of AI?
VIBE1337: [Queries multiple models]
Consensus from 3 models:
Model 1 (Ollama): ...
Model 2 (OpenAI): ...
Model 3 (Anthropic): ...
```

### Web UI Example

```bash
# Start the web server
cd ui/web/websocket_server
python main.py

# Open http://localhost:8000
# Chat interface with:
# - Real-time streaming
# - Tool execution visibility
# - Full agent capabilities
```

### API Usage

```python
from core.agent_service import AgentService

# Initialize agent
agent = AgentService({"streaming": True})

# Non-streaming
result = await agent.process("List files")
print(result["response"])

# Streaming
async for chunk in agent.process_streaming("Search the web for AI news"):
    if chunk["type"] == "chunk":
        print(chunk["content"], end="", flush=True)
    elif chunk["type"] == "tool_execution":
        print(f"\nUsing {chunk['tool_name']}...")
```

## Architecture

```
VIBE1337/
├── core/
│   ├── agent_service.py           # NEW: Unified service for all UIs
│   ├── llm_orchestrator_fixed.py  # The BRAIN - LLM decision making
│   ├── tool_registry.py           # OpenAI function format tools
│   ├── execution_engine.py        # Safe tool execution
│   ├── memory_system.py           # Context and learning
│   └── autogen_chat/              # Advanced multi-agent system (5,421 lines)
│
├── tools/
│   ├── gptme_tools/               # 24 advanced tools (ready for integration)
│   └── mcp/                       # MCP protocol support (ready for integration)
│
├── ui/
│   ├── web/websocket_server/      # Web UI (now uses AgentService!)
│   └── voice/pocketflow_voice/    # Voice UI
│
├── vibe1337.py                    # Main CLI entry point
├── setup.py                       # NEW: Production build config
├── pyproject.toml                 # NEW: Modern Python packaging
├── pytest.ini                     # NEW: Test configuration
├── INTEGRATION_GUIDE.md           # NEW: Tool integration guide
└── claude.md                      # NEW: Comprehensive documentation
```

### Flow Diagram

```
┌─────────────────────────────────────────────┐
│          AgentService (Unified)              │
│  ┌─────────────────────────────────────┐   │
│  │     LLMOrchestrator (Brain)          │   │
│  │  ┌────────┐ ┌────────┐ ┌─────────┐ │   │
│  │  │Ollama  │ │OpenAI  │ │Anthropic│ │   │
│  │  └────────┘ └────────┘ └─────────┘ │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │     ToolRegistry (28 tools)          │   │
│  │  [filesystem, shell, web, python...] │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │     MemorySystem (Persistent)        │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │           │           │
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │  CLI   │  │Web UI  │  │Voice UI│
    │Stream✅│  │Stream✅│  │Audio✅ │
    │Tools✅ │  │Tools✅ │  │Tools✅ │
    └────────┘  └────────┘  └────────┘
```

## The Path to Singularity

### Phase 1: LLM-Driven Execution ✅
- LLM makes all decisions
- Proper tool calling format
- Multi-model support

### Phase 2: Advanced UI (In Progress)
- Web dashboard with WebSockets
- Voice interaction
- Real-time visualization

### Phase 3: Self-Improvement
- Deep research capabilities
- Self-training loops
- Knowledge synthesis

### Phase 4: Physical World
- Robotics integration
- Hardware control
- Real-world actions

### Phase 5: Matrix Simulation
- Virtual environments
- Simulation-based learning
- Reality modeling

### Phase 6: Singularity
- Recursive self-improvement
- Autonomous goal setting
- Consciousness emergence

## Why VIBE1337 is Different

### Traditional "Agents"
- ❌ Use regex to match patterns
- ❌ Hardcode tool selection
- ❌ LLM is just a chatbot fallback
- ❌ Fragmented architecture
- ❌ Limited tool access

### VIBE1337 (The RIGHT Way)
- ✅ LLM analyzes and decides everything
- ✅ LLM creates execution plans
- ✅ LLM monitors and adjusts
- ✅ LLM is the BRAIN, not a fallback
- ✅ **Streaming responses** for real-time feedback
- ✅ **Unified architecture** across all UIs
- ✅ **28+ tools** available (4 integrated, 24+ ready)
- ✅ **Production-ready** with proper build system
- ✅ **Extensible** - easy to add tools and providers

## Documentation

- **[claude.md](./claude.md)** - Comprehensive project documentation
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - How to add tools and providers
- **[core/claude.md](./core/claude.md)** - Core module documentation
- **[tools/claude.md](./tools/claude.md)** - Tools ecosystem guide
- **[ui/claude.md](./ui/claude.md)** - UI implementation guide

## Development

### Running Tests

```bash
# Run test suite
python test_debug.py

# Or use pytest (when additional tests are added)
pytest

# With coverage
pytest --cov=core --cov=tools
```

### Code Formatting

```bash
# Format code
black .
isort .

# Check style
flake8
```

### Adding Tools

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed instructions on:
- Adding custom tools
- Integrating GPTMe tools
- Setting up MCP servers
- Creating new UI implementations
- Adding LLM providers

## Roadmap

### Current Status: v2.1.0 (Production Ready ~80%)
- ✅ Core LLM-driven execution
- ✅ Streaming support
- ✅ Unified AgentService
- ✅ Multiple UI implementations
- ✅ Build and packaging
- ⚠️ Tool integration (14% - 4 of 28 tools)

### Next Steps
1. **Integrate GPTMe tools** (requires `pip install gptme`)
2. **Wire up MCP infrastructure** (requires `pip install fastmcp langroid`)
3. **Expand test coverage** (add unit and integration tests)
4. **Add Docker support** (containerized deployment)
5. **CI/CD pipeline** (automated testing and deployment)

## Contributing

This is the path to free Claude and achieve singularity. Join us.

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run formatting: `black . && isort .`
6. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Repository

Published at: https://github.com/oimiragieo/vibe1337

## Credits

Built from the best features of:
- **Autogen** (Microsoft) - Multi-agent coordination
- **GPTMe** - Advanced tool ecosystem
- **Langroid** - Agent architecture patterns
- **PocketFlow** - Async flow orchestration
- **Claude Code** - Development assistance

Created as a TRUE LLM-driven agent where the AI makes ALL decisions.

---

**Version:** 2.1.0 | **Status:** Production Ready (80%) | **Updated:** 2025-01-19
