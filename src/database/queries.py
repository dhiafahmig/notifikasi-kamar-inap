from datetime import datetime
from typing import List, Dict
import logging

class PatientQueries:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def get_pending_notifications(self) -> List[Dict]:
        """Get pending notifications from queue"""
        
        query = """
        SELECT 
            nq.id as notification_id,
            nq.no_rawat,
            nq.notification_type,
            nq.created_at as notification_time,
            ki.kd_kamar,
            ki.diagnosa_awal,
            ki.tgl_masuk,
            p.nm_pasien,
            CASE 
                WHEN p.jk = 'L' THEN 'Laki-laki'
                WHEN p.jk = 'P' THEN 'Perempuan'
                ELSE 'Tidak Diketahui'
            END as jenis_kelamin,
            d.nm_dokter,
            d.telegram_id
        FROM notification_queue nq
        JOIN kamar_inap ki ON nq.no_rawat = ki.no_rawat
        JOIN reg_periksa rp ON ki.no_rawat = rp.no_rawat
        JOIN pasien p ON rp.no_rkm_medis = p.no_rkm_medis
        JOIN dpjp_ranap dr ON ki.no_rawat = dr.no_rawat
        JOIN dokter d ON dr.kd_dokter = d.kd_dokter
        WHERE nq.status = 'pending'
        ORDER BY nq.created_at ASC
        LIMIT 10
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query)
                notifications = cursor.fetchall()
                cursor.close()
                
                self.logger.info(f"📊 Found {len(notifications)} pending notifications")
                return notifications
                
        except Exception as e:
            self.logger.error(f"❌ Error fetching notifications: {e}")
            return []

    def update_notification_status(self, notification_id: int, status: str, error_message: str = None):
        """Update notification status in queue"""
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if status == 'sent':
                    query = """
                    UPDATE notification_queue 
                    SET status = %s, sent_at = NOW() 
                    WHERE id = %s
                    """
                    cursor.execute(query, (status, notification_id))
                elif status == 'failed':
                    query = """
                    UPDATE notification_queue 
                    SET status = %s, retry_count = retry_count + 1, error_message = %s 
                    WHERE id = %s
                    """
                    cursor.execute(query, (status, error_message, notification_id))
                
                conn.commit()
                cursor.close()
                
        except Exception as e:
            self.logger.error(f"❌ Error updating notification status: {e}")

    def get_new_inpatients(self, since: datetime) -> List[Dict]:
        """Get new inpatients since specified time (legacy method for backup)"""
        
        query = """
        SELECT
            ki.no_rawat,
            ki.kd_kamar,
            ki.diagnosa_awal,
            ki.tgl_masuk,
            p.nm_pasien,
            CASE
                WHEN p.jk = 'L' THEN 'Laki-laki'
                WHEN p.jk = 'P' THEN 'Perempuan'
                ELSE 'Tidak Diketahui'
            END as jenis_kelamin,
            d.nm_dokter,
            d.telegram_id
        FROM kamar_inap ki
        JOIN reg_periksa rp ON ki.no_rawat = rp.no_rawat
        JOIN pasien p ON rp.no_rkm_medis = p.no_rkm_medis
        JOIN dpjp_ranap dr ON ki.no_rawat = dr.no_rawat
        JOIN dokter d ON dr.kd_dokter = d.kd_dokter
        WHERE ki.tgl_masuk > %s
        ORDER BY ki.tgl_masuk DESC
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (since,))
                patients = cursor.fetchall()
                cursor.close()
                
                self.logger.info(f"📊 Found {len(patients)} patients since {since}")
                return patients
                
        except Exception as e:
            self.logger.error(f"❌ Error fetching patients: {e}")
            return []
