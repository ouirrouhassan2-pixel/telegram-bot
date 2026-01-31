import telebot
from telebot import types
from config import BOT_TOKEN, REMOVE_BG_API_KEY, CHANNEL_USERNAME
from remove_bg import handle_remove_bg
from video_downloader import download_video
import qrcode
import io

bot = telebot.TeleBot(BOT_TOKEN)

# ---------------- شرط الاشتراك ----------------
def resolve_channel():
    try:
        uname = CHANNEL_USERNAME
        if not uname.startswith("@"):
            uname_with_at = "@" + uname
        else:
            uname_with_at = uname
        chat = bot.get_chat(uname_with_at)
        return chat.id
    except:
        return None

CHANNEL_ID = resolve_channel()

def is_subscribed(user_id):
    if CHANNEL_ID is None:
        return False
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

def make_join_keyboard():
    if CHANNEL_USERNAME.startswith("@"):
        url = f"https://t.me/{CHANNEL_USERNAME[1:]}"
    else:
        url = f"https://t.me/{CHANNEL_USERNAME}"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔗 انضم إلى القناة", url=url))
    kb.add(types.InlineKeyboardButton("🔄 تحقَّق الآن", callback_data="check_sub"))
    return kb

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check_sub(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "✅ شكراً! أنت الآن مشترك.")
        bot.send_message(call.message.chat.id,
                         "✅ ممتاز — يمكنك الآن استخدام البوت.\nأرسل صورة أو رابط.")
    else:
        bot.answer_callback_query(call.id, "⚠️ لم يبدُ أنك مشترك بعد.")
        bot.send_message(call.message.chat.id,
                         "🔒 يتوجب عليك الانضمام أولاً ثم اضغط 'تحقَّق الآن'.",
                         reply_markup=make_join_keyboard())

# ---------------- start ----------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            f"🔒 يجب عليك الاشتراك في القناة أولاً: {CHANNEL_USERNAME}",
            reply_markup=make_join_keyboard()
        )
        return

    bot.send_message(
        message.chat.id,
        "✅ مرحباً! أرسل صورة لأزيل الخلفية تلقائيًا أو رابط لمعالجة الفيديو/QR."
    )

# ---------------- صورة ----------------
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            "🔒 يجب الاشتراك في القناة أولاً.",
            reply_markup=make_join_keyboard()
        )
        return
    handle_remove_bg(bot, message, REMOVE_BG_API_KEY)

# ---------------- رابط ----------------
user_links = {}  # تخزين مؤقت للرابط لكل مستخدم

@bot.message_handler(func=lambda m: m.text and m.text.startswith(("http://","https://")))
def handle_link(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            "🔒 يجب الاشتراك في القناة أولاً.",
            reply_markup=make_join_keyboard()
        )
        return

    # تخزين الرابط مؤقتًا
    user_links[user_id] = message.text

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎥 تحميل فيديو", callback_data="video"))
    kb.add(types.InlineKeyboardButton("🎵 تحميل صوت", callback_data="audio"))
    kb.add(types.InlineKeyboardButton("🔳 QR Code", callback_data="qr"))
    bot.send_message(message.chat.id, "📌 اختر ماذا تريد أن أفعل بهذا الرابط:", reply_markup=kb)

# ---------------- callback ----------------
@bot.callback_query_handler(func=lambda call: call.data in ["qr","video","audio"])
def handle_callbacks(call):
    user_id = call.from_user.id
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "🔒 يجب الاشتراك أولاً.")
        bot.send_message(call.message.chat.id, "🔒 يرجى الانضمام للقناة أولاً.", reply_markup=make_join_keyboard())
        return

    url = user_links.get(user_id)
    if not url:
        bot.send_message(call.message.chat.id, "⚠️ لم أجد الرابط، أعد إرساله.")
        return

    if call.data == "qr":
        img = qrcode.make(url)
        bio = io.BytesIO()
        bio.name = "qr.png"
        img.save(bio)
        bio.seek(0)
        bot.send_document(call.message.chat.id, bio, caption="✅ QR Code جاهز")
    elif call.data == "video":
        bot.send_message(call.message.chat.id, "⏳ جاري تحميل الفيديو ...")
        download_video(bot, call.message.chat.id, url, format_type='video')
    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ جاري تحميل الصوت ...")
        download_video(bot, call.message.chat.id, url, format_type='audio')

# ---------------- أي رسالة أخرى ----------------
@bot.message_handler(func=lambda m: True)
def handle_other(message):
    bot.send_message(message.chat.id, "⚠️ أرسل صورة لإزالة الخلفية أو رابط لمعالجة الفيديو/QR.")

# ---------------- تشغيل البوت ----------------
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
