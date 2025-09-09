#!/usr/bin/env python3

import os
import sys
import time
import schedule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database.connection import DatabaseManager
from database.queries import PatientQueries
from notifiers.telegram import TelegramNotifier
from notifiers.whatsapp import WhatsAppNotifier
from utils.logger import get_logger
from utils.config import Config

class HospitalNotificationQueueMonitor:
    def __init__(self):
        """Initialize sistem monitoring notifikasi rawat inap"""
        self.config = Config()
        self.logger = get_logger(__name__)
        self.db_manager = DatabaseManager(self.config.database)
        self.patient_queries = PatientQueries(self.db_manager)
        self.telegram = TelegramNotifier(self.config.telegram)
        self.whatsapp = WhatsAppNotifier(self.config.whatsapp)

    # ------------------------------------------------------------ #
    def test_connections(self):
        """Test semua koneksi saat startup"""
        self.logger.info("🔍 Testing all connections...")
        
        # Test database connection
        try:
            if self.db_manager.test_connection():
                self.logger.info("✅ Database connection OK")
            else:
                self.logger.error("❌ Database connection failed")
        except Exception as e:
            self.logger.error(f"❌ Database connection error: {e}")
            
        # Test Telegram connection
        try:
            if hasattr(self.telegram, 'test_connection') and self.telegram.test_connection():
                self.logger.info("✅ Telegram connection OK")
            else:
                self.logger.error("❌ Telegram connection failed")
        except Exception as e:
            self.logger.error(f"❌ Telegram connection error: {e}")
            
        # WhatsApp - hanya cek apakah enabled atau tidak (no connection test)
        try:
            if self.whatsapp.enabled:
                self.logger.info("✅ WhatsApp notification enabled")
            else:
                self.logger.info("⚠️ WhatsApp notification disabled")
        except Exception as e:
            self.logger.error(f"❌ WhatsApp configuration error: {e}")

    def process_notification_queue(self):
        """Ambil notifikasi pending, kirim Telegram + WhatsApp, update status."""
        try:
            self.logger.info("🔍 Checking notification queue…")
            pending = self.patient_queries.get_pending_notifications()
            
            if not pending:
                self.logger.info("ℹ️ No pending notifications")
                return

            self.logger.info("🆕 Found %s pending notifications", len(pending))
            
            for notif in pending:
                self._process_single_notification(notif)
                
        except Exception as err:
            self.logger.error("❌ Error processing queue: %s", err)

    # ------------------------------------------------------------ #
    def _process_single_notification(self, notif: dict):
        """Process single notification dengan dual channel (Telegram + WhatsApp)"""
        notif_id = notif["notification_id"]
        
        try:
            self.logger.info(
                "📤 Processing notification %s for %s",
                notif_id,
                notif["nm_pasien"]
            )

            # Send to both channels
            telegram_sent = False
            whatsapp_sent = False
            
            # Try Telegram
            try:
                if notif.get("telegram_id"):
                    telegram_sent = self.telegram.send_patient_notification(notif)
                    if telegram_sent:
                        self.logger.info("✅ Telegram sent successfully")
                    else:
                        self.logger.warning("⚠️ Telegram send failed")
                else:
                    self.logger.warning("⚠️ Doctor %s has no Telegram ID", notif["nm_dokter"])
            except Exception as e:
                self.logger.error("❌ Telegram send error: %s", e)
            
            # Try WhatsApp
            try:
                if notif.get("whatsapp_number"):
                    whatsapp_sent = self.whatsapp.send_patient_notification(notif)
                    if whatsapp_sent:
                        self.logger.info("✅ WhatsApp sent successfully")
                    else:
                        self.logger.warning("⚠️ WhatsApp send failed")
                else:
                    self.logger.warning("⚠️ Doctor %s has no WhatsApp number", notif["nm_dokter"])
            except Exception as e:
                self.logger.error("❌ WhatsApp send error: %s", e)

            # Update status based on results
            if telegram_sent or whatsapp_sent:
                # Success if at least one channel worked
                self.patient_queries.update_notification_status(notif_id, "sent")
                self.logger.info(
                    "✅ Notification %s sent - TG: %s, WA: %s",
                    notif_id,
                    "✓" if telegram_sent else "✗",
                    "✓" if whatsapp_sent else "✗"
                )
            else:
                # Failed both channels
                error_msg = self._generate_error_message(notif)
                self.patient_queries.update_notification_status(
                    notif_id, "failed", error_msg
                )
                self.logger.error("❌ Notification %s completely failed: %s", notif_id, error_msg)
                
        except Exception as err:
            self.patient_queries.update_notification_status(
                notif_id, "failed", str(err)
            )
            self.logger.error(
                "💥 Error processing notification %s: %s", notif_id, err
            )

    def _generate_error_message(self, notif: dict) -> str:
        """Generate appropriate error message based on available contact methods"""
        has_telegram = bool(notif.get("telegram_id"))
        has_whatsapp = bool(notif.get("whatsapp_number"))
        
        if not has_telegram and not has_whatsapp:
            return "Doctor has no Telegram ID or WhatsApp number"
        elif not has_telegram:
            return "Doctor has no Telegram ID, WhatsApp send failed"
        elif not has_whatsapp:
            return "Doctor has no WhatsApp number, Telegram send failed"
        else:
            return "Failed to send via both Telegram and WhatsApp"

    # ------------------------------------------------------------ #
    def start_monitoring(self):
        """Start monitoring dengan connection test awal"""
        try:
            # Test connections first
            self.test_connections()
            
            interval = self.config.app.get("check_interval", 10)
            self.logger.info("🚀 Monitor started — interval %s s", interval)
            
            # Schedule the notification checking
            schedule.every(interval).seconds.do(self.process_notification_queue)
            
            # First run immediately
            self.process_notification_queue()
            
            # Main monitoring loop
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("🛑 Stopped by user")
                    break
                except Exception as err:
                    self.logger.error("💥 Runtime error: %s", err)
                    time.sleep(5)  # Wait 5 seconds before continuing
                    
        except Exception as e:
            self.logger.error("💥 Fatal error during monitoring: %s", e)
            raise

    def stop_monitoring(self):
        """Gracefully stop the monitoring system"""
        self.logger.info("🛑 Stopping notification monitor...")
        schedule.clear()  # Clear all scheduled jobs

if __name__ == "__main__":
    try:
        monitor = HospitalNotificationQueueMonitor()
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"💥 Fatal application error: {e}")
        sys.exit(1)
