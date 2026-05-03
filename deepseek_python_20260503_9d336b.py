import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = "8662031831:AAExZ3KbV-XVUrekVuQNEeVBsorsz91yZVQ"
ADMIN_ID = int(7949539794)
TARGET_CHANNEL = -1003777949379
PHONE_NUMBER = "917977997989"

# Source channels (from where to dump)
SOURCE_CHANNELS = [
    -1002467711013,  # E3 HACKER official channel
    -1001541596773,  # VritraSec ™
    -1002566434520,  # 𝐇𝐈𝐃𝐃𝐄𝐍 𝐄𝐘𝐄
    -1003892030550,  # ᑕᖇᗩᑕKᗴᗪ ᗷY ᗴ᙭OᗪᑌՏ
    -1002806543363,  # DarkNyte Exodus
    -1002390641319,  # CYBER SECURITY🔒
]

# Custom mapping: source -> specific target (optional)
CUSTOM_MAPPING = {}  # {source_chat_id: target_chat_id}