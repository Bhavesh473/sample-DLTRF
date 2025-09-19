import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, Optional

# config via env var; default path inside container (mount to host for Member B)
LOG_PATH = os.getenv("DLTRF_LOG_PATH", "logs/events.log")
_lock = threading.Lock()

def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def init_logger(path: Optional[str] = None) -> str:
    global LOG_PATH
    if path:
        LOG_PATH = path
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    # create file if not exists
    open(LOG_PATH, "a", encoding="utf-8").close()
    return LOG_PATH

def _write_line(line: str) -> None:
    with _lock:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()

def _make_event(event_type: str, payload: Dict[str, Any], user_id: Optional[str], timestamp: Optional[str]) -> Dict[str, Any]:
    return {
        "timestamp": timestamp or _now_iso(),
        "event_type": event_type,
        "user_id": user_id,
        "payload": payload or {}
    }

def log_event(event_type: str, payload: Dict[str, Any], user_id: Optional[str] = None, timestamp: Optional[str] = None) -> Dict[str, Any]:
    if not os.path.exists(LOG_PATH):
        init_logger()
    event = _make_event(event_type, payload, user_id, timestamp)
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    try:
        _write_line(line)
    except Exception as e:
        print(f"ERROR writing log: {e}", flush=True)
    return event

def flask_request_hook(request):
    try:
        json_body = request.get_json(silent=True)
    except Exception:
        json_body = None

    payload = {
        "path": request.path,
        "method": request.method,
        "args": request.args.to_dict(),
        "json": json_body
    }
    user_id = request.headers.get("X-User-Id") or None
    return log_event("http_request", payload, user_id=user_id)
