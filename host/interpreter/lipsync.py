# липсинк, я наношу на себя липсинк 

import numpy as np


def audio_to_envelope(audio: np.ndarray, sample_rate: int, frame_ms: int = 50) -> list[float]:
    frame_len = max(1, int(sample_rate * frame_ms / 1000))
    n_frames = max(1, len(audio) // frame_len)

    envelope = []
    for i in range(n_frames):
        chunk = audio[i * frame_len : (i + 1) * frame_len]
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2))) if len(chunk) else 0.0
        envelope.append(rms)

    peak = max(envelope) or 1.0
    return [v / peak for v in envelope]


def envelope_to_mouth_angles(
    envelope: list[float],
    mouth_min: float,
    mouth_max: float,
    smoothing: float = 0.35,
) -> list[float]:
    angles = []
    prev = mouth_min
    for v in envelope:
        target = mouth_min + v * (mouth_max - mouth_min)
        prev = prev * (1 - smoothing) + target * smoothing
        angles.append(prev)
    return angles