import os
import requests
import json
import time
import base64

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_FILE = os.getenv("GITHUB_FILE", "users.json")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ---------------- GITHUB FUNCTIONS ----------------
def get_users():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    print("GitHub fetch status:", r.status_code)
    print("GitHub response:", r.text)
    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode()
    sha = data["sha"]
    return json.loads(content), sha


def update_users(users, sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    new_content = base64.b64encode(json.dumps(users, indent=2).encode()).decode()
    payload = {
        "message": "Update user progress",
        "content": new_content,
        "sha": sha,
        "branch": GITHUB_BRANCH
    }
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()["content"]["sha"]

# ---------------- TELEGRAM FUNCTIONS ----------------
def send_message(chat_id, text, buttons=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        data["reply_markup"] = json.dumps(buttons)
    try:
        r = requests.post(BASE_URL + "/sendMessage", data=data, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("Send message error:", e)

def answer_callback(callback_id):
    try:
        requests.post(BASE_URL + "/answerCallbackQuery", data={"callback_query_id": callback_id}, timeout=5)
    except requests.RequestException as e:
        print("Callback error:", e)

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    try:
        r = requests.get(BASE_URL + "/getUpdates", params=params, timeout=110)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print("Get updates error:", e)
        return {}

# ---------------- BOT LOOP ----------------
print("🤖 German Daily Bot running...")
offset = None

while True:
    try:
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
                    buttons = {"inline_keyboard":[[{"text":"📘 Start Day 1","callback_data":"day1"}]]}
                    send_message(chat_id, welcome, buttons)

            # -------- Callback queries --------
            if "callback_query" in update:
                query = update["callback_query"]
                chat_id = query["message"]["chat"]["id"]
                data = query["data"]
                callback_id = query["id"]

                # Stop button loading animation immediately
                answer_callback(callback_id)

                if data == "day1":
                    # Fetch users.json from GitHub safely
                    try:
                        users, sha = get_users()
                    except Exception as e:
                        send_message(chat_id, "⚠️ Sorry, something went wrong. Please try again later.")
                        print("GitHub fetch error:", e)
                        continue

                    # Send Day 1 lesson
                    lesson = (
                        "📘 <b>German – Day 1: Basics</b>\n\n"
                        "👋 <b>Greeting</b>\n<b>Hallo</b> = Hello\nPronunciation: <i>HA-lo</i>\n\n"
                        "💬 <b>How are you?</b>\n<b>Wie geht es dir?</b> = How are you?\nPronunciation: <i>Vee gayt es deer</i>\n\n"
                        "🙂 <b>Common answers</b>\n<b>Mir geht es gut</b> = I am fine\nPronunciation: <i>Meer gayt es goot</i>\n\n"
                        "<b>Es geht</b> = So-so / Not bad\nPronunciation: <i>Es gayt</i>\n\n"
                        "🌍 <b>Where are you from?</b>\n<b>Woher kommst du?</b> = Where are you from?\nPronunciation: <i>Vo-hair komst doo</i>\n\n"
                        "🧑 <b>I am from…</b>\n<b>Ich komme aus Indien</b> = I am from India\nPronunciation: <i>Ikh komme aus In-dee-en</i>\n\n"
                        "📝 <b>Practice (say aloud)</b>\n➡ Hallo!\n➡ Wie geht es dir?\n➡ Ich komme aus ____\n\n"
                        "👏 Great job! You completed Day 1."
                    )
                    send_message(chat_id, lesson)

                    # Update GitHub progress safely
                    try:
                        users[str(chat_id)] = {"day":1, "last_active": time.strftime("%Y-%m-%d")}
                        sha = update_users(users, sha)
                    except Exception as e:
                        print("GitHub update error:", e)

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
