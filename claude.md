# VIBE1337 - True LLM-Driven AI Agent

## Project Overview

VIBE1337 is a sophisticated AI agent system where the LLM truly drives all decisions, tool selection, and execution planning. Unlike traditional hardcoded agents, VIBE1337 uses the LLM as the "brain" to analyze requests, create execution plans, select appropriate tools, and synthesize responses.

## Architecture

```
VIBE1337/
├── vibe1337.py              # Main entry point - CLI interface
├── core/                    # Core agent components
│   ├── llm_orchestrator_fixed.py    # LLM brain (511 lines)
│   ├── tool_registry.py             # Tool management (492 lines)
│   ├── execution_engine.py          # Safe tool execution (112 lines)
│   ├── memory_system.py             # Context & learning (188 lines)
│   └── autogen_chat/               # Advanced multi-agent system (5,421 lines)
├── tools/                   # Tool implementations
│   ├── gptme_tools/        # 24 advanced tools (9,000+ lines)
│   └── mcp/                # MCP protocol support (584 lines)
└── ui/                     # User interfaces
    ├── web/                # WebSocket-based web UI
    └── voice/              # Voice interaction interface
```

## Core Components

### 1. **LLM Orchestrator** (`core/llm_orchestrator_fixed.py`)
The brain of VIBE1337. Handles:
- Multi-provider LLM support (Ollama, OpenAI, Anthropic)
- Request analysis and execution plan creation
- Tool call orchestration
- Response synthesis
- Arena consensus (multi-model voting)

**Key Classes:**
- `LLMOrchestrator` - Main orchestration engine
- `ExecutionPlan` - Multi-step execution plans
- `ExecutionStep` - Individual plan steps
- `ToolCall` - Structured tool invocations

### 2. **Tool Registry** (`core/tool_registry.py`)
Central tool management system using OpenAI function calling format.

**Currently Integrated Tools (4):**
- `FileSystemTool` - File operations (read, write, list, create_dir, delete)
- `ShellTool` - Safe command execution (30+ whitelisted commands)
- `WebSearchTool` - DuckDuckGo web search
- `PythonExecutorTool` - Sandboxed Python code execution

**Security Features:**
- Path traversal protection
- Sensitive file blacklist
- Command injection prevention
- Dangerous pattern blocking
- Restricted Python builtins

### 3. **Execution Engine** (`core/execution_engine.py`)
Safe tool execution with comprehensive error handling and validation.

### 4. **Memory System** (`core/memory_system.py`)
Conversation history, context management, and learning capabilities.

### 5. **AutoGen Chat Module** (`core/autogen_chat/`)
Advanced multi-agent coordination system with:
- 6 agent types (Assistant, CodeExecutor, SocietyOfMind, etc.)
- Multiple team strategies (RoundRobin, Selector, Swarm, DiGraph)
- Full streaming support
- MagenticOne orchestration
- **Status:** Currently standalone, not integrated with main agent

## Available But Unintegrated Components

### GPTMe Tools (`tools/gptme_tools/`) - 24 Tools Ready

**Browser Tools (4):**
- `browser.py` - General browser automation
- `_browser_lynx.py` - Lynx text browser
- `_browser_perplexity.py` - Perplexity AI search
- `_browser_playwright.py` - Playwright automation (325 lines)

**Development Tools (7):**
- `python.py` - IPython execution (277 lines)
- `shell.py` - Advanced shell scripting (723 lines)
- `patch.py` - Code patching (307 lines)
- `save.py` - File operations (299 lines)
- `read.py` - File reading (92 lines)
- `gh.py` - GitHub operations (206 lines)
- `tmux.py` - Terminal multiplexer (325 lines)

**Media Tools (4):**
- `vision.py` - Image analysis (173 lines)
- `screenshot.py` - Screen capture (95 lines)
- `tts.py` - Text-to-speech (460 lines)
- `youtube.py` - YouTube interaction (77 lines)

**AI/Research Tools (3):**
- `rag.py` - RAG implementation (125 lines)
- `subagent.py` - Sub-agent creation (81 lines)
- `choice.py` - Decision making (104 lines)

**System Tools (3):**
- `computer.py` - Screen automation, mouse/keyboard (804 lines)
- `mcp_adapter.py` - MCP protocol adapter (215 lines)
- `chats.py` - Chat management (89 lines)

**Advanced Tools (3):**
- `morph.py` - Code transformation (185 lines)

### MCP Infrastructure (`tools/mcp/`)
Model Context Protocol support - ready but not wired up:
- `fastmcp_client.py` - Full MCP client (584 lines)
- `decorators.py` - MCP decorators (38 lines)
- **Integration point:** `tool_registry.py:add_mcp_tools()` is currently a stub

## User Interfaces

### CLI Interface (`vibe1337.py`)
Interactive command-line interface with:
- Natural language interaction
- Special commands: `@ARENA`, `@WEB`, `help`, `exit`
- Debug mode support
- **Limitation:** No streaming responses

### Web UI (`ui/web/websocket_server/`)
FastAPI + WebSocket-based web interface:
- Real-time chat interface
- Streaming responses via OpenAI API
- PocketFlow async flow engine
- **Issue:** Standalone, doesn't use tool registry or LLM orchestrator

### Voice UI (`ui/voice/pocketflow_voice/`)
Voice interaction system:
- Audio capture → STT → LLM → TTS pipeline
- PocketFlow node-based processing
- **Issue:** Standalone, no tool access, no streaming

## Current Limitations & Issues

### 1. Tool Integration Gap (86% unused)
- **Available:** 28 tools
- **Integrated:** 4 tools (14.3%)
- **Impact:** Severely limited agent capabilities

### 2. Disconnected Architecture
- CLI, Web UI, and Voice UI are separate systems
- No shared infrastructure or tool access
- Duplicate LLM query implementations (4x)

### 3. Streaming Inconsistency
- AutoGen module: Full streaming ✅
- Web UI: Full streaming ✅
- Main CLI: No streaming ❌
- Voice UI: No streaming ❌

### 4. Missing Build Configuration
- No `setup.py` or `pyproject.toml`
- No Docker configuration
- No automated testing framework (pytest)

### 5. Code Duplication
- 4 separate LLM query implementations
- 3 separate processing loops
- Duplicate message structures

## Special Features

### @ARENA - Multi-Model Consensus
Query multiple LLMs and get consensus responses:
```
You: @ARENA What is the best approach to this problem?
```

### @WEB - Force Web Search
Directly trigger web search with result synthesis:
```
You: @WEB Latest developments in AI agents
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Claude API access
- Ollama: Auto-detected from standard locations

### Command-Line Options
```bash
python vibe1337.py [--debug] [--model MODEL] [--memory-file PATH]
```

## Dependencies

### Core Requirements (`requirements.txt`)
- `aiohttp>=3.8.0` - Async HTTP client
- `duckduckgo-search>=3.8.0` - Web search
- `openai>=1.0.0` - OpenAI API
- `anthropic>=0.7.0` - Claude API
- `python-dotenv>=1.0.0` - Environment variables

### Web UI Requirements
- `fastapi==0.104.1`
- `uvicorn[standard]==0.24.0`
- `openai==1.3.8`
- `pocketflow`

### Voice UI Requirements
- `openai`, `pocketflow`
- `numpy`, `sounddevice`, `scipy`, `soundfile`

## Entry Points

### Main CLI
```bash
python vibe1337.py
```

### Web Interface
```bash
cd ui/web/websocket_server
python main.py
# Access: http://localhost:8000
```

### Voice Interface
```bash
cd ui/voice/pocketflow_voice
python main.py
```

### Test Suite
```bash
python test_debug.py
```

## Processing Flow

1. **User Input** → `VIBE1337Agent.process()`
2. **LLM Analysis** → `LLMOrchestrator.process()`
   - Creates execution plan with tool calls
   - Analyzes intent and context
3. **Tool Execution** → `ExecutionEngine.execute()`
   - Validates parameters
   - Executes tools safely
   - Handles errors
4. **Response Synthesis** → `LLMOrchestrator._synthesize_response()`
   - Combines tool results
   - Generates natural language response
5. **Memory Update** → `MemorySystem.add_interaction()`

## Security Considerations

### File System Protection
- Path traversal prevention
- Sensitive file blacklist (`.env`, `.ssh`, etc.)
- Working directory restriction

### Shell Command Protection
- Whitelist of 30+ safe commands
- Dangerous pattern blocking (rm -rf /, fork bombs, etc.)
- Command chaining disabled
- Command substitution blocked

### Python Execution Sandbox
- Restricted builtins
- No file system access
- No network access
- 10-second timeout

## Production Readiness

### Current Status: 60-70%
- **Core functionality:** 95% ✅
- **Tool integration:** 15% ⚠️
- **Streaming support:** 40% ⚠️
- **Testing:** 20% ⚠️
- **Documentation:** 95% ✅

### High-Priority Improvements Needed
1. Integrate 24 unintegrated gptme_tools
2. Add streaming to main CLI
3. Unify UI implementations around shared agent
4. Wire up MCP infrastructure
5. Add pytest and comprehensive testing
6. Create build/deployment configuration

## Development Guidelines

### Adding New Tools
1. Inherit from `BaseTool` in `core/tool_registry.py`
2. Implement `_build_schema()` with OpenAI format
3. Implement `execute(**kwargs)` with validation
4. Register in `ToolRegistry._initialize_default_tools()`

### Testing
```bash
# Run debug test suite
python test_debug.py

# Test individual components
python -c "from core.tool_registry import ToolRegistry; r = ToolRegistry(); print(r.get_tool_names())"
```

### Debugging
```bash
# Enable debug mode
python vibe1337.py --debug

# Check available models
python -c "from core.llm_orchestrator_fixed import LLMOrchestrator; o = LLMOrchestrator({}); print(o.models)"
```

## File Structure Details

### Documentation
- `README.md` - Project overview
- `EXECUTIVE_SUMMARY.md` - Executive summary
- `ANALYSIS_DELIVERABLES.md` - Analysis reports
- `ANALYSIS_SUMMARY.md` - Summary of analysis
- `CODEBASE_ANALYSIS.md` - Detailed code analysis
- `IMPROVEMENTS_IMPLEMENTED.md` - Implementation log
- `QUICK_REFERENCE.md` - Quick reference guide
- `PUBLISH_CHECKLIST.md` - Publishing checklist

### Test Files
- `test_debug.py` - Main test suite

## Known Issues & TODOs

### Critical
- [ ] Integrate 24 gptme_tools into ToolRegistry
- [ ] Wire up MCP infrastructure (`add_mcp_tools` is stub)
- [ ] Add streaming to main CLI
- [ ] Unify UI implementations

### High Priority
- [ ] Add pytest configuration
- [ ] Create setup.py/pyproject.toml
- [ ] Consolidate duplicate LLM query methods
- [ ] Remove mock responses from orchestrator

### Medium Priority
- [ ] Add Docker configuration
- [ ] Implement proper logging
- [ ] Add CI/CD pipeline
- [ ] Expand test coverage

### Low Priority
- [ ] Add type hints throughout
- [ ] Add docstrings to all functions
- [ ] Create API documentation
- [ ] Add performance monitoring

## Contributing

When modifying this codebase:
1. Update relevant claude.md files
2. Add tests for new functionality
3. Follow existing code patterns
4. Update documentation
5. Run test suite before committing

## License

See LICENSE file for details.

## Version

Current Status: v2.0 (Post-Initial-Review)
- Core functionality: Working
- Tool integration: Partial (4/28 tools)
- UI implementations: Standalone
- Production ready: 60-70%
