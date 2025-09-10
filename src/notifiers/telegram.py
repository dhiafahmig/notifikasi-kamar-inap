import requests
import logging
from datetime import datetime
from .base import BaseNotifier


class TelegramNotifier(BaseNotifier):
    def __init__(self, config):
        super().__init__()
        self.token = config.get("bot_token")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.logger = logging.getLogger(__name__)

    # ---------------------------------------------------------- #
    def send_patient_notification(self, patient: dict) -> bool:
        if not patient.get("telegram_id"):
            self.logger.warning("⚠️ Doctor %s has no Telegram ID", patient["nm_dokter"])
            return False

        payload = {
            "chat_id": patient["telegram_id"],
            "text": self._format_message(patient),
            "parse_mode": "Markdown",
        }

        try:
            self.logger.info("📤 Sending to chat_id %s", patient["telegram_id"])
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            self.logger.info(
                "✅ Telegram sent to Dr. %s — Patient: %s",
                patient["nm_dokter"],
                patient["nm_pasien"],
            )
            return True
        except requests.exceptions.RequestException as err:
            self.logger.error(
                "❌ Telegram failed for Dr. %s: %s", patient["nm_dokter"], err
            )
            return False

    # ---------------------------------------------------------- #
    def _format_message(self, patient: dict) -> str:
        notif_type = patient.get("notification_type", "new_patient_dpjp")
        if notif_type == "new_patient_dpjp":
            header = "🏥 *PASIEN BARU RAWAT INAP - DPJP ASSIGNED*"
        elif notif_type == "dpjp_changed":
            header = "🔄 *PERUBAHAN DPJP PASIEN RAWAT INAP*"
        else:
            header = "🏥 *NOTIFIKASI PASIEN RAWAT INAP*"

        return (
            f"{header}\n\n"
            f"👨‍⚕️ *DPJP:* {patient['nm_dokter']}\n\n"
            f"👤 *Nama Pasien:* {patient['nm_pasien']}\n"
            f"🚻 *Jenis Kelamin:* {patient['jenis_kelamin']}\n"
            f"📋 *No. Rawat:* {patient['no_rawat']}\n"
            f"📋 *No. Rekam Medis:* {patient['no_rkm_medis']}\n\n"
            f"🏠 *Kamar:* {patient['kd_kamar']}\n"
            f"🏥 *Bangsal:* {patient['nm_bangsal']} _(Kode: {patient['kd_bangsal']})_\n\n"
            f"📅 *Tanggal Masuk:* {patient['tgl_masuk'].strftime('%d/%m/%Y %H:%M WIB')}\n"
            f"🩺 *Diagnosa Awal:* {patient['diagnosa_awal']}\n"
            f"⏰ Notifikasi: {datetime.now().strftime('%d/%m/%Y %H:%M WIB')}"
        )

    # ---------------------------------------------------------- #
    def test_connection(self) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as err:
            self.logger.error("❌ Telegram connection test failed: %s", err)
            return False
