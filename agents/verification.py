from agents.perception import perception_agent
from logger import logger
from typing import Dict, Any

class VerificationAgent:
    def __init__(self):
        self.name = "VerificationAgent"

    def verify_completion(self, final_goal: str) -> Dict[str, Any]:
        """
        Performs a final audit to ensure the overall task goal was achieved.
        """
        logger.log_event(self.name, "verification_start", {"target_goal": final_goal})
        
        # 1. Capture current end state
        capture = perception_agent.capture_screen()
        
        if capture["status"] != "success":
            return {"status": "inconclusive", "reason": "Failed to capture final state"}

        # 2. Analyze the final state against the ultimate goal
        # In production, this is a distinct LLM call specifically for "verification"
        analysis = perception_agent.analyze_state(capture["filepath"], final_goal)
        
        success = analysis.get("matches_goal", False)
        
        result = {
            "status": "verified" if success else "failed_verification",
            "goal_met": success,
            "observations": analysis.get("visible_elements", []),
            "discrepancies": analysis.get("discrepancies", [])
        }
        
        logger.log_event(self.name, "verification_complete", result, 
                         status="success" if success else "error")
        return result

# Instance for use
verification_agent = VerificationAgent()
