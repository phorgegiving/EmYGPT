"""
тюнер сервоприводов.
позволяет двигать каждый сервопривод по отдельности и подбирать лимиты.

Запуск: python -m tools.servo_tuner  (из корня проекта)
"""
import asyncio
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from host.interpreter.transport import HeadTransport
from host.interpreter.emotion_map import SERVO_ORDER, LID_SERVOS, EMOTION_POSES
from host.interpreter.servo_calc import calculate, to_array

STEP = 5

LIMITS_PATH = Path(__file__).parent.parent / "config" / "servo_limits.yaml"

RUSSIAN_NAMES = {
    "eyes_pan": "Глаза — гор.",
    "eyes_tilt": "Глаза — верт.",
    "lid_tl": "Веко верх-лев",
    "lid_tr": "Веко верх-прав",
    "lid_bl": "Веко низ-лев",
    "lid_br": "Веко низ-прав",
    "mouth": "Рот",
}


def load_limits() -> dict:
    with open(LIMITS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def raw_neutral_pose(limits: dict) -> dict:
    pose = {}
    for servo in SERVO_ORDER:
        lim = limits[servo]
        if servo in LID_SERVOS:
            pose[servo] = lim["open"]
        else:
            pose[servo] = lim.get("center", 0)
    return pose


class Tuner:
    def __init__(self, limits: dict):
        self.limits = limits
        self.pose = raw_neutral_pose(limits)
        self.selected = 0  # индекс в SERVO_ORDER
        self.transport = HeadTransport()

    async def connect(self):
        await self.transport.connect()
        angles = [self.pose[s] for s in SERVO_ORDER]
        await self.transport.send_pose(angles)

    def print_state(self):
        print("\n" + "=" * 50)
        print("SERVO TUNER — управление сервоприводами (сырые градусы)")
        print("=" * 50)
        for i, servo in enumerate(SERVO_ORDER):
            marker = "→ " if i == self.selected else "  "
            name = RUSSIAN_NAMES.get(servo, servo)
            angle = self.pose[servo]
            lim = self.limits[servo]
            print(f"{marker}{name:20s} {angle:6.1f}°   (диапазон {lim['min']}–{lim['max']})")
        print("-" * 50)
        print("Команды:")
        print("  w/s — выбрать сервопривод (вверх/вниз)")
        print(f"  a/d — уменьшить/увеличить угол на {STEP}°")
        print("  число — ввести угол напрямую (например 5)")
        print("  n — вернуть все в нейтраль (веки открыты, центр)")
        print("  e — тест эмоции (полная поза через интерпретатор)")
        print("  b — тест моргания (одиночное)")
        print("  bb — тест серии морганий (3 подряд)")
        print("  q — выход")
        print("=" * 50)

    def _clamp(self, servo: str, value: float) -> float:
        lim = self.limits[servo]
        return max(lim["min"], min(lim["max"], value))

    async def apply(self):
        angles = [self.pose[s] for s in SERVO_ORDER]
        try:
            await self.transport.send_pose(angles)
        except Exception as e:
            print(f"[ошибка отправки] {e}")

    async def test_emotion(self, loop):
        names = list(EMOTION_POSES.keys())
        print("\nДоступные эмоции:")
        for i, name in enumerate(names, 1):
            print(f"  {i}. {name}")

        choice = await loop.run_in_executor(None, input, "Номер? (Enter для отмены): ")
        choice = choice.strip()
        if not choice:
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
            print("Нет номера!")
            return

        emotion = names[int(choice) - 1]
        pose = calculate({emotion: 1.0}, functions=[], limits=self.limits)

        print(f"\n[тест] эмоция: {emotion}")
        print(f"[тест] углы: {pose}")

        self.pose = pose
        await self.apply()

    async def run(self):
        loop = asyncio.get_event_loop()

        while True:
            self.print_state()
            cmd = await loop.run_in_executor(None, input, "> ")
            cmd = cmd.strip().lower()

            if cmd == "q":
                break
            elif cmd == "w":
                self.selected = (self.selected - 1) % len(SERVO_ORDER)
            elif cmd == "s":
                self.selected = (self.selected + 1) % len(SERVO_ORDER)
            elif cmd == "a":
                servo = SERVO_ORDER[self.selected]
                self.pose[servo] = self._clamp(servo, self.pose[servo] - STEP)
                await self.apply()
            elif cmd == "d":
                servo = SERVO_ORDER[self.selected]
                self.pose[servo] = self._clamp(servo, self.pose[servo] + STEP)
                await self.apply()
            elif cmd == "n":
                self.pose = raw_neutral_pose(self.limits)
                await self.apply()
            elif cmd == "e":
                await self.test_emotion(loop)
            elif cmd == "b":
                try:
                    await self.transport.send_blink(times=1)
                except Exception as e:
                    print(f"[ошибка blink] {e}")
            elif cmd == "bb":
                try:
                    await self.transport.send_blink(times=3)
                except Exception as e:
                    print(f"[ошибка blink] {e}")
            elif cmd.lstrip("-").replace(".", "", 1).isdigit():
                servo = SERVO_ORDER[self.selected]
                self.pose[servo] = self._clamp(servo, float(cmd))
                await self.apply()
            else:
                print("Неизвестная команда")

        await self.transport.disconnect()


async def main():
    limits = load_limits()
    tuner = Tuner(limits)
    print("Подключение к ESP32...")
    try:
        await tuner.connect()
    except Exception as e:
        print(f"[ошибка] тип: {type(e).__name__}")
        print(f"[ошибка] repr: {e!r}")
        import traceback
        traceback.print_exc()
        return

    await tuner.run()


if __name__ == "__main__":
    asyncio.run(main())