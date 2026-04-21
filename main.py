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
        bot.send_message(message.chat.id, "سڵاو كاك فەلاح! 🤖\nهەمی کێشەیێن یوتوب هاتنە چارەسەرکرن.\nتکایە لینکا ڤیدیۆیێ بفرێکه (TikTok, Insta, FB, YouTube).")
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
    msg = bot.reply_to(message, "⏳ Tech AI خەریکی دانلۆدکردنە...\nخەریکە بەربەستەکانی یوتوب تێک دەشکێنین.")
    
    # ڕێکخستنێن پیشەیی بۆ تێپەڕاندنی بلۆکا یوتوب
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'vid_{int(time.time())}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'add_header': [
            'Accept-Language: en-US,en;q=0.9',
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        ],
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['dash', 'hls']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename): # هندەک جاران ناڤێ فایلی دهێتە گۆهۆڕین بۆ .mkv
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆیا تە ئامادەیە ✅\nب ڕێکا: @tech_ai_falah")
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"ئیشکال: یوتوب ڕێگریێ دکەت. ئەگەر ڤیدیۆیا Shorts بیت یان تەمەنێ وێ +١٨ بیت، سێرڤەر نەشێت دانلۆد بکەت.", message.chat.id, msg.message_id)

app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def run(): app.run(host='0.0.0.0', port=os.getenv('PORT', 8080))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
