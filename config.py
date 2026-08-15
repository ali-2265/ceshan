import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    API_ID = int(os.getenv('API_ID', 0))
    API_HASH = os.getenv('API_HASH')
    
    # Proxy settings
    PROXY_HOST = os.getenv('PROXY_HOST')
    PROXY_PORT = os.getenv('PROXY_PORT')
    
    if PROXY_PORT:
        try:
            PROXY_PORT = int(PROXY_PORT)
        except ValueError:
            PROXY_PORT = None
    else:
        PROXY_PORT = None
    
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
