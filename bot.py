import os
import requests
import time
import json

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if buttons:
        payload["reply_markup"] = json.dumps(buttons)

    requests.post(BASE_URL + "/sendMessage", data=payload)

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
                        "Ich bin Faizan. = I am Faizan.\n"
                        "Pronunciation: Ikh bin Faizan\n\n"
                        "Danke = Thank you\n"
                        "Bitte = Please\n\n"
                        "✅ Day 1 Completed!"
                    )

                    send_message(chat_id, lesson)

            # ---- Handle messages ----
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                name = msg["from"].get("first_name", "Friend")

                if text == "/start":
                    welcome = (
                        f"👋 Hallo {name}!\n\n"
                        "🇩🇪 Willkommen beim German Daily Bot\n"
                        "🇬🇧 Welcome to German Daily Bot\n\n"
                        "Click below to begin learning."
                    )

                    buttons = {
                        "inline_keyboard": [
                            [{"text": "📘 Start Day 1", "callback_data": "day1"}]
                        ]
                    }

                    send_message(chat_id, welcome, buttons)

    time.sleep(1)