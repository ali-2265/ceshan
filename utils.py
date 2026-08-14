import os
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.account import UpdateProfileRequest
import json
from datetime import datetime

class SessionManager:
    def __init__(self, config):
        self.config = config
        self.sessions = {}
        os.makedirs(config.SESSION_DIR, exist_ok=True)
    
    def get_session_path(self, phone):
        return os.path.join(self.config.SESSION_DIR, f"{phone}.session")
    
    async def create_session(self, phone, code, password=None):
        session_path = self.get_session_path(phone)
        
        # Proxy configuration
        proxy = None
        if self.config.PROXY_HOST:
            proxy = {
                'proxy_type': 'socks5',
                'addr': self.config.PROXY_HOST,
                'port': self.config.PROXY_PORT,
                'username': self.config.PROXY_USERNAME,
                'password': self.config.PROXY_PASSWORD
            }
        
        client = TelegramClient(
            session_path,
            self.config.API_ID,
            self.config.API_HASH,
            proxy=proxy,
            device_model=self.config.DEVICE_MODEL,
            system_version=self.config.SYSTEM_VERSION,
            app_version=self.config.APP_VERSION,
            lang_code=self.config.LANG_CODE,
            system_lang_code=self.config.SYSTEM_LANG_CODE
        )
        
        try:
            await client.connect()
            
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                await asyncio.sleep(2)
                
                await client.sign_in(phone, code)
                
                if password:
                    await client.sign_in(password=password)
            
            me = await client.get_me()
            
            session_info = {
                'phone': phone,
                'user_id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'created_at': datetime.now().isoformat()
            }
            
            json_path = session_path + '.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
            self.sessions[phone] = client
            return client, me
            
        except errors.PhoneCodeInvalidError:
            raise ValueError("کد تایید نامعتبر است")
        except errors.PasswordHashInvalidError:
            raise ValueError("رمز عبور دو مرحله‌ای نامعتبر است")
        except Exception as e:
            raise Exception(f"خطا در ساخت سشن: {str(e)}")
    
    async def load_session(self, phone):
        session_path = self.get_session_path(phone)
        if os.path.exists(session_path + '.session'):
            proxy = None
            if self.config.PROXY_HOST:
                proxy = {
                    'proxy_type': 'socks5',
                    'addr': self.config.PROXY_HOST,
                    'port': self.config.PROXY_PORT,
                    'username': self.config.PROXY_USERNAME,
                    'password': self.config.PROXY_PASSWORD
                }
            
            client = TelegramClient(
                session_path,
                self.config.API_ID,
                self.config.API_HASH,
                proxy=proxy,
                device_model=self.config.DEVICE_MODEL,
                system_version=self.config.SYSTEM_VERSION,
                app_version=self.config.APP_VERSION,
                lang_code=self.config.LANG_CODE,
                system_lang_code=self.config.SYSTEM_LANG_CODE
            )
            
            await client.connect()
            if await client.is_user_authorized():
                self.sessions[phone] = client
                return client
        return None
    
    async def send_message_to_saved(self, phone, message):
        client = await self.load_session(phone)
        if not client:
            raise Exception("سشن فعال نیست")
        
        try:
            saved_messages = await client.get_entity('me')
            await client.send_message(saved_messages, message)
            return True
        except Exception as e:
            raise Exception(f"خطا در ارسال پیام: {str(e)}")
    
    def get_session_info(self, phone):
        json_path = self.get_session_path(phone) + '.json'
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_sessions(self):
        sessions = []
        for file in os.listdir(self.config.SESSION_DIR):
            if file.endswith('.session.json'):
                with open(os.path.join(self.config.SESSION_DIR, file), 'r', encoding='utf-8') as f:
                    sessions.append(json.load(f))
        return sessions
