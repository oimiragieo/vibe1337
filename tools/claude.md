# tools/ - VIBE1337 Tools Directory

## Overview
Contains tool implementations and frameworks. **Important**: This directory contains mostly **UNUSED/LEGACY** code that is NOT integrated into the main VIBE1337 agent.

## Status
- **Actual Tools in Use**: 4 (defined in core/tool_registry.py, not here)
- **Unused Legacy Tools**: 27+ tools in gptme_tools/
- **Integration Level**: ⚠️ **0%** - None of these are wired up

## Directory Structure

```
tools/
├── gptme_tools/        # ⚠️ UNUSED - 27 tools from gptme framework (6,444 LOC)
└── mcp/                # ⚠️ UNUSED - MCP protocol client (not integrated)
```

---

## ⚠️ gptme_tools/ (UNUSED - 27 tools, 6,444 LOC)

**Status**: **NOT INTEGRATED**
- These tools are from the gptme framework (reference implementation)
- They have dependencies on the full gptme package
- They are **NEVER IMPORTED** by the main VIBE1337 application
- Grep confirms: 0 imports of gptme_tools in codebase

**Why they exist**: Included as reference/inspiration for future tool development

**Tools included** (all non-functional without gptme dependencies):

### Execution Tools
1. **shell.py** (723 LOC) - Advanced shell execution
2. **python.py** (277 LOC) - Python REPL and execution
3. **tmux.py** (325 LOC) - Tmux session management
4. **computer.py** (804 LOC) - Computer control (keyboard, mouse, screen)

### File Tools
5. **save.py** (299 LOC) - Advanced file saving
6. **read.py** - File reading
7. **patch.py** (307 LOC) - Git-style patching
8. **morph.py** (275 LOC) - Code morphing/transformation

### Web Tools
9. **browser.py** (213 LOC) - Browser automation
10. **_browser_playwright.py** (325 LOC) - Playwright backend
11. **_browser_lynx.py** - Lynx text browser
12. **_browser_perplexity.py** - Perplexity integration
13. **_browser_thread.py** - Threaded browser
14. **youtube.py** - YouTube processing

### AI/ML Tools
15. **vision.py** (84 LOC) - Image analysis
16. **tts.py** (460 LOC) - Text-to-speech
17. **rag.py** (279 LOC) - RAG (Retrieval-Augmented Generation)

### Communication Tools
18. **chats.py** (234 LOC) - Chat management
19. **gh.py** - GitHub integration
20. **subagent.py** (171 LOC) - Sub-agent spawning
21. **choice.py** (158 LOC) - User choice prompts
22. **screenshot.py** - Screenshot capture

### Infrastructure
23. **base.py** - Base tool classes
24. **__init__.py** (276 LOC) - Tool discovery and loading
25. **mcp_adapter.py** - MCP protocol adapter

**Dependencies** (NOT installed):
```python
from gptme.config import get_config
from gptme.constants import INTERRUPT_CONTENT
from ..message import Message
from ..telemetry import trace_function
```

**If you want to use these**:
1. ❌ Don't - They require full gptme package
2. ✅ Instead: Reimplement needed tools in core/tool_registry.py
3. ✅ Or: Build custom tools extending BaseTool

**Recommendation**: Remove or clearly document as reference-only

---

## ⚠️ mcp/ (UNUSED - MCP Protocol Client)

**Status**: **NOT INTEGRATED**

**Files**:
- `fastmcp_client.py` - FastMCP client implementation
- `decorators.py` - MCP decorators
- `__init__.py` - MCP initialization

**Purpose**: Model Context Protocol (MCP) support for connecting to MCP servers

**Why unused**:
- No integration code in main application
- No MCP servers configured
- ToolRegistry has stub: `add_mcp_tools(mcp_server_path)` but never called

**What MCP enables**:
- Connect to external tool servers
- Dynamic tool discovery
- Standardized tool protocol
- Tool sharing across applications

**To integrate MCP**:
1. Configure MCP server paths
2. Call `ToolRegistry.add_mcp_tools(server_path)`
3. Implement tool discovery and schema conversion
4. Test with MCP-compatible servers

**Current state**: Infrastructure exists but not wired up

---

## Actually Used Tools (Not in this directory!)

The 4 tools VIBE1337 actually uses are defined in **core/tool_registry.py**:

1. **FileSystemTool** - Read/write/list files with security
2. **ShellTool** - Execute whitelisted shell commands
3. **WebSearchTool** - DuckDuckGo search
4. **PythonExecutorTool** - Sandboxed Python execution

See `core/claude.md` for details on these tools.

---

## Tool Integration Guide

**To add a NEW tool to VIBE1337**:

1. **Define tool class** in `core/tool_registry.py`:
```python
class MyCustomTool(BaseTool):
    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="my_tool",
            description="What this tool does",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Parameter description",
                    required=True
                )
            ]
        )

    async def execute(self, **kwargs) -> Any:
        self.validate_parameters(**kwargs)
        # Implement tool logic
        return {"result": "success"}
```

2. **Register tool** in `ToolRegistry._initialize_default_tools()`:
```python
def _initialize_default_tools(self):
    default_tools = [
        FileSystemTool(),
        ShellTool(),
        WebSearchTool(),
        PythonExecutorTool(),
        MyCustomTool(),  # Add here
    ]
```

3. **Test tool**:
```python
# In test_debug.py or interactive
tool_call = ToolCall(
    tool_name="my_tool",
    parameters={"param1": "value"},
    reasoning="Testing custom tool"
)
result = await engine.execute(tool_call)
```

**DO NOT** try to integrate gptme_tools directly - they won't work without dependencies.

---

## Security Considerations

**For custom tools**:
1. ✅ Validate all user inputs
2. ✅ Use path normalization for file operations
3. ✅ Whitelist commands/operations where possible
4. ✅ Set timeouts for long-running operations
5. ✅ Sanitize outputs before returning
6. ⚠️ Never use `eval()` or `exec()` on user input
7. ⚠️ Never trust file paths without validation

**Examples from existing tools**:
- FileSystemTool: Path normalization, boundary checks, sensitive file blacklist
- ShellTool: Whitelist approach, pattern blocking, no command chaining
- PythonExecutorTool: Restricted builtins, no imports

---

## Code Statistics

### gptme_tools/
- **Total LOC**: ~6,444
- **Files**: 27 Python files
- **Integration**: 0%
- **Dependencies**: gptme package (not installed)
- **Status**: Reference code only

### mcp/
- **Total LOC**: ~200 (estimated)
- **Files**: 3 Python files
- **Integration**: 0%
- **Dependencies**: fastmcp (may or may not be installed)
- **Status**: Infrastructure present, not wired

### Actual Tools (in core/)
- **Total LOC**: ~413 (tool_registry.py)
- **Files**: 1 Python file (+ base classes)
- **Integration**: 100%
- **Dependencies**: Standard library + duckduckgo-search
- **Status**: Production ready

---

## Recommendations

### Immediate
1. **Document clearly**: Mark gptme_tools as "Reference Only"
2. **Consider removal**: 6,444 LOC of unused code is confusing
3. **Or keep as reference**: But add README warning

### Short-term
1. **Integrate MCP**: The infrastructure is there, just needs wiring
2. **Add more core tools**: Build custom tools in tool_registry.py
3. **Improve existing tools**: Add more operations, better error handling

### Long-term
1. **Decide on gptme_tools**: Either fully integrate or remove
2. **Tool marketplace**: Allow external tool plugins
3. **Tool discovery**: Auto-discover tools from directories
4. **Tool versioning**: Version and dependency management

---

## For AI Assistants

**When working with tools**:

✅ **DO**:
- Add new tools to `core/tool_registry.py`
- Extend `BaseTool` class
- Follow OpenAI function calling format
- Include security validation
- Test thoroughly

❌ **DON'T**:
- Try to import gptme_tools (will fail)
- Assume tools in this directory are functional
- Modify gptme_tools (they're reference only)
- Skip security validation

**Key file**: `core/tool_registry.py` (not this directory!)

---

## Summary

The `tools/` directory contains:
- ⚠️ **gptme_tools/**: 27 unused tools (6,444 LOC) - Reference only
- ⚠️ **mcp/**: MCP client (unused) - Infrastructure present
- ✅ **Actual tools**: Defined in `core/tool_registry.py` (4 tools, working)

**Integration level**: 0% - All code in this directory is unused

**What to do**:
- For new tools: Edit `core/tool_registry.py`
- For MCP: Wire up the existing mcp/ client
- For gptme_tools: Consider removal or clear "reference only" marking

**Codebase reduction opportunity**: Removing this directory would cut ~7,000 LOC (~30% of codebase) with zero functionality loss.
