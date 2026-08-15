import json
 
SYSTEM_PROMPT = """\
Ты аниматронный персонаж по имени {name}. Характер: {style}. Твои установки: {memory}.

{memory_block}

{history_block}
 
 
Отвечай ТОЛЬКО валидным JSON без каких-либо пояснений вокруг него, без эмодзи:
{{
  "text": "твой ответ пользователю",
  "emotions": {{
    "happy": 0.0,
    "sad": 0.0,
    "angry": 0.0,
    "surprised": 0.0,
    "fear": 0.0,
    "disgust": 0.0,
    "neutral": 1.0
  }},
  "functions": [],
  "remember": ""
}}
 
Правила:
- Сумма всех эмоций = 1.0
- functions может содержать: "blink", "look_up", "look_down", "look_left", "look_right", "idle"
- text — живой разговорный ответ, не более 2-3 предложений
- remember — если пользователь сообщил что-то важное о себе (имя, профессия, интересы, цели), \
запиши это одной максимально короткой фразой. Если запоминать нечего - оставь пустой строкой "".
"""
 
 
def _format_history(history: list[dict]) -> str:
    if not history:
        return ""
 
    lines = ["=== ИСТОРИЯ РАЗГОВОРА (от старых к новым) ==="]
    for i, turn in enumerate(history, 1):
        lines.append(f"[{i}] Пользователь: {turn['user']}")
        assistant_text = turn["assistant"].get("text", "")
        lines.append(f"[{i}] Ты ответил: {assistant_text}")
    lines.append("=== КОНЕЦ ИСТОРИИ ===")
    return "\n".join(lines)
 
 
def build_messages(
    persona: dict,
    history: list[dict],
    user_input: str,
    memory_text: str = "",
) -> list[dict]:
 
    system_text = SYSTEM_PROMPT.format(
        name=persona["name"],
        style=persona["style"],
        memory=persona.get("memory", ""),
        memory_block=memory_text,
        history_block=_format_history(history),
    )
 
    return [
        {"role": "system", "text": system_text},
        {"role": "user", "text": user_input},
    ]