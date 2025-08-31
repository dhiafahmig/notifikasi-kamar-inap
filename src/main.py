#!/usr/bin/env python3

import sys
import os
import time
import schedule
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseManager
from database.queries import PatientQueries
from notifiers.telegram import TelegramNotifier
from utils.logger import get_logger
from utils.config import Config

class HospitalNotificationQueueMonitor:
    def __init__(self):
        self.config = Config()
        self.logger = get_logger(__name__)
        self.db_manager = DatabaseManager(self.config.database)
        self.patient_queries = PatientQueries(self.db_manager)
        self.telegram = TelegramNotifier(self.config.telegram)
        
    def process_notification_queue(self):
        """Process pending notifications from queue"""
        try:
            self.logger.info("🔍 Checking notification queue...")
            
            pending_notifications = self.patient_queries.get_pending_notifications()
            
            if pending_notifications:
                self.logger.info(f"🆕 Found {len(pending_notifications)} pending notifications")
                
                for notification in pending_notifications:
                    self._process_single_notification(notification)
            else:
                self.logger.info("ℹ️ No pending notifications")
                
        except Exception as e:
            self.logger.error(f"❌ Error processing notification queue: {e}")
    
    def _process_single_notification(self, notification):
        """Process a single notification"""
        try:
            notification_id = notification['notification_id']
            self.logger.info(f"📤 Processing notification {notification_id} for patient: {notification['nm_pasien']}")
            
            if notification.get('telegram_id'):
                # Kirim notifikasi Telegram
                if self.telegram.send_patient_notification(notification):
                    # Update status ke 'sent'
                    self.patient_queries.update_notification_status(notification_id, 'sent')
                    self.logger.info(f"✅ Notification {notification_id} sent successfully")
                else:
                    # Update status ke 'failed'
                    self.patient_queries.update_notification_status(
                        notification_id, 'failed', 'Failed to send Telegram message'
                    )
                    self.logger.error(f"❌ Notification {notification_id} failed to send")
            else:
                # Dokter tidak punya Telegram ID
                self.patient_queries.update_notification_status(
                    notification_id, 'failed', f'Doctor {notification["nm_dokter"]} has no Telegram ID'
                )
                self.logger.warning(f"⚠️ Doctor {notification['nm_dokter']} has no Telegram ID")
                
        except Exception as e:
            # Update status ke 'failed' dengan error message
            if 'notification_id' in locals():
                self.patient_queries.update_notification_status(
                    notification['notification_id'], 'failed', str(e)
                )
            self.logger.error(f"❌ Error processing notification: {e}")

    def start_monitoring(self):
        """Start the queue monitoring system"""
        check_interval = self.config.app.get('check_interval', 10)  # Check setiap 10 detik
        
        self.logger.info("🚀 Hospital Notification Queue Monitor Started")
        self.logger.info(f"⏱️ Check interval: {check_interval} seconds")
        
        # Schedule regular checks
        schedule.every(check_interval).seconds.do(self.process_notification_queue)
        
        # Initial check
        self.process_notification_queue()
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("🛑 System stopped by user")
                break
            except Exception as e:
                self.logger.error(f"💥 System error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = HospitalNotificationQueueMonitor()
    monitor.start_monitoring()
