#!/usr/bin/env python3
import os
import sys
import time
import schedule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database.connection import DatabaseManager
from database.queries   import PatientQueries
from notifiers.telegram import TelegramNotifier
from utils.logger       import get_logger
from utils.config       import Config


class HospitalNotificationQueueMonitor:
    def __init__(self):
        self.config          = Config()
        self.logger          = get_logger(__name__)
        self.db_manager      = DatabaseManager(self.config.database)
        self.patient_queries = PatientQueries(self.db_manager)
        self.telegram        = TelegramNotifier(self.config.telegram)

    # ------------------------------------------------------------ #
    def process_notification_queue(self):
        """Ambil notifikasi pending, kirim Telegram, update status."""
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
        notif_id = notif["notification_id"]
        try:
            self.logger.info(
                "📤 Processing notification %s for %s",
                notif_id,
                notif["nm_pasien"],
            )

            if not notif.get("telegram_id"):
                self.patient_queries.update_notification_status(
                    notif_id, "failed", "Doctor has no Telegram ID"
                )
                self.logger.warning(
                    "⚠️ Doctor %s has no Telegram ID", notif["nm_dokter"]
                )
                return

            if self.telegram.send_patient_notification(notif):
                self.patient_queries.update_notification_status(notif_id, "sent")
                self.logger.info("✅ Notification %s sent", notif_id)
            else:
                self.patient_queries.update_notification_status(
                    notif_id, "failed", "Telegram send error"
                )
                self.logger.error("❌ Notification %s failed to send", notif_id)

        except Exception as err:
            self.patient_queries.update_notification_status(notif_id, "failed", str(err))
            self.logger.error("💥 Error processing notification %s: %s", notif_id, err)

    # ------------------------------------------------------------ #
    def start_monitoring(self):
        interval = self.config.app.get("check_interval", 10)  # detik
        self.logger.info("🚀 Monitor started — interval %s s", interval)

        schedule.every(interval).seconds.do(self.process_notification_queue)
        self.process_notification_queue()  # first run

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("🛑 Stopped by user")
                break
            except Exception as err:
                self.logger.error("💥 Runtime error: %s", err)
                time.sleep(5)


if __name__ == "__main__":
    HospitalNotificationQueueMonitor().start_monitoring()
