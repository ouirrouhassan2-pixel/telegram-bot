import os
import yt_dlp
import tempfile
import shutil

# الحد الأقصى لحجم الفيديو للتحميل عبر Telegram
MAX_FILE_SIZE_MB = 50

def get_ytdlp_options(temp_dir, format_type='video'):
    """
    إعدادات yt-dlp لكل نوع تحميل
    - الفيديو: أفضل جودة MP4
    - الصوت: تحويل MP3
    - تجاوز القيود الجغرافية
    - أسماء ملفات آمنة بدون Emoji أو Unicode غير مدعوم
    """
    common_opts = {
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'outtmpl': f'{temp_dir}/%(title).50s.%(ext)s',
        'restrictfilenames': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    if format_type == 'audio':
        common_opts['format'] = 'bestaudio/best'
        common_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Try to limit video size by selecting lower height if needed
        common_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        common_opts['merge_output_format'] = 'mp4'

    return common_opts

def download_video(bot, chat_id, url, format_type='video'):
    """
    تحميل الفيديو أو الصوت وإرساله عبر البوت
    - bot: كائن telebot
    - chat_id: رقم الدردشة لإرسال الملفات
    - url: رابط الفيديو
    - format_type: 'video' أو 'audio'
    """
    temp_dir = tempfile.mkdtemp()
    try:
        ydl_opts = get_ytdlp_options(temp_dir, format_type)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                bot.send_message(chat_id, "❌ لم أتمكن من تحميل الفيديو.")
                return

            filename = ydl.prepare_filename(info)

            # في حالة تحويل الصوت
            if format_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            elif not filename.endswith('.mp4'):
                potential_mp4 = os.path.splitext(filename)[0] + '.mp4'
                if os.path.exists(potential_mp4):
                    filename = potential_mp4

            # التأكد من الحجم
            file_size = os.path.getsize(filename) / (1024 * 1024)

            # إذا كان الملف لا يزال كبيراً، نحاول تقليل الجودة باستخدام ffmpeg
            if file_size > MAX_FILE_SIZE_MB:
                bot.send_message(chat_id, f"⚠️ الملف كبير ({file_size:.1f}MB)، جاري ضغطه ليلائم تيليجرام...")
                compressed_filename = os.path.splitext(filename)[0] + "_compressed" + os.path.splitext(filename)[1]
                
                if format_type == 'audio':
                    # تقليل جودة الصوت إلى 64k
                    os.system(f"ffmpeg -i '{filename}' -ab 64k '{compressed_filename}' -y")
                else:
                    # تقليل جودة الفيديو (تقليل الدقة والبت ريت)
                    os.system(f"ffmpeg -i '{filename}' -vf scale=-1:480 -vcodec libx264 -crf 28 -preset fast '{compressed_filename}' -y")
                
                if os.path.exists(compressed_filename):
                    filename = compressed_filename
                    file_size = os.path.getsize(filename) / (1024 * 1024)

            if file_size > MAX_FILE_SIZE_MB:
                with open(filename, 'rb') as f:
                    bot.send_document(chat_id, document=f,
                                      caption=f"📦 {info.get('title')}\n(Sent as document due to size: {file_size:.1f}MB)")
                return

            with open(filename, 'rb') as f:
                if format_type == 'audio':
                    bot.send_audio(chat_id, audio=f, title=info.get('title', 'Audio'))
                else:
                    bot.send_video(chat_id, video=f, caption=f"✅ {info.get('title')}")

    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء التحميل: {str(e)[:200]}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
