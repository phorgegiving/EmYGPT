from host.llm.yandex_client import ask
from host.llm.prompt_builder import build_messages
from host.data_layer.persona import load_persona
from host.data_layer.history import History
from host.data_layer.state_control import EmotionState


def main():
    persona = load_persona()
    history = History()
    emotion_state = EmotionState()

    print(f"{persona['name']} готов. Собщение?\n")

    while True:
        try:
            user_input = input("Вы: ").strip()
        except KeyboardInterrupt:
            print("Выход.")
            break

        if not user_input:
            continue

        messages = build_messages(persona, history.get(), user_input)

        try:
            response = ask(messages)
        except Exception as e:
            print(f"[ошибка LLM] {e}")
            continue

        emotion_state.update(response.get("emotions", {}))
        history.add(user_input, response)

        print(f"\n{persona['name']}: {response['text']}")
        print(f"  эмоции: {emotion_state.dominant()} | {response.get('functions', [])}\n")


if __name__ == "__main__":
    main()