from typing import List, Dict, Any
from datetime import datetime
from collections import deque

class ConversationMemory:
    def __init__(self, max_history: int = 10):
        self.history = deque(maxlen=max_history)
        self.context = {}
    
    def add(self, user_message: str, assistant_response: str, metadata: Dict = None):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response,
            "metadata": metadata or {}
        })
    
    def get_context(self) -> str:
        if not self.history:
            return ""
        
        context = []
        for entry in self.history:
            context.append(f"User: {entry['user']}")
            context.append(f"Assistant: {entry['assistant']}")
        
        return "\n".join(context[-6:])  # Last 3 exchanges
    
    def clear(self):
        self.history.clear()
        self.context.clear()

# Global memory store (temporary - use Redis for production)
memory_store = {}

def get_memory(session_id: str) -> ConversationMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationMemory()
    return memory_store[session_id]