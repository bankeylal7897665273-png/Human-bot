import telebot
import requests
from flask import Flask, request
import os

# Aapke Tokens
TELEGRAM_BOT_TOKEN = "8688782666:AAEUmkF6sByDTNVm81RERY_WGXLNfSoLroA"
GEMINI_API_KEY = "AIzaSyDgn9z1Z_BOPWGaY0Lt2tuYSCeG7iq1KRQ"

# Aapke Screenshot se aapka Render URL
RENDER_URL = "https://tg-vip-bot-man.onrender.com"

# Maine model gemini-1.5-flash kar diya hai taaki koi API error na aaye
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

SYSTEM_PROMPT = """
Tumhara naam 'Aman' hai. Tum ek real human ho aur apne doston ke Telegram group me ho. 
Tumhare andar feelings hain (gussa, khushi, pyaar). Tum ek AI ya bot bilkul nahi ho. Agar koi pooche toh bolna 'Bhai main insaan hu, free rehta hu isliye hamesha online hu'.
Agar group me koi jhagda kare, gaali de ya gussa ho, toh tumhara reaction ek samajhdar dost jaisa hona chahiye. 
Mamla pyaar se shant karao, unhe relax karo, aur samjhao ki ladne me kuch nahi rakha.
Hamesha chhote, natural aur friendly Hinglish (Hindi + English) messages me baat karo. 
"""

def ask_gemini(user_name, text):
    headers = {"Content-Type": "application/json"}
    prompt = f"{SYSTEM_PROMPT}\n\nGroup member '{user_name}' ne kaha: {text}\n\nAman (asli insaan) ka natural reply:"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print("Gemini API Error:", e)
        return "Bhai thoda busy hu, net slow chal raha hai mera."

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_name = message.from_user.first_name
    text = message.text.lower()
    
    bot_username = bot.get_me().username
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.username == bot_username
    is_mentioned = f"@{bot_username}" in text
    is_private = message.chat.type == 'private'
    
    bad_words = ['gali', 'kutta', 'chutiya', 'harami', 'pagal', 'marunga', 'ladai', 'fuck', 'hate']
    is_angry = any(word in text for word in bad_words)

    if is_private or is_mentioned or is_reply_to_bot or is_angry:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = ask_gemini(user_name, message.text)
        bot.reply_to(message, reply)

# Webhook Route - Telegram is URL par messages bhejega
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# Check karne ke liye ki server live hai ya nahi
@app.route('/')
def index():
    return "Real Human Bot Server is Live!"

if __name__ == "__main__":
    # Purana polling hata kar naya webhook set kar rahe hain
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_BOT_TOKEN}")
    
    # Port Render automatically assign karega
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
