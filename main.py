import os
import telebot
import yt_dlp
import time
from telebot import types
from flask import Flask
from threading import Thread

# --- زانیاریێن بۆتی ---
API_TOKEN = "8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q"
CHANNEL_ID = "@tech_ai_falah"
CHANNEL_URL = "https://t.me/tech_ai_falah"

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(message.chat.id, "سڵاو كاك فەلاح! لینکا ڤیدیۆیێ بفرێکه (TikTok, Insta, YT, FB) دا بۆ تە دانلۆد بکەم.")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_URL))
        markup.add(types.InlineKeyboardButton("جوین بووم ✅", callback_data="check"))
        bot.send_message(message.chat.id, f"بەڕێز، بۆ کارپێکرنا بۆتی تکایە سەرەتا جوینی کەناڵێ مە بکه:\n{CHANNEL_URL}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "سوپاس! نوکە دشێی بۆتی بکاربینی ✅")
        bot.edit_message_text("تۆماربوونی تە سەرکەفتوو بوو! لینکا ڤیدیۆیێ بفرێکه.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تە هێشتا جوین نەکرییه! ❌", show_alert=True)

@bot.message_handler(func=lambda m: True)
def handle_download(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    
    url = message.text
    if not url.startswith("http"):
        return

    msg = bot.reply_to(message, "⏳ Tech AI خەریکی دانلۆدکردنە...")
    
    # ڕێکخستنێن yt-dlp بۆ کارکرن ل سەر سێرڤەری
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'video_{int(time.time())}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆیا تە ئامادەیە ✅\nب ڕێکا: @tech_ai_falah")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("ئیشکالەک چێبوو! یان ڤیدیۆ یا تایبەتە یان لینک یا خەلەتە.", message.chat.id, msg.message_id)

# بەشێ پێدڤی بۆ کارکرن ل سەر Railway (Flask Server)
@server.route('/')
def home():
    return "Bot is Running"

def run():
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
