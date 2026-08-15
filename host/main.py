from host.llm.yandex_client import ask
from host.llm.prompt_builder import build_messages
from host.llm.memory import Memory
from host.data_layer.persona import load_persona
from host.data_layer.history import History
from host.data_layer.state_control import EmotionState


def main():
    persona = load_persona()
    history = History()
    emotion_state = EmotionState()
    memory = Memory()
    print(Memory.as_text(memory))
 
    print(f"[{persona['name']}] готов.")
    facts = memory.get_facts()
 
    while True:
        try:
            user_input = input("Вы: ").strip()
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
 
        print(f"\n{persona['name']}: {response['text']}")
        print(f"  эмоции: {emotion_state.dominant()} | functions: {response.get('functions', [])}\n")
 
 
if __name__ == "__main__":
    main()