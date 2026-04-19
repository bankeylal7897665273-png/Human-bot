import telebot
import requests
import threading
from flask import Flask
import os

# Aapke diye gaye credentials
TELEGRAM_BOT_TOKEN = "8688782666:AAEUmkF6sByDTNVm81RERY_WGXLNfSoLroA"
GEMINI_API_KEY = "AIzaSyDgn9z1Z_BOPWGaY0Lt2tuYSCeG7iq1KRQ"

# Aapka custom endpoint (Gemini 2.5 Flash)
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Render ke liye Dummy Web Server (Taki app crash na ho)
app = Flask(__name__)

@app.route('/')
def index():
    return "Real Human Bot is Live on Render!"

# Ye prompt bot ko ek asli insaan banayega
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
        return "Bhai mera thoda net slow chal raha hai, baad me batata hu."

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_name = message.from_user.first_name
    text = message.text.lower()
    
    bot_username = bot.get_me().username
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.username == bot_username
    is_mentioned = f"@{bot_username}" in text
    is_private = message.chat.type == 'private'
    
    # Jhagda ya gaali detect karne ke words
    bad_words = ['gali', 'kutta', 'chutiya', 'harami', 'pagal', 'marunga', 'ladai', 'fuck', 'hate']
    is_angry = any(word in text for word in bad_words)

    # Bot tabhi reply karega jab:
    # 1. Private chat ho
    # 2. Koi bot ko mention kare ya reply kare
    # 3. Group me koi GAALI de ya jhagda kare (Auto-intervene karega)
    if is_private or is_mentioned or is_reply_to_bot or is_angry:
        
        # Real lagne ke liye "typing..." status dikhana
        bot.send_chat_action(message.chat.id, 'typing')
        
        reply = ask_gemini(user_name, message.text)
        bot.reply_to(message, reply)

def run_telegram_bot():
    print("Bot started polling...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Threading use kar rahe hain taaki Telegram Bot aur Web Server dono ek sath chalein
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.start()
    
    # Render automatic PORT assign karta hai
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
