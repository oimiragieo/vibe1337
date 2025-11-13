"""
VIBE1337 Tool Registry
Unified tool system combining best of all agents
Uses OpenAI function calling format for LLM decisions
"""

import json
import inspect
import logging
from typing import Dict, Any, List, Optional, Type, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ToolParameter:
    """Tool parameter specification (OpenAI format)"""

    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict[str, "ToolParameter"]] = None  # For object types
    items: Optional["ToolParameter"] = None  # For array types


@dataclass
class ToolSchema:
    """OpenAI-compatible tool schema"""

    name: str
    description: str
    parameters: List[ToolParameter]

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        properties = {}
        required = []

        for param in self.parameters:
            prop_def = {"type": param.type, "description": param.description}

            if param.enum:
                prop_def["enum"] = param.enum

            if param.type == "object" and param.properties:
                prop_def["properties"] = {k: v.to_openai_format() for k, v in param.properties.items()}

            if param.type == "array" and param.items:
                prop_def["items"] = param.items.to_openai_format()

            properties[param.name] = prop_def

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": properties, "required": required},
            },
        }


class BaseTool(ABC):
    """Base class for all tools"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.schema = self._build_schema()

    @abstractmethod
    def _build_schema(self) -> ToolSchema:
        """Build the tool schema"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters against schema"""
        for param in self.schema.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Required parameter '{param.name}' missing")

            if param.name in kwargs:
                value = kwargs[param.name]
                # Add type validation here if needed

        return True


class FileSystemTool(BaseTool):
    """File system operations tool"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="filesystem",
            description="Perform file system operations like reading, writing, listing files",
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="Operation to perform",
                    enum=["read", "write", "list", "create_dir", "delete"],
                ),
                ToolParameter(name="path", type="string", description="File or directory path"),
                ToolParameter(name="content", type="string", description="Content for write operation", required=False),
            ],
        )

    async def execute(self, **kwargs) -> Any:
        """Execute file system operation"""
        import os
        from pathlib import Path

        self.validate_parameters(**kwargs)

        operation = kwargs["operation"]
        path = Path(kwargs["path"])

        # Security: Validate path to prevent directory traversal
        try:
            # Resolve to absolute path and check if it's within allowed directory
            resolved_path = path.resolve()
            cwd = Path.cwd().resolve()

            # Ensure path is within current working directory or its subdirectories
            # This prevents access to parent directories via ../
            if not str(resolved_path).startswith(str(cwd)):
                # Allow access to current directory and below
                return {"error": f"Access denied: Path outside working directory"}

            path = resolved_path

        except (OSError, RuntimeError) as e:
            return {"error": f"Invalid path: {str(e)}"}

        if operation == "read":
            if not path.exists():
                return {"error": f"File not found: {path}"}
            # Additional check: don't read sensitive files
            if path.name in [".env", ".git", "id_rsa", "id_dsa", ".ssh"]:
                return {"error": f"Access to {path.name} is restricted"}
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return {"content": f.read()}
            except UnicodeDecodeError:
                return {"error": "File is not a text file"}

        elif operation == "write":
            content = kwargs.get("content", "")
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "message": f"Written to {path}"}

        elif operation == "list":
            if not path.exists():
                return {"error": f"Directory not found: {path}"}
            files = list(path.iterdir()) if path.is_dir() else [path]
            return {"files": [str(f) for f in files]}

        elif operation == "create_dir":
            path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Created directory {path}"}

        elif operation == "delete":
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    import shutil

                    shutil.rmtree(path)
                return {"success": True, "message": f"Deleted {path}"}
            return {"error": f"Path not found: {path}"}


class ShellTool(BaseTool):
    """Shell command execution tool"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="shell",
            description="Execute shell commands",
            parameters=[
                ToolParameter(name="command", type="string", description="Command to execute"),
                ToolParameter(
                    name="timeout", type="number", description="Timeout in seconds", required=False, default=30
                ),
            ],
        )

    async def execute(self, **kwargs) -> Any:
        """Execute shell command"""
        import subprocess
        import shlex

        self.validate_parameters(**kwargs)

        command = kwargs["command"]
        timeout = kwargs.get("timeout", 30)

        # Security check - improved filtering
        # Extract the base command (first word)
        try:
            parts = shlex.split(command)
            if not parts:
                return {"error": "Empty command"}
            base_command = parts[0].lower()
        except ValueError:
            return {"error": "Invalid command syntax"}

        # Whitelist of allowed commands (safe, common utilities)
        allowed_commands = {
            "ls",
            "dir",
            "pwd",
            "echo",
            "cat",
            "head",
            "tail",
            "grep",
            "find",
            "wc",
            "sort",
            "uniq",
            "cut",
            "sed",
            "awk",
            "date",
            "whoami",
            "hostname",
            "uname",
            "env",
            "printenv",
            "python",
            "python3",
            "node",
            "npm",
            "git",
            "pip",
            "pip3",
            "curl",
            "wget",
            "ping",
            "which",
            "whereis",
            "file",
            "stat",
            "df",
            "du",
            "ps",
            "top",
            "mkdir",
            "touch",
            "cp",
            "mv",
        }

        # Blacklist of dangerous patterns (comprehensive)
        dangerous_patterns = [
            "rm -rf /",
            "rm -rf .*",
            "rm -r /",
            "mkfs",
            "dd if=",
            ":(){:|:&};:",  # fork bomb
            "> /dev/sda",
            "> /dev/hda",
            "mv * /dev/null",
            "chmod -R 777 /",
            "chown -R",
            "format",
            "del /f /s /q",
            "shutdown",
            "reboot",
            "halt",
            "poweroff",
            "kill -9 -1",
            "killall -9",
            "wget | sh",
            "curl | sh",
            "curl | bash",
            "/dev/null >&",
            "& disown",
        ]

        # Check if base command is in whitelist
        if base_command not in allowed_commands:
            return {
                "error": f"Command '{base_command}' not in allowed list. "
                f"For security, only whitelisted commands can be executed."
            }

        # Check for dangerous patterns
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return {"error": f"Command blocked: contains dangerous pattern '{pattern}'"}

        # Additional checks
        if "&&" in command or "||" in command or ";" in command:
            return {"error": "Command chaining (&&, ||, ;) is not allowed for security"}

        if "`" in command or "$(" in command:
            return {"error": "Command substitution is not allowed for security"}

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}


class WebSearchTool(BaseTool):
    """Web search tool using DuckDuckGo"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="web_search",
            description="Search the web for information",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query"),
                ToolParameter(
                    name="max_results",
                    type="number",
                    description="Maximum number of results",
                    required=False,
                    default=5,
                ),
            ],
        )

    async def execute(self, **kwargs) -> Any:
        """Execute web search"""
        try:
            from duckduckgo_search import DDGS

            query = kwargs["query"]
            max_results = kwargs.get("max_results", 5)

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return {"results": results}
        except ImportError:
            return {"error": "duckduckgo-search not installed"}
        except Exception as e:
            return {"error": str(e)}


class PythonExecutorTool(BaseTool):
    """Execute Python code in sandboxed environment"""

    def _build_schema(self) -> ToolSchema:
        return ToolSchema(
            name="python_executor",
            description="Execute Python code and return the result",
            parameters=[
                ToolParameter(name="code", type="string", description="Python code to execute"),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Execution timeout in seconds",
                    required=False,
                    default=10,
                ),
            ],
        )

    async def execute(self, **kwargs) -> Any:
        """Execute Python code"""
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr

        code = kwargs["code"]

        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        # Create a restricted globals dict
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            }
        }

        try:
            # Redirect stdout and stderr
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # Execute the code
                exec(code, safe_globals)

            return {"success": True, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
            }


class ToolRegistry:
    """
    Central registry for all tools
    LLM queries this to know what tools are available
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_default_tools()

    def _initialize_default_tools(self):
        """Register default tools"""
        default_tools = [
            FileSystemTool(),
            ShellTool(),
            WebSearchTool(),
            PythonExecutorTool(),
        ]

        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.schema.name] = tool
        logger.info(f"Registered tool: {tool.schema.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas in OpenAI format for LLM"""
        return [tool.schema.to_openai_format() for tool in self.tools.values()]

    def get_tool_names(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool by name with parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}

        try:
            return await tool.execute(**parameters)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": str(e)}

    def add_mcp_tools(self, mcp_server_path: str):
        """Add tools from an MCP server"""
        # This will integrate with the MCP implementation we copied
        pass
