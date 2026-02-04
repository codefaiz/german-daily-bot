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

            # Handle /start message
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                name = msg["from"].get("first_name", "Friend")

                if text == "/start":
                    welcome = (
                        f"👋 Welcome {name}!\n\n"
                        "🇩🇪 Welcome to German Daily Bot\n"
                        "🇬🇧 Learn German step by step.\n\n"
                        "Click below to start learning.\n"
                    )

                    buttons = {
                        "inline_keyboard": [
                            [{"text": "📘 Start Day 1", "callback_data": "day1"}]
                        ]
                    }

                    send_message(chat_id, welcome, buttons)

            # Handle button clicks
            if "callback_query" in update:
                query = update["callback_query"]
                chat_id = query["message"]["chat"]["id"]
                data = query["data"]

                if data == "day1":
                    lesson = (
                        "📘 <b>German Day 1</b>\n\n"
                        "Hallo = Hello\n"
                        "Pronunciation: HA-lo\n\n"
                        "Wie geht es dir? = How are you?\n"
                        "Pronunciation: Vee gayt es deer\n\n"
                        "Woher kommst du? = Where are you from?\n"
                        "Pronunciation: Vo-hair komst doo\n\n"
                        "Reply in German today! 🇩🇪"
                    )

                    send_message(chat_id, lesson)

    time.sleep(1)