# 🤖 Telegram Dumping Bot

## Files:
- **main.py** - Bot start, command handlers, inline buttons
- **config.py** - Tokens, channel IDs, phone number
- **database.py** - SQLite (duplicate check, stats, status)
- **tg_client.py** - Telethon login, get/forward messages
- **dumper.py** - Main dumping loop (24/7)
- **requirements.txt** - Dependencies
- **Dockerfile** - Render deployment
- **render.yaml** - Render config

## Commands:
/start - Show menu with all buttons

## Buttons:
- Daily/Monthly Stats
- Source Stats  
- Start/Stop per channel
- Start All / Stop All
- Login Status

## Deploy on Render:
1. Push to GitHub
2. Connect repo on Render
3. Add env variables
4. Deploy

## Note:
First time /start - OTP login hoga. Then auto dumping start.