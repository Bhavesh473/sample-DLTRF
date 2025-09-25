As Member A (Sumitra), your role in the universal logging hook microservice app is to handle Core Service Development. Phase 1: Service Foundation focuses on laying the groundwork for the core service, which will ingest, process, and prepare logs for storage and replay. This phase can be done independently of Member B's work, as per the PDF.

I'll provide step-by-step instructions, assuming you're on a Windows machine (based on prior context). We'll use **Visual Studio Code (VS Code)** as the primary code editor (it's free, supports Python, Git, and has a built-in terminal). We'll install necessary apps/tools, write code in VS Code, and run commands in the terminal (either VS Code's integrated terminal or Windows PowerShell/Command Prompt). No other special apps are needed beyond what's listed.

The service will use **Python** (for simplicity and compatibility with FastAPI) and **FastAPI** (preferred over Flask for its async support and automatic API docs, as it's modern and efficient for microservices in 2025). We'll set up the repository structure as outlined in the PDF: `universal-logging-microservice/src/core/` for your files.

### Step 0: Install Required Apps and Tools
Before starting, install these if not already done. Use your web browser to download.

1. **Install Python 3.12+** (required for FastAPI):
   - Download from [python.org](https://www.python.org/downloads/). Choose the latest stable version (e.g., 3.12.6 as of 2025).
   - During installation, check "Add Python to PATH" and install pip.
   - Verify in terminal: Open PowerShell (search in Start menu) and run `python --version`. It should show 3.12+.

2. **Install Visual Studio Code (VS Code)**:
   - Download from [code.visualstudio.com](https://code.visualstudio.com/download).
   - Install extensions in VS Code (open VS Code, go to Extensions sidebar, search and install):
     - Python (by Microsoft) – for code editing, debugging.
     - GitLens – for Git integration.
     - YAML – for later Docker/K8s files.
   - Open VS Code's integrated terminal: View > Terminal (or Ctrl+`).

3. **Install Git** (for version control and repository setup):
   - Download from [git-scm.com](https://git-scm.com/download/win).
   - Verify: In terminal, run `git --version`.

4. **Optional but Recommended: Install WSL 2 and Docker Desktop** (for later containerization in Phase 3, and to run Linux-based tools like Redis/MongoDB easily):
   - In PowerShell as Admin: `wsl --install` (installs Ubuntu by default).
   - Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop). Enable WSL 2 backend during setup.
   - Verify: `docker --version`.

If you're using WSL, run all subsequent terminal commands inside WSL (open Ubuntu app or `wsl` in PowerShell).

### Step 1: Service Definition & Architecture
Define what the service does: A microservice that hooks into applications to capture logs universally, processes them (normalize, timestamp), and prepares for storage/replay. Architecture: RESTful API with FastAPI, input via POST endpoints, output as JSON. It will integrate with storage (Phase 2) but for now, focus on in-memory processing.

1. Open VS Code.
2. Create the repository folder:
   - In terminal (VS Code or PowerShell): `mkdir universal-logging-microservice && cd universal-logging-microservice`
3. Initialize Git:
   - `git init`
   - Create `.gitignore` file in VS Code (File > New File > .gitignore) and add:
     ```
     __pycache__/
     *.pyc
     .env
     ```
   - Commit: `git add .gitignore && git commit -m "Initial commit"`
4. Create the core folder structure (your part):
   - In terminal: `mkdir -p src/core`
5. Define the service in a README or doc file (use Markdown for clarity).
   - In VS Code, create `src/core/README.md` (File > New File).
   - Write:
     ```
     # Core Service: Universal Logging Hook Microservice

     ## Service Definition
     - Purpose: Capture, process, and store logs from any app for deterministic replay.
     - Key Features: Log ingestion, normalization, timestamping, ordering, checkpointing, replay.
     - Tech Stack: Python, FastAPI for API, Redis for queuing, MongoDB for storage.

     ## Architecture
     - HTTP Server: FastAPI handles endpoints.
     - Processing Pipeline: Normalize logs (e.g., standardize formats), add timestamps.
     - Data Flow: Ingest -> Process -> Queue/Store -> Replay.
     - Scalability: Async processing, containerized for K8s.
     ```
   - Save and commit: `git add src/core/README.md && git commit -m "Step 1: Service definition and architecture"`

### Step 2: API Contract Design (JSON Schema, Endpoints)
Design the API: Endpoints for ingestion and later replay. Use JSON Schema for validation (via Pydantic in FastAPI).

1. In VS Code, create `src/core/schema.py` (defines models).
   - Write:
     ```python
     from pydantic import BaseModel
     from datetime import datetime
     from typing import Dict, Any

     class LogEvent(BaseModel):
         """JSON Schema for incoming log events."""
         source: str  # e.g., 'app1' or 'legacy-system'
         level: str  # e.g., 'INFO', 'ERROR'
         message: str
         metadata: Dict[str, Any] = {}  # Optional extra data
         timestamp: datetime = None  # Will be set if missing
     ```
2. Document endpoints in `src/core/README.md` (append to the file):
   ```
   ## API Contract
   - POST /logs/ingest: Ingest a log event (body: LogEvent schema).
     - Response: {"status": "ingested", "event_id": "uuid"}
   - GET /logs/replay/{event_id}: Replay a log (for Phase 2).
     - Response: Log details or error.
   - Validation: Uses Pydantic for JSON schema enforcement.
   ```
3. Commit: `git add src/core/schema.py src/core/README.md && git commit -m "Step 2: API contract design"`

### Step 4: HTTP Server Implementation (FastAPI)
Implement the basic server. We'll add processing in Step 5.

1. Install FastAPI and dependencies (in terminal, inside the project folder):
   - `python -m venv venv` (create virtual env)
   - `.\venv\Scripts\activate` (activate on Windows; or `source venv/bin/activate` in WSL)
   - `pip install fastapi uvicorn pydantic`
   - Create `requirements.txt`: `pip freeze > requirements.txt`
2. In VS Code, create `src/core/api_server.py`:
   ```python
   from fastapi import FastAPI
   from .schema import LogEvent  # Import from same folder

   app = FastAPI(title="Universal Logging Hook Microservice")

   @app.post("/logs/ingest")
   async def ingest_log(event: LogEvent):
       # Placeholder: Will process in Step 5
       return {"status": "ingested", "event_id": "placeholder-uuid"}
   ```
3. Create a main entry point for testing (as per repo structure, `src/main.py` combines parts, but for now, test core independently).
   - Create `src/main.py`:
     ```python
     from core.api_server import app  # Import your app

     if __name__ == "__main__":
         import uvicorn
         uvicorn.run(app, host="0.0.0.0", port=8000)
     ```
4. Run and test:
   - In terminal: `python src/main.py`
   - Open browser to http://localhost:8000/docs (FastAPI's auto-docs).
   - Test ingestion: Use curl in another terminal `curl -X POST http://localhost:8000/logs/ingest -H "Content-Type: application/json" -d '{"source": "test", "level": "INFO", "message": "Hello"}'`
   - Stop with Ctrl+C.
5. Commit: `git add src/core/api_server.py src/main.py requirements.txt && git commit -m "Step 4: HTTP server implementation"`

### Step 5: Log Processing Pipeline (Normalization, Timestamping)
Add processing: Normalize (e.g., standardize keys, convert to lowercase), add timestamp if missing.

1. In VS Code, create `src/core/log_processor.py`:
   ```python
   from datetime import datetime
   from typing import Dict, Any

   def process_log(event_dict: Dict[str, Any]) -> Dict[str, Any]:
       """Normalization and timestamping pipeline."""
       # Timestamp if missing
       if 'timestamp' not in event_dict or event_dict['timestamp'] is None:
           event_dict['timestamp'] = datetime.utcnow().isoformat()
       
       # Normalize: Lowercase keys in metadata, standardize level
       if 'metadata' in event_dict:
           event_dict['metadata'] = {k.lower(): v for k, v in event_dict['metadata'].items()}
       if 'level' in event_dict:
           event_dict['level'] = event_dict['level'].upper()
       
       return event_dict
   ```
2. Integrate into API: Update `src/core/api_server.py` (add import and call):
   ```python
   from fastapi import FastAPI
   from .schema import LogEvent
   from .log_processor import process_log
   import uuid

   app = FastAPI(title="Universal Logging Hook Microservice")

   @app.post("/logs/ingest")
   async def ingest_log(event: LogEvent):
       event_dict = event.dict()  # Convert to dict for processing
       processed = process_log(event_dict)
       event_id = str(uuid.uuid4())  # Generate unique ID
       # For now, just return; storage in Phase 2
       return {"status": "processed", "event_id": event_id, "processed_log": processed}
   ```
3. Test again: Run `python src/main.py`, then curl as in Step 4. Check response for timestamp and normalization.
4. Commit: `git add src/core/log_processor.py src/core/api_server.py && git commit -m "Step 5: Log processing pipeline"`

### Next Steps and Tips
- You've completed Phase 1! The core service now has a basic API that ingests and processes logs.
- Push to GitHub if collaborating: Create a repo on GitHub, then `git remote add origin <repo-url> && git push -u origin main`.
- For Phase 2, you'll add storage (`src/core/storage.py` with Redis/MongoDB – install via pip when ready).
- If errors: Check Python path, venv activation, or FastAPI docs at fastapi.tiangolo.com.
- Total time: 1-2 hours if tools are installed.

If you encounter issues or need Phase 2 guidance, provide details!
