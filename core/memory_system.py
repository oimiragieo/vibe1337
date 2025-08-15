"""
VIBE1337 Memory System
Stores context, conversations, and learned patterns
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque
import pickle
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
        self.memory_file = Path(self.config.get("memory_file", "vibe1337_memory.pkl"))
        
        # Load existing memory if available
        self.load_memory()
    
    async def get_context(self, limit: int = 10) -> Dict[str, Any]:
        """Get relevant context for LLM"""
        return {
            "recent_interactions": list(self.short_term)[-limit:],
            "conversation_summary": self._summarize_conversation(),
            "learned_patterns": list(self.learned_patterns.keys())[:10],
            "total_interactions": len(self.conversation_history)
        }
    
    async def add_interaction(self, user_input: str, response: Any):
        """Add an interaction to memory"""
        memory_item = MemoryItem(
            timestamp=time.time(),
            type="conversation",
            content={
                "user": user_input,
                "assistant": response
            }
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
            content={
                "tool": tool_name,
                "parameters": parameters,
                "result": result
            }
        )
        self.short_term.append(memory_item)
    
    def learn_pattern(self, pattern_key: str, pattern_data: Any):
        """Store a learned pattern"""
        self.learned_patterns[pattern_key] = {
            "data": pattern_data,
            "timestamp": time.time(),
            "usage_count": 0
        }
    
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
        """Save memory to disk"""
        try:
            memory_data = {
                "conversation_history": self.conversation_history,
                "learned_patterns": self.learned_patterns,
                "timestamp": time.time()
            }
            
            with open(self.memory_file, 'wb') as f:
                pickle.dump(memory_data, f)
                
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load_memory(self):
        """Load memory from disk"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'rb') as f:
                    memory_data = pickle.load(f)
                    
                self.conversation_history = memory_data.get("conversation_history", [])
                self.learned_patterns = memory_data.get("learned_patterns", {})
                
                # Populate short-term from recent history
                for item in self.conversation_history[-100:]:
                    self.short_term.append(item)
                    
        except Exception as e:
            print(f"Error loading memory: {e}")
    
    def clear(self):
        """Clear all memory"""
        self.short_term.clear()
        self.long_term.clear()
        self.conversation_history.clear()
        self.learned_patterns.clear()