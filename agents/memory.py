import json
import os
from logger import logger
from typing import Dict, Any, List

class MemoryAgent:
    def __init__(self, memory_file="/Users/vartikasrivastava/project/task_memory.json"):
        self.name = "MemoryAgent"
        self.memory_file = memory_file
        self._init_memory()

    def _init_memory(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({"successful_tasks": {}, "preferred_coords": {}}, f)

    def store_success(self, task_description: str, steps: List[Dict[str, Any]]):
        """
        Stores a successful sequence of steps for a task description.
        """
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
            
            # Simple key-based storage (in reality, use embeddings)
            data["successful_tasks"][task_description.lower()] = steps
            
            with open(self.memory_file, "w") as f:
                json.dump(data, f, indent=4)
            
            logger.log_event(self.name, "memory_stored", {"task": task_description})
        except Exception as e:
            logger.log_event(self.name, "memory_failure", {"error": str(e)}, status="error")

    def retrieve_experience(self, task_description: str):
        """
        Attempts to find a similar past task in memory.
        """
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
            
            # Simple exact/substring match
            search_key = task_description.lower()
            for stored_task, steps in data["successful_tasks"].items():
                if stored_task in search_key or search_key in stored_task:
                    logger.log_event(self.name, "memory_retrieved", {"task": stored_task})
                    return steps
            
            return None
        except Exception:
            return None

# Instance for use
memory_agent = MemoryAgent()
