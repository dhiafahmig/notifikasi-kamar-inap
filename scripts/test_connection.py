#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseManager
from notifiers.telegram import TelegramNotifier
from utils.config import Config

def main():
    config = Config()
    
    print("🔍 Testing Hospital Notification System...")
    
    # Test database
    print("\n📊 Testing database connection...")
    try:
        db = DatabaseManager(config.database)
        if db.test_connection():
            print("✅ Database connection OK")
        else:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Test Telegram
    print("\n📱 Testing Telegram bot...")
    try:
        telegram = TelegramNotifier(config.telegram)
        if telegram.test_connection():
            print("✅ Telegram bot OK")
        else:
            print("❌ Telegram bot failed")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

if __name__ == "__main__":
    main()
