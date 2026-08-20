import torch
import numpy as np
import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "tts.yaml"

_model = None
_config = None


def _load_config() -> dict:
    global _config
    if _config is None:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            _config = yaml.safe_load(f)
    return _config


def _load_model():
    global _model
    if _model is not None:
        return _model

    cfg = _load_config()
    print("[TTS] загрузка модели Silero (займёт несколько секунд)...")

    torch.set_num_threads(4)
    device = torch.device(cfg["device"])

    model, _ = torch.hub.load(
        repo_or_dir="snakers4/silero-models",
        model="silero_tts",
        language=cfg["language"],
        speaker="v4_ru",
    )
    model.to(device)

    _model = model
    print("[TTS] модель загружена и готова")
    return _model


def synthesize(text: str) -> tuple[np.ndarray, int]:
    cfg = _load_config()
    model = _load_model()

    with torch.no_grad():
        audio = model.apply_tts(
            text=text,
            speaker=cfg["speaker"],
            sample_rate=cfg["sample_rate"],
        )

    return audio.numpy(), cfg["sample_rate"]


def warmup():
    _load_model()
    synthesize("Проверка.")
    print("[TTS] прогрев завершён")