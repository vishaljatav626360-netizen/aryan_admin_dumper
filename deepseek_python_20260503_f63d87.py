from telethon import TelegramClient, events
import asyncio
import logging

logger = logging.getLogger(__name__)

class TelegramClientManager:
    def __init__(self, phone_number, api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e"):
        self.phone = phone_number
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)
        self.connected = False
    
    async def start(self):
        try:
            await self.client.start(phone=self.phone)
            self.connected = True
            logger.info("Telegram client connected")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def send_otp(self):
        await self.client.send_code_request(self.phone)
    
    async def sign_in(self, code):
        try:
            await self.client.sign_in(self.phone, code)
            self.connected = True
            return True
        except:
            return False
    
    def is_connected(self):
        return self.connected
    
    async def get_messages(self, chat_id, limit=100, offset_id=0):
        async with self.client:
            return await self.client.get_messages(chat_id, limit=limit, offset_id=offset_id)
    
    async def forward_message(self, to_chat, message):
        try:
            await self.client.forward_messages(to_chat, message)
            return True
        except Exception as e:
            logger.error(f"Forward failed: {e}")
            return False