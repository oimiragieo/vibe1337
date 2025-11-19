"""
VIBE1337 Agent Service
Unified interface for all UI implementations (CLI, Web, Voice)
Provides both streaming and non-streaming modes
"""

import asyncio
import logging
from typing import Dict, Any, AsyncGenerator, Optional, Callable
from datetime import datetime

from .llm_orchestrator_fixed import LLMOrchestrator, ToolCall, ExecutionPlan
from .tool_registry import ToolRegistry
from .execution_engine import ExecutionEngine
from .memory_system import MemorySystem

logger = logging.getLogger(__name__)


class AgentService:
    """
    Unified agent service that provides streaming and non-streaming interfaces.

    This service wraps the core agent components and provides:
    - Streaming responses for real-time UIs
    - Standard responses for simple interactions
    - Consistent tool access across all UIs
    - Shared memory and context
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the agent service with all core components"""
        self.config = config or {}

        # Initialize core components
        self.tool_registry = ToolRegistry()
        self.memory = MemorySystem(self.config.get("memory", {}))
        self.execution_engine = ExecutionEngine(self.tool_registry)
        self.orchestrator = LLMOrchestrator(self.config)

        # Wire dependencies
        self.orchestrator.tool_registry = self.tool_registry
        self.orchestrator.memory = self.memory
        self.orchestrator.execution_engine = self.execution_engine

        logger.info(f"AgentService initialized with {len(self.tool_registry.tools)} tools")

    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user input and return complete response.

        Args:
            user_input: The user's input text
            context: Optional context dictionary

        Returns:
            Dictionary with response, plan, execution results, etc.
        """
        return await self.orchestrator.process(user_input, context)

    async def process_streaming(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process user input with streaming response.

        Yields chunks of the response as they're generated, along with
        metadata about execution progress.

        Args:
            user_input: The user's input text
            context: Optional context dictionary

        Yields:
            Dictionaries with:
            - type: 'start' | 'planning' | 'tool_execution' | 'chunk' | 'end'
            - content: The content (varies by type)
            - metadata: Additional information
        """
        try:
            # Signal start
            yield {
                "type": "start",
                "content": "",
                "timestamp": datetime.now().isoformat()
            }

            # Get context and available tools
            memory_context = await self.memory.get_context() if self.memory else {}
            available_tools = self.tool_registry.get_schemas() if self.tool_registry else []

            # Phase 1: Planning
            yield {
                "type": "planning",
                "content": "Analyzing request and creating execution plan...",
                "timestamp": datetime.now().isoformat()
            }

            # Create analysis prompt
            analysis_prompt = self.orchestrator._create_analysis_prompt(
                user_input, memory_context, available_tools
            )

            # Query LLM for plan (streaming)
            plan_text = ""
            async for chunk in self._query_llm_streaming("primary", analysis_prompt):
                plan_text += chunk
                yield {
                    "type": "planning_chunk",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                }

            # Parse execution plan
            plan = self.orchestrator._parse_execution_plan(plan_text, user_input)

            yield {
                "type": "plan_ready",
                "content": f"Plan created with {len(plan.steps)} steps",
                "plan": {
                    "goal": plan.goal,
                    "steps": len(plan.steps),
                    "expected_outcome": plan.expected_outcome
                },
                "timestamp": datetime.now().isoformat()
            }

            # Phase 2: Execution
            results = []
            for i, step in enumerate(plan.steps):
                yield {
                    "type": "step_start",
                    "content": f"Step {i+1}/{len(plan.steps)}: {step.description}",
                    "step": i+1,
                    "total_steps": len(plan.steps),
                    "timestamp": datetime.now().isoformat()
                }

                if step.requires_tool:
                    # Execute tool
                    yield {
                        "type": "tool_execution",
                        "content": f"Executing tool: {step.tool_call.tool_name}",
                        "tool_name": step.tool_call.tool_name,
                        "parameters": step.tool_call.parameters,
                        "timestamp": datetime.now().isoformat()
                    }

                    result = await self.orchestrator._execute_tool_call(step.tool_call)
                    results.append(result)

                    yield {
                        "type": "tool_result",
                        "content": "Tool execution completed",
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Pure LLM response - stream it
                    response_text = ""
                    prompt = step.prompt or user_input

                    async for chunk in self._query_llm_streaming(step.model or "primary", prompt):
                        response_text += chunk
                        yield {
                            "type": "chunk",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat()
                        }

                    results.append({"response": response_text})

            # Phase 3: Synthesis
            if results:
                yield {
                    "type": "synthesizing",
                    "content": "Synthesizing final response...",
                    "timestamp": datetime.now().isoformat()
                }

                final_response = await self.orchestrator._synthesize_response(
                    user_input, plan, results
                )
            else:
                final_response = "I understand your request. How can I help you further?"

            # Update memory
            if self.memory:
                await self.memory.add_interaction(user_input, final_response)

            # Send final response
            yield {
                "type": "end",
                "content": final_response,
                "plan": plan,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Streaming processing error: {e}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _query_llm_streaming(self, model_key: str, prompt: str) -> AsyncGenerator[str, None]:
        """
        Query LLM with streaming response.

        Yields:
            String chunks of the response
        """
        model_info = self.orchestrator.models.get(
            model_key,
            self.orchestrator.models.get("primary")
        )

        if not model_info:
            yield "No models available."
            return

        provider = model_info.get("provider")

        # For now, only implement streaming for OpenAI and Anthropic
        # Ollama streaming would require different implementation

        if provider == "openai" or (hasattr(provider, "value") and provider.value == "openai"):
            async for chunk in self._query_openai_streaming(model_info["model"], prompt):
                yield chunk
        elif provider == "anthropic" or (hasattr(provider, "value") and provider.value == "anthropic"):
            async for chunk in self._query_anthropic_streaming(model_info["model"], prompt):
                yield chunk
        else:
            # Fallback to non-streaming for other providers
            response = await self.orchestrator._query_llm(model_key, prompt)
            yield response

    async def _query_openai_streaming(self, model: str, prompt: str) -> AsyncGenerator[str, None]:
        """Query OpenAI with streaming"""
        if not self.orchestrator.api_keys.get("openai"):
            yield "OpenAI API key not found."
            return

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.orchestrator.api_keys["openai"])

            stream = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except ImportError:
            yield "OpenAI library not installed."
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield f"OpenAI error: {str(e)}"

    async def _query_anthropic_streaming(self, model: str, prompt: str) -> AsyncGenerator[str, None]:
        """Query Anthropic with streaming"""
        if not self.orchestrator.api_keys.get("anthropic"):
            yield "Anthropic API key not found."
            return

        try:
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=self.orchestrator.api_keys["anthropic"])

            async with client.messages.stream(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except ImportError:
            yield "Anthropic library not installed."
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            yield f"Anthropic error: {str(e)}"

    def get_available_tools(self) -> list:
        """Get list of available tool names"""
        return self.tool_registry.get_tool_names()

    def get_tool_schemas(self) -> list:
        """Get all tool schemas in OpenAI format"""
        return self.tool_registry.get_schemas()

    def get_memory_stats(self) -> dict:
        """Get memory system statistics"""
        return self.memory.get_stats() if self.memory else {}

    async def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear_memory()

    def shutdown(self):
        """Shutdown the agent service and save state"""
        if self.memory:
            self.memory.save_memory()
        logger.info("AgentService shutdown complete")
