from agents.action import action_agent
from agents.perception import perception_agent
from agents.error_correction import error_correction_agent
from agents.planning import planning_agent
from agents.memory import memory_agent
from agents.verification import verification_agent
from agents.notification import notification_agent
from agents.discovery import discovery_agent
from logger import logger
import time

class Orchestrator:
    def __init__(self):
        self.name = "Orchestrator"

    def run_task(self, task_description, steps=None, webhook_url=None):
        """
        Executes a multi-step task with a proactive historical learning loop,
        intelligent planning, and final verification.
        """
        logger.log_event(self.name, "task_start", {"description": task_description})
        notification_agent.send_update("started", f"Starting task: {task_description}", webhook_url)

        # ── 1. PRE-PLANNING: Memory & Planning ─────────────────────────────
        if not steps:
            # Check experience first
            steps = memory_agent.retrieve_experience(task_description)
            if steps:
                logger.log_event(self.name, "memory_applied", {"description": task_description})
            else:
                # Generate new plan
                steps = planning_agent.create_plan(task_description)
                logger.log_event(self.name, "plan_generated", {"step_count": len(steps)})

        results = []
        task_success = True

        for i, step in enumerate(steps):
            logger.log_event(self.name, "step_start", {"step_index": i, "step": step})
            
            # ── 2. PRE-EXECUTION: Vet step against historical failures ──────────
            vet_result = error_correction_agent.vet_step_against_history(step)
            effective_params = vet_result["params"]
            
            if vet_result["status"] == "adjusted":
                logger.log_event(self.name, "params_adjusted_by_history", {
                    "adjustments": vet_result["adjustments"],
                    "original": step["params"],
                    "adjusted": effective_params
                })
            
            # ── 3. EXECUTE with (possibly adjusted) params ──────────────────────
            action_result = action_agent.execute_command(step["type"], effective_params)
            
            # ── 4. PERCEIVE current state ────────────────────────────────────────
            capture_result = perception_agent.capture_screen()
            perception_result = {}
            if capture_result["status"] == "success":
                perception_result = perception_agent.analyze_state(
                    capture_result["filepath"], step.get("goal", "")
                )
            
            # ── 5. REVIEW: Error correction with specific suggestion ─────────────
            review = error_correction_agent.review_execution(action_result, perception_result)
            
            if review["status"] == "needs_correction":
                logger.log_event(self.name, "correction_loop_triggered", {
                    "feedback": review["feedback"],
                    "suggested_action": review["suggested_action"]
                })
                
                retry_result = self._apply_correction(step, effective_params, review["suggested_action"])
                results.append({
                    "step_index": i,
                    "step": step,
                    "status": retry_result["status"],
                    "details": retry_result
                })
                if retry_result["status"] != "success":
                    task_success = False
            else:
                results.append({
                    "step_index": i,
                    "step": step,
                    "status": "success",
                    "details": action_result
                })
            
            time.sleep(1)  # Gap between steps

        # ── 6. FINAL VERIFICATION ────────────────────────────────────────────
        verification = verification_agent.verify_completion(task_description)
        
        # ── 7. POST-TASK: Learning & Notification ───────────────────────────
        overall_status = "success" if (task_success and verification["goal_met"]) else "failed"
        
        if overall_status == "success":
            memory_agent.store_success(task_description, steps)
        
        notification_agent.send_update(
            overall_status, 
            f"Task complete: {task_description}", 
            webhook_url,
            {"verification": verification, "results_count": len(results)}
        )

        logger.log_event(self.name, "task_complete", {
            "status": overall_status, 
            "results_count": len(results)
        })
        
        return {
            "status": overall_status,
            "verification": verification,
            "results": results
        }

    def _apply_correction(self, step, last_params, suggestion):
        """
        Applies the specific correction strategy suggested by the ErrorCorrectionAgent.
        """
        if suggestion is None:
            suggestion = {"type": "retry_modified"}

        stype = suggestion.get("type", "retry_modified")

        if stype == "skip":
            logger.log_event(self.name, "step_skipped", {
                "reason": suggestion.get("reason", "No reason given")
            })
            return {"status": "skipped", "reason": suggestion.get("reason")}

        elif stype == "retry_with_delay":
            delay = suggestion.get("delay", 2)
            logger.log_event(self.name, "retry_with_delay", {"delay_seconds": delay})
            time.sleep(delay)
            result = action_agent.execute_command(step["type"], last_params)
            return {"status": result["status"], "strategy": stype, "result": result}

        elif stype == "adjust_coordinates":
            offset_x = suggestion.get("offset_x", 10)
            offset_y = suggestion.get("offset_y", 10)
            new_params = dict(last_params)
            if "x" in new_params:
                new_params["x"] = new_params.get("x", 0) + offset_x
            if "y" in new_params:
                new_params["y"] = new_params.get("y", 0) + offset_y

            logger.log_event(self.name, "retry_adjusted_coords", {
                "original": last_params,
                "adjusted": new_params
            })
            result = action_agent.execute_command(step["type"], new_params)
            return {"status": result["status"], "strategy": stype, "result": result}

        else:  # retry_modified or unknown
            logger.log_event(self.name, "retry_modified", {
                "reason": suggestion.get("reason", "Generic retry")
            })
            result = action_agent.execute_command(step["type"], last_params)
            return {"status": result["status"], "strategy": stype, "result": result}


# Instance for use
orchestrator = Orchestrator()
