🏥 Notifikasi Rawat Inap Ke Dokter DPJP 
Sistem notifikasi real-time untuk rumah sakit yang mengirim alert Telegram kepada dokter ketika ada pasien baru rawat inap yang ditugaskan sebagai DPJP (Dokter Penanggung Jawab Pasien).

Compatible dengan database SIMRS Khanza.

📋 Table of Contents
Features

Architecture

Prerequisites

Installation

Database Setup

Telegram Bot Setup

Configuration

Usage

Monitoring

Troubleshooting

Contributing

License

✨ Features
🚨 Real-time notifications via database triggers

📱 Telegram integration for instant messaging

🏥 SIMRS Khanza compatible

📊 Queue-based architecture untuk reliability

🔄 Automatic retry mechanism untuk failed notifications

📝 Comprehensive logging untuk monitoring dan debugging

⚙️ Configurable intervals untuk checking

🛡️ Error handling yang robust

📈 Scalable design untuk multiple hospitals

🏗️ Architecture
text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SIMRS Khanza  │    │   MySQL Trigger  │    │ Notification    │
│   (Java App)    │───▶│   (Database)     │───▶│ Queue Table     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Telegram Bot    │◀───│ Python Monitor   │◀───│ Queue Processor │
│ (Notifications) │    │ (Main App)       │    │ (Background)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
📋 Prerequisites
Python 3.8+

MySQL/MariaDB 5.7+

SIMRS Khanza atau database dengan struktur serupa

Telegram Bot Token

Windows/Linux Server

🚀 Installation
1. Clone Repository
bash
git clone https://github.com/yourusername/hospital-notification-system.git
cd hospital-notification-system
2. Create Virtual Environment
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Create Directory Structure
bash
mkdir -p logs config
🗄️ Database Setup
1. Create Notification Queue Table
sql
CREATE TABLE notification_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    no_rawat VARCHAR(20) NOT NULL,
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    notification_type VARCHAR(50) DEFAULT 'new_patient_dpjp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL,
    retry_count INT DEFAULT 0,
    error_message TEXT NULL,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_no_rawat (no_rawat)
);
2. Add Telegram ID Column to Doctor Table
sql
ALTER TABLE dokter 
ADD COLUMN telegram_id VARCHAR(50) NULL;
3. Create Database Trigger
sql
DELIMITER $$

CREATE TRIGGER trg_after_insert_dpjp_notification
AFTER INSERT ON dpjp_ranap
FOR EACH ROW
BEGIN
    INSERT INTO notification_queue (no_rawat, notification_type, status, created_at)
    VALUES (NEW.no_rawat, 'new_patient_dpjp', 'pending', NOW());
END$$

DELIMITER ;
🤖 Telegram Bot Setup
1. Create Telegram Bot
Chat dengan @BotFather di Telegram

Kirim /newbot

Ikuti instruksi untuk membuat bot

Simpan Bot Token yang diberikan

2. Get Doctor Chat IDs
Minta setiap dokter untuk chat dengan bot Anda

Dokter kirim /start ke bot

Ambil Chat ID dengan mengakses:

text
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
Salin chat.id dari response JSON

3. Update Doctor Data
sql
-- Update telegram_id untuk setiap dokter
UPDATE dokter SET telegram_id = '123456789' WHERE kd_dokter = 'D001';
UPDATE dokter SET telegram_id = '987654321' WHERE kd_dokter = 'D002';
-- Dst...
⚙️ Configuration
1. Environment Configuration
Copy dan edit file environment:

bash
cp config/.env.example config/.env
Edit config/.env:

text
# Database Configuration
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=sik
DB_PORT=3306

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Application Settings
CHECK_INTERVAL=10
LOG_LEVEL=INFO
2. YAML Configuration
Edit config/config.yaml:

text
app:
  name: "Hospital Patient Notification System"
  version: "1.0.0"
  check_interval: 10  # seconds
  debug: false

database:
  host: "localhost"
  port: 3306
  user: "root"
  password: ""
  database: "sik"
  charset: "utf8mb4"
  autocommit: true

telegram:
  bot_token: "your_telegram_bot_token"
  enabled: true

logging:
  level: "INFO"
  file: "logs/patient_monitor.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
🏃‍♂️ Usage
Running the Application
Development Mode
bash
python src/main.py
Production Mode (Linux)
Install as systemd service:

bash
sudo cp systemd/hospital-notification.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hospital-notification
sudo systemctl start hospital-notification
Check status:

bash
sudo systemctl status hospital-notification
Production Mode (Windows)
bash
# Run as Windows Service menggunakan NSSM atau Task Scheduler
# Atau jalankan di PowerShell:
python src/main.py
Expected Output
text
🚀 Hospital Notification Queue Monitor Started
⏱️ Check interval: 10 seconds
🔍 Checking notification queue...
🆕 Found 1 pending notifications
📤 Processing notification 1 for patient: John Doe
✅ Telegram sent to Dr. Ahmad - Patient: John Doe
✅ Notification 1 sent successfully
📊 Monitoring
Log Files
bash
# Monitor real-time logs
tail -f logs/patient_monitor.log

# Check system logs (Linux)
sudo journalctl -u hospital-notification -f
Database Monitoring
sql
-- Check notification queue status
SELECT 
    status, 
    COUNT(*) as count,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM notification_queue 
GROUP BY status;

-- Check failed notifications
SELECT * FROM notification_queue 
WHERE status = 'failed' 
ORDER BY created_at DESC 
LIMIT 10;
Health Check Endpoints
bash
# Test database connection
python scripts/test_connection.py

# Test Telegram bot
python scripts/test_telegram.py
🐛 Troubleshooting
Common Issues
1. No Notifications Received
Check:

Database trigger is created: SHOW TRIGGERS LIKE 'trg_after_insert_dpjp_notification';

Doctor has telegram_id: SELECT telegram_id FROM dokter WHERE kd_dokter = 'D001';

Queue has pending items: SELECT * FROM notification_queue WHERE status = 'pending';

2. Database Connection Error
Solutions:

Verify database credentials in config files

Check if MySQL service is running

Test connection: python scripts/test_connection.py

3. Telegram API Error
Solutions:

Verify bot token is correct

Check if bot is blocked by user

Test with: python scripts/test_telegram.py

4. Unicode/Emoji Errors (Windows)
Solution:

bash
# Set PowerShell to UTF-8
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
python src/main.py
Debug Mode
Enable debug logging in config/config.yaml:

text
app:
  debug: true
logging:
  level: "DEBUG"
🤝 Contributing
Fork the repository

Create feature branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push to branch: git push origin feature/amazing-feature

Open Pull Request

Development Setup
bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black src/
flake8 src/
📁 Project Structure
text
hospital-notification-system/
├── src/
│   ├── database/
│   │   ├── connection.py      # Database connection pool
│   │   └── queries.py         # SQL queries
│   ├── notifiers/
│   │   ├── base.py           # Base notifier class
│   │   └── telegram.py       # Telegram integration
│   ├── utils/
│   │   ├── config.py         # Configuration loader
│   │   └── logger.py         # Logging setup
│   └── main.py               # Main application
├── config/
│   ├── .env.example          # Environment template
│   └── config.yaml           # YAML configuration
├── scripts/
│   ├── test_connection.py    # Database test
│   └── test_telegram.py      # Telegram test
├── systemd/
│   └── hospital-notification.service
├── logs/                     # Log files
├── requirements.txt          # Python dependencies
└── README.md
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Authors
Dhia Fahmi Ghufron - @dhiafahmig

🙏 Acknowledgments
SIMRS Khanza untuk struktur database

Telegram Bot API untuk messaging platform

Hospital staff yang memberikan requirements dan feedback

📞 Support

Email: fahmighufron@gmail.com

⭐ Jika project ini membantu Anda, mohon berikan star di GitHub! ⭐