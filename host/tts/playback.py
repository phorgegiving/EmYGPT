import asyncio
import yaml
from pathlib import Path

import numpy as np
import sounddevice as sd

from host.interpreter.lipsync import audio_to_envelope, envelope_to_mouth_angles
from host.interpreter.emotion_map import SERVO_ORDER

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "tts.yaml"


def _load_lipsync_config() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return {
        "frame_ms": cfg["lipsync_frame_ms"],
        "smoothing": cfg["lipsync_smoothing"],
        "start_delay_ms": cfg.get("lipsync_start_delay_ms", 0),
    }


async def speak_with_lipsync(
    audio: np.ndarray,
    sample_rate: int,
    base_pose: dict,
    limits: dict,
    transport,
    connected: bool,
):
    
    lc = _load_lipsync_config()
    mouth_lim = limits["mouth"]

    envelope = audio_to_envelope(audio, sample_rate, frame_ms=lc["frame_ms"])
    mouth_angles = envelope_to_mouth_angles(
        envelope, mouth_lim["min"], mouth_lim["max"], smoothing=lc["smoothing"]
    )

    loop = asyncio.get_event_loop()

    sd.play(audio, sample_rate)

    if connected:
        frame_s = lc["frame_ms"] / 1000
        start_delay_s = lc["start_delay_ms"] / 1000
        t0 = loop.time() + start_delay_s

        for i, angle in enumerate(mouth_angles):
            target_time = t0 + i * frame_s
            now = loop.time()
            sleep_for = target_time - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)

            try:
                await transport.send_mouth(angle)
            except Exception as e:
                print(f"[BLE] ошибка кадра липсинка: {e}")
                break

        try:
            await transport.send_pose([base_pose[s] for s in SERVO_ORDER])
        except Exception:
            pass
    else:
        await asyncio.sleep(len(audio) / sample_rate)

    sd.wait()