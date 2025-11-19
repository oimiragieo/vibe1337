# Tools Module - VIBE1337 Tool Ecosystem

## Overview

The `tools/` directory contains a comprehensive ecosystem of tools that can be used by the LLM agent to interact with the system, web, and external services. This includes both integrated tools (4) and a large collection of ready-to-integrate advanced tools (24+).

## Structure

```
tools/
├── gptme_tools/           # 24 advanced tools (9,000+ lines)
│   ├── __init__.py        # Tool orchestration
│   ├── base.py            # Base tool class (574 lines)
│   ├── Browser Tools (4 files)
│   ├── Development Tools (7 files)
│   ├── Media Tools (4 files)
│   ├── AI/Research Tools (3 files)
│   └── System Tools (6 files)
└── mcp/                   # MCP protocol support
    ├── __init__.py
    ├── decorators.py      # MCP decorators (38 lines)
    └── fastmcp_client.py  # MCP client (584 lines)
```

## Tool Categories

### Integrated Tools (in `../core/tool_registry.py`)

These 4 tools are currently registered and available to the agent:

1. **FileSystemTool** - File operations
2. **ShellTool** - Command execution
3. **WebSearchTool** - Web search
4. **PythonExecutorTool** - Code execution

See `../core/claude.md` for detailed documentation.

---

## GPTMe Tools (`gptme_tools/`)

### Status: **READY BUT NOT INTEGRATED**

These 24+ production-ready tools from the GPTMe project are fully implemented but not currently wired into the ToolRegistry. They represent 86% of the available tooling capability.

### Base Infrastructure

**`base.py` (574 lines)**
- Base tool class definition
- Tool parameter handling
- Tool execution framework
- Error handling utilities

**`__init__.py`**
- Tool discovery and loading
- Tool registration
- Metadata management

---

### Browser Tools (4 implementations)

#### 1. `browser.py` (213 lines)
General browser automation tool.

**Features:**
- URL fetching
- Content extraction
- Link following
- Form interaction

**Capabilities:**
- HTML parsing
- JavaScript execution
- Cookie management
- Session persistence

**Dependencies:** Requires browser backend

---

#### 2. `_browser_lynx.py` (195 lines)
Text-based browser using Lynx.

**Features:**
- Text-only browsing
- Fast content retrieval
- No JavaScript overhead
- Low resource usage

**Use Cases:**
- Quick content fetching
- Text extraction
- Accessibility testing

**TODO:**
- Create LYNX_CFG configuration

---

#### 3. `_browser_perplexity.py` (107 lines)
Perplexity AI search integration.

**Features:**
- AI-powered search
- Source citation
- Answer synthesis
- Real-time information

**Use Cases:**
- Research queries
- Fact-checking
- Current events

---

#### 4. `_browser_playwright.py` (325 lines)
Full browser automation via Playwright.

**Features:**
- Full browser control
- JavaScript execution
- Screenshot capture
- Network interception
- Multi-browser support (Chrome, Firefox, Safari)

**Capabilities:**
- Element interaction (click, type, scroll)
- Wait for elements
- Handle popups/alerts
- File uploads/downloads

**Use Cases:**
- Complex web automation
- Testing web applications
- Scraping dynamic content

**Dependencies:**
- `playwright` library
- Browser binaries

---

### Development Tools (7 implementations)

#### 1. `python.py` (277 lines)
Advanced Python execution using IPython.

**Features:**
- IPython REPL integration
- Rich output formatting
- Magic commands
- Interactive debugging

**Advantages over PythonExecutorTool:**
- Full Python environment
- Package imports
- File system access
- Interactive workflows

**TODO:**
- Launch IPython in current venv

**Security:** Less restricted than PythonExecutorTool

---

#### 2. `shell.py` (723 lines)
Advanced shell scripting and command execution.

**Features:**
- Multi-line scripts
- Environment variable support
- Working directory management
- Background processes
- Output streaming

**Capabilities:**
- Script persistence
- Command history
- Output buffering
- Error handling

**Advantages over ShellTool:**
- No whitelist restrictions
- Command chaining
- Script composition
- Process management

**TODO:**
- Implement smart-wait for async commands

**Security:** Full shell access (use with caution)

---

#### 3. `patch.py` (307 lines)
Code patching and modification.

**Features:**
- Unified diff application
- Code block replacement
- Multi-file patches
- Conflict detection

**Use Cases:**
- Code refactoring
- Bug fixes
- Feature additions
- Version updates

**Capabilities:**
- Patch validation
- Dry-run mode
- Rollback support
- Context matching

---

#### 4. `save.py` (299 lines)
Advanced file saving and management.

**Features:**
- Atomic writes
- Backup creation
- Permission handling
- Directory creation

**Capabilities:**
- File locking
- Checksum validation
- Metadata preservation
- Safe overwrites

**Advantages over FileSystemTool:**
- More robust error handling
- Automatic backups
- Atomic operations

---

#### 5. `read.py` (92 lines)
Enhanced file reading.

**Features:**
- Multiple encoding support
- Large file handling
- Stream reading
- Binary/text detection

**Capabilities:**
- Encoding detection
- Partial reads
- Line-by-line reading

---

#### 6. `gh.py` (206 lines)
GitHub operations and automation.

**Features:**
- Issue management
- PR creation/review
- Repository operations
- GitHub API integration

**Capabilities:**
- Create/update issues
- Manage PRs
- Code review
- Release management
- Workflow triggers

**Authentication:**
- GitHub token required
- SSH key support

**Note:** Deprecated `--confirm` and `-y` flags

---

#### 7. `tmux.py` (325 lines)
Terminal multiplexer integration.

**Features:**
- Session management
- Window/pane control
- Command execution in sessions
- Output capture

**Use Cases:**
- Long-running processes
- Multiple shell sessions
- Persistent terminals
- Remote workflows

**TODO:**
- Implement smart-wait functionality

**Dependencies:**
- `tmux` installed

---

### Media Tools (4 implementations)

#### 1. `vision.py` (173 lines)
Image analysis and computer vision.

**Features:**
- Image classification
- Object detection
- OCR (text extraction)
- Scene understanding

**Capabilities:**
- Multi-modal LLM integration
- Image preprocessing
- Bounding boxes
- Confidence scores

**Use Cases:**
- Screenshot analysis
- Document processing
- Visual QA
- Content moderation

**Dependencies:**
- Vision API or model

---

#### 2. `screenshot.py` (95 lines)
Screen capture utility.

**Features:**
- Full screen capture
- Region selection
- Window capture
- Multi-monitor support

**Capabilities:**
- Format selection (PNG, JPG)
- Quality settings
- Clipboard integration

**Dependencies:**
- Platform-specific screen capture tools

**Integration:** Works with `vision.py` for analysis

---

#### 3. `tts.py` (460 lines)
Text-to-speech synthesis.

**Features:**
- Multiple TTS engines
- Voice selection
- Speed/pitch control
- Audio file output

**Supported Engines:**
- OpenAI TTS API
- Local TTS engines
- Cloud TTS services

**Capabilities:**
- Streaming audio
- Voice cloning
- Emotion/style control
- Multi-language support

**Use Cases:**
- Accessibility
- Content creation
- Voice assistants
- Audio books

**Dependencies:**
- TTS API or engine

---

#### 4. `youtube.py` (77 lines)
YouTube interaction and content retrieval.

**Features:**
- Video metadata
- Transcript extraction
- Search functionality
- Comment retrieval

**Capabilities:**
- Parse video URLs
- Extract captions
- Get video info
- Search videos

**Dependencies:**
- `yt-dlp` or similar

---

### AI/Research Tools (3 implementations)

#### 1. `rag.py` (125 lines)
Retrieval-Augmented Generation.

**Features:**
- Document embedding
- Semantic search
- Context retrieval
- Answer synthesis

**Capabilities:**
- Vector database integration
- Chunking strategies
- Relevance ranking
- Citation tracking

**Use Cases:**
- Document QA
- Knowledge retrieval
- Research assistance
- Technical support

**Components:**
- Embedding model
- Vector store
- Retrieval logic
- Response generation

---

#### 2. `subagent.py` (81 lines)
Sub-agent creation and delegation.

**Features:**
- Spawn specialized agents
- Task delegation
- Result aggregation
- Parallel execution

**Use Cases:**
- Complex tasks
- Divide-and-conquer
- Specialization
- Parallel processing

**Capabilities:**
- Agent configuration
- Communication protocols
- Result merging

---

#### 3. `choice.py` (104 lines)
Decision-making and option selection.

**Features:**
- Multi-criteria decision making
- Option comparison
- Preference modeling
- Recommendation generation

**Capabilities:**
- Weighted scoring
- Trade-off analysis
- Constraint satisfaction

**Use Cases:**
- Option selection
- Planning
- Optimization

---

### System Tools (6 implementations)

#### 1. `computer.py` (804 lines)
**Comprehensive screen automation, mouse, and keyboard control.**

**Features:**
- Mouse control (move, click, drag)
- Keyboard input (type, hotkeys)
- Screen reading
- Window management

**Capabilities:**
- Pixel-perfect automation
- GUI interaction
- Application control
- Desktop automation

**Use Cases:**
- UI testing
- Application automation
- RPA (Robotic Process Automation)
- Accessibility

**TODO:**
- Retrieve screen dimensions

**Security:** Powerful - requires careful use
**Dependencies:**
- Platform-specific automation libraries

---

#### 2. `mcp_adapter.py` (215 lines)
Model Context Protocol adapter.

**Purpose:** Bridge between VIBE1337 and MCP servers.

**Features:**
- MCP server communication
- Tool discovery
- Request/response translation
- Protocol compliance

**Capabilities:**
- Dynamic tool loading
- Server multiplexing
- Error handling

**Status:** Not integrated with ToolRegistry

---

#### 3. `chats.py` (89 lines)
Chat management and conversation handling.

**Features:**
- Conversation persistence
- Chat history
- Message threading
- Context management

**Use Cases:**
- Multi-turn conversations
- Chat logs
- Context switching

---

#### 4. `morph.py` (185 lines)
Code transformation and refactoring.

**Features:**
- AST manipulation
- Code generation
- Refactoring patterns
- Code analysis

**Capabilities:**
- Variable renaming
- Function extraction
- Dead code removal
- Style transformation

**Use Cases:**
- Code modernization
- Refactoring
- Code generation

---

## MCP Module (`mcp/`)

### Model Context Protocol Integration

**Purpose:** Enable VIBE1337 to connect to MCP servers and use external tools.

**Status:** **Implemented but not integrated** - 584 lines of code ready to use.

### Components

#### `fastmcp_client.py` (584 lines)
Full-featured MCP client implementation.

**Features:**
- Server connection management
- Tool discovery
- Request/response handling
- Error recovery

**Capabilities:**
- Connect to MCP servers
- List available tools
- Execute remote tools
- Handle streaming responses

**Protocol:** Model Context Protocol v1.0

**Supported Transports:**
- HTTP/HTTPS
- WebSocket
- stdio (subprocess)

---

#### `decorators.py` (38 lines)
MCP tool decorators.

**Purpose:** Simplify MCP tool definition.

**Decorators:**
- `@mcp_tool` - Mark function as MCP tool
- `@mcp_resource` - Mark as MCP resource
- `@mcp_prompt` - Mark as MCP prompt

---

### Integration Path

**Current Stub:**
```python
# In core/tool_registry.py
def add_mcp_tools(self, mcp_server_path: str):
    """Add tools from an MCP server"""
    # This will integrate with the MCP implementation we copied
    pass  # ← NEEDS IMPLEMENTATION
```

**Required Implementation:**
1. Import `fastmcp_client`
2. Connect to MCP server
3. Discover tools
4. Create `BaseTool` wrappers
5. Register tools dynamically

**Example:**
```python
def add_mcp_tools(self, mcp_server_url: str):
    from tools.mcp.fastmcp_client import MCPClient

    client = MCPClient(mcp_server_url)
    tools = client.list_tools()

    for tool in tools:
        wrapped_tool = self._create_mcp_tool_wrapper(tool, client)
        self.register_tool(wrapped_tool)
```

---

## Integration Strategy

### Priority 1: Core Development Tools
These should be integrated first:
1. `patch.py` - Code modification
2. `gh.py` - GitHub operations
3. `read.py` + `save.py` - Enhanced file operations

### Priority 2: Browser & Web
4. `_browser_playwright.py` - Full browser automation
5. `_browser_perplexity.py` - AI search

### Priority 3: System & Automation
6. `computer.py` - Screen automation
7. `tmux.py` - Terminal multiplexing
8. `screenshot.py` + `vision.py` - Visual analysis

### Priority 4: Advanced Features
9. `rag.py` - Document search
10. `subagent.py` - Task delegation
11. `python.py` - Full Python environment
12. `shell.py` - Advanced shell

### Priority 5: Media & Misc
13. `tts.py` - Text-to-speech
14. `youtube.py` - Video content
15. `morph.py` - Code transformation

---

## Implementation Steps

### 1. Create Tool Wrappers

Each gptme tool needs a wrapper to conform to `BaseTool` interface:

```python
# Example: Wrapping patch.py
from tools.gptme_tools import patch

class PatchTool(BaseTool):
    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="patch",
            description="Apply code patches and modifications",
            parameters=[
                ToolParameter(name="patch_content", type="string",
                            description="Unified diff patch"),
                ToolParameter(name="target_file", type="string",
                            description="File to patch")
            ]
        )

    async def execute(self, **kwargs):
        result = await patch.apply_patch(
            kwargs["patch_content"],
            kwargs["target_file"]
        )
        return result
```

### 2. Register Tools

```python
# In ToolRegistry._initialize_default_tools()
self.register_tool(PatchTool())
self.register_tool(GithubTool())
# ... etc
```

### 3. Test Integration

```python
# Test each tool
registry = ToolRegistry()
tool = registry.get_tool("patch")
result = await tool.execute(patch_content="...", target_file="...")
```

---

## Dependencies

### GPTMe Tools
- `playwright` - Browser automation
- `yt-dlp` - YouTube access
- `tmux` - Terminal multiplexing
- Platform-specific automation libs (pyautogui, etc.)

### MCP
- `httpx` or `aiohttp` - HTTP client
- `websockets` - WebSocket client

---

## Security Considerations

### High-Risk Tools
These tools require careful security review:
- `shell.py` - Full shell access
- `python.py` - Unrestricted Python
- `computer.py` - Desktop automation
- `save.py` / `patch.py` - File modification

### Recommended Safeguards
1. **Sandboxing** - Run in containers
2. **Permissions** - User confirmation for dangerous operations
3. **Auditing** - Log all tool executions
4. **Rate Limiting** - Prevent abuse
5. **Whitelisting** - Allowed paths/commands

---

## Testing

### Unit Tests Needed
- Each tool should have unit tests
- Mock external dependencies
- Test error handling
- Validate schemas

### Integration Tests
- Test tool execution flow
- Test LLM tool selection
- Test error propagation
- Test resource cleanup

---

## Performance

### Bottlenecks
- Browser automation (slow)
- External API calls
- File I/O operations
- Subprocess overhead

### Optimization
- Connection pooling for browsers
- Caching for web requests
- Async I/O for file operations
- Process reuse for shells

---

## Future Enhancements

1. **Tool Composition** - Chain tools together
2. **Parallel Execution** - Run independent tools concurrently
3. **Caching** - Cache tool results
4. **Versioning** - Track tool versions
5. **Metrics** - Tool usage statistics
6. **Auto-discovery** - Scan for new tools
7. **Hot Reload** - Update tools without restart

---

## Contributing

### Adding New Tools

1. Create tool file in `gptme_tools/`
2. Implement tool logic
3. Add tests
4. Document usage
5. Create `BaseTool` wrapper
6. Register in ToolRegistry
7. Update this documentation

### Tool Guidelines
- Clear, single-purpose tools
- Comprehensive error handling
- Async-first design
- Security-conscious
- Well-documented
- Tested

---

## Version History

- v1.0 - Basic 4 tools integrated
- v2.0 - GPTMe tools imported (not integrated)
- v2.1 - MCP infrastructure added (not integrated)
- v3.0 (target) - All 28+ tools integrated, MCP working
