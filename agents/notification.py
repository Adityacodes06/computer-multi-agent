import requests
from logger import logger
from typing import Dict, Any

class NotificationAgent:
    def __init__(self):
        self.name = "NotificationAgent"

    def send_update(self, status: str, message: str, webhook_url: str = None, details: Dict[str, Any] = None):
        """
        Sends notifications to external services (n8n, Slack, etc.) 
        about the task progress or completion.
        """
        payload = {
            "agent": "MultiAgentSystem",
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        logger.log_event(self.name, "notification_trigger", payload)

        # If a webhook URL is provided (e.g. from n8n), send a POST request
        if webhook_url:
            try:
                response = requests.post(webhook_url, json=payload, timeout=5)
                logger.log_event(self.name, "webhook_success", {"url": webhook_url, "code": response.status_code})
            except Exception as e:
                logger.log_event(self.name, "webhook_failure", {"url": webhook_url, "error": str(e)}, status="error")

        # For demonstration: and logic could go here to send to Slack/Discord
        return payload

# Instance for use
notification_agent = NotificationAgent()
