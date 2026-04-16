from logger import logger
from typing import List, Dict, Any

class PlanningAgent:
    def __init__(self):
        self.name = "PlanningAgent"

    def create_plan(self, task_description: str) -> List[Dict[str, Any]]:
        """
        In a production environment, this would call an LLM (like GPT-4 or Gemini)
        to decompose a natural language request into a sequence of atomic steps.
        """
        logger.log_event(self.name, "planning_start", {"description": task_description})
        
        # Simplified Mock Logic: In a real app, this is an LLM call.
        # We'll return a structured plan based on keywords for demonstration.
        plan = []
        desc = task_description.lower()

        if "google" in desc or "search" in desc:
            plan = [
                {"type": "hotkey", "params": {"keys": ["command", "space"]}, "goal": "Open Spotlight"},
                {"type": "type", "params": {"text": "Chrome"}, "goal": "Type Chrome"},
                {"type": "hotkey", "params": {"keys": ["enter"]}, "goal": "Launch Chrome"},
                {"type": "type", "params": {"text": "https://google.com"}, "goal": "Go to Google"},
                {"type": "hotkey", "params": {"keys": ["enter"]}, "goal": "Confirm URL"}
            ]
        elif "notepad" in desc or "text" in desc:
            plan = [
                {"type": "hotkey", "params": {"keys": ["command", "space"]}, "goal": "Open Spotlight"},
                {"type": "type", "params": {"text": "TextEdit"}, "goal": "Type TextEdit"},
                {"type": "hotkey", "params": {"keys": ["enter"]}, "goal": "Launch TextEdit"},
                {"type": "type", "params": {"text": "Hello, this is my autonomous agent speaking!"}, "goal": "Type message"}
            ]
        else:
            # Fallback for generic tasks
            plan = [
                {"type": "move", "params": {"x": 500, "y": 500}, "goal": "Move to center"},
                {"type": "click", "params": {"x": 500, "y": 500}, "goal": "Click center"}
            ]

        logger.log_event(self.name, "planning_complete", {"steps_count": len(plan)})
        return plan

# Instance for use
planning_agent = PlanningAgent()
