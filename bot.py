import os
import requests
import time

TOKEN = os.getenv("BOT_TOKEN")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    r = requests.get(url, params=params)
    return r.json()

print("Bot running...")

offset = None

while True:
    updates = get_updates(offset)

    if "result" in updates:
        for update in updates["result"]:
            offset = update["update_id"] + 1

            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")

                if text == "/start":
                    lesson = (
                        "🇩🇪 German Daily Bot\n\n"
                        "Hallo = Hello\n"
                        "Ich bin = I am\n"
                        "Danke = Thank you\n"
                    )
                    send_message(chat_id, lesson)

    time.sleep(1)