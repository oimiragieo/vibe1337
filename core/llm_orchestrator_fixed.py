"""
VIBE1337 - LLM Orchestrator (FIXED)
The BRAIN that drives all decisions - DEBUGGED VERSION
"""

import asyncio
import json
import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ToolCall:
    """Structured tool call from LLM"""
    tool_name: str
    parameters: Dict[str, Any]
    reasoning: str = ""
    confidence: float = 1.0
    
    def to_json(self) -> str:
        return json.dumps({
            "tool": self.tool_name,
            "parameters": self.parameters,
            "reasoning": self.reasoning,
            "confidence": self.confidence
        })


@dataclass
class ExecutionStep:
    """Single step in execution plan"""
    step_id: str
    description: str
    tool_call: Optional[ToolCall] = None
    dependencies: List[str] = field(default_factory=list)
    model: str = "primary"
    prompt: Optional[str] = None
    
    @property
    def requires_tool(self) -> bool:
        return self.tool_call is not None


@dataclass
class ExecutionPlan:
    """Multi-step execution plan created by LLM"""
    goal: str
    steps: List[ExecutionStep]
    expected_outcome: str
    fallback_strategy: Optional[str] = None


class LLMOrchestrator:
    """
    FIXED VERSION - Handles edge cases and Ollama properly
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_path = None
        self.models = self._initialize_models()
        self.tool_registry = None  # Will be injected
        self.memory = None  # Will be injected
        self.execution_engine = None  # Will be injected
        self.api_keys = self._load_api_keys()
        
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize all available models"""
        models = {}
        
        # Check and initialize Ollama
        if self._check_ollama():
            ollama_models = self._get_ollama_models()
            for model in ollama_models:
                models[f"ollama:{model}"] = {
                    "provider": ModelProvider.OLLAMA,
                    "model": model,
                    "local": True
                }
            logger.info(f"Found {len(ollama_models)} Ollama models")
        
        # Cloud models (with API keys)
        if os.getenv("OPENAI_API_KEY"):
            models["openai:gpt-4"] = {
                "provider": ModelProvider.OPENAI,
                "model": "gpt-4-turbo-preview",
                "local": False
            }
        
        if os.getenv("ANTHROPIC_API_KEY"):
            models["anthropic:claude"] = {
                "provider": ModelProvider.ANTHROPIC,
                "model": "claude-3-opus-20240229",
                "local": False
            }
        
        # Check if we have any models
        if not models:
            logger.warning("No LLM models available! Will use mock responses for testing.")
            # Add a mock model for testing
            models["mock:test"] = {
                "provider": "mock",
                "model": "test",
                "local": True
            }
        
        # Set primary model
        if "ollama:qwen2.5:7b" in models:
            primary_key = "ollama:qwen2.5:7b"
        elif "ollama:mistral:7b-instruct-q4_K_M" in models:
            primary_key = "ollama:mistral:7b-instruct-q4_K_M"
        elif models:
            primary_key = list(models.keys())[0]
        else:
            primary_key = "mock:test"
            
        models["primary"] = models.get(primary_key, models.get("mock:test"))
        
        return models
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        ollama_paths = [
            os.path.expanduser("~/AppData/Local/Programs/Ollama/ollama.exe"),  # Windows user path
            "ollama",  # PATH
            "/usr/local/bin/ollama",  # macOS/Linux
        ]
        
        for path in ollama_paths:
            try:
                result = subprocess.run(
                    [path, "list"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.ollama_path = path
                    logger.info(f"Found Ollama at: {path}")
                    return True
            except:
                continue
        
        logger.warning("Ollama not found")
        return False
    
    def _get_ollama_models(self) -> List[str]:
        """Get available Ollama models"""
        if not self.ollama_path:
            return []
        
        try:
            result = subprocess.run(
                [self.ollama_path, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                models = []
                lines = result.stdout.strip().split('\n')
                
                # Skip header line if present
                start_idx = 1 if lines and "NAME" in lines[0] else 0
                
                for line in lines[start_idx:]:
                    if line.strip():
                        # Extract model name (first column)
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            models.append(model_name)
                
                return models
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
        
        return []
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        }
    
    async def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main processing loop - FIXED VERSION
        """
        try:
            # Get context and available tools
            memory_context = await self.memory.get_context() if self.memory else {}
            available_tools = self.tool_registry.get_schemas() if self.tool_registry else []
            
            # Step 1: LLM analyzes intent and creates plan
            analysis_prompt = self._create_analysis_prompt(user_input, memory_context, available_tools)
            analysis = await self._query_llm("primary", analysis_prompt)
            
            # Step 2: Parse LLM's execution plan
            plan = self._parse_execution_plan(analysis, user_input)
            
            # Step 3: Execute plan
            results = []
            for step in plan.steps:
                logger.info(f"Executing step: {step.description}")
                
                if step.requires_tool:
                    # Execute tool call
                    result = await self._execute_tool_call(step.tool_call)
                    results.append(result)
                else:
                    # Pure LLM response
                    response = await self._query_llm(step.model or "primary", step.prompt or user_input)
                    results.append({"response": response})
            
            # Step 4: Synthesize final response
            if results:
                final_response = await self._synthesize_response(user_input, plan, results)
            else:
                final_response = "I understand your request. How can I help you further?"
            
            # Step 5: Update memory
            if self.memory:
                await self.memory.add_interaction(user_input, final_response)
            
            return {
                "response": final_response,
                "plan": plan,
                "execution_results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {
                "response": f"I encountered an error: {str(e)}. Let me try a different approach.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_analysis_prompt(self, user_input: str, context: Dict, tools: List) -> str:
        """Create prompt for LLM to analyze and plan"""
        # Simplified prompt that's more likely to get valid JSON
        tools_summary = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in tools[:5]])
        
        return f"""Analyze this request and create a plan.

User Request: {user_input}

Available Tools:
{tools_summary}

Respond with a JSON plan:
{{
    "goal": "what to achieve",
    "plan": [
        {{
            "step_id": "1",
            "description": "what this step does",
            "tool_call": {{
                "tool_name": "tool_name_here",
                "parameters": {{"param": "value"}}
            }}
        }}
    ],
    "expected_outcome": "what success looks like"
}}

If no tools needed, omit tool_call. Keep it simple."""
    
    def _parse_execution_plan(self, llm_response: str, user_input: str) -> ExecutionPlan:
        """Parse LLM's response into execution plan - FIXED"""
        try:
            # Try to extract JSON
            json_str = llm_response
            
            # Look for JSON markers
            if "```json" in llm_response:
                json_str = llm_response.split("```json")[1].split("```")[0]
            elif "```" in llm_response:
                json_str = llm_response.split("```")[1].split("```")[0]
            elif "{" in llm_response:
                # Try to find JSON object
                start = llm_response.find("{")
                end = llm_response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = llm_response[start:end]
            
            data = json.loads(json_str.strip())
            
            steps = []
            for i, step_data in enumerate(data.get("plan", [])):
                tool_call = None
                if "tool_call" in step_data and step_data["tool_call"]:
                    tc = step_data["tool_call"]
                    tool_call = ToolCall(
                        tool_name=tc.get("tool_name", ""),
                        parameters=tc.get("parameters", {}),
                        reasoning=tc.get("reasoning", "")
                    )
                
                step = ExecutionStep(
                    step_id=step_data.get("step_id", str(i+1)),
                    description=step_data.get("description", "Execute step"),
                    tool_call=tool_call,
                    dependencies=step_data.get("dependencies", []),
                    prompt=step_data.get("prompt")
                )
                steps.append(step)
            
            return ExecutionPlan(
                goal=data.get("goal", "Process user request"),
                steps=steps if steps else [ExecutionStep(
                    step_id="1",
                    description="Respond directly",
                    prompt=user_input
                )],
                expected_outcome=data.get("expected_outcome", "User satisfied")
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse plan, using fallback: {e}")
            # Fallback plan
            return ExecutionPlan(
                goal="Respond to user",
                steps=[ExecutionStep(
                    step_id="1",
                    description="Direct response",
                    prompt=user_input,
                    model="primary"
                )],
                expected_outcome="User question answered"
            )
    
    async def _execute_tool_call(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call"""
        if self.execution_engine:
            return await self.execution_engine.execute(tool_call)
        else:
            return {"error": "No execution engine available"}
    
    async def _synthesize_response(self, user_input: str, plan: ExecutionPlan, results: List[Any]) -> str:
        """Synthesize final response from results"""
        if not results:
            return "I processed your request but got no results."
        
        # Simple synthesis for now
        if len(results) == 1 and isinstance(results[0], dict):
            if "response" in results[0]:
                return results[0]["response"]
            elif "output" in results[0]:
                return json.dumps(results[0]["output"], indent=2)
            else:
                return json.dumps(results[0], indent=2)
        
        # Multiple results
        response_parts = []
        for i, result in enumerate(results):
            if isinstance(result, dict):
                if "response" in result:
                    response_parts.append(result["response"])
                elif "output" in result:
                    response_parts.append(f"Step {i+1}: {json.dumps(result['output'])}")
                else:
                    response_parts.append(f"Step {i+1}: {json.dumps(result)}")
            else:
                response_parts.append(str(result))
        
        return "\n".join(response_parts)
    
    async def _query_llm(self, model_key: str, prompt: str) -> str:
        """Query an LLM model - FIXED"""
        if not self.models:
            return "No models available. Please install Ollama or set API keys."
        
        model_info = self.models.get(model_key, self.models.get("primary"))
        
        if model_info["provider"] == "mock":
            return self._mock_response(prompt)
        elif model_info["provider"] == ModelProvider.OLLAMA:
            return await self._query_ollama_fixed(model_info["model"], prompt)
        elif model_info["provider"] == ModelProvider.OPENAI:
            return await self._query_openai(model_info["model"], prompt)
        else:
            return "Model provider not implemented"
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response for testing"""
        if "list" in prompt.lower() and "file" in prompt.lower():
            return json.dumps({
                "goal": "List files",
                "plan": [{
                    "step_id": "1",
                    "description": "List files in directory",
                    "tool_call": {
                        "tool_name": "filesystem",
                        "parameters": {"operation": "list", "path": "."}
                    }
                }],
                "expected_outcome": "Files listed"
            })
        else:
            return json.dumps({
                "goal": "Respond",
                "plan": [{
                    "step_id": "1",
                    "description": "Direct response",
                    "prompt": prompt
                }],
                "expected_outcome": "Response provided"
            })
    
    async def _query_ollama_fixed(self, model: str, prompt: str) -> str:
        """Query Ollama model - FIXED to not hang"""
        if not self.ollama_path:
            return "Ollama not available"
        
        try:
            # Write prompt to temp file to avoid encoding issues
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name
            
            try:
                # Use a non-interactive approach
                cmd = [self.ollama_path, "run", model, f"< {prompt_file}"]
                
                # Alternative: use echo to pipe input
                if os.name == 'nt':  # Windows
                    full_cmd = f'echo {json.dumps(prompt)} | "{self.ollama_path}" run {model}'
                else:
                    full_cmd = f'echo {json.dumps(prompt)} | {self.ollama_path} run {model}'
                
                result = subprocess.run(
                    full_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()
                else:
                    return f"Ollama error: {result.stderr if result.stderr else 'No response'}"
                    
            finally:
                # Clean up temp file
                if os.path.exists(prompt_file):
                    os.remove(prompt_file)
                    
        except subprocess.TimeoutExpired:
            return "Ollama query timed out (30s limit)"
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return f"Error: {str(e)}"
    
    async def _query_openai(self, model: str, prompt: str) -> str:
        """Query OpenAI model"""
        # Implementation remains the same
        return "OpenAI not implemented in this debug version"
    
    async def arena_consensus(self, query: str, models: Optional[List[str]] = None) -> str:
        """@ARENA - Get consensus from multiple models"""
        if not models:
            models = [k for k in self.models.keys() if k != "primary" and k != "mock:test"][:3]
        
        if len(models) < 2:
            return await self._query_llm("primary", query)
        
        responses = []
        for model in models:
            response = await self._query_llm(model, query)
            responses.append(response)
        
        # Simple consensus
        return f"Consensus from {len(models)} models:\n" + "\n---\n".join(responses)