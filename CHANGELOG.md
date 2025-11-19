# Changelog

All notable changes to VIBE1337 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-19

### Added
- **Streaming Support** - Real-time token-by-token responses in CLI
  - Added `core/agent_service.py` - Unified service with streaming capabilities
  - Streaming support for OpenAI and Anthropic providers
  - Progressive updates showing planning, tool execution, and response chunks
  - CLI option `--no-streaming` to disable streaming

- **Unified Architecture** - All UIs now use the same backend
  - `AgentService` provides consistent interface across CLI, Web, and Voice UIs
  - Web UI now has full tool access (previously bypassed core agent)
  - Voice UI ready for tool integration
  - Consistent behavior and capabilities across all interfaces

- **Production-Ready Build System**
  - `setup.py` with full package configuration
  - `pyproject.toml` for modern Python packaging
  - `pytest.ini` for test configuration
  - Entry point: `vibe1337` command after installation
  - Extra dependencies: `web`, `voice`, `dev`, `all`

- **Comprehensive Documentation**
  - `claude.md` - Main project documentation
  - `core/claude.md` - Core module documentation (511 lines)
  - `tools/claude.md` - Tools ecosystem guide
  - `ui/claude.md` - UI implementation guide
  - `docs/claude.md` - Documentation directory guide
  - `INTEGRATION_GUIDE.md` - Step-by-step integration instructions
  - `CHANGELOG.md` - This file

- **Enhanced Web UI**
  - Integrated with AgentService instead of direct OpenAI calls
  - Tool execution visibility (shows which tools are being used)
  - Status updates during planning and execution
  - Full access to all 4 core tools

- **Development Tools**
  - Black configuration for code formatting
  - isort configuration for import sorting
  - flake8 configuration for linting
  - mypy configuration for type checking
  - `.gitignore` with comprehensive exclusions

### Changed
- **CLI Implementation** - Refactored to use AgentService
  - Streaming now enabled by default (use `--no-streaming` to disable)
  - Cleaner separation between UI and agent logic
  - Better error handling and user feedback
  - Shows streaming status in banner

- **Web UI** (`ui/web/websocket_server/nodes.py`)
  - Replaced direct OpenAI streaming with AgentService streaming
  - Added support for multiple message types (status, tool, chunk, end)
  - Better integration with agent capabilities

- **Main Entry Point** (`vibe1337.py`)
  - Now uses AgentService for all processing
  - Maintains backward compatibility with existing code
  - Improved shutdown handling (saves memory properly)
  - Better command-line argument handling

### Fixed
- Tool execution now properly streamed to all UIs
- Memory system consistently saved on shutdown
- Proper async handling in all streaming paths
- WebSocket message format consistency

### Documentation
- Updated README.md with v2.1 features
- Added installation instructions with pip
- Added API usage examples
- Added architecture diagrams
- Clarified tool integration status (4 integrated, 24 available)
- Added development guidelines
- Added roadmap and next steps

### Performance
- Streaming responses reduce perceived latency
- Unified service reduces code duplication
- Better async handling throughout

### Security
- All existing security features maintained
- Path traversal protection
- Command injection prevention
- Sandboxed Python execution
- Sensitive file blacklist

---

## [2.0.0] - Previous Version

### Added
- Core agent functionality
- 4 integrated tools (filesystem, shell, web_search, python_executor)
- Multi-model support (Ollama, OpenAI, Anthropic)
- Memory system with persistence
- Web UI with WebSocket support
- Voice UI with STT/TTS
- AutoGen chat module integration
- Arena consensus mode (@ARENA)
- Web search shortcut (@WEB)

### Features
- LLM-driven decision making
- Dynamic execution planning
- Tool registry with OpenAI function calling format
- Safe execution engine
- Context-aware responses
- Conversation history

---

## [1.0.0] - Initial Release

### Added
- Basic agent framework
- Initial tool implementations
- CLI interface
- LLM orchestrator
- Tool registry foundation

---

## Future Plans

### [2.2.0] - Planned
- Integrate GPTMe tools (browser, GitHub, patch, etc.)
- Wire up MCP infrastructure
- Expand test coverage with pytest
- Add Docker support
- CI/CD pipeline

### [3.0.0] - Vision
- Full tool ecosystem (28+ tools integrated)
- Advanced multi-agent coordination
- Self-improvement capabilities
- Enhanced security features
- Production deployment guides

---

## Version Support

| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| 2.1.x   | Active | Current       | Latest features, streaming support |
| 2.0.x   | Maintenance | 2025-06-19 | Core features, no streaming |
| 1.x.x   | Deprecated | - | Upgrade recommended |

---

## Migration Guides

### From 2.0.x to 2.1.0

**No Breaking Changes** - Fully backward compatible!

**Optional Upgrades:**
1. Enable streaming in your code:
   ```python
   # Old (still works)
   result = await orchestrator.process(user_input)

   # New (recommended)
   from core.agent_service import AgentService
   agent = AgentService({"streaming": True})

   async for chunk in agent.process_streaming(user_input):
       if chunk["type"] == "chunk":
           print(chunk["content"], end="", flush=True)
   ```

2. Update Web UI to use AgentService (already done in this release)

3. Install as package:
   ```bash
   pip install -e .
   # Now can use: vibe1337
   ```

### From 1.x.x to 2.x.x

**Breaking Changes:**
- Tool interface changed to OpenAI function calling format
- LLM orchestrator redesigned
- Memory system format changed

**Migration Steps:**
1. Update tool implementations to use `BaseTool`
2. Update any custom LLM integrations
3. Migrate memory files (if needed)

---

## Contributing

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for contribution guidelines.

---

## Links

- **Repository:** https://github.com/oimiragieo/vibe1337
- **Issues:** https://github.com/oimiragieo/vibe1337/issues
- **Documentation:** [claude.md](./claude.md)
- **Integration Guide:** [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

---

**Maintained by:** VIBE1337 Contributors
**License:** MIT
