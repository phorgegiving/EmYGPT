import json
import time
from pathlib import Path

HISTORY_PATH = Path(__file__).parent.parent / "data" / "history.json"
MAX_TURNS = 3


class History:
    def __init__(self):
        HISTORY_PATH.parent.mkdir(exist_ok=True)
        HISTORY_PATH.touch(exist_ok=True)

    def add(self, user_input: str, assistant_response: dict):
        entry = {
            "ts": int(time.time()),
            "user": user_input,
            "assistant": assistant_response,
        }
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + ", \n")

    def get(self) -> list[dict]:
        lines = []
        try:
            with open(HISTORY_PATH, encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            return []

        recent = lines[-MAX_TURNS:]
        result = []
        for line in recent:
            try:
                entry = json.loads(line)
                result.append({
                    "user": entry["user"],
                    "assistant": entry["assistant"],
                })
            except json.JSONDecodeError:
                continue
        return result

    def clear(self):
        HISTORY_PATH.write_text("", encoding="utf-8")