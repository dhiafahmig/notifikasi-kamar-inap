import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
        load_dotenv(env_path)

        # Load YAML config
        config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config file tidak ditemukan: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            raise

        # Override with environment variables
        self._load_env_overrides()

    def _load_env_overrides(self):
        """Load configuration overrides from environment"""
        # Database overrides
        if os.getenv('DB_HOST'):
            self._config['database']['host'] = os.getenv('DB_HOST')
        if os.getenv('DB_USER'):
            self._config['database']['user'] = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self._config['database']['password'] = os.getenv('DB_PASSWORD')
        if os.getenv('DB_NAME'):
            self._config['database']['database'] = os.getenv('DB_NAME')
            
        # Telegram overrides
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self._config['telegram']['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
        if os.getenv('TELEGRAM_ENABLED'):
            self._config['telegram']['enabled'] = os.getenv('TELEGRAM_ENABLED').lower() == 'true'
            
         # WhatsApp overrides (FORMAT BARU)
        if os.getenv('WHATSAPP_USER_CODE'):
            self._config['whatsapp']['user_code'] = os.getenv('WHATSAPP_USER_CODE')
        if os.getenv('WHATSAPP_SECRET'):
            self._config['whatsapp']['secret'] = os.getenv('WHATSAPP_SECRET')
        if os.getenv('WHATSAPP_DEVICE_ID'):
            self._config['whatsapp']['device_id'] = os.getenv('WHATSAPP_DEVICE_ID')
        if os.getenv('WHATSAPP_ENABLED'):
            self._config['whatsapp']['enabled'] = os.getenv('WHATSAPP_ENABLED').lower() == 'true'

    @property
    def database(self):
        return self._config['database']

    @property
    def telegram(self):
        return self._config['telegram']

    @property
    def whatsapp(self):  # PROPERTY BARU
        return self._config['whatsapp']

    @property
    def app(self):
        return self._config['app']
