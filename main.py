import os, telebot, yt_dlp, time
from telebot import types
from flask import Flask
from threading import Thread

# --- زانیاریێن بۆتی ---
API_TOKEN = "8643259960:AAEizSJj1TgwJNXxnU5fY_GO8HUAjP-I-M4"
CHANNEL_ID = "@tech_ai_falah"
CHANNEL_URL = "https://t.me/tech_ai_falah"
bot = telebot.TeleBot(API_TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception: return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    if check_sub(user_id):
        bot.send_message(message.chat.id, f"سڵاو {name}! لینکا ڤیدیۆیێ بفرێکه.")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_URL))
        markup.add(types.InlineKeyboardButton("جوین بووم", callback_data="check"))
        bot.send_message(message.chat.id, f"بەڕێز {name}، تکایە سەرەتا جوینی کەناڵێ مە بکه:\n{CHANNEL_URL}", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_download(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    url = message.text
    if not url.startswith("http"): return
    msg = bot.reply_to(message, "⏳ Tech AI خەریکی دانلۆدکردنە...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'vid_{int(time.time())}.%(ext)s',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆیا تە ب ڕێکا Tech AI ئامادەیە ✅")
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"ئیشکال: {str(e)}", message.chat.id, msg.message_id)

# --- بۆ ئەوەی ٢٤ دەمژمێرا هشیار بیت ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
