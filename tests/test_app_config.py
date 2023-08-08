import unittest
from environs import Env

from src.app_config import DBConfig, NimbleAPIConfig, AppConfig


class TestDBConfig(unittest.TestCase):
    def test_from_env(self):
        env = Env()
        env.read_env("tests/test.env", False)

        db_config = DBConfig.from_env(env)

        self.assertEqual(db_config.DB_HOST, "192.168.10.22")
        self.assertEqual(db_config.DB_PORT, 5438)
        self.assertEqual(db_config.DB_NAME, "your_db_name")
        self.assertEqual(db_config.DB_USER, "your_db_user")
        self.assertEqual(db_config.DB_PASSWORD, "your_db_password")
        self.assertEqual(db_config.DB_CONTAINER_NAME, "your_db_container_name")
        self.assertEqual(db_config.DB_SERVICE_NAME, "your_db_service_name")


class TestNimbleAPIConfig(unittest.TestCase):
    def test_from_env(self):
        env = Env()
        env.read_env("tests/test.env", False)

        nimble_api_config = NimbleAPIConfig.from_env(env)

        self.assertEqual(nimble_api_config.NIMBLE_API_KEY, "XxxYyyZzzXxxYyyZzzXxxYyyZzzXxx")
        self.assertEqual(nimble_api_config.NIMBLE_API_URL, "https://api.somecompany.com/api/v1/contacts")


class TestAppConfig(unittest.TestCase):
    def test_from_env(self):
        env = Env()
        env.read_env("tests/test.env", False)

        app_config = AppConfig.from_env(env)

        self.assertIsInstance(app_config.db_config, DBConfig)
        self.assertIsInstance(app_config.nimble_api_config, NimbleAPIConfig)


if __name__ == "__main__":
    unittest.main()
