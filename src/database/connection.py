import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import logging

class DatabaseManager:
    def __init__(self, db_config):
        self.logger = logging.getLogger(__name__)
        self.config = db_config
        self._pool = None
        self._create_pool()
    
    def _create_pool(self):
        """Create connection pool"""
        try:
            pool_config = {
                'pool_name': 'hospital_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                **self.config
            }
            
            self._pool = pooling.MySQLConnectionPool(**pool_config)
            self.logger.info("✅ Database connection pool created")
            
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except mysql.connector.Error as e:
            self.logger.error(f"❌ Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"❌ Connection test failed: {e}")
            return False
