"""
тюнер сервоприводов.
позволяет двигать каждый сервопривод по отдельности и подбирать лимиты.

Запуск: python -m tools.servo_tuner  (из корня проекта)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from host.interpreter.transport import HeadTransport
from host.interpreter.emotion_map import SERVO_ORDER, NEUTRAL_POSE

STEP = 5  # градусов за одно нажатие

RUSSIAN_NAMES = {
    "eyes_pan": "Глаза — гор.",
    "eyes_tilt": "Глаза — верт.",
    "lid_tl": "Веко верх-лев",
    "lid_tr": "Веко верх-прав",
    "lid_bl": "Веко низ-лев",
    "lid_br": "Веко низ-прав",
    "mouth": "Рот",
}


class Tuner:
    def __init__(self):
        self.pose = dict(NEUTRAL_POSE)
        self.selected = 0 
        self.transport = HeadTransport()

    async def connect(self):
        await self.transport.connect()
        await self.transport.send_center()

    def print_state(self):
        print("\n" + "=" * 50)
        print("SERVO TUNER — управление сервоприводами")
        print("=" * 50)
        for i, servo in enumerate(SERVO_ORDER):
            marker = "→ " if i == self.selected else "  "
            name = RUSSIAN_NAMES.get(servo, servo)
            angle = self.pose[servo]
            print(f"{marker}{name:20s} {angle:6.1f}°   ({servo})")
        print("-" * 50)
        print("Команды:")
        print("  w/s — выбрать сервопривод (вверх/вниз)")
        print("  a/d — уменьшить/увеличить угол")
        print("  число — ввести угол напрямую (например 90)")
        print("  c — центрировать всё")
        print("  q — выход")
        print("=" * 50)

    async def apply(self):
        angles = [self.pose[s] for s in SERVO_ORDER]
        try:
            await self.transport.send_pose(angles)
        except Exception as e:
            print(f"[ошибка отправки] {e}")

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
                self.pose[servo] = max(0, self.pose[servo] - STEP)
                await self.apply()
            elif cmd == "d":
                servo = SERVO_ORDER[self.selected]
                self.pose[servo] = min(180, self.pose[servo] + STEP)
                await self.apply()
            elif cmd == "c":
                self.pose = dict(NEUTRAL_POSE)
                await self.transport.send_center()
            elif cmd.lstrip("-").isdigit():
                servo = SERVO_ORDER[self.selected]
                self.pose[servo] = max(0, min(180, int(cmd)))
                await self.apply()
            else:
                print("Неизвестная команда")

        await self.transport.disconnect()


async def main():
    tuner = Tuner()
    print("Подключение к ESP32...")
    try:
        await tuner.connect()
    except Exception as e:
        print(f"[ошибка] {e}")
        return

    await tuner.run()


if __name__ == "__main__":
    asyncio.run(main())