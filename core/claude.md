# Core Module - VIBE1337 Brain & Infrastructure

## Overview

The `core/` directory contains the fundamental components that make VIBE1337 function as a true LLM-driven agent. These components work together to analyze requests, plan execution, manage tools, execute safely, and maintain context.

## Architecture

```
core/
├── __init__.py                    # Module initialization
├── llm_orchestrator_fixed.py      # LLM brain (511 lines)
├── tool_registry.py               # Tool management (492 lines)
├── execution_engine.py            # Safe execution (112 lines)
├── memory_system.py               # Context & memory (188 lines)
├── tool_message.py                # Message structures (381 lines)
└── autogen_chat/                  # Multi-agent system (5,421 lines)
    ├── agents/                    # 6 agent types
    ├── base/                      # Base abstractions
    ├── conditions/                # Termination conditions
    ├── teams/                     # Team coordination
    ├── messages.py                # Message handling
    ├── state/                     # State management
    ├── tools/                     # Tool wrappers
    ├── ui/                        # Console UI
    └── utils/                     # Utilities
```

## Core Components

### 1. LLM Orchestrator (`llm_orchestrator_fixed.py`)

**Purpose:** The "brain" that drives all agent decisions.

**Key Classes:**

#### `ModelProvider(Enum)`
Supported LLM providers:
- `OLLAMA` - Local Ollama models
- `OPENAI` - OpenAI GPT models
- `ANTHROPIC` - Anthropic Claude models

#### `ToolCall(dataclass)`
Structured tool invocation from LLM:
```python
@dataclass
class ToolCall:
    tool_name: str
    parameters: Dict[str, Any]
    reasoning: str = ""
    confidence: float = 1.0
```

#### `ExecutionStep(dataclass)`
Single step in execution plan:
```python
@dataclass
class ExecutionStep:
    step_id: str
    description: str
    tool_call: Optional[ToolCall] = None
    dependencies: List[str] = []
    model: str = "primary"
    prompt: Optional[str] = None
```

#### `ExecutionPlan(dataclass)`
Complete multi-step plan:
```python
@dataclass
class ExecutionPlan:
    goal: str
    steps: List[ExecutionStep]
    expected_outcome: str
    fallback_strategy: Optional[str] = None
```

#### `LLMOrchestrator`
Main orchestration engine.

**Key Methods:**

- `__init__(config)` - Initialize with configuration
  - Auto-detects available models (Ollama, OpenAI, Anthropic)
  - Loads API keys from environment
  - Sets primary model

- `async process(user_input, context=None)` - Main processing loop
  1. Gets context from memory
  2. Creates analysis prompt with available tools
  3. Queries LLM to create execution plan
  4. Parses plan into structured format
  5. Executes each step (tools or pure LLM)
  6. Synthesizes final response
  7. Updates memory

- `_create_analysis_prompt(user_input, context, tools)` - Creates structured prompt for LLM
  - Includes user request
  - Lists available tools with descriptions
  - Requests JSON response format

- `_parse_execution_plan(llm_response, user_input)` - Parses LLM's JSON plan
  - Handles various JSON formats (```json, plain, embedded)
  - Fallback to simple plan on parse failure
  - Extracts tool calls and dependencies

- `async _query_llm(model_key, prompt)` - Routes to appropriate provider
  - Supports mock, Ollama, OpenAI, Anthropic
  - Handles errors gracefully

- `async _query_ollama_fixed(model, prompt)` - Ollama-specific query
  - Uses shell piping to avoid hangs
  - 30-second timeout
  - Temp file for prompt encoding

- `async _query_openai(model, prompt)` - OpenAI API query
  - Uses AsyncOpenAI client
  - 2000 token limit
  - Temperature 0.7

- `async _query_anthropic(model, prompt)` - Anthropic API query
  - Uses AsyncAnthropic client
  - 2000 token limit

- `async arena_consensus(query, models)` - Multi-model consensus
  - Queries multiple models
  - Combines responses
  - Returns consensus view

**Current Issues:**
- Contains mock responses for testing (should be removed)
- No streaming support (returns complete response)
- Ollama query uses shell subprocess (fragile)

---

### 2. Tool Registry (`tool_registry.py`)

**Purpose:** Central tool management using OpenAI function calling format.

**Key Classes:**

#### `ToolParameter(dataclass)`
OpenAI-compatible parameter specification:
```python
@dataclass
class ToolParameter:
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict] = None  # For objects
    items: Optional["ToolParameter"] = None  # For arrays
```

#### `ToolSchema(dataclass)`
OpenAI function calling schema:
```python
@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: List[ToolParameter]

    def to_openai_format(self) -> Dict[str, Any]:
        # Converts to OpenAI function calling JSON
```

#### `BaseTool(ABC)`
Abstract base class for all tools.

**Required Methods:**
- `_build_schema()` - Returns ToolSchema
- `async execute(**kwargs)` - Executes the tool
- `validate_parameters(**kwargs)` - Validates inputs

#### Built-in Tools

**`FileSystemTool`**
File system operations with security hardening.

Operations:
- `read` - Read file contents (UTF-8 text only)
- `write` - Write content to file
- `list` - List directory contents
- `create_dir` - Create directory
- `delete` - Delete file or directory

Security:
- Path traversal prevention (resolves to absolute, checks within CWD)
- Sensitive file blacklist (`.env`, `.git`, `.ssh`, etc.)
- Binary file detection

**`ShellTool`**
Safe shell command execution.

Features:
- Whitelist of 30+ safe commands (ls, cat, grep, git, npm, etc.)
- Dangerous pattern blocking (rm -rf /, fork bombs, etc.)
- No command chaining (&&, ||, ;)
- No command substitution (`, $())
- Configurable timeout (default 30s)

Allowed commands: ls, dir, pwd, echo, cat, head, tail, grep, find, wc, sort, uniq, cut, sed, awk, date, whoami, hostname, uname, env, printenv, python, python3, node, npm, git, pip, pip3, curl, wget, ping, which, whereis, file, stat, df, du, ps, top, mkdir, touch, cp, mv

**`WebSearchTool`**
DuckDuckGo web search.

Parameters:
- `query` - Search query string
- `max_results` - Max results to return (default: 5)

Returns: List of search results with title, link, snippet

**`PythonExecutorTool`**
Sandboxed Python code execution.

Features:
- Restricted builtins (no file I/O, no imports)
- Captures stdout/stderr
- 10-second timeout
- Safe globals only

Allowed builtins: print, len, range, enumerate, zip, map, filter, sum, min, max, abs, round, sorted, list, dict, set, tuple, str, int, float, bool

#### `ToolRegistry`

**Key Methods:**

- `__init__()` - Initializes and registers default tools
- `register_tool(tool)` - Registers a BaseTool instance
- `get_tool(name)` - Retrieves tool by name
- `get_schemas()` - Returns all schemas in OpenAI format for LLM
- `get_tool_names()` - Lists available tool names
- `async execute_tool(tool_name, parameters)` - Executes tool by name
- `add_mcp_tools(mcp_server_path)` - **STUB** - Not implemented

**Current State:**
- 4 tools registered (filesystem, shell, web_search, python_executor)
- 24 tools available but not integrated (in `../tools/gptme_tools/`)
- MCP integration stub exists but empty

---

### 3. Execution Engine (`execution_engine.py`)

**Purpose:** Safe tool execution with error handling.

**Key Class:** `ExecutionEngine`

**Methods:**

- `__init__(tool_registry)` - Initialize with tool registry
- `async execute(tool_call: ToolCall)` - Execute a tool call
  - Validates tool exists
  - Extracts parameters
  - Calls tool's execute method
  - Handles errors gracefully
  - Returns standardized result format

**Result Format:**
```python
{
    "success": bool,
    "output": Any,  # Tool's return value
    "error": Optional[str],
    "tool_name": str,
    "parameters": dict,
    "execution_time": float
}
```

**Features:**
- Comprehensive error handling
- Execution time tracking
- Standardized response format
- Logging of all executions

---

### 4. Memory System (`memory_system.py`)

**Purpose:** Conversation history and context management.

**Key Class:** `MemorySystem`

**Storage:**
- In-memory conversation history
- Persistent JSON file storage
- Configurable memory limits

**Methods:**

- `__init__(config)` - Initialize memory
  - Sets memory file path
  - Loads existing memory
  - Configures limits

- `async add_interaction(user_input, agent_response, metadata)` - Store interaction
  - Adds to conversation history
  - Includes timestamp
  - Stores metadata

- `async get_context(max_items)` - Retrieve recent context
  - Returns last N interactions
  - Formatted for LLM context

- `get_relevant_context(query)` - **STUB** - Semantic search not implemented

- `save_memory()` - Persist to disk
  - Saves to JSON file
  - Creates directory if needed

- `clear_memory()` - Clear all history

- `get_stats()` - Memory statistics

**Configuration:**
- `memory_file` - Path to JSON file (default: `~/.vibe1337/memory.json`)
- `max_items` - Max items to keep (default: 1000)

---

### 5. Tool Message (`tool_message.py`)

**Purpose:** Message structures for tool communication.

**Contains:**
- Message format definitions
- Tool call serialization
- Response formatting

**Status:** 381 lines, partially overlaps with `autogen_chat/messages.py`

---

### 6. AutoGen Chat Module (`autogen_chat/`)

**Purpose:** Advanced multi-agent coordination system.

**Status:** Fully implemented (5,421 lines) but **not integrated** with main agent.

#### Submodules

**`agents/` - Agent Implementations**
- `_assistant_agent.py` (1,699 lines) - General assistant
- `_base_chat_agent.py` (674 lines) - Base chat agent
- `_code_executor_agent.py` (881 lines) - Code execution
- `_message_filter_agent.py` (284 lines) - Message filtering
- `_society_of_mind_agent.py` (302 lines) - Meta-reasoning
- `_user_proxy_agent.py` (395 lines) - User proxy

**`base/` - Core Abstractions**
- `_chat_agent.py` - Base chat interface
- `_handoff.py` - Agent handoff logic
- `_task.py` - Task definitions
- `_team.py` - Team coordination
- `_termination.py` - Termination conditions

**`conditions/` - Termination Conditions**
- `_terminations.py` (614 lines) - Various termination strategies

**`teams/` - Team Coordination**
- `_group_chat/_base_group_chat.py` (834 lines) - Base group chat
- `_group_chat/_round_robin_group_chat.py` (328 lines) - Round-robin strategy
- `_group_chat/_selector_group_chat.py` (730 lines) - Selector strategy
- `_group_chat/_swarm_group_chat.py` (321 lines) - Swarm coordination
- `_group_chat/_sequential_routed_agent.py` (246 lines)
- `_group_chat/_graph/_digraph_group_chat.py` (877 lines) - Graph-based routing
- `_magentic_one/` - Advanced orchestration (1,033 lines total)

**`messages.py`** (693 lines) - Message handling with streaming

**Features:**
- Full streaming support (`run_stream()` methods)
- Multiple coordination strategies
- Advanced orchestration (MagenticOne)
- Graph-based agent routing
- Society of Mind architecture

**Integration Opportunity:**
This module could replace significant portions of the main orchestrator and provide much more powerful multi-agent capabilities.

---

## Integration Points

### Current Flow
```
User Input
    ↓
LLMOrchestrator.process()
    ↓
_create_analysis_prompt() → _query_llm()
    ↓
_parse_execution_plan()
    ↓
ExecutionEngine.execute() → ToolRegistry.execute_tool()
    ↓
_synthesize_response()
    ↓
MemorySystem.add_interaction()
```

### Dependencies
- `llm_orchestrator_fixed.py` → `tool_registry.py`, `execution_engine.py`, `memory_system.py`
- `execution_engine.py` → `tool_registry.py`
- All components inject dependencies at runtime

---

## Current Issues & Improvements Needed

### High Priority
1. **Remove mock responses** from LLMOrchestrator
2. **Add streaming support** to main process() method
3. **Integrate AutoGen chat** module with main agent
4. **Wire up MCP** in ToolRegistry.add_mcp_tools()

### Medium Priority
5. **Consolidate message structures** (tool_message.py vs autogen_chat/messages.py)
6. **Improve Ollama querying** (current subprocess approach is fragile)
7. **Add retry logic** for API calls
8. **Implement semantic search** in MemorySystem.get_relevant_context()

### Low Priority
9. **Add type hints** throughout
10. **Improve error messages**
11. **Add performance monitoring**
12. **Expand test coverage**

---

## Testing

**Test File:** `../test_debug.py`

Tests include:
- Execution plan parsing
- Tool schema generation
- Tool execution
- Full agent flow

**Run tests:**
```bash
python test_debug.py
```

---

## Development Guidelines

### Adding a New Tool

1. **Define Tool Class:**
```python
class MyTool(BaseTool):
    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="my_tool",
            description="What this tool does",
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Parameter description"
                )
            ]
        )

    async def execute(self, **kwargs) -> Any:
        self.validate_parameters(**kwargs)
        # Tool logic here
        return {"result": "value"}
```

2. **Register Tool:**
```python
# In ToolRegistry._initialize_default_tools()
self.register_tool(MyTool())
```

### Adding a New Model Provider

1. Add to `ModelProvider` enum
2. Implement `_query_<provider>()` method
3. Add to `_initialize_models()`
4. Add API key loading in `_load_api_keys()`

---

## Dependencies

### Required
- `aiohttp` - Async HTTP (for API calls)
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `duckduckgo-search` - Web search

### Optional
- Ollama - Local LLM runtime (auto-detected)

---

## Performance Considerations

### Bottlenecks
1. **Ollama subprocess calls** - Each query spawns shell process
2. **No response caching** - Repeated queries re-execute
3. **Sequential step execution** - No parallelization
4. **Memory loading** - Loads entire history on each context retrieval

### Optimization Opportunities
1. Use Ollama's Python library instead of subprocess
2. Add LRU cache for similar queries
3. Execute independent steps in parallel
4. Implement sliding window for memory

---

## Security

### Current Protections
- Path traversal prevention in FileSystemTool
- Command whitelist in ShellTool
- Sandboxed Python execution
- API key environment variable loading

### Additional Protections Needed
- Rate limiting for API calls
- Resource limits for tool execution
- Audit logging for all tool calls
- Input sanitization for LLM prompts

---

## Version History

- v1.0 - Initial implementation
- v2.0 - Fixed orchestrator, improved parsing, security hardening
- v2.1 - Current (needs streaming, tool integration, AutoGen integration)
