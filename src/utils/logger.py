import logging
import logging.handlers
from pathlib import Path
import sys

class Utf8StreamHandler(logging.StreamHandler):
    """Custom stream handler yang support UTF-8 untuk Windows"""
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        super().__init__(stream)
    
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Coba write ke buffer dengan UTF-8 encoding
            if hasattr(stream, 'buffer'):
                stream.buffer.write((msg + self.terminator).encode('utf-8'))
                stream.buffer.flush()
            else:
                # Fallback ke stream biasa
                stream.write(msg + self.terminator)
                stream.flush()
        except (UnicodeEncodeError, AttributeError):
            # Jika gagal, hapus emoji dan coba lagi
            try:
                clean_msg = self._clean_unicode(self.format(record))
                self.stream.write(clean_msg + self.terminator)
                self.stream.flush()
            except Exception:
                self.handleError(record)
    
    def _clean_unicode(self, text):
        """Ganti emoji dengan text alternatif"""
        emoji_map = {
            '🔍': '[SEARCH]',
            '⏱️': '[TIMER]', 
            'ℹ️': '[INFO]',
            '🚀': '[START]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🆕': '[NEW]',
            '📊': '[DATA]',
            '🛑': '[STOP]',
            '💥': '[CRASH]',
            '🏥': '[HOSPITAL]',
            '👤': '[PATIENT]',
            '📋': '[ID]',
            '🏠': '[ROOM]',
            '📅': '[DATE]',
            '🩺': '[DIAGNOSIS]',
            '👨‍⚕️': '[DOCTOR]'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        return text

def get_logger(name):
    """Get configured logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create logs directory
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler with UTF-8 encoding
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'patient_monitor.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'  # Penting: set encoding UTF-8
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler dengan UTF-8 support
        console_handler = Utf8StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger
