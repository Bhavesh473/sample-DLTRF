import json
from datetime import datetime
import time
import os

LOG_FILE = os.getenv("DLTRF_LOG_PATH", "logs/events.log")

def load_logs(file_path):
    logs = []
    if not os.path.exists(file_path):
        print(f"No log file found at {file_path}")
        return logs

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                pass
    return logs

def sort_logs(logs):
    def parse_ts(ts):
        return datetime.fromisoformat(ts.replace("Z", ""))
    return sorted(logs, key=lambda x: parse_ts(x["timestamp"]))

def replay_events(logs, real_time=False):
    last_time = None
    for log in logs:
        ts = datetime.fromisoformat(log["timestamp"].replace("Z", ""))
        event_type = log.get("event_type", "unknown")
        payload = log.get("payload", {})

        if real_time and last_time:
            gap = (ts - last_time).total_seconds()
            time.sleep(max(gap, 0))

        print(f"[REPLAY] {ts} | Event: {event_type} | Payload: {payload}")

        if not real_time:
            time.sleep(1)

        last_time = ts

if __name__ == "__main__":
    logs = load_logs(LOG_FILE)
    if not logs:
        print("No logs to replay.")
    else:
        logs = sort_logs(logs)
        print(f"Loaded {len(logs)} events from {LOG_FILE}")
        replay_events(logs, real_time=False)
