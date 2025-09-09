# scripts/debug_whatsapp_config.py
#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import Config

def debug_whatsapp_config():
    """Debug konfigurasi WhatsApp yang ter-load"""
    
    print("🔍 Debugging WhatsApp Configuration...")
    
    try:
        config = Config()
        whatsapp_config = config.whatsapp
        
        print("\n📱 WhatsApp Config yang ter-load:")
        print(f"  - api_url: {whatsapp_config.get('api_url')}")
        print(f"  - user_code: {whatsapp_config.get('user_code')}")
        print(f"  - secret: {whatsapp_config.get('secret')[:20]}..." if whatsapp_config.get('secret') else "None")
        print(f"  - device_id: {whatsapp_config.get('device_id')}")
        print(f"  - enabled: {whatsapp_config.get('enabled')}")
        print(f"  - timeout: {whatsapp_config.get('timeout')}")
        
        # Bandingkan dengan nilai yang berhasil di script test
        print("\n🆚 Perbandingan dengan script test yang berhasil:")
        print(f"  Script test user_code: KMKF65925")
        print(f"  Config user_code: {whatsapp_config.get('user_code')}")
        print(f"  Match: {'✅' if whatsapp_config.get('user_code') == 'KMKF65925' else '❌'}")
        
        print(f"  Script test device_id: D-LJSK1") 
        print(f"  Config device_id: {whatsapp_config.get('device_id')}")
        print(f"  Match: {'✅' if whatsapp_config.get('device_id') == 'D-LJSK1' else '❌'}")
        
        print(f"  Script test URL: https://api.kirimi.id/v1/send-message")
        print(f"  Config URL: {whatsapp_config.get('api_url')}")
        print(f"  Match: {'✅' if whatsapp_config.get('api_url') == 'https://api.kirimi.id/v1/send-message' else '❌'}")
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")

if __name__ == "__main__":
    debug_whatsapp_config()
