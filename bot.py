import os
import json
import requests
import time

# -----------------------------
# Load environment variables
# -----------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# -----------------------------
# Load lessons from JSON
# -----------------------------
with open("lessons.json", "r", encoding="utf-8") as f:
    LESSONS = json.load(f)

# -----------------------------
# Helper functions
# -----------------------------
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

# -----------------------------
# Lesson rendering
# -----------------------------
def format_lesson(day_key):
    day = LESSONS[day_key]
    text = f"📘 <b>{day['title']}</b>\n\n"
    
    for idx, word in enumerate(day["words"], 1):
        text += f"{idx}️⃣ <b>{word['word']}</b>\n"
        text += f"{word['meaning']}\n"
        text += f"<code>Pronunciation:</code> {word['pronunciation']}\n"
        text += f"<i>Example:</i> {word['example']}\n\n"
    
    text += "📝 <b>Practice Tips:</b>\n"
    for tip in day["practice_tips"]:
        text += f"• {tip}\n"

    return text

def format_quiz(day_key):
    day = LESSONS[day_key]
    text = f"📝 <b>{day['title']} Mini Quiz</b>\n\n"
    for idx, q in enumerate(day["quiz"], 1):
        text += f"{idx}️⃣ {q}\n"
    text += "\nReply in chat with your answers!"
    return text

# -----------------------------
# Bot main loop
# -----------------------------
print("🤖 German Daily Bot running...")
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

            # -------- Day Lesson --------
            if data.startswith("day"):
                lesson_text = format_lesson(data)
                send_message(chat_id, lesson_text)

                # Next buttons: Quiz + Next Day
                day_number = int(data.replace("day", ""))
                next_day_key = f"day{day_number + 1}"
                buttons = [
                    [{"text": "📝 Take Mini Quiz", "callback_data": f"quiz_{data}"}]
                ]
                if next_day_key in LESSONS:
                    buttons[0].append({"text": "➡ Next Day", "callback_data": next_day_key})

                send_message(chat_id, "✅ Ready for a mini quiz or next lesson? Click below:", {"inline_keyboard": buttons})

            # -------- Quiz --------
            elif data.startswith("quiz_day"):
                day_key = data.replace("quiz_", "")
                quiz_text = format_quiz(day_key)
                send_message(chat_id, quiz_text)