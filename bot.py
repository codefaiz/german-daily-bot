import os
import requests
import time
import json

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, buttons=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if buttons:
        data["reply_markup"] = json.dumps(buttons)

    requests.post(BASE_URL + "/sendMessage", data=data)

def answer_callback(callback_id):
    requests.post(
        BASE_URL + "/answerCallbackQuery",
        data={"callback_query_id": callback_id}
    )

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    r = requests.get(BASE_URL + "/getUpdates", params=params)
    return r.json()

print("Bot running...")

offset = None

while True:
    updates = get_updates(offset)

    if updates.get("result"):
        for update in updates["result"]:
            offset = update["update_id"] + 1

            # ---- Handle button clicks FIRST ----
if "callback_query" in update:
    query = update["callback_query"]
    callback_id = query["id"]
    chat_id = query["message"]["chat"]["id"]
    data = query["data"]

    # SAFE name extraction
    user = query.get("from", {})
    name = user.get("first_name") or "Friend"

    answer_callback(callback_id)

    if data == "day1":
        lesson = (
            "📘 <b>German Day 1 — Basics</b>\n\n"
            "Hallo = Hello\n"
            "Pronunciation: HA-lo\n\n"

            "Wie geht es dir? = How are you?\n"
            "Pronunciation: Vee gayt es deer\n\n"

            "Woher kommst du? = Where are you from?\n"
            "Pronunciation: Vo-hair komst doo\n\n"

            f"Ich bin {name}. = I am {name}.\n"
            "Pronunciation: Ikh bin <your name>\n\n"

            "Danke = Thank you\n"
            "Bitte = Please\n\n"

            "✅ Day 1 Completed!"
        )

        send_message(chat_id, lesson)

    time.sleep(1)