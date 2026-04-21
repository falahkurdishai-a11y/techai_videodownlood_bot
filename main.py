import os, telebot, yt_dlp, time
from telebot import types
from flask import Flask
from threading import Thread

# --- زانیاریێن بۆتی ---
API_TOKEN = "8631109877:AAHFNwNoHJgeSGLUozS2choOiTc17ePqD1Q"
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
    if check_sub(user_id):
        bot.send_message(message.chat.id, "سڵاو كاك فەلاح! 🤖\nلینکا ڤیدیۆیێ بفرێکه (TikTok, Insta, FB, YouTube).\n\nتێبینی: ئەگەر یوتوب کار نەکرد، لینکا کورت (Shorts) تاقی بکە.")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel", url=CHANNEL_URL))
        markup.add(types.InlineKeyboardButton("جوین بووم ✅", callback_data="check"))
        bot.send_message(message.chat.id, f"بەڕێز، بۆ کارپێکرنا بۆتی تکایە سەرەتا جوینی کەناڵێ مە بکه:\n{CHANNEL_URL}", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_download(message):
    if not check_sub(message.from_user.id):
        start(message)
        return
    url = message.text
    if not url.startswith("http"): return
    msg = bot.reply_to(message, "⏳ Tech AI خەریکی دانلۆدکردنە...\nهەوڵ دەدەین بەربەستەکانی یوتوب ببڕین.")
    
    ydl_opts = {
        # بکارئینانا ڤێرژنا ئەندرۆید بۆ دەربازبوون ژ بلۆکا یوتوب
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'vid_{int(time.time())}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'youtube_include_dash_manifest': False,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
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
        error_msg = str(e)
        if "Sign in to confirm your age" in error_msg:
            bot.edit_message_text("ئیشکال: یوتوب داخوازا تەمەنی دەکەت، ئەڤ ڤیدیۆیە ناهێتە دانلۆدکرن.", message.chat.id, msg.message_id)
        elif "The read operation timed out" in error_msg:
            bot.edit_message_text("ئیشکال: سێرڤەر زۆر خاوە، دووبارە تاقی بکەوە.", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("ئیشکال: یوتوب ڕێگری ل سێرڤەری دەکەت. تکایە تەنێ ڤیدیۆ کورتەکان (Shorts) تاقی بکە.", message.chat.id, msg.message_id)

app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=os.getenv('PORT', 8080))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
