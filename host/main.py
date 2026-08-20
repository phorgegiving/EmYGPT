import asyncio
import yaml
from pathlib import Path

from host.llm.yandex_client import ask
from host.llm.prompt_builder import build_messages
from host.llm.memory import Memory
from host.data_layer.persona import load_persona
from host.data_layer.history import History
from host.data_layer.state_control import EmotionState
from host.interpreter.transport import HeadTransport
from host.interpreter.servo_calc import calculate, to_array
from host.tts.engine import warmup, synthesize
from host.tts.playback import speak_with_lipsync


LIMITS_PATH = Path(__file__).parent.parent / "config" / "servo_limits.yaml"
LLM_BLINK_TIMES = 2
 
 
def load_limits() -> dict:
    with open(LIMITS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)
 
 
async def main():
    persona = load_persona()
    history = History()
    emotion_state = EmotionState()
    memory = Memory()
    limits = load_limits()
 
    transport = HeadTransport()
    connected = False
    try:
        await transport.connect(timeout=5.0)
        connected = True
    except Exception as e:
        print(f"[BLE] не удалось подключиться: {e}")
        print("[BLE] продолжаем в текстовом режиме (без движения)")
 
    print(f"[{persona['name']}] готов. Введите сообщение (ctrl+c для выхода).")
    facts = memory.get_facts()
    if facts:
        print(f"  загружено фактов из памяти: {len(facts)}")

            # прогрев
    print("[TTS] прогрев модели...")
    await asyncio.get_event_loop().run_in_executor(None, warmup)
    print()
 
    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Вы: ")
            user_input = user_input.strip()
        except KeyboardInterrupt:
            print("Выход.")
            break
 
        if not user_input:
            continue

        messages = build_messages(
            persona=persona,
            history=history.get(),
            user_input=user_input,
            memory_text=memory.as_text(),
        )
 
        try:
            response = ask(messages)
        except Exception as e:
            print(f"[ошибка LLM] {e}")
            continue
 
        remember = response.get("remember", "").strip()
        if remember:
            memory.add_fact(remember)
            print(f"  [память] запомнено: {remember}")
 
        emotion_state.update(response.get("emotions", {}))
        history.add(user_input, response)
 
        functions = response.get("functions", [])
        pose = calculate(emotion_state.get(), functions, limits)
 
        if connected:
            try:
                await transport.send_pose(to_array(pose))
            except Exception as e:
                print(f"[BLE] ошибка отправки: {e}")

            if "blink" in functions:
                try:
                    await transport.send_blink(times=LLM_BLINK_TIMES)
                except Exception as e:
                    print(f"[BLE] ошибка отправки blink: {e}")
 
        try:
            audio, sample_rate = await asyncio.get_event_loop().run_in_executor(
                None, synthesize, response["text"]
            )
            await speak_with_lipsync(
                audio=audio,
                sample_rate=sample_rate,
                base_pose=pose,
                limits=limits,
                transport=transport,
                connected=connected,
            )
        except Exception as e:
            print(f"[TTS] ошибка озвучки: {e}")

        print(f"\n{persona['name']}: {response['text']}")
        print(f"  эмоции: {emotion_state.dominant()} | functions: {functions}")
        print(f"  поза: {pose}\n")
 
    if connected:
        await transport.disconnect()
 
 
if __name__ == "__main__":
    asyncio.run(main())