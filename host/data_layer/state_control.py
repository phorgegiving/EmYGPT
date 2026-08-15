import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "emotions.yaml"

EMOTIONS = ["happy", "sad", "angry", "surprised", "fear", "disgust", "neutral"]


class EmotionState:
    def __init__(self):
        cfg = yaml.safe_load(open(_CONFIG_PATH))
        self.decay_rate: float = cfg["decay_rate"]

        self._current = {e: 0.0 for e in EMOTIONS}
        self._current["neutral"] = 1.0

    def update(self, new_emotions: dict):

        d = self.decay_rate
        for e in EMOTIONS:
            incoming = new_emotions.get(e, 0.0)
            self._current[e] = self._current[e] * (1 - d) + incoming * d
        self._normalize()

    def get(self) -> dict:
        return dict(self._current)

    def _normalize(self):
        total = sum(self._current.values())
        if total > 0:
            for e in self._current:
                self._current[e] /= total

    def dominant(self) -> str:
        return max(self._current, key=self._current.get)