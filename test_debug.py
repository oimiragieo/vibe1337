#!/usr/bin/env python
"""
Debug test for VIBE1337
Tests the logic flow without requiring Ollama
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.llm_orchestrator_fixed import LLMOrchestrator, ToolCall, ExecutionPlan, ExecutionStep
from core.tool_registry import ToolRegistry
from core.execution_engine import ExecutionEngine
from core.memory_system import MemorySystem


async def test_parsing():
    """Test parsing of execution plans"""
    print("=" * 60)
    print("Testing Execution Plan Parsing")
    print("=" * 60)

    orchestrator = LLMOrchestrator({})

    # Test valid JSON
    valid_json = """
    ```json
    {
        "goal": "List files in directory",
        "plan": [
            {
                "step_id": "1",
                "description": "List files",
                "tool_call": {
                    "tool_name": "filesystem",
                    "parameters": {"operation": "list", "path": "."}
                }
            }
        ],
        "expected_outcome": "Files listed"
    }
    ```
    """

    plan = orchestrator._parse_execution_plan(valid_json, "list files")
    print(f"\nParsed plan goal: {plan.goal}")
    print(f"Steps: {len(plan.steps)}")
    if plan.steps:
        print(f"First step: {plan.steps[0].description}")
        if plan.steps[0].tool_call:
            print(f"Tool: {plan.steps[0].tool_call.tool_name}")
            print(f"Params: {plan.steps[0].tool_call.parameters}")

    # Test invalid JSON (should fallback)
    invalid_json = "This is not JSON at all"
    plan2 = orchestrator._parse_execution_plan(invalid_json, "test fallback")
    print(f"\nFallback plan goal: {plan2.goal}")
    print(f"Steps: {len(plan2.steps)}")

    print("\n[OK] Parsing tests completed")


async def test_tool_execution():
    """Test tool execution flow"""
    print("\n" + "=" * 60)
    print("Testing Tool Execution")
    print("=" * 60)

    # Setup components
    registry = ToolRegistry()
    engine = ExecutionEngine(registry)

    # Test filesystem tool
    tool_call = ToolCall(
        tool_name="filesystem", parameters={"operation": "list", "path": "."}, reasoning="User wants to list files"
    )

    print(f"\nExecuting tool: {tool_call.tool_name}")
    print(f"Parameters: {tool_call.parameters}")

    result = await engine.execute(tool_call)

    print(f"Success: {result.get('success')}")
    if result.get("success"):
        output = result.get("output")
        if isinstance(output, dict) and "files" in output:
            files = output["files"]
            print(f"Found {len(files)} files")
            print(f"First 5: {files[:5]}")
    else:
        print(f"Error: {result.get('error')}")

    print("\n[OK] Tool execution test completed")


async def test_full_flow():
    """Test the complete flow"""
    print("\n" + "=" * 60)
    print("Testing Full Agent Flow")
    print("=" * 60)

    # Create all components
    config = {"debug": True}

    registry = ToolRegistry()
    memory = MemorySystem()
    engine = ExecutionEngine(registry)
    orchestrator = LLMOrchestrator(config)

    # Inject dependencies
    orchestrator.tool_registry = registry
    orchestrator.memory = memory
    orchestrator.execution_engine = engine

    # Test a simple query
    user_input = "list files in current directory"

    print(f"\nUser input: {user_input}")
    print("Processing...")

    result = await orchestrator.process(user_input)

    print(f"\nResponse: {result.get('response', 'No response')[:200]}")

    if "plan" in result and result["plan"]:
        plan = result["plan"]
        print(f"\nExecution plan:")
        print(f"  Goal: {plan.goal}")
        print(f"  Steps: {len(plan.steps)}")

    print("\n[OK] Full flow test completed")


async def test_tool_schemas():
    """Test tool schema generation"""
    print("\n" + "=" * 60)
    print("Testing Tool Schemas")
    print("=" * 60)

    registry = ToolRegistry()
    schemas = registry.get_schemas()

    print(f"\nFound {len(schemas)} tools:")
    for schema in schemas:
        func = schema.get("function", {})
        print(f"\n- {func.get('name')}:")
        print(f"  Description: {func.get('description')}")
        params = func.get("parameters", {})
        props = params.get("properties", {})
        print(f"  Parameters: {list(props.keys())}")

    print("\n[OK] Schema test completed")


async def main():
    """Run all tests"""
    print("\nVIBE1337 DEBUG TEST SUITE")
    print("=" * 60)

    try:
        await test_parsing()
        await test_tool_schemas()
        await test_tool_execution()
        await test_full_flow()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
