"""
VIBE1337 - The Ultimate AI Agent
A TRUE agent where LLM drives all decisions
Built from the best of all frameworks
"""

import asyncio
import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from core.agent_service import AgentService
from core.llm_orchestrator_fixed import ToolCall

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class VIBE1337Agent:
    """
    The Ultimate AI Agent - VIBE1337

    This is a REAL agent where:
    - LLM analyzes and decides what tools to use
    - LLM creates execution plans
    - LLM evaluates results and adjusts
    - NOT hardcoded patterns or regex!
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize VIBE1337"""
        self.config = config or {}

        print(
            """
================================================================

  ##   ##  ####  #####   #####   ##  #####  #####  #######
  ##   ##   ##   ##  ##  ##     ###  ##  ## ##  ##     ##
  ##   ##   ##   #####   ####    ##   ####   ####      ##
   ## ##    ##   ##  ##  ##      ##    ##     ##      ##
    ###    ####  #####   #####  ####  ####   ####     ##

           The Ultimate AI Agent - Path to Singularity
================================================================
        """
        )

        # Initialize unified agent service
        self.agent = AgentService(self.config)

        # Keep references for compatibility
        self.tool_registry = self.agent.tool_registry
        self.memory = self.agent.memory
        self.execution_engine = self.agent.execution_engine
        self.orchestrator = self.agent.orchestrator

        print("\n[+] VIBE1337 Initialized")
        print(f"[+] Available Models: {len(self.orchestrator.models)}")
        print(f"[+] Available Tools: {len(self.tool_registry.tools)}")
        print(f"[+] Streaming: {'Enabled' if self.config.get('streaming', True) else 'Disabled'}")
        print("[+] Ready for singularity...\n")

    async def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input - the RIGHT way
        LLM decides everything!
        """
        logger.info(f"Processing: {user_input}")

        # Special commands
        if user_input.lower() == "exit":
            return {"response": "Goodbye! Shutting down VIBE1337...", "exit": True}

        if user_input.lower() == "help":
            return {"response": self._get_help_text()}

        # Check for special triggers
        if "@ARENA" in user_input:
            # Multi-model consensus
            query = user_input.replace("@ARENA", "").strip()
            response = await self.orchestrator.arena_consensus(query)
            return {"response": response, "type": "arena"}

        if "@WEB" in user_input:
            # Force web search
            query = user_input.replace("@WEB", "").strip()
            tool_call = ToolCall(
                tool_name="web_search",
                parameters={"query": query, "max_results": 5},
                reasoning="User requested web search",
            )
            result = await self.execution_engine.execute(tool_call)

            # Let LLM synthesize the results
            synthesis_prompt = f"Summarize these web search results for '{query}': {json.dumps(result)}"
            response = await self.orchestrator._query_llm("primary", synthesis_prompt)
            return {"response": response, "type": "web_search"}

        # Normal processing - Use streaming if enabled
        if self.config.get("streaming", True):
            # Collect streaming response
            full_response = ""
            final_result = None

            async for chunk in self.agent.process_streaming(user_input):
                chunk_type = chunk.get("type")

                if chunk_type == "chunk":
                    # Print streaming chunks in real-time
                    content = chunk.get("content", "")
                    print(content, end="", flush=True)
                    full_response += content
                elif chunk_type == "end":
                    final_result = chunk
                    if not full_response:
                        # No streaming chunks, use final content
                        full_response = chunk.get("content", "")

            print()  # Newline after streaming

            return final_result or {"response": full_response}
        else:
            # Non-streaming mode
            result = await self.agent.process(user_input)
            return result

    def _get_help_text(self) -> str:
        """Get help text"""
        return """
VIBE1337 Commands:
==================
- Regular conversation: Just type normally
- @ARENA <query>: Get consensus from multiple models
- @WEB <query>: Search the web
- help: Show this help
- exit: Quit

Available Tools:
- filesystem: Read, write, list files
- shell: Execute shell commands
- web_search: Search the internet
- python_executor: Run Python code

The AI will automatically decide when to use tools based on your request.
No need to specify - just ask naturally!
"""

    async def run_interactive(self):
        """Run interactive CLI mode"""
        print("VIBE1337 Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Process input
                result = await self.process(user_input)

                # Check for exit
                if result.get("exit"):
                    print("\n" + result["response"])
                    break

                # Display response (if not already streamed)
                if not self.config.get("streaming", True):
                    response = result.get("response", "No response generated")

                    # Format based on type
                    if isinstance(response, dict):
                        # If response is still a dict, format it nicely
                        response = json.dumps(response, indent=2)

                    print(f"\nVIBE1337: {response}\n")
                else:
                    # Response was already streamed, just add newline
                    print()

                # Show execution details if in debug mode
                if self.config.get("debug"):
                    if "plan" in result:
                        print(f"[DEBUG] Execution plan: {result['plan']}")
                    if "execution_results" in result:
                        print(f"[DEBUG] Results: {result['execution_results']}")

            except KeyboardInterrupt:
                print("\n[Interrupted]")
                continue
            except Exception as e:
                print(f"\n[Error: {e}]\n")
                if self.config.get("debug"):
                    import traceback

                    traceback.print_exc()

    def run(self):
        """Main entry point"""
        # Create event loop and run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.run_interactive())
        finally:
            # Shutdown agent service (saves memory)
            self.agent.shutdown()
            loop.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="VIBE1337 - The Ultimate AI Agent")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--model", type=str, help="Primary model to use")
    parser.add_argument("--memory-file", type=str, help="Memory file path")
    parser.add_argument("--no-streaming", action="store_true", help="Disable streaming responses")

    args = parser.parse_args()

    # Create config
    config = {
        "debug": args.debug,
        "streaming": not args.no_streaming,  # Default to streaming enabled
        "memory": {}
    }

    if args.model:
        config["primary_model"] = args.model

    if args.memory_file:
        config["memory"]["memory_file"] = args.memory_file

    # Create and run agent
    agent = VIBE1337Agent(config)
    agent.run()


if __name__ == "__main__":
    main()
