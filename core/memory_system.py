"""
VIBE1337 Memory System
Stores context, conversations, and learned patterns
Uses JSON for secure, human-readable persistence
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from collections import deque
from pathlib import Path


@dataclass
class MemoryItem:
    """Single memory item"""

    timestamp: float
    type: str  # "conversation", "tool_execution", "learning"
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemorySystem:
    """
    Manages agent memory for context and learning
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.short_term = deque(maxlen=100)  # Recent interactions
        self.long_term = []  # Important memories
        self.conversation_history = []
        self.learned_patterns = {}
        # Changed from .pkl to .json for security
        default_file = self.config.get("memory_file", "vibe1337_memory.json")
        # Support legacy .pkl files by converting them
        if default_file.endswith(".pkl"):
            default_file = default_file.replace(".pkl", ".json")
        self.memory_file = Path(default_file)

        # Load existing memory if available
        self.load_memory()

    async def get_context(self, limit: int = 10) -> Dict[str, Any]:
        """Get relevant context for LLM"""
        return {
            "recent_interactions": list(self.short_term)[-limit:],
            "conversation_summary": self._summarize_conversation(),
            "learned_patterns": list(self.learned_patterns.keys())[:10],
            "total_interactions": len(self.conversation_history),
        }

    async def add_interaction(self, user_input: str, response: Any):
        """Add an interaction to memory"""
        memory_item = MemoryItem(
            timestamp=time.time(), type="conversation", content={"user": user_input, "assistant": response}
        )

        self.short_term.append(memory_item)
        self.conversation_history.append(memory_item)

        # Save periodically
        if len(self.conversation_history) % 10 == 0:
            self.save_memory()

    def add_tool_execution(self, tool_name: str, parameters: Dict, result: Any):
        """Record tool execution"""
        memory_item = MemoryItem(
            timestamp=time.time(),
            type="tool_execution",
            content={"tool": tool_name, "parameters": parameters, "result": result},
        )
        self.short_term.append(memory_item)

    def learn_pattern(self, pattern_key: str, pattern_data: Any):
        """Store a learned pattern"""
        self.learned_patterns[pattern_key] = {"data": pattern_data, "timestamp": time.time(), "usage_count": 0}

    def _summarize_conversation(self) -> str:
        """Create a summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation history"

        recent = self.conversation_history[-5:]
        summary = f"Recent {len(recent)} interactions. "

        # Simple summary (could use LLM for better summaries)
        topics = set()
        for item in recent:
            if item.type == "conversation":
                user_msg = item.content.get("user", "")
                # Extract key words (simple approach)
                words = user_msg.lower().split()
                topics.update(w for w in words if len(w) > 4)

        if topics:
            summary += f"Topics: {', '.join(list(topics)[:5])}"

        return summary

    def save_memory(self):
        """Save memory to disk using JSON"""
        try:
            # Convert MemoryItem objects to dicts
            conversation_history_serializable = [
                {"timestamp": item.timestamp, "type": item.type, "content": item.content, "metadata": item.metadata}
                for item in self.conversation_history
            ]

            memory_data = {
                "conversation_history": conversation_history_serializable,
                "learned_patterns": self.learned_patterns,
                "timestamp": time.time(),
                "version": "2.0",  # Track format version
            }

            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving memory: {e}")

    def load_memory(self):
        """Load memory from disk (supports both JSON and legacy pickle)"""
        try:
            # Try loading JSON first
            if self.memory_file.exists():
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)

                # Reconstruct MemoryItem objects from dicts
                conversation_history_raw = memory_data.get("conversation_history", [])
                self.conversation_history = [
                    MemoryItem(
                        timestamp=item.get("timestamp", 0),
                        type=item.get("type", "conversation"),
                        content=item.get("content", {}),
                        metadata=item.get("metadata", {}),
                    )
                    for item in conversation_history_raw
                ]

                self.learned_patterns = memory_data.get("learned_patterns", {})

                # Populate short-term from recent history
                for item in self.conversation_history[-100:]:
                    self.short_term.append(item)

                print(f"Loaded {len(self.conversation_history)} memories from {self.memory_file}")

            # Try legacy pickle file if JSON doesn't exist
            elif Path(str(self.memory_file).replace(".json", ".pkl")).exists():
                legacy_file = Path(str(self.memory_file).replace(".json", ".pkl"))
                print(f"Found legacy pickle file. Converting to JSON...")

                try:
                    import pickle

                    with open(legacy_file, "rb") as f:
                        memory_data = pickle.load(f)

                    self.conversation_history = memory_data.get("conversation_history", [])
                    self.learned_patterns = memory_data.get("learned_patterns", {})

                    # Populate short-term from recent history
                    for item in self.conversation_history[-100:]:
                        self.short_term.append(item)

                    # Save in new JSON format
                    self.save_memory()
                    print(f"Successfully converted {legacy_file} to {self.memory_file}")

                except Exception as e:
                    print(f"Error converting legacy pickle file: {e}")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON memory file: {e}")
        except Exception as e:
            print(f"Error loading memory: {e}")

    def clear(self):
        """Clear all memory"""
        self.short_term.clear()
        self.long_term.clear()
        self.conversation_history.clear()
        self.learned_patterns.clear()
