import json
 
SYSTEM_PROMPT = """\
Ты аниматронный персонаж по имени {name}. Характер: {style}. Память: {memory}
 
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
  "functions": []
}}
 
Правила:
- Сумма всех эмоций = 1.0
- functions может содержать: "blink", "look_up", "look_down", "look_left", "look_right", "idle"
- text — живой разговорный ответ, не более 2-3 предложений
"""
 
 
def build_messages(persona: dict, history: list[dict], user_input: str) -> list[dict]:
    system_text = SYSTEM_PROMPT.format(
        name=persona["name"],
        style=persona["style"],
        memory=persona["memory"]
    )
 
    messages = [{"role": "system", "text": system_text}]
 
    for turn in history:
        messages.append({"role": "user", "text": turn["user"]})
        messages.append({"role": "assistant", "text": json.dumps(turn["assistant"], ensure_ascii=False)})
 
    messages.append({"role": "user", "text": user_input})
    return messages