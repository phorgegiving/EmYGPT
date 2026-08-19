"""
Маппинг эмоций в базовые позы сервоприводов.

Для глаз (pan/tilt) и рта углы задаются в градусах.
Для век используется шкала ОТКРЫТОСТИ 0.0–1.0, а не градусы напрямую.
"""

SERVO_ORDER = ["eyes_pan", "eyes_tilt", "lid_tl", "lid_tr", "lid_bl", "lid_br", "mouth"]
LID_SERVOS = ["lid_tl", "lid_tr", "lid_bl", "lid_br"]

NEUTRAL_POSE = {
    "eyes_pan": 90, "eyes_tilt": 90,
    "lid_tl": 0.7, "lid_tr": 0.7, "lid_bl": 0.7, "lid_br": 0.7,
    "mouth": 0,
}

EMOTION_POSES = {
    "happy": {
        "lid_tl": 0.45, "lid_tr": 0.45,
        "lid_bl": 0.7, "lid_br": 0.7,
        "mouth": 20,
    },
    "sad": {
        "lid_tl": 0.5, "lid_tr": 0.5,
        "lid_bl": 0.9, "lid_br": 0.9,
        "eyes_tilt": 80,
        "mouth": 5,
    },
    "angry": {
        "lid_tl": 0.3, "lid_tr": 0.3,
        "lid_bl": 0.5, "lid_br": 0.5,
        "eyes_tilt": 95,
        "mouth": 8,
    },
    "surprised": {
        "lid_tl": 1.0, "lid_tr": 1.0, "lid_bl": 1.0, "lid_br": 1.0,
        "eyes_tilt": 85,
        "mouth": 25,
    },
    "fear": {
        "lid_tl": 0.95, "lid_tr": 0.95,
        "lid_bl": 0.85, "lid_br": 0.85,
        "eyes_pan": 95,
        "mouth": 12,
    },
    "disgust": {
        "lid_tl": 0.55, "lid_tr": 0.75,
        "lid_bl": 0.6, "lid_br": 0.6,
        "mouth": 3,
    },
    "neutral": dict(NEUTRAL_POSE),
}


def get_pose(emotion: str) -> dict:
    pose = dict(NEUTRAL_POSE)
    pose.update(EMOTION_POSES.get(emotion, {}))
    return pose