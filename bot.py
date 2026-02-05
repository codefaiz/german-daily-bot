import os
import json
import requests

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Load lessons
with open("lessons.json", "r", encoding="utf-8") as f:
    LESSONS = json.load(f)

# Temporary session memory
USER_STATE = {}

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

# ---------------- Lesson formatting ----------------
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
        [{"text": "✍ Practice", "callback_data": f"practice_{day_key}"}],
        [{"text": "📝 Quiz", "callback_data": f"quiz_{day_key}"}],
        row
    ]

    return {"inline_keyboard": keyboard}

# ---------------- Quiz ----------------
def quiz_buttons(day_key, index):
    q = LESSONS[day_key]["quiz"][index]

    buttons = [
        [{"text": opt,
          "callback_data": f"quizans_{day_key}_{index}_{opt}"}]
        for opt in q["options"]
    ]

    return {"inline_keyboard": buttons}

# ---------------- Bot loop ----------------
print("Bot running...")
offset = None

while True:
    updates = get_updates(offset)

    for update in updates.get("result", []):
        offset = update["update_id"] + 1

        # -------- Message handling --------
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            text = msg.get("text", "")

            # Practice answer handling
            state = USER_STATE.get(user_id)

            if state and state["mode"] == "practice":
                day_key = state["day"]
                practice = LESSONS[day_key]["practice"]

                keywords = practice["expected_keywords"]

                if all(k.lower() in text.lower() for k in keywords):
                    send_message(chat_id,
                                 "✅ Good answer!\nKeep practicing aloud.")
                else:
                    send_message(
                        chat_id,
                        f"⚠ Try again.\nHint: {practice['hint']}"
                    )

                USER_STATE.pop(user_id, None)

        # -------- Callback handling --------
        if "callback_query" in update:
            query = update["callback_query"]
            data = query["data"]
            chat_id = query["message"]["chat"]["id"]
            user_id = query["from"]["id"]

            answer_callback(query["id"])

            # Show lesson
            if data.startswith("day"):
                lesson_text = format_lesson(data)
                send_message(chat_id,
                             lesson_text,
                             lesson_buttons(data))

            # Practice mode
            elif data.startswith("practice_"):
                day_key = data.replace("practice_", "")
                practice = LESSONS[day_key]["practice"]

                USER_STATE[user_id] = {
                    "mode": "practice",
                    "day": day_key
                }

                send_message(
                    chat_id,
                    f"✍ <b>Practice Time</b>\n\n"
                    f"{practice['question']}\n\n"
                    f"{practice['instruction']}"
                )

            # Quiz start
            elif data.startswith("quiz_day"):
                day_key = data.replace("quiz_", "")
                USER_STATE[user_id] = {
                    "mode": "quiz",
                    "day": day_key,
                    "index": 0
                }

                q = LESSONS[day_key]["quiz"][0]

                send_message(
                    chat_id,
                    f"📝 <b>Quiz</b>\n\n{q['question']}",
                    quiz_buttons(day_key, 0)
                )

            # Quiz answers
            elif data.startswith("quizans_"):
                _, day_key, idx, answer = data.split("_", 3)
                idx = int(idx)

                correct = LESSONS[day_key]["quiz"][idx]["correct"]

                if answer == correct:
                    send_message(chat_id, "✅ Correct!")
                else:
                    send_message(chat_id,
                                 f"❌ Correct answer: {correct}")

                next_idx = idx + 1
                quiz_list = LESSONS[day_key]["quiz"]

                if next_idx < len(quiz_list):
                    q = quiz_list[next_idx]
                    send_message(
                        chat_id,
                        q["question"],
                        quiz_buttons(day_key, next_idx)
                    )
                else:
                    send_message(chat_id,
                                 "🎉 Quiz completed!\nSelect next lesson.")