# VIBE1337 - True LLM-Driven AI Agent

**Version 2.1.0** - Production-ready agent with streaming, unified architecture, and intelligent tool execution

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/status-production--ready-green.svg)]()

## What Makes VIBE1337 Different

This is a **TRUE AI agent** where the LLM makes ALL decisions - not hardcoded patterns or regex matching.

### Traditional "Agents" ❌
- Use regex to match patterns
- Hardcode tool selection logic
- LLM is just a chatbot fallback
- Fragmented architecture across UIs

### VIBE1337 ✅
- **LLM analyzes** every request and decides what tools to use
- **LLM creates** structured execution plans
- **LLM monitors** results and adjusts strategy
- **LLM is the brain**, not a fallback
- **Unified architecture** - all UIs use the same powerful backend
- **Real-time streaming** - see responses as they're generated

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/oimiragieo/vibe1337.git
cd vibe1337

# Install with pip (recommended)
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt

# Optional: Install with specific features
pip install -e ".[web]"    # Web UI support
pip install -e ".[voice]"  # Voice UI support (experimental)
pip install -e ".[dev]"    # Development tools
pip install -e ".[all]"    # Everything
```

### Configuration

```bash
# Optional - works locally with Ollama without API keys
export OPENAI_API_KEY=your_key      # For OpenAI GPT-4
export ANTHROPIC_API_KEY=your_key   # For Anthropic Claude

# Ollama users: just install Ollama and models will be auto-detected
# Download from: https://ollama.ai
```

### Run

```bash
# CLI mode with streaming (default)
python vibe1337.py

# CLI mode without streaming
python vibe1337.py --no-streaming

# Debug mode for development
python vibe1337.py --debug

# Web UI (requires [web] extras)
cd ui/web/websocket_server
python main.py
# Open http://localhost:8000 in your browser
```

## Core Features

### ✅ LLM-Driven Intelligence
- **Adaptive Decision Making**: LLM analyzes each request and chooses appropriate tools
- **Dynamic Planning**: Creates multi-step execution plans on the fly
- **Self-Monitoring**: Evaluates results and adjusts strategy
- **Streaming Responses**: Real-time token-by-token output (OpenAI, Anthropic)

### ✅ Multi-Model Support
| Provider | Models | Status | Notes |
|----------|--------|--------|-------|
| **Ollama** | Any installed model | ✅ Auto-detected | Local, free, private |
| **OpenAI** | GPT-4, GPT-3.5 | ✅ API key required | Cloud-based |
| **Anthropic** | Claude 3 Opus/Sonnet | ✅ API key required | Cloud-based |
| **Arena Mode** | Multi-model consensus | ✅ Use `@ARENA` | Queries all available models |

### ✅ Integrated Tools (4 Core)

All tools use OpenAI function calling format with proper parameter validation and security checks.

| Tool | Capabilities | Security |
|------|-------------|----------|
| **filesystem** | read, write, list, create_dir, delete | Path traversal protection, sensitive file blacklist |
| **shell** | Execute commands | 30+ whitelisted safe commands (ls, git, python, curl, etc.) |
| **web_search** | DuckDuckGo search | Configurable result limits |
| **python_executor** | Run Python code | Sandboxed execution, restricted builtins |

### ✅ Multiple User Interfaces

| Interface | Status | Features |
|-----------|--------|----------|
| **CLI** | ✅ Fully Integrated | Streaming, tool access, memory, special commands |
| **Web UI** | ✅ Fully Integrated | WebSocket-based, streaming, tool visualization |
| **Voice UI** | ⚠️ Experimental | Audio capture/playback (partial agent integration) |

**CLI Special Commands:**
- `@ARENA <query>` - Query all available models and show consensus
- `@WEB <query>` - Force web search for the query
- `help` - Show available commands
- `exit` - Save memory and quit

### ✅ Persistent Memory
- **Short-term memory**: Recent interactions (max 100)
- **Long-term memory**: Important patterns and learnings
- **Conversation history**: Full context with timestamps
- **JSON storage**: Human-readable, version-controllable
- **Auto-save**: Every 10 interactions

### ✅ Production-Ready Infrastructure
- **Modern packaging**: `setup.py` + `pyproject.toml`
- **Testing framework**: pytest with async support
- **Code quality**: black, isort, flake8, mypy configured
- **Security**: Input validation, sandboxing, whitelists
- **Documentation**: Comprehensive claude.md files for all modules
- **CI/CD ready**: Structured for automated deployment

## Usage Examples

### CLI Interactive Session

```bash
$ python vibe1337.py

You: List all Python files in the current directory
VIBE1337: [Planning...]
🛠️ Using filesystem tool with action: list
Found 8 Python files:
  - vibe1337.py
  - test_debug.py
  - core/agent_service.py
  - core/llm_orchestrator_fixed.py
  - core/tool_registry.py
  - core/execution_engine.py
  - core/memory_system.py
  - core/tool_message.py

You: @WEB Latest developments in quantum computing 2024
VIBE1337: [Searching web...]
🔍 Using web_search tool...
Based on recent results, key developments include:
1. Google's Willow quantum chip achieving...
2. IBM's advances in quantum error correction...
3. New quantum algorithms for...

You: @ARENA What is consciousness?
VIBE1337: [Querying 3 models...]
📊 Model 1 (ollama:llama2): Consciousness is...
📊 Model 2 (openai:gpt-4): Consciousness can be understood as...
📊 Model 3 (anthropic:claude-3): From a philosophical perspective...

Consensus: All models agree that consciousness involves...
```

### Programmatic API Usage

```python
from core.agent_service import AgentService
import asyncio

async def main():
    # Initialize agent
    agent = AgentService({"streaming": True})

    # Non-streaming request
    result = await agent.process("List files in the current directory")
    print(result["response"])

    # Streaming request
    async for chunk in agent.process_streaming("Search for AI news"):
        if chunk["type"] == "chunk":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "tool_execution":
            print(f"\n🛠️ Using {chunk['tool_name']}...")
        elif chunk["type"] == "complete":
            print("\n✅ Done!")

asyncio.run(main())
```

### Web UI

```bash
# Start the web server
cd ui/web/websocket_server
python main.py

# Open http://localhost:8000
# Features:
# - Real-time streaming chat interface
# - Tool execution visualization
# - Full agent capabilities via WebSocket
# - Clean, modern UI
```

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────┐
│         AgentService (Unified Backend)           │
│  ┌─────────────────────────────────────────┐   │
│  │   LLMOrchestrator (The Brain)            │   │
│  │  - Analyzes user input                   │   │
│  │  - Creates execution plans               │   │
│  │  - Synthesizes responses                 │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐    │   │
│  │  │Ollama  │ │OpenAI  │ │Anthropic │    │   │
│  │  └────────┘ └────────┘ └──────────┘    │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │   ToolRegistry (4 Core Tools)            │   │
│  │  [filesystem, shell, web_search, python] │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │   ExecutionEngine (Safe Execution)       │   │
│  │  - Parallel tool execution               │   │
│  │  - Retry logic & error handling          │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │   MemorySystem (Persistent Context)      │   │
│  │  - Conversation history                  │   │
│  │  - Pattern learning                      │   │
│  │  - JSON storage                          │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
    ┌────────┐    ┌──────────┐   ┌────────┐
    │  CLI   │    │  Web UI  │   │ Voice  │
    │Stream✅│    │ Stream✅ │   │Audio⚠️ │
    │Tools✅ │    │ Tools✅  │   │Tools⚠️ │
    └────────┘    └──────────┘   └────────┘
```

### Directory Structure

```
vibe1337/
├── core/                          # Core agent implementation (2,005 LOC)
│   ├── agent_service.py           # Unified service for all UIs (streaming support)
│   ├── llm_orchestrator_fixed.py  # LLM decision-making and planning
│   ├── tool_registry.py           # Tool definitions and validation
│   ├── execution_engine.py        # Safe tool execution with retry logic
│   ├── memory_system.py           # Persistent memory and learning
│   ├── tool_message.py            # Structured tool communication
│   ├── autogen_chat/              # Advanced multi-agent system (reference)
│   └── claude.md                  # Core module documentation
│
├── tools/                         # Tools ecosystem
│   ├── gptme_tools/               # 27 advanced tools (available for integration)
│   ├── mcp/                       # MCP protocol infrastructure (stub)
│   └── claude.md                  # Tools documentation
│
├── ui/                            # User interface implementations
│   ├── web/websocket_server/      # Web UI (FastAPI + WebSocket)
│   ├── voice/pocketflow_voice/    # Voice UI (experimental)
│   └── claude.md                  # UI documentation
│
├── docs/                          # Documentation
│   ├── archive/                   # Historical analysis documents
│   ├── UNUSED_COMPONENTS.md       # Inventory of non-integrated code
│   ├── PUBLISH_CHECKLIST.md       # Publication guidelines
│   └── claude.md                  # Documentation index
│
├── vibe1337.py                    # Main CLI entry point
├── test_debug.py                  # Debug test suite
├── setup.py                       # Installation configuration
├── pyproject.toml                 # Modern Python packaging
├── pytest.ini                     # Test configuration
├── requirements.txt               # Core dependencies
├── CHANGELOG.md                   # Version history
├── INTEGRATION_GUIDE.md           # Guide for extending VIBE1337
├── QUICK_REFERENCE.md             # Quick reference guide
├── LICENSE                        # MIT License
└── README.md                      # This file
```

### Core Components (100% Functional)

| Module | LOC | Purpose | Status |
|--------|-----|---------|--------|
| `agent_service.py` | 321 | Unified interface for all UIs, streaming support | ✅ Production |
| `llm_orchestrator_fixed.py` | 511 | LLM decision-making, planning, synthesis | ✅ Production |
| `tool_registry.py` | 492 | Tool definitions, validation, schema generation | ✅ Production |
| `execution_engine.py` | 112 | Safe tool execution, retry logic | ✅ Production |
| `memory_system.py` | 188 | Persistent memory, learning, history | ✅ Production |
| `tool_message.py` | 381 | Structured tool communication | ✅ Production |
| **Total** | **2,005** | **Core functional code** | **✅ 100%** |

## Available for Integration

VIBE1337 includes additional tools and frameworks that are **not currently integrated** but available for future development:

### GPTMe Tools (27 tools, 6,444 LOC)
**Status**: ⚠️ Requires `gptme` package (not installed)

Categories:
- **Browser**: Playwright, Lynx, Perplexity search
- **Code**: patch, refactor, analyze
- **Computer**: mouse/keyboard control, screenshots
- **Media**: vision, text-to-speech, YouTube
- **Development**: GitHub operations, RAG, sub-agents
- **Execution**: shell, Python, tmux

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for integration instructions.

### MCP Protocol Support
**Status**: ⚠️ Infrastructure present, not wired up

The `tools/mcp/` directory contains MCP protocol client code, but no servers are configured.

### AutoGen Multi-Agent Framework
**Status**: ⚠️ Reference implementation (not imported)

The `core/autogen_chat/` directory contains Microsoft's AutoGen framework (~15,000 LOC) as reference material for future multi-agent capabilities.

## Development

### Running Tests

```bash
# Run basic test suite
python test_debug.py

# Or use pytest (for future test additions)
pytest

# With coverage reporting
pytest --cov=core --cov=tools --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Check style
flake8

# Type checking
mypy core/
```

### Adding Custom Tools

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed instructions on:
- Creating custom tools
- Integrating GPTMe tools
- Setting up MCP servers
- Adding new LLM providers
- Building UI implementations

## Roadmap

### Current: v2.1.0 - Production Ready ✅
- ✅ Core LLM-driven execution
- ✅ Streaming support (OpenAI, Anthropic)
- ✅ Unified AgentService architecture
- ✅ CLI and Web UIs fully functional
- ✅ 4 core tools integrated
- ✅ Persistent memory system
- ✅ Production packaging and build

### Next: v2.2.0 - Extended Tools
- [ ] Integrate GPTMe browser tools (Playwright)
- [ ] Add GitHub operations tools
- [ ] MCP server infrastructure
- [ ] Voice UI full integration with AgentService
- [ ] Expanded test coverage (unit + integration)

### Future: v3.0.0 - Multi-Agent
- [ ] AutoGen integration for multi-agent workflows
- [ ] Agent coordination and task delegation
- [ ] Specialized agent roles
- [ ] Docker containerization
- [ ] CI/CD pipeline

### Long-term Vision
- [ ] Self-improvement capabilities
- [ ] Advanced research and synthesis
- [ ] Physical world integration (robotics)
- [ ] Simulation environments
- [ ] Autonomous goal-setting

## Documentation

- **[claude.md](./claude.md)** - Comprehensive project overview
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Adding tools and providers
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick command reference
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history
- **[core/claude.md](./core/claude.md)** - Core modules documentation
- **[tools/claude.md](./tools/claude.md)** - Tools ecosystem guide
- **[ui/claude.md](./ui/claude.md)** - UI implementation guide
- **[docs/UNUSED_COMPONENTS.md](./docs/UNUSED_COMPONENTS.md)** - Non-integrated code inventory

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Format** your code (`black . && isort .`)
6. **Test** your changes (`pytest`)
7. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
8. **Push** to your branch (`git push origin feature/amazing-feature`)
9. **Open** a Pull Request

### Contribution Guidelines
- Follow existing code style (black, isort)
- Add tests for new features
- Update documentation
- Keep commits focused and atomic
- Write clear commit messages

## Security

VIBE1337 implements multiple security layers:

- **Path Traversal Protection**: Filesystem operations validate and sanitize paths
- **Command Whitelist**: Shell tool only allows 30+ pre-approved safe commands
- **Sandboxed Execution**: Python executor restricts dangerous builtins
- **Sensitive File Blacklist**: Prevents access to credentials, keys, passwords
- **Input Validation**: All tool parameters validated against schemas
- **No Remote Code Execution**: LLM cannot execute arbitrary commands

Report security issues to the GitHub issues page.

## FAQ

**Q: Do I need API keys to use VIBE1337?**
A: No! Install [Ollama](https://ollama.ai) and any local model. VIBE1337 auto-detects Ollama models. API keys are optional for OpenAI/Anthropic access.

**Q: How is this different from AutoGPT, BabyAGI, etc?**
A: VIBE1337 uses proper LLM-driven decision making with structured function calling. The LLM analyzes each request and creates execution plans - no hardcoded regex patterns or predefined workflows.

**Q: Can I use this commercially?**
A: Yes! MIT license allows commercial use. See [LICENSE](LICENSE) for details.

**Q: What about the 27 GPTMe tools?**
A: They're available but require the `gptme` package which isn't currently installed. See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for integration steps.

**Q: Is streaming supported?**
A: Yes! Streaming works with OpenAI and Anthropic. Ollama falls back to non-streaming mode.

**Q: Can I add my own tools?**
A: Absolutely! See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for a step-by-step guide.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built from the best features of:
- **Microsoft AutoGen** - Multi-agent coordination patterns
- **GPTMe** - Advanced tool ecosystem design
- **Langroid** - Agent architecture concepts
- **PocketFlow** - Async flow orchestration
- **Claude Code** - Development assistance

VIBE1337 is created as a TRUE LLM-driven agent where AI makes ALL decisions.

## Repository & Contact

- **GitHub**: https://github.com/oimiragieo/vibe1337
- **Issues**: https://github.com/oimiragieo/vibe1337/issues
- **License**: MIT

---

**Version**: 2.1.0 | **Status**: Production Ready | **Updated**: 2025-11-20
