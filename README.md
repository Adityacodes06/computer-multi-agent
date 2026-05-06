# Multi-Agent Computer Control System 🤖💻

An autonomous, self-learning multi-agent system for computer control. This system utilizes a coordinated "See-Think-Act" loop with proactive error correction, historical learning, and visual verification.

## 🌟 Key Features
- **Orchestrator (The Brain)**: Manages the high-level workflow and agent cooperation.
- **Planning Agent**: Decomposes natural language tasks into atomic OS commands.
- **Action Agent**: Executes mouse, keyboard, and system commands via PyAutoGUI.
- **Perception Agent**: Captures and analyzes the screen state.
- **Error Correction Agent**: Proactively learns from historical failures to adjust parameters on the fly.
- **Verification Agent**: Audits the final state to ensure the task goal was successfully met.
- **Memory Agent**: Stores successful task patterns in a local JSON "experience" database.
- **Notification Agent**: Communicates status updates to external webhooks (like n8n).

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- macOS (Optimized for Mac OS, requires screen recording permissions)

### Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the System
Start the FastAPI server:
```bash
python main.py
```
Send a task via the API:
```bash
curl -X POST http://localhost:8000/execute_task \
     -H "Content-Type: application/json" \
     -d '{"task_description": "Search Google for tech news"}'
```

## 📂 Project Structure
- `agents/`: Specialist agent logic (Planning, Action, Perception, etc.)
- `static/`: Frontend assets
- `templates/`: HTML templates for the dashboard
- `logger.py`: Structured JSONL logging system
- `task_memory.json`: Learned successful task patterns

## 🛡️ License
MIT


*Automated maintenance update: 2026-05-06 18:15:21*
