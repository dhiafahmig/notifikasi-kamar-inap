#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseManager
from utils.config import Config
from datetime import datetime, timedelta

def test_query():
    config = Config()
    db_manager = DatabaseManager(config.database)
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Query dengan telegram_id
            query = """
            SELECT 
                ki.no_rawat,
                ki.kd_kamar,
                ki.tgl_masuk,
                p.nm_pasien,
                d.nm_dokter,
                d.telegram_id
            FROM kamar_inap ki
            JOIN reg_periksa rp ON ki.no_rawat = rp.no_rawat
            JOIN pasien p ON rp.no_rkm_medis = p.no_rkm_medis
            JOIN dpjp_ranap dr ON ki.no_rawat = dr.no_rawat
            JOIN dokter d ON dr.kd_dokter = d.kd_dokter
            WHERE ki.tgl_masuk > %s
            ORDER BY ki.tgl_masuk DESC
            LIMIT 5
            """
            
            # Test dengan 1 jam yang lalu
            since = datetime.now() - timedelta(hours=1)
            
            cursor.execute(query, (since,))
            patients = cursor.fetchall()
            
            print(f"🔍 Query test results (since {since}):")
            print(f"📊 Found {len(patients)} patients:")
            
            for patient in patients:
                print(f"  - {patient['nm_pasien']} ({patient['no_rawat']}) - {patient['tgl_masuk']}")
                print(f"    Doctor: {patient['nm_dokter']} - Telegram ID: {patient.get('telegram_id', 'None')}")
                print(f"    Room: {patient['kd_kamar']}")
                print()
            
            cursor.close()
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_query()
