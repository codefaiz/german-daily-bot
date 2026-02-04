import os
import requests
import time
import json

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if buttons:
        payload["reply_markup"] = json.dumps(buttons)

    try:
        r = requests.post(f"{BASE_URL}/sendMessage", data=payload, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("Send message error:", e)


def answer_callback(callback_id):
    try:
        requests.post(
            f"{BASE_URL}/answerCallbackQuery",
            data={"callback_query_id": callback_id},
            timeout=5
        )
    except requests.RequestException as e:
        print("Callback error:", e)


def get_updates(offset=None):
    try:
        params = {"timeout": 100, "offset": offset}
        r = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=110)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print("Get updates error:", e)
        return {}


print("🤖 Bot running...")
offset = None

while True:
    updates = get_updates(offset)

    for update in updates.get("result", []):
        offset = update["update_id"] + 1

        # -------- Messages --------
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

        # -------- Callback Queries --------
        if "callback_query" in update:
            query = update["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            data = query["data"]

            answer_callback(query["id"])

            if data == "day1":
                lesson = (
                    "📘 <b>German Day 1</b>\n\n"
                    "<b>Hallo</b> = Hello\n"
                    "Pronunciation: HA-lo\n\n"
                    "<b>Wie geht es dir?</b> = How are you?\n"
                    "Pronunciation: Vee gayt es deer\n\n"
                    "<b>Woher kommst du?</b> = Where are you from?\n"
                    "Pronunciation: Vo-hair komst doo\n\n"
                    "🗣 Practice speaking today!"
                )

                send_message(chat_id, lesson)
