from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)
app.secret_key = "chatdevotion-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Kullanıcı verisi
user_data = {}

# Örnek veri
with open("data/gpt_context_data.json", "r", encoding="utf-8") as f:
    gpt_context = json.load(f)

# Öneriler
with open("data/suggestions.json", "r", encoding="utf-8") as f:
    all_suggestions = json.load(f)

THERAPEUTIC_PROMPT = "You are a compassionate mental health assistant who listens without judgment and offers thoughtful reflections to help users better understand their emotional state."

def analyze_with_gpt(text, lang="tr"):
    if lang == "en":
        prompt = f"Analyze the following emotional message and offer a thoughtful, empathetic reflection in English:\n{text}"
    else:
        prompt = f"Aşağıdaki duygusal metni analiz et ve empatik, düşünceli bir psikolojik değerlendirme sun:\n{text}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": THERAPEUTIC_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def detect_emotion(analysis_text):
    keywords = {
        "motivation": ["motivasyon", "hedef", "ilerleme"],
        "sadness": ["üzgün", "hüzün", "depresyon", "karamsar"],
        "anxiety": ["anksiyete", "kaygı", "panik"],
        "loneliness": ["yalnız", "yalnızlık", "yalnızım"]
    }
    for emotion, words in keywords.items():
        for word in words:
            if word.lower() in analysis_text.lower():
                return emotion
    return "motivation"  # default

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        if username:
            session["username"] = username
            if username not in user_data:
                user_data[username] = {
                    "chat_memory": [],
                    "chat_sessions": {},
                    "active_session_id": "Sohbet 1",
                    "counter": 1,
                    "gpt_analysis": None,
                    "language": "tr"
                }
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = user_data[username]
    suggestions = []

    if request.method == "POST":
        if request.form.get("new_chat") == "1":
            if user["chat_memory"]:
                user["chat_sessions"][user["active_session_id"]] = user["chat_memory"].copy()
            user["counter"] += 1
            user["active_session_id"] = f"Sohbet {user['counter']}"
            user["chat_memory"] = []
            user["gpt_analysis"] = None
            return redirect(url_for("index"))

        if request.form.get("delete_chat"):
            to_delete = request.form.get("delete_chat")
            if to_delete in user["chat_sessions"]:
                del user["chat_sessions"][to_delete]
            return redirect(url_for("index"))

        user_input = request.form.get("user_input", "").strip()
        user["language"] = request.form.get("language", "tr")

        if user_input:
            sys_message = {"role": "system", "content": (
                "You are an empathetic assistant who communicates in English with kindness and understanding."
                if user["language"] == "en"
                else "Sen, Türkçe iletişim kuran anlayışlı ve yardımsever bir asistansın."
            )}

            chat_sequence = [sys_message]
            for example in gpt_context[:5]:
                chat_sequence.append({"role": "user", "content": example["user_input"]})
                chat_sequence.append({"role": "assistant", "content": example["gpt_response"]})
            chat_sequence.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_sequence
            )
            reply = response.choices[0].message.content

            user["chat_memory"].append({"role": "user", "content": user_input})
            user["chat_memory"].append({"role": "assistant", "content": reply})

            user["gpt_analysis"] = analyze_with_gpt(user_input, user["language"])
            emotion = detect_emotion(user["gpt_analysis"])
            suggestions = all_suggestions.get(emotion, [])

    return render_template("index.html",
                           username=username,
                           chat_memory=user["chat_memory"],
                           gpt_analysis=user["gpt_analysis"],
                           selected_language=user["language"],
                           chat_sessions=user["chat_sessions"],
                           active_session_id=user["active_session_id"],
                           suggestions=suggestions)
