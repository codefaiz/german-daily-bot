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

    if "result" in updates:
        for update in updates["result"]:
            offset = update["update_id"] + 1

            # -------- /start command --------
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                name = msg["from"].get("first_name", "Friend")

                if text == "/start":
                    welcome = (
                        f"👋 Hallo {name}!\n\n"
                        "🇩🇪 Willkommen beim German Daily Bot!\n"
                        "🇬🇧 Welcome to German Daily Bot!\n\n"
                        "📘 Start learning German step by step.\n"
                        "Click below to begin Day 1."
                    )

                    buttons = {
                        "inline_keyboard": [
                            [{"text": "📘 Start Day 1", "callback_data": "day1"}]
                        ]
                    }

                    send_message(chat_id, welcome, buttons)

            # -------- Button Click --------
            if "callback_query" in update:
                query = update["callback_query"]
                chat_id = query["message"]["chat"]["id"]
                data = query["data"]
                callback_id = query["id"]

                # stop loading animation
                answer_callback(callback_id)

                if data == "day1":
                    lesson = (
    "📘 <b>German Day 1 — Basics</b>\n\n"

    "👋 Greeting\n"
    "Hallo = Hello\n"
    "Pronunciation: HA-lo\n\n"

    "😊 Asking how someone is\n"
    "Wie geht es dir? = How are you?\n"
    "Pronunciation: Vee gayt es deer\n\n"

    "🌍 Asking origin\n"
    "Woher kommst du? = Where are you from?\n"
    "Pronunciation: Vo-hair komst doo\n\n"

    "🙋 Introducing yourself\n"
    "Ich bin Faizan. = I am Faizan.\n"
    "Pronunciation: Ikh bin Faizan\n\n"

    "🙏 Polite words\n"
    "Danke = Thank you\n"
    "Pronunciation: DAN-ke\n\n"
    "Bitte = Please / Welcome\n"
    "Pronunciation: BIT-te\n\n"

    "🗣 Practice Task\n"
    "Reply with:\n"
    "'Hallo, ich bin <your name>'\n\n"

    "✅ Day 1 Completed!"
)

                    send_message(chat_id, lesson)

    time.sleep(1)