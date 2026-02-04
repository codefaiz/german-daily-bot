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
                    f"👋 <b>Hallo {name}!</b>\n\n"
                    "🇩🇪 Willkommen beim <b>German Daily Bot</b>\n"
                    "🇬🇧 Welcome to <b>German Daily Bot</b>\n\n"
                    "📘 Start learning German step by step.\n"
                    "Click the button below to begin <b>Day 1</b>."
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

            # -------- Day 1 Lesson --------
            if data == "day1":
                lesson = (
                    "📘 <b>German Day 1</b>\n\n"
                    "1️⃣ <b>Hallo</b> = Hello\n"
                    "<code>Pronunciation:</code> HA-lo\n"
                    "<i>Example:</i> Hallo! Wie geht's? = Hello! How are you? (HA-lo! Vee gayt es geets?)\n\n"
                    "2️⃣ <b>Wie geht es dir?</b> = How are you?\n"
                    "<code>Pronunciation:</code> Vee gayt es deer\n"
                    "<i>Example:</i> Wie geht es dir heute? = How are you today? (Vee gayt es deer hoy-te?)\n\n"
                    "3️⃣ <b>Woher kommst du?</b> = Where are you from?\n"
                    "<code>Pronunciation:</code> Vo-hair komst doo\n"
                    "<i>Example:</i> Woher kommst du? Ich komme aus Deutschland. = Where are you from? I come from Germany. "
                    "(Vo-hair komst doo? Ish komme ous Dooych-lahnd.)\n\n"
                    "📝 <b>Practice Tips:</b>\n"
                    "• Say each sentence aloud 3 times\n"
                    "• Try greeting a friend in German\n"
                    "• Write your own answer to “Woher kommst du?” in German\n"
                )

                send_message(chat_id, lesson)

                # Quiz button separately
                quiz_button = {
                    "inline_keyboard": [
                        [{"text": "📝 Take Mini Quiz", "callback_data": "quiz_day1"}]
                    ]
                }
                send_message(chat_id, "✅ Ready for a mini quiz? Click below when you are ready!", quiz_button)

            # -------- Day 1 Quiz --------
            elif data == "quiz_day1":
                quiz = (
                    "📝 <b>Day 1 Mini Quiz</b>\n\n"
                    "1️⃣ How do you say 'Hello' in German?\n"
                    "2️⃣ How do you ask 'How are you?' in German?\n"
                    "3️⃣ How do you ask someone where they are from in German?\n\n"
                    "Reply in chat with your answers!"
                )
                send_message(chat_id, quiz)
