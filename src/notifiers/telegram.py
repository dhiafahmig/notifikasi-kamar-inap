import requests
from datetime import datetime
import logging
from .base import BaseNotifier

class TelegramNotifier(BaseNotifier):
    def __init__(self, config):
        super().__init__()
        self.token = config.get('bot_token')
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.logger = logging.getLogger(__name__)

    def send_patient_notification(self, patient: dict) -> bool:
        """Send patient notification via Telegram"""
        
        if not patient.get('telegram_id'):
            self.logger.warning(f"⚠️ No Telegram chat ID for {patient['nm_dokter']}")
            return False

        message = self._format_message(patient)
        
        payload = {
            'chat_id': patient['telegram_id'],
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            self.logger.info(f"📤 Sending to chat_id: {patient['telegram_id']}")
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"✅ Telegram sent to {patient['nm_dokter']} - Patient: {patient['nm_pasien']}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Telegram failed for {patient['nm_dokter']}: {e}")
            return False

    def _format_message(self, patient: dict) -> str:
        """Format patient notification message"""
        
        notification_type = patient.get('notification_type', 'new_patient_dpjp')
        
        if notification_type == 'new_patient_dpjp':
            header = "🏥 *PASIEN BARU RAWAT INAP - DPJP ASSIGNED*"
        elif notification_type == 'dpjp_changed':
            header = "🔄 *PERUBAHAN DPJP PASIEN RAWAT INAP*"
        else:
            header = "🏥 *NOTIFIKASI PASIEN RAWAT INAP*"
        
        return f"""
{header}

👤 *Nama Pasien:* {patient['nm_pasien']}
🚻 *Jenis Kelamin:* {patient['jenis_kelamin']}
📋 *No. Rawat:* {patient['no_rawat']}
🏠 *Kamar:* {patient['kd_kamar']}
📅 *Tanggal Masuk:* {patient['tgl_masuk'].strftime('%d/%m/%Y %H:%M WIB')}
🩺 *Diagnosa Awal:* {patient['diagnosa_awal']}
👨‍⚕️ *DPJP:* {patient['nm_dokter']}

⏰ Notifikasi: {datetime.now().strftime('%d/%m/%Y %H:%M WIB')}
        """

    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"❌ Telegram connection test failed: {e}")
            return False
