import os
import json
import requests

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

LESSONS_FILE = "lessons.json"
PROGRESS_FILE = "progress.json"

# Load lessons
with open(LESSONS_FILE, "r", encoding="utf-8") as f:
    LESSONS = json.load(f)

# Load or create progress storage
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        USER_PROGRESS = json.load(f)
else:
    USER_PROGRESS = {}

def save_progress():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_PROGRESS, f, indent=2)
        f.flush()

def set_progress(user_id, day):
    USER_PROGRESS[str(user_id)] = day
    save_progress()
    print("Progress saved:", user_id, day)

def get_progress(user_id):
    return USER_PROGRESS.get(str(user_id), "day1")

# ---------------- Telegram helpers ----------------
def send_message(chat_id, text, buttons=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if buttons:
        payload["reply_markup"] = json.dumps(buttons)

    requests.post(f"{BASE_URL}/sendMessage", data=payload)

def answer_callback(callback_id):
    requests.post(
        f"{BASE_URL}/answerCallbackQuery",
        data={"callback_query_id": callback_id}
    )

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    r = requests.get(f"{BASE_URL}/getUpdates", params=params)
    return r.json()

# ---------------- Lesson format ----------------
def format_lesson(day_key):
    day = LESSONS[day_key]

    text = f"📘 <b>{day['title']}</b>\n\n"

    for i, w in enumerate(day["words"], 1):
        text += (
            f"{i}️⃣ <b>{w['word']}</b>\n"
            f"{w['meaning']}\n"
            f"<code>Pronunciation:</code> {w['pronunciation']}\n"
            f"<i>Example:</i> {w['example']}\n\n"
        )

    text += "📝 <b>Practice Tips:</b>\n"
    for tip in day["practice_tips"]:
        text += f"• {tip}\n"

    return text

def format_quiz(day_key):
    day = LESSONS[day_key]
    text = f"📝 <b>{day['title']} Quiz</b>\n\n"

    for i, q in enumerate(day["quiz"], 1):
        text += f"{i}️⃣ {q}\n"

    text += "\nReply with your answers!"
    return text

def lesson_buttons(day_key):
    day_num = int(day_key.replace("day", ""))
    prev_day = f"day{day_num-1}"
    next_day = f"day{day_num+1}"

    row = []

    if prev_day in LESSONS:
        row.append({"text": "⬅ Previous", "callback_data": prev_day})

    if next_day in LESSONS:
        row.append({"text": "➡ Next", "callback_data": next_day})

    keyboard = [
        [{"text": "📝 Quiz", "callback_data": f"quiz_{day_key}"}],
        row
    ]

    return {"inline_keyboard": keyboard}

# ---------------- Bot loop ----------------
print("Bot running...")
offset = None

while True:
    updates = get_updates(offset)

    for update in updates.get("result", []):
        offset = update["update_id"] + 1

        # -------- Message --------
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")
            name = msg["from"].get("first_name", "Friend")

            if text == "/start":
                current_day = get_progress(user_id)

                welcome = (
                    f"👋 <b>Hallo {name}!</b>\n\n"
                    "Welcome to German Daily Bot.\n\n"
                    "Continue your lesson below."
                )

                buttons = {
                    "inline_keyboard": [
                        [{"text": "▶ Continue Lesson",
                          "callback_data": current_day}]
                    ]
                }

                send_message(chat_id, welcome, buttons)

        # -------- Callback --------
        if "callback_query" in update:
            query = update["callback_query"]
            data = query["data"]
            chat_id = query["message"]["chat"]["id"]
            user_id = query["from"]["id"]

            answer_callback(query["id"])

            # Show lesson
            if data.startswith("day"):
    print("Opening lesson:", data, "for user:", user_id)
    set_progress(user_id, data)

                lesson_text = format_lesson(data)
                send_message(chat_id, lesson_text,
                             lesson_buttons(data))

            # Show quiz
            elif data.startswith("quiz_day"):
                day_key = data.replace("quiz_", "")
                send_message(chat_id, format_quiz(day_key))