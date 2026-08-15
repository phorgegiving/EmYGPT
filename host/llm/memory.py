import json
from pathlib import Path

MEMORY_PATH = Path(__file__).parent.parent / "data" / "memory.json"
MAX_FACTS = 20


class Memory:
    def __init__(self):
        self._path = MEMORY_PATH
        self._data = self._load()

    def _load(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"facts": []}

    def _save(self):
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_facts(self) -> list[str]:
        return self._data.get("facts", [])

    def add_fact(self, fact: str):
        fact = fact.strip()
        if not fact:
            return
        existing = self._data["facts"]
        if fact not in existing:
            existing.append(fact)

            if len(existing) > MAX_FACTS:
                self._data["facts"] = existing[-MAX_FACTS:]
            self._save()

    def as_text(self) -> str:
        facts = self.get_facts()
        if not facts:
            return ""
        return "Что я знаю о пользователе:\n" + "\n".join(f"- {f}" for f in facts)