from collections import deque

MAX_TURNS = 3


class History:
    def __init__(self):
        self._turns = deque(maxlen=MAX_TURNS)

    def add(self, user_input: str, assistant_response: dict):
        self._turns.append({"user": user_input, "assistant": assistant_response})

    def get(self) -> list[dict]:
        return list(self._turns)

    def clear(self):
        self._turns.clear()