import requests

def handle_remove_bg(bot, message, REMOVE_BG_API_KEY):
    """
    إزالة الخلفية من الصورة التي أرسلها المستخدم.
    bot: instance من telebot
    message: رسالة تحتوي على الصورة
    REMOVE_BG_API_KEY: مفتاح API الخاص بموقع remove.bg
    """
    bot.send_message(message.chat.id, "⏳ جاري إزالة الخلفية ...")

    try:
        # الحصول على ملف الصورة من Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        img_data = requests.get(file_url).content

        # طلب إزالة الخلفية
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": ("image.png", img_data)},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY}
        )

        if response.status_code == 200:
            # حفظ وإرسال الصورة بدون خلفية
            with open("no_bg.png", "wb") as f:
                f.write(response.content)
            with open("no_bg.png", "rb") as f:
                bot.send_document(
                    message.chat.id,
                    f,
                    caption="✅ تمت إزالة الخلفية بنجاح"
                )
        else:
            bot.send_message(message.chat.id, "❌ حدث خطأ أثناء معالجة الصورة. راجع API Key.")
            print("remove.bg error:", response.status_code, response.text)

    except Exception as e:
        print("Error processing photo:", e)
        bot.send_message(message.chat.id, "❌ حدث خطأ داخلي أثناء المعالجة.")
