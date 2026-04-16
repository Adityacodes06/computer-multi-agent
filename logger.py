import logging
import json
import os
from datetime import datetime

class AgentLogger:
    def __init__(self, log_file="/Users/vartikasrivastava/project/agent_log.jsonl"):
        self.log_file = log_file
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configure standard logging for console
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("MultiAgentSystem")

    def log_event(self, agent_name, event_type, details, status="success"):
        """
        Logs an event in a structured JSONL format for easy parsing by other agents.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "event": event_type,
            "status": status,
            "details": details
        }
        
        # Log to console
        self.logger.info(f"[{agent_name}] {event_type}: {status} - {details}")
        
        # Append to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_recent_logs(self, limit=10):
        """
        Retrieves recent logs for error correction.
        """
        if not os.path.exists(self.log_file):
            return []
            
        with open(self.log_file, "r") as f:
            lines = f.readlines()
            return [json.loads(line) for line in lines[-limit:]]

    def get_historical_failures(self, command_type=None, limit=100):
        """
        Retrieves historical failed logs to learn from mistakes.
        """
        if not os.path.exists(self.log_file):
            return []
            
        failures = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("status") in ["failed", "error"] or entry.get("event") == "execution_failure":
                        # If filtering by command type
                        if command_type:
                            details = entry.get("details", {})
                            if details.get("command") != command_type:
                                continue
                        failures.append(entry)
                except json.JSONDecodeError:
                    continue
        return failures[-limit:]

# Global instance
logger = AgentLogger()
