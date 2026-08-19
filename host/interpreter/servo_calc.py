# выход: dict {servo_name: angle} готовый к отправке на ESP
from .emotion_map import get_pose, SERVO_ORDER, NEUTRAL_POSE

LOOK_OFFSETS = {
    "look_left":  {"eyes_pan": -25},
    "look_right": {"eyes_pan": +25},
    "look_up":    {"eyes_tilt": -15},
    "look_down":  {"eyes_tilt": +15},
}

BLINK_POSE = {"lid_tl": 0, "lid_tr": 0, "lid_bl": 45, "lid_br": 45}


def blend_pose(emotions: dict) -> dict:
    blended = {k: 0.0 for k in NEUTRAL_POSE}

    total_weight = sum(emotions.values()) or 1.0
    for emotion, weight in emotions.items():
        if weight <= 0:
            continue
        pose = get_pose(emotion)
        w = weight / total_weight
        for servo, angle in pose.items():
            blended[servo] += angle * w

    return blended


def apply_functions(pose: dict, functions: list[str]) -> dict: # функции поверх эмоц. позы
    result = dict(pose)

    for fn in functions:
        if fn in LOOK_OFFSETS:
            for servo, delta in LOOK_OFFSETS[fn].items():
                result[servo] += delta
        elif fn == "blink":
            result.update(BLINK_POSE)

    return result


def clamp(pose: dict, limits: dict) -> dict:
    result = {}
    for servo, angle in pose.items():
        lim = limits.get(servo, {"min": 0, "max": 180})
        result[servo] = max(lim["min"], min(lim["max"], angle))
    return result


def calculate(emotions: dict, functions: list[str], limits: dict) -> dict:
    pose = blend_pose(emotions)
    pose = apply_functions(pose, functions)
    pose = clamp(pose, limits)
    return pose


def to_array(pose: dict) -> list[float]:
    return [pose[s] for s in SERVO_ORDER]