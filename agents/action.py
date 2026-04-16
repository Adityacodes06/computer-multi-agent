import pyautogui
import time
from logger import logger

class ActionAgent:
    def __init__(self):
        self.name = "ActionAgent"
        # Safety setting: move mouse to corner to abort
        pyautogui.FAILSAFE = True

    def execute_command(self, command_type, params):
        """
        Executes a low-level OS command.
        Supported commands: 'click', 'type', 'move', 'hotkey'
        """
        try:
            logger.log_event(self.name, "execution_start", {"command": command_type, "params": params})
            
            if command_type == "click":
                x, y = params.get("x"), params.get("y")
                pyautogui.click(x, y)
            elif command_type == "type":
                text = params.get("text")
                pyautogui.write(text, interval=0.1)
            elif command_type == "move":
                x, y = params.get("x"), params.get("y")
                pyautogui.moveTo(x, y, duration=0.5)
            elif command_type == "hotkey":
                keys = params.get("keys", [])
                pyautogui.hotkey(*keys)
            else:
                raise ValueError(f"Unknown command type: {command_type}")

            logger.log_event(self.name, "execution_success", {"command": command_type})
            return {"status": "success", "message": f"Executed {command_type}"}

        except Exception as e:
            error_msg = str(e)
            logger.log_event(self.name, "execution_failure", {"command": command_type, "error": error_msg}, status="failed")
            return {"status": "failed", "error": error_msg}

# Instance for use
action_agent = ActionAgent()
