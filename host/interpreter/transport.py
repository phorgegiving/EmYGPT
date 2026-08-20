import asyncio
import json
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "AnimatronicHead"
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
CHAR_UUID = "abcdefab-cdef-abcd-efab-cdefabcdefab"


class HeadTransport:
    def __init__(self):
        self._client: BleakClient | None = None
        self._address: str | None = None

    async def connect(self, timeout: float = 10.0, retries: int = 3):
        print(f"[BLE] поиск устройства '{DEVICE_NAME}'...")
        device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=timeout)

        if device is None:
            raise RuntimeError(f"Устройство '{DEVICE_NAME}' не найдено. Проверь что ESP32 включена и рекламируется.")

        self._address = device.address

        last_error = None
        for attempt in range(1, retries + 1):
            self._client = BleakClient(device)
            try:
                print(f"[BLE] подключение (попытка {attempt}/{retries})...")
                await self._client.connect(timeout=timeout)
                print(f"[BLE] подключено к {self._address}")
                return
            except Exception as e:
                last_error = e
                print(f"[BLE] попытка {attempt} не удалась: {type(e).__name__}: {e!r}")
                try:
                    await self._client.disconnect()
                except Exception:
                    pass
                await asyncio.sleep(1.5)

        raise RuntimeError(
            f"Не удалось подключиться за {retries} попыток. "
            f"Последняя ошибка: {type(last_error).__name__}: {last_error!r}"
        )

    async def disconnect(self):
        if self._client and self._client.is_connected:
            await self._client.disconnect()
            print("[BLE] отключено")

    async def send_pose(self, angles: list[float]):
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE не подключён. Вызови connect() сначала.")

        payload = json.dumps({"s": angles})
        await self._client.write_gatt_char(CHAR_UUID, payload.encode("utf-8"))

    async def send_center(self):
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE не подключён.")

        payload = json.dumps({"cmd": "center"})
        await self._client.write_gatt_char(CHAR_UUID, payload.encode("utf-8"))

    async def send_blink(self, times: int = 1):
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE не подключён.")

        payload = json.dumps({"cmd": "blink", "times": times})
        await self._client.write_gatt_char(CHAR_UUID, payload.encode("utf-8"))

    async def send_mouth(self, angle: float):
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE не подключён.")

        payload = json.dumps({"m": round(angle, 1)})
        await self._client.write_gatt_char(
            CHAR_UUID, payload.encode("utf-8"), response=False
        )

    @property
    def is_connected(self) -> bool:
        return bool(self._client and self._client.is_connected)


async def _test(): # (ble transport test)
    transport = HeadTransport()
    await transport.connect()
    await transport.send_center()
    await asyncio.sleep(1)
    await transport.send_pose([110, 90, 35, 35, 10, 10, 20])
    await asyncio.sleep(2)
    await transport.send_center()
    await transport.disconnect()


if __name__ == "__main__":
    asyncio.run(_test())