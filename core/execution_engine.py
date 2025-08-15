"""
VIBE1337 Execution Engine
Safely executes tool calls from LLM decisions
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import traceback

from .tool_registry import ToolRegistry
from .llm_orchestrator_fixed import ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result from tool execution"""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""
    parameters: Dict[str, Any] = None


class ExecutionEngine:
    """
    Executes tool calls from LLM decisions
    Handles sandboxing, error recovery, and result formatting
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.execution_history = []
        self.max_retries = 3
        
    async def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call from LLM"""
        import time
        start_time = time.time()
        
        try:
            # Log the execution attempt
            logger.info(f"Executing tool: {tool_call.tool_name}")
            logger.debug(f"Parameters: {tool_call.parameters}")
            
            # Execute the tool
            result = await self.tool_registry.execute_tool(
                tool_call.tool_name,
                tool_call.parameters
            )
            
            # Create execution result
            exec_result = ExecutionResult(
                success=not isinstance(result, dict) or "error" not in result,
                output=result,
                execution_time=time.time() - start_time,
                tool_name=tool_call.tool_name,
                parameters=tool_call.parameters
            )
            
            # Store in history
            self.execution_history.append(exec_result)
            
            return {
                "success": exec_result.success,
                "output": exec_result.output,
                "execution_time": exec_result.execution_time,
                "tool": tool_call.tool_name
            }
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            logger.error(traceback.format_exc())
            
            return {
                "success": False,
                "error": str(e),
                "tool": tool_call.tool_name,
                "execution_time": time.time() - start_time
            }
    
    async def execute_parallel(self, tool_calls: List[ToolCall]) -> List[Dict[str, Any]]:
        """Execute multiple tool calls in parallel"""
        tasks = [self.execute(tc) for tc in tool_calls]
        return await asyncio.gather(*tasks)
    
    async def execute_with_retry(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute with automatic retry on failure"""
        for attempt in range(self.max_retries):
            result = await self.execute(tool_call)
            
            if result.get("success"):
                return result
            
            logger.warning(f"Attempt {attempt + 1} failed: {result.get('error')}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return result
    
    def get_history(self, limit: int = 10) -> List[ExecutionResult]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history.clear()