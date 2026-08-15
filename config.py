import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('8541453435:AAEqXEyRE46CydJBPMPoKc87YwmCAHZWP54')
    API_ID = int(os.getenv('34855392  
', 0))
    API_HASH = os.getenv('5e40d435847009c31c24042e2a3c0d3b')
    
    # Proxy settings (Germany) - با خطاگیری
    PROXY_HOST = os.getenv('PROXY_HOST')
    PROXY_PORT = os.getenv('PROXY_PORT')
    
    # اگر پروکسی پورت خالی بود یا وجود نداشت، از None استفاده کن
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
