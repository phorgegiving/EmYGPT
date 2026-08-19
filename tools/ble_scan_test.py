import asyncio
from bleak import BleakScanner


async def scan():
    print("Скан эфира ble... (10 секунд)")
    devices = await BleakScanner.discover(timeout=10.0)

    if not devices:
        print("Ни одного ble устройства не найдено =(")
        print("Точно ли включён ли bluetooth на компьютере, работает ли ESP32?")
        return

    print(f"Найдено устройств: {len(devices)}\n")
    for d in devices:
        name = d.name or "(без имени)"
        marker = " <-- ЭТО ESP32" if name == "AnimatronicHead" else ""
        print(f"  {d.address}  {name}{marker}")


if __name__ == "__main__":
    asyncio.run(scan())