# VIBE1337 Integration Guide

## Overview

This guide explains how to integrate additional tools and capabilities into VIBE1337. The system is designed to be extensible, allowing you to add new tools, LLM providers, and UI implementations.

## Current Integration Status

**✅ Fully Integrated (Ready to Use)**
- 4 core tools: filesystem, shell, web_search, python_executor
- 3 LLM providers: Ollama, OpenAI, Anthropic
- 2 UIs: CLI, Web (both with streaming)
- Persistent memory system
- AgentService unified backend

**⚠️ Available for Integration (Requires Setup)**
- 27 GPTMe tools (requires `pip install gptme`)
- MCP protocol infrastructure (stub implementation only)
- Voice UI (requires full AgentService integration)

**📚 Reference Material (Not Imported)**
- AutoGen multi-agent framework (~15,000 LOC in `core/autogen_chat/`)

This guide explains how to integrate additional tools and capabilities into VIBE1337. The system is designed to be extensible, allowing you to add new tools, LLM providers, and UI implementations.

## Table of Contents

1. [Adding Custom Tools](#adding-custom-tools)
2. [Integrating GPTMe Tools](#integrating-gptme-tools)
3. [Setting up MCP Servers](#setting-up-mcp-servers)
4. [Creating UI Implementations](#creating-ui-implementations)
5. [Adding LLM Providers](#adding-llm-providers)

---

## Adding Custom Tools

### Simple Tool Example

To add a new tool to VIBE1337:

```python
# In core/tool_registry.py or a new file

from core.tool_registry import BaseTool, ToolSchema, ToolParameter

class WeatherTool(BaseTool):
    """Get weather information for a location"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="weather",
            description="Get current weather for a location",
            parameters=[
                ToolParameter(
                    name="location",
                    type="string",
                    description="City name or location"
                ),
                ToolParameter(
                    name="units",
                    type="string",
                    description="Units (celsius/fahrenheit)",
                    required=False,
                    default="celsius",
                    enum=["celsius", "fahrenheit"]
                )
            ]
        )

    async def execute(self, **kwargs) -> Any:
        """Execute weather query"""
        self.validate_parameters(**kwargs)

        location = kwargs["location"]
        units = kwargs.get("units", "celsius")

        # Your weather API logic here
        # Example using a hypothetical weather API:
        try:
            # import weather_api
            # result = weather_api.get_weather(location, units)
            # return {"temperature": result.temp, "conditions": result.conditions}

            # Placeholder for demonstration
            return {
                "location": location,
                "temperature": "22°C" if units == "celsius" else "72°F",
                "conditions": "Partly cloudy"
            }
        except Exception as e:
            return {"error": str(e)}
```

### Registering the Tool

```python
# In core/tool_registry.py, in _initialize_default_tools():

def _initialize_default_tools(self):
    default_tools = [
        FileSystemTool(),
        ShellTool(),
        WebSearchTool(),
        PythonExecutorTool(),
        WeatherTool(),  # Add your tool here
    ]

    for tool in default_tools:
        self.register_tool(tool)
```

### Testing Your Tool

```python
# Create a test file: tests/test_weather_tool.py

import pytest
from core.tool_registry import ToolRegistry

@pytest.mark.asyncio
async def test_weather_tool():
    registry = ToolRegistry()
    tool = registry.get_tool("weather")

    assert tool is not None

    result = await tool.execute(
        location="San Francisco",
        units="celsius"
    )

    assert "temperature" in result
    assert "conditions" in result
```

---

## Integrating GPTMe Tools

**⚠️ IMPORTANT: GPTMe tools are NOT currently integrated.**

The `tools/gptme_tools/` directory contains 27 advanced tools (6,444 LOC) that are **not functional** without additional setup. All these files have hard dependencies on the `gptme` package which is not installed or included in `requirements.txt`.

### Prerequisites

GPTMe tools require the full `gptme` package and its dependencies:

```bash
# This package is NOT currently installed
pip install gptme

# Note: This may install additional dependencies and could conflict
# with existing packages. Test in a virtual environment first.
```

### Dependencies for Specific Tools

**Browser Tools:**
```bash
pip install playwright
playwright install  # Install browser binaries
```

**Computer Control:**
```bash
pip install pyautogui pillow
```

**Voice:**
```bash
pip install openai-whisper sounddevice
```

**GitHub:**
```bash
# Requires gh CLI tool
# Install from: https://cli.github.com/
```

### Integration Steps

1. **Install Dependencies**

```bash
# Full gptme environment
pip install gptme[all]
```

2. **Create Wrapper Tools**

```python
# In tools/gptme_integration.py

from core.tool_registry import BaseTool, ToolSchema, ToolParameter
from tools.gptme_tools import patch, browser, gh

class GptmePatchTool(BaseTool):
    """Code patching using gptme patch tool"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="code_patch",
            description="Apply code patches and modifications",
            parameters=[
                ToolParameter(
                    name="patch_content",
                    type="string",
                    description="Unified diff patch"
                ),
                ToolParameter(
                    name="target_file",
                    type="string",
                    description="File to patch"
                )
            ]
        )

    async def execute(self, **kwargs):
        from tools.gptme_tools.patch import apply_patch

        try:
            result = await apply_patch(
                kwargs["patch_content"],
                kwargs["target_file"]
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
```

3. **Register Wrapper Tools**

```python
# In core/tool_registry.py

from tools.gptme_integration import GptmePatchTool, GptmeBrowserTool

def _initialize_default_tools(self):
    default_tools = [
        # ... existing tools ...
        GptmePatchTool(),
        GptmeBrowserTool(),
    ]
```

### Available GPTMe Tools Matrix

| Tool | Dependencies | Complexity | Priority |
|------|-------------|------------|----------|
| patch.py | None | Low | High |
| save.py | None | Low | High |
| read.py | None | Low | High |
| gh.py | gh CLI | Low | High |
| shell.py | None | Medium | Medium |
| python.py | IPython | Medium | Medium |
| browser_playwright.py | playwright | High | Medium |
| computer.py | pyautogui | High | Medium |
| screenshot.py | platform-specific | Medium | Low |
| vision.py | Vision API | High | Low |
| tts.py | TTS API | Medium | Low |

---

## Setting up MCP Servers

**⚠️ IMPORTANT: MCP infrastructure is a stub implementation.**

The `tools/mcp/` directory contains infrastructure code but the `add_mcp_tools()` method in `tool_registry.py` is currently empty (stub implementation). MCP server integration requires additional development.

### What is MCP?

Model Context Protocol (MCP) allows VIBE1337 to connect to external tool servers and dynamically load their capabilities.

### Prerequisites

```bash
# These packages are mentioned but not currently installed
pip install fastmcp langroid

# Note: MCP integration requires implementing the add_mcp_tools() method
```

### Creating an MCP Server

```python
# my_mcp_server.py

from fastmcp import FastMCP
from pydantic import BaseModel

app = FastMCP("My Tool Server")

class CalculateInput(BaseModel):
    expression: str

@app.tool()
def calculate(input: CalculateInput) -> str:
    """Evaluate a mathematical expression"""
    try:
        result = eval(input.expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Connecting to MCP Server

```python
# In core/tool_registry.py

def add_mcp_tools(self, mcp_server_url: str):
    """Add tools from an MCP server"""
    from tools.mcp.fastmcp_client import FastMCPClient

    async def load_mcp_tools():
        async with FastMCPClient(mcp_server_url) as client:
            # List available tools
            tools = await client.list_tools()

            for tool_spec in tools:
                # Create wrapper for each MCP tool
                wrapped_tool = self._create_mcp_tool_wrapper(tool_spec, client)
                self.register_tool(wrapped_tool)

    # Run async initialization
    import asyncio
    asyncio.run(load_mcp_tools())

def _create_mcp_tool_wrapper(self, tool_spec, client):
    """Create a BaseTool wrapper for an MCP tool"""
    from core.tool_registry import BaseTool, ToolSchema, ToolParameter

    class MCPToolWrapper(BaseTool):
        def __init__(self, spec, mcp_client):
            self.spec = spec
            self.client = mcp_client
            super().__init__()

        def _build_schema(self):
            # Convert MCP schema to ToolSchema
            params = [
                ToolParameter(
                    name=p.name,
                    type=p.type,
                    description=p.description,
                    required=p.required
                )
                for p in self.spec.parameters
            ]

            return ToolSchema(
                name=self.spec.name,
                description=self.spec.description,
                parameters=params
            )

        async def execute(self, **kwargs):
            # Call MCP server
            result = await self.client.call_tool(self.spec.name, kwargs)
            return result

    return MCPToolWrapper(tool_spec, client)
```

### Using MCP Tools

```python
# In your initialization code

registry = ToolRegistry()
registry.add_mcp_tools("http://localhost:8001")

# Now MCP tools are available
schemas = registry.get_schemas()
```

---

## Creating UI Implementations

### Using AgentService

All UIs should use the unified `AgentService` for consistent behavior:

```python
from core.agent_service import AgentService

# Initialize once
agent = AgentService({
    "debug": False,
    "streaming": True
})

# For streaming responses
async for chunk in agent.process_streaming(user_input):
    chunk_type = chunk.get("type")
    content = chunk.get("content", "")

    if chunk_type == "chunk":
        # Display streaming text
        print(content, end="", flush=True)
    elif chunk_type == "tool_execution":
        # Show tool being used
        print(f"\nUsing tool: {chunk.get('tool_name')}")
    elif chunk_type == "end":
        # Final response
        print("\nComplete!")

# For non-streaming
result = await agent.process(user_input)
print(result["response"])
```

### REST API Example

```python
# api_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from core.agent_service import AgentService

app = FastAPI()
agent = AgentService({})

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    result = await agent.process(request.message)
    return {
        "response": result["response"],
        "tools_used": len(result.get("execution_results", []))
    }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for chunk in agent.process_streaming(request.message):
            yield json.dumps(chunk) + "\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Mobile App Integration

```javascript
// React Native example

const VIBE_API = 'http://localhost:8000';

async function chat(message) {
    const response = await fetch(`${VIBE_API}/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
    });

    const data = await response.json();
    return data.response;
}

// Streaming
async function* chatStream(message) {
    const response = await fetch(`${VIBE_API}/chat/stream`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message})
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(Boolean);

        for (const line of lines) {
            yield JSON.parse(line);
        }
    }
}
```

---

## Adding LLM Providers

### Custom Provider Example

```python
# In core/llm_orchestrator_fixed.py

class ModelProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"  # Add your provider

# In LLMOrchestrator class:

def _initialize_models(self) -> Dict[str, Any]:
    models = {}

    # ... existing providers ...

    # Add custom provider
    if os.getenv("CUSTOM_API_KEY"):
        models["custom:model"] = {
            "provider": ModelProvider.CUSTOM,
            "model": "your-model-name",
            "local": False
        }

    return models

async def _query_custom(self, model: str, prompt: str) -> str:
    """Query custom LLM provider"""
    if not self.api_keys.get("custom"):
        return "Custom API key not found."

    try:
        # Your custom API client code
        from your_llm_sdk import CustomLLM

        client = CustomLLM(api_key=self.api_keys["custom"])

        response = await client.generate(
            model=model,
            prompt=prompt,
            max_tokens=2000
        )

        return response.text

    except Exception as e:
        logger.error(f"Custom API error: {e}")
        return f"Custom API error: {str(e)}"

# In _query_llm method, add:
elif model_info["provider"] == ModelProvider.CUSTOM:
    return await self._query_custom(model_info["model"], prompt)
```

### Streaming Support for Custom Provider

```python
# In core/agent_service.py

async def _query_custom_streaming(self, model: str, prompt: str):
    """Query custom provider with streaming"""
    if not self.orchestrator.api_keys.get("custom"):
        yield "Custom API key not found."
        return

    try:
        from your_llm_sdk import CustomLLM

        client = CustomLLM(api_key=self.orchestrator.api_keys["custom"])

        async for chunk in client.generate_stream(
            model=model,
            prompt=prompt,
            max_tokens=2000
        ):
            yield chunk.text

    except Exception as e:
        yield f"Custom API error: {str(e)}"
```

---

## Testing Integrations

### Unit Tests

```python
# tests/test_integration.py

import pytest
from core.tool_registry import ToolRegistry
from core.agent_service import AgentService

@pytest.mark.asyncio
async def test_custom_tool_integration():
    registry = ToolRegistry()
    # Your custom tool should be registered
    assert "your_tool" in registry.get_tool_names()

    tool = registry.get_tool("your_tool")
    result = await tool.execute(param="value")

    assert result["success"] == True

@pytest.mark.asyncio
async def test_agent_service_with_tools():
    agent = AgentService({})

    result = await agent.process("use my custom tool")

    assert "response" in result
```

### Integration Tests

```python
# tests/test_full_integration.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_integration():
    registry = ToolRegistry()

    # Start test MCP server
    # Add MCP tools
    registry.add_mcp_tools("http://localhost:8001")

    # Test tool is available
    assert "mcp_tool_name" in registry.get_tool_names()

    # Test execution through agent
    agent = AgentService({})
    result = await agent.process("use the MCP tool")

    assert result["success"]
```

---

## Best Practices

### Tool Development

1. **Clear descriptions** - LLM uses these to decide when to use tools
2. **Type validation** - Validate all parameters
3. **Error handling** - Return structured errors
4. **Async-first** - Use async/await throughout
5. **Security** - Sanitize inputs, restrict access
6. **Testing** - Unit test each tool independently

### Performance

1. **Connection pooling** - Reuse HTTP clients
2. **Caching** - Cache frequently used results
3. **Timeouts** - Set appropriate timeouts
4. **Parallel execution** - Run independent tools concurrently
5. **Resource cleanup** - Always cleanup in finally blocks

### Security

1. **Input validation** - Never trust user input
2. **Sandboxing** - Run dangerous tools in containers
3. **Rate limiting** - Prevent abuse
4. **API key rotation** - Regular key rotation
5. **Audit logging** - Log all tool executions

---

## Troubleshooting

### Tool Not Found

```python
# Check tool registration
registry = ToolRegistry()
print(registry.get_tool_names())

# Verify schema format
tool = registry.get_tool("your_tool")
print(tool.schema.to_openai_format())
```

### LLM Not Using Tool

- Check tool description clarity
- Verify parameter types match schema
- Test with explicit tool request
- Review LLM's reasoning in debug mode

### MCP Connection Issues

```python
# Test MCP server directly
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8001/tools")
    print(response.json())
```

### Import Errors

```bash
# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check package installation
pip list | grep vibe1337
```

---

## Support

For additional help:
- Check the [documentation](./claude.md)
- Review [example implementations](./docs/)
- Open an issue on GitHub

---

**Version:** 2.1.0
**Last Updated:** 2025-11-20
