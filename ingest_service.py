from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
from pydantic import BaseModel, field_validator  # Updated import
from threading import Lock

app = Flask(__name__)

# Log file path (DLTRF style)
LOG_PATH = os.getenv("DLTRF_LOG_PATH", "logs/events.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# JSON Schema Validation
class LogEvent(BaseModel):
    timestamp: str
    event_type: str
    user_id: str = None
    payload: dict = {}

    @field_validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid ISO timestamp')

# Thread-safe lock (DLTRF se inspired)
_lock = Lock()

def _write_line(line: str):
    with _lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")

@app.route('/ingest', methods=['POST'])
def ingest_log():
    try:
      data = request.get_json()
      if not data:
          return jsonify({'error': 'No JSON provided'}), 400

      # Validate schema
      event = LogEvent(**data)

      # Timestamp add karo agar missing
      if not event.timestamp:
          event.timestamp = datetime.timezone.utc().isoformat() + 'Z'

      # JSON banao aur file mein save (DLTRF format)
      event_dict = event.model_dump()
      line = json.dumps(event_dict, separators=(",", ":"))
      _write_line(line)

      return jsonify({'status': 'logged', 'event': event_dict}), 200
    except Exception as e:
      return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)