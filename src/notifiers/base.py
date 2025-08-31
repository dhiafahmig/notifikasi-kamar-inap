from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    """Base class for all notifiers"""
    
    @abstractmethod
    def send_patient_notification(self, patient: dict) -> bool:
        """Send patient notification"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test notifier connection"""
        pass
