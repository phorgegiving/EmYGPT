import os
import json
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
 
 
def ask(messages: list[dict]) -> dict:
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 200,
        },
        "messages": messages,
    }
 
    response = requests.post(YANDEX_API_URL, headers=headers, json=body, timeout=15)
    response.raise_for_status()
 
    raw_text = response.json()["result"]["alternatives"][0]["message"]["text"]
 
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:

        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        return json.loads(raw_text[start:end])