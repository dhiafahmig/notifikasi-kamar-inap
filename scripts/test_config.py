#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import Config

def main():
    print("🔧 Testing Configuration Loading...")
    
    try:
        config = Config()
        
        print("\n📱 App Config:")
        print(f"  - Name: {config.app.get('name', 'N/A')}")
        print(f"  - Check Interval: {config.app.get('check_interval', 30)}")
        
        print("\n📊 Database Config:")
        print(f"  - Host: {config.database.get('host', 'N/A')}")
        print(f"  - Database: {config.database.get('database', 'N/A')}")
        
        print("\n📲 Telegram Config:")
        print(f"  - Bot Token: {'***' + config.telegram.get('bot_token', '')[-10:] if config.telegram.get('bot_token') else 'Not set'}")
        
        print("\n✅ Configuration loaded successfully!")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")

if __name__ == "__main__":
    main()
