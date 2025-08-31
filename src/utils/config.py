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
        if os.getenv('DB_HOST'):
            self._config['database']['host'] = os.getenv('DB_HOST')
        if os.getenv('DB_USER'):
            self._config['database']['user'] = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self._config['database']['password'] = os.getenv('DB_PASSWORD')
        if os.getenv('DB_NAME'):
            self._config['database']['database'] = os.getenv('DB_NAME')
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self._config['telegram']['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')

    @property
    def database(self):
        return self._config['database']

    @property
    def telegram(self):
        return self._config['telegram']

    @property
    def app(self):
        return self._config['app']
