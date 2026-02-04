import os
import requests
import time
import json

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ================= FUNCTIONS =================
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

# ================= BOT LOOP =================
print("🤖 German Daily Bot is running...")
offset = None

while True:
    updates = get_updates(offset)

    for update in updates.get("result", []):
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
                    "🇩🇪 Willkommen beim German Daily Bot\n"
                    "🇬🇧 Welcome to German Daily Bot\n\n"
                    "📘 Learn German step by step.\n"
                    "Click below to begin Day 1."
                )

                buttons = {
                    "inline_keyboard": [
                        [{"text": "📘 Start Day 1", "callback_data": "day1"}]
                    ]
                }

                send_message(chat_id, welcome, buttons)

        # -------- Button click --------
        if "callback_query" in update:
            query = update["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            data = query["data"]

            answer_callback(query["id"])

            if data == "day1":
                lesson = (
                    "📘 <b>German – Day 1: Basics</b>\n\n"

                    "👋 <b>Greeting</b>\n"
                    "<b>Hallo</b> = Hello\n"
                    "Pronunciation: <i>HA-lo</i>\n\n"

                    "💬 <b>How are you?</b>\n"
                    "<b>Wie geht es dir?</b> = How are you?\n"
                    "Pronunciation: <i>Vee gayt es deer</i>\n\n"

                    "🙂 <b>Common answers</b>\n"
                    "<b>Mir geht es gut</b> = I am fine\n"
                    "Pronunciation: <i>Meer gayt es goot</i>\n\n"

                    "<b>Es geht</b> = So-so / Not bad\n"
                    "Pronunciation: <i>Es gayt</i>\n\n"

                    "🌍 <b>Where are you from?</b>\n"
                    "<b>Woher kommst du?</b> = Where are you from?\n"
                    "Pronunciation: <i>Vo-hair komst doo</i>\n\n"

                    "🧑 <b>I am from…</b>\n"
                    "<b>Ich komme aus Indien</b> = I am from India\n"
                    "Pronunciation: <i>Ikh komme aus In-dee-en</i>\n\n"

                    "📝 <b>Practice (say aloud)</b>\n"
                    "➡ Hallo!\n"
                    "➡ Wie geht es dir?\n"
                    "➡ Ich komme aus ____\n\n"

                    "👏 Great job! You completed Day 1."
                )

                send_message(chat_id, lesson)

    # Long polling already waits — no extra sleep needed
