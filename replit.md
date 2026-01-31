# Telegram Multi-Tool Bot

## Overview

This is a multifunctional Telegram bot that provides users with several convenient tools in a single interface:

1. **Video/Audio Downloader** - Downloads content from major social media platforms (YouTube, TikTok, Instagram, Facebook, Twitter/X) in MP4 or MP3 format
2. **Image Background Remover** - Removes backgrounds from user-uploaded photos using the remove.bg API
3. **QR Code Generator** - Generates QR codes from text or URLs

The bot enforces channel subscription before allowing access to features, using inline keyboards for user interaction.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Technology**: Python with pyTeleBot (telebot) library
- **Rationale**: pyTeleBot provides a simple, synchronous API for Telegram bot development with built-in support for inline keyboards and callback queries
- **Alternative considered**: python-telegram-bot (async) - chose telebot for simpler implementation

### Module Structure
The application follows a modular design pattern with separate files for each feature:

| File | Purpose |
|------|---------|
| `main.py` | Bot initialization, command handlers, subscription verification |
| `config.py` | Configuration constants (tokens, API keys, channel info) |
| `remove_bg.py` | Background removal logic using remove.bg API |
| `video_downloader.py` | Video/audio download using yt-dlp |
| `qr_generator.py` | QR code generation using qrcode library |

### User Flow Architecture
1. User sends `/start` command
2. Bot checks channel subscription status via Telegram API
3. If not subscribed → show join button + verification callback
4. If subscribed → welcome message with feature explanation
5. User input determines action:
   - Photo → Background removal
   - Text/URL → Show options (Download Video, Download Audio, Generate QR)

### Subscription Gate Pattern
- Bot resolves channel ID from username at startup
- Each user action checks subscription status via `get_chat_member` API
- Uses inline keyboard with callback for re-verification

### File Handling Strategy
- Temporary files used for video downloads (cleaned up after sending)
- 50MB limit enforced for Telegram uploads
- Large files sent as documents rather than media

## External Dependencies

### Third-Party APIs
| Service | Purpose | Configuration |
|---------|---------|---------------|
| Telegram Bot API | Core bot functionality | `BOT_TOKEN` in config.py |
| remove.bg API | Background removal | `REMOVE_BG_API_KEY` in config.py |

### Python Libraries
| Library | Purpose |
|---------|---------|
| `telebot` (pyTeleBot) | Telegram bot framework |
| `yt-dlp` | Video/audio downloading from social platforms |
| `qrcode` | QR code generation |
| `requests` | HTTP requests for API calls |
| `FFmpeg` | Audio extraction/conversion (system dependency) |

### Telegram Channel Integration
- Channel: `@Hasxan_Ph` (configurable in config.py)
- Used for subscription verification before bot usage
- Bot must be admin in the channel to check membership

### System Requirements
- FFmpeg must be installed for audio extraction features
- Stable internet connection for API calls and media downloads