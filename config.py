import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_ID = int(os.getenv('API_ID', 0))
    API_HASH = os.getenv('API_HASH')
    
    # Proxy settings (Germany)
    PROXY_HOST = os.getenv('PROXY_HOST', 'de.proxy.example.com')
    PROXY_PORT = int(os.getenv('PROXY_PORT', 1080))
    PROXY_USERNAME = os.getenv('PROXY_USERNAME', '')
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', '')
    
    # Session settings
    SESSION_DIR = 'sessions'
    DEVICE_MODEL = 'Windows 11'
    SYSTEM_VERSION = '10.0.22621'
    APP_VERSION = '4.16.0'
    LANG_CODE = 'en'
    SYSTEM_LANG_CODE = 'en-US'
    
    # Support
    SUPPORT_ID = '@ID_ALI_BI_GHAM'
