SERVO_ORDER = ["eyes_pan", "eyes_tilt", "lid_tl", "lid_tr", "lid_bl", "lid_br", "mouth"]

NEUTRAL_POSE = {
    "eyes_pan": 90, "eyes_tilt": 90,
    "lid_tl": 22, "lid_tr": 22, "lid_bl": 22, "lid_br": 22,
    "mouth": 0,
}

EMOTION_POSES = {
    "happy": {
        "lid_tl": 35, "lid_tr": 35, "lid_bl": 10, "lid_br": 10,
        "mouth": 20,
    },
    "sad": {
        "lid_tl": 10, "lid_tr": 10, "lid_bl": 30, "lid_br": 30,
        "eyes_tilt": 80,  # смотрит вниз
        "mouth": 5,
    },
    "angry": {
        "lid_tl": 40, "lid_tr": 40, "lid_bl": 30, "lid_br": 30,
        "eyes_tilt": 95,
        "mouth": 8,
    },
    "surprised": {
        "lid_tl": 45, "lid_tr": 45, "lid_bl": 0, "lid_br": 0,
        "eyes_tilt": 85,
        "mouth": 25,
    },
    "fear": {
        "lid_tl": 42, "lid_tr": 42, "lid_bl": 5, "lid_br": 5,
        "eyes_pan": 95,
        "mouth": 12,
    },
    "disgust": {
        "lid_tl": 15, "lid_tr": 15, "lid_bl": 25, "lid_br": 25,
        "mouth": 3,
    },
    "neutral": dict(NEUTRAL_POSE),
}


def get_pose(emotion: str) -> dict:
    pose = dict(NEUTRAL_POSE)
    pose.update(EMOTION_POSES.get(emotion, {}))
    return pose