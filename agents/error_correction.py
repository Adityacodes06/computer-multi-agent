from logger import logger
import json
import copy

class ErrorCorrectionAgent:
    def __init__(self):
        self.name = "ErrorCorrectionAgent"

    def vet_step_against_history(self, step):
        """
        Pre-execution check: Looks at historical failures for this command type
        and proactively adjusts parameters to avoid repeating known mistakes.
        """
        command_type = step.get("type")
        params = step.get("params", {})
        
        past_failures = logger.get_historical_failures(command_type=command_type)
        
        if not past_failures:
            return {"status": "ok", "params": params, "adjustments": []}
        
        adjusted_params = copy.deepcopy(params)
        adjustments = []
        failure_count = len(past_failures)
        
        logger.log_event(self.name, "history_check", {
            "command_type": command_type, 
            "past_failures_found": failure_count
        })
        
        if command_type == "click" or command_type == "move":
            # If we've seen failures for click/move, shift coordinates
            # The more failures, the larger the offset we try
            x = adjusted_params.get("x")
            y = adjusted_params.get("y")
            
            if x is not None and y is not None:
                # Check if past failures had similar coordinates
                similar_failures = self._find_similar_coordinate_failures(past_failures, x, y)
                if similar_failures > 0:
                    offset = min(similar_failures * 10, 50)  # Cap at 50px shift
                    adjusted_params["x"] = x + offset
                    adjusted_params["y"] = y + offset
                    adjustments.append(
                        f"Shifted coordinates by +{offset}px (x: {x}->{adjusted_params['x']}, "
                        f"y: {y}->{adjusted_params['y']}) due to {similar_failures} past failures"
                    )
        
        elif command_type == "hotkey":
            keys = adjusted_params.get("keys", [])
            if not keys and failure_count > 0:
                adjustments.append(
                    f"Warning: Empty hotkey detected. {failure_count} past failures with empty keys."
                )
        
        elif command_type == "type":
            text = adjusted_params.get("text", "")
            if not text and failure_count > 0:
                adjustments.append(
                    f"Warning: Empty text detected. {failure_count} past failures with empty text."
                )
        
        if adjustments:
            logger.log_event(self.name, "learning_applied", {
                "adjustments": adjustments,
                "original_params": params,
                "adjusted_params": adjusted_params
            })
            return {"status": "adjusted", "params": adjusted_params, "adjustments": adjustments}
        
        return {"status": "ok", "params": params, "adjustments": []}

    def _find_similar_coordinate_failures(self, failures, target_x, target_y, threshold=100):
        """
        Counts how many past failures had coordinates close to the target.
        """
        count = 0
        for failure in failures:
            details = failure.get("details", {})
            params = details.get("params", {})
            fx = params.get("x")
            fy = params.get("y")
            if fx is not None and fy is not None:
                if abs(fx - target_x) <= threshold and abs(fy - target_y) <= threshold:
                    count += 1
        return count

    def review_execution(self, last_action, perception_results):
        """
        Reviews the last action and the current state to identify errors.
        Now generates specific correction suggestions based on failure type.
        """
        logger.log_event(self.name, "review_start", {"last_action": last_action})
        
        is_error = False
        feedback = ""
        suggested_action = None
        
        if last_action.get("status") == "failed":
            is_error = True
            error_msg = last_action.get("error", "")
            feedback = f"Action failed: {error_msg}"
            suggested_action = self._generate_suggestion(last_action, error_msg)
            
        elif not perception_results.get("matches_goal", True):
            is_error = True
            feedback = f"Goal not met. Discrepancies: {perception_results.get('discrepancies')}"
            suggested_action = {
                "type": "retry_with_delay",
                "delay": 2,
                "reason": "Goal not matched by perception—retrying after a short delay."
            }
            
        if is_error:
            logger.log_event(self.name, "error_detected", {
                "feedback": feedback,
                "suggested_action": suggested_action
            }, status="error")
            return {
                "status": "needs_correction", 
                "feedback": feedback, 
                "suggested_action": suggested_action
            }
        
        logger.log_event(self.name, "review_complete", {"status": "all_good"})
        return {"status": "ok"}

    def _generate_suggestion(self, last_action, error_msg):
        """
        Generates a specific correction suggestion based on the error type.
        """
        error_lower = error_msg.lower()
        
        if "failsafe" in error_lower or "corner" in error_lower:
            return {
                "type": "adjust_coordinates",
                "reason": "PyAutoGUI failsafe triggered. Target coordinates may be too close to screen edge.",
                "offset_x": 50,
                "offset_y": 50
            }
        elif "not found" in error_lower or "invalid" in error_lower:
            return {
                "type": "retry_with_delay",
                "delay": 3,
                "reason": "Target element may not have loaded yet. Retrying after delay."
            }
        elif "unknown command" in error_lower:
            return {
                "type": "skip",
                "reason": "Command type is not recognized. Skipping this step."
            }
        else:
            return {
                "type": "retry_modified",
                "reason": f"Generic failure: {error_msg}. Retrying with slight modifications."
            }

# Instance for use
error_correction_agent = ErrorCorrectionAgent()
