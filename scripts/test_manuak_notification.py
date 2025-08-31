# scripts\test_manual_notification.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notifiers.telegram import TelegramNotifier
from utils.config import Config
from datetime import datetime

def test_notification():
    config = Config()
    telegram = TelegramNotifier(config.telegram)
    
    # Sample patient data dengan telegram_id
    sample_patient = {
        'nm_pasien': 'Test Patient',
        'jenis_kelamin': 'Laki-laki',
        'no_rawat': 'TEST001',
        'kd_kamar': 'VIP01',
        'tgl_masuk': datetime.now(),
        'diagnosa_awal': 'Test Notification',
        'nm_dokter': 'Dr. Test',
        'telegram_id': '@guardianteed'  # Ganti dengan telegram_id dokter yang valid
    }
    
    print("📱 Testing manual notification...")
    
    if telegram.send_patient_notification(sample_patient):
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Test notification failed!")

if __name__ == "__main__":
    test_notification()
