import unittest
from unittest.mock import patch, MagicMock

from src.db_manager import DBManager, _DBContextManager


class TestDBManager(unittest.TestCase):
    @patch("src.db_manager.psycopg2.pool.SimpleConnectionPool")
    def test_object_creation(self, mock_conn_pool_class):
        db_config = MagicMock()
        db_config.DB_HOST = "localhost"
        db_config.DB_CONTAINER_NAME = "your_container_name"
        db_config.DB_SERVICE_NAME = "your_service_name"
        db_config.DB_PORT = 5438
        db_config.DB_NAME = "your_db_name"
        db_config.DB_USER = "your_db_user"
        db_config.DB_PASSWORD = "your_db_password"

        mock_conn_pool = MagicMock()
        mock_conn_pool.dsn = "your_mocked_dsn"
        mock_conn_pool_class.return_value = mock_conn_pool

        db_manager = DBManager(db_config)

        self.assertIsNotNone(db_manager.conn_pool)
        self.assertEqual(
            db_manager.conn_pool.dsn,
            "your_mocked_dsn",
        )


class TestDBContextManager(unittest.TestCase):
    def test_enter_and_exit(self):
        conn_pool = MagicMock()
        conn_pool.getconn.return_value = "your_mocked_connection"

        with _DBContextManager(conn_pool) as conn:
            self.assertEqual(conn, "your_mocked_connection")

        conn_pool.putconn.assert_called_once_with("your_mocked_connection")


if __name__ == '__main__':
    unittest.main()
