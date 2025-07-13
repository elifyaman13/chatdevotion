OPENAI_API_KEY="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"
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mesaj geçmişi
messages = [{"role": "system", "content": "Sen kibar bir Türkçe asistanısın."}]

print("🧠 Chatdevition başlatıldı. (Çıkmak için 'exit' yaz)")
while True:
    user_input = input("Sen: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response.choices[0].message.content
    print("GPT:", reply)
    
    messages.append({"role": "assistant", "content": reply})






     


