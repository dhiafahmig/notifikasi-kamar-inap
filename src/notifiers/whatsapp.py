import requests
import logging
from datetime import datetime
from .base import BaseNotifier

class WhatsAppNotifier(BaseNotifier):
    def __init__(self, config):
        super().__init__()
        # URL YANG BENAR sesuai Postman
        self.api_url = config.get("api_url", "https://api.kirimi.id/v1/send-message")
        self.user_code = config.get("user_code")
        self.secret = config.get("secret")
        self.device_id = config.get("device_id")
        self.enabled = config.get("enabled", True)
        self.timeout = config.get("timeout", 15)
        self.logger = logging.getLogger(__name__)
        
        if not (self.user_code and self.secret and self.device_id):
            self.logger.warning("⚠️ WhatsApp credentials not configured")
            self.enabled = False

    def send_patient_notification(self, patient: dict) -> bool:
        """Kirim notifikasi dengan format yang PERSIS SAMA dengan Postman"""
        if not self.enabled:
            return False
            
        whatsapp_number = patient.get("whatsapp_number")
        if not whatsapp_number:
            self.logger.warning("⚠️ Doctor %s has no WhatsApp number", patient["nm_dokter"])
            return False

        formatted_number = self._format_phone_number(whatsapp_number)
        
        # PAYLOAD FORMAT SAMA DENGAN POSTMAN
        payload = {
            "user_code": self.user_code,
            "secret": self.secret,
            "device_id": self.device_id,
            "receiver": formatted_number,
            "message": self._format_message(patient)
        }
        
        headers = {"Content-Type": "application/json"}

        try:
            self.logger.info("📤 Sending WhatsApp to %s", formatted_number)
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            self.logger.info(f"WhatsApp API Response: Status {response.status_code}, Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == True:
                    self.logger.info(
                        "✅ WhatsApp sent to Dr. %s — Patient: %s",
                        patient["nm_dokter"],
                        patient["nm_pasien"]
                    )
                    return True
            
            self.logger.error(
                "❌ WhatsApp failed for Dr. %s: HTTP %s - %s",
                patient["nm_dokter"],
                response.status_code,
                response.text
            )
            return False
            
        except requests.exceptions.RequestException as err:
            self.logger.error(
                "❌ WhatsApp request failed for Dr. %s: %s",
                patient["nm_dokter"],
                err
            )
            return False

    def _format_phone_number(self, phone: str) -> str:
        """Format nomor telepon"""
        if not phone:
            return ""
        
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        
        if clean_phone.startswith('0'):
            return clean_phone  # Format: 085758779026
        elif clean_phone.startswith('62'):
            return clean_phone[2:]  # Convert 6285758779026 -> 085758779026
        else:
            return clean_phone

    def _format_message(self, patient: dict) -> str:
        """Format pesan untuk notifikasi rawat inap"""
        notif_type = patient.get("notification_type", "new_patient_dpjp")
        
        if notif_type == "new_patient_dpjp":
            header = "🏥 *PASIEN BARU RAWAT INAP - DPJP ASSIGNED*"
        elif notif_type == "dpjp_changed":
            header = "🔄 *PERUBAHAN DPJP PASIEN RAWAT INAP*"
        else:
            header = "🏥 *NOTIFIKASI PASIEN RAWAT INAP*"

        # Format tanggal
        tgl_masuk = patient.get('tgl_masuk', datetime.now())
        if isinstance(tgl_masuk, str):
            try:
                tgl_masuk = datetime.strptime(tgl_masuk, '%Y-%m-%d %H:%M:%S')
            except:
                tgl_masuk = datetime.now()

        return f"""{header}

👤 *Nama Pasien:* {patient.get('nm_pasien', 'N/A')}
🚻 *Jenis Kelamin:* {patient.get('jenis_kelamin', 'N/A')}
📋 *No. Rawat:* {patient.get('no_rawat', 'N/A')}
📋 *No. Rekam Medis:* {patient.get('no_rkm_medis', 'N/A')}

🏠 *Kamar:* {patient.get('kd_kamar', 'N/A')}
🏥 *Bangsal:* {patient.get('nm_bangsal', 'N/A')} _(Kode: {patient.get('kd_bangsal', 'N/A')})_

📅 *Tanggal Masuk:* {tgl_masuk.strftime('%d/%m/%Y %H:%M WIB')}
🩺 *Diagnosa Awal:* {patient.get('diagnosa_awal', 'N/A')}
👨‍⚕️ *DPJP:* {patient.get('nm_dokter', 'N/A')}

⏰ Notifikasi: {datetime.now().strftime('%d/%m/%Y %H:%M WIB')}

_Notifikasi otomatis SIAK-RSBW_"""
