"""
Расчёт финальных углов сервоприводов.
Вход: вектор эмоций (dict) + список функций (list[str]) + лимиты (из YAML)
Выход: dict {servo_name: angle} готовый к отправке на ESP32

Веки обрабатываются в шкале openness (0.0–1.0) до последнего шага,
и только в конце конвертируются в реальные градусы через калибровку
open/closed из servo_limits.yaml — так асинхронные и разнонаправленные
веки считаются так же просто, как и обычные сервоприводы.
"""
from .emotion_map import get_pose, SERVO_ORDER, NEUTRAL_POSE, LID_SERVOS

LOOK_OFFSETS = {
    "look_left":  {"eyes_pan": -15},
    "look_right": {"eyes_pan": +15},
    "look_up":    {"eyes_tilt": -10},
    "look_down":  {"eyes_tilt": +10},
}

BLINK_POSE = {s: 0.0 for s in LID_SERVOS}


def blend_pose(emotions: dict) -> dict:
    blended = {k: 0.0 for k in NEUTRAL_POSE}

    total_weight = sum(emotions.values()) or 1.0
    for emotion, weight in emotions.items():
        if weight <= 0:
            continue
        pose = get_pose(emotion)
        w = weight / total_weight
        for servo, value in pose.items():
            blended[servo] += value * w

    return blended


def apply_functions(pose: dict, functions: list[str]) -> dict:
    result = dict(pose)

    for fn in functions:
        if fn in LOOK_OFFSETS:
            for servo, delta in LOOK_OFFSETS[fn].items():
                result[servo] += delta
        elif fn == "blink":
            result.update(BLINK_POSE)

    return result


def clamp_openness(pose: dict) -> dict:
    result = dict(pose)
    for servo in LID_SERVOS:
        result[servo] = max(0.0, min(1.0, result[servo]))
    return result


def lids_to_angles(pose: dict, limits: dict) -> dict:
    result = dict(pose)
    for servo in LID_SERVOS:
        cal = limits[servo]
        openness = result[servo]
        result[servo] = cal["closed"] + openness * (cal["open"] - cal["closed"])
    return result


def clamp_degrees(pose: dict, limits: dict) -> dict:
    result = {}
    for servo, angle in pose.items():
        lim = limits.get(servo, {"min": 0, "max": 180})
        result[servo] = max(lim["min"], min(lim["max"], angle))
    return result


def calculate(emotions: dict, functions: list[str], limits: dict) -> dict:
    pose = blend_pose(emotions)
    pose = apply_functions(pose, functions)
    pose = clamp_openness(pose)          # веки: 0.0–1.0
    pose = lids_to_angles(pose, limits)  # веки: openness → градусы
    pose = clamp_degrees(pose, limits)   # финальная физическая обрезка всех сервоприводов
    return pose


def to_array(pose: dict) -> list[float]:
    """Конвертирует dict в список в порядке SERVO_ORDER — формат для прошивки."""
    return [pose[s] for s in SERVO_ORDER]