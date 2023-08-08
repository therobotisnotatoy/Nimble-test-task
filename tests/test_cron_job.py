import logging
import requests
import unittest
from unittest.mock import patch, MagicMock

from src.cron_job import cron_job_main
from src.utils import HUMAN_READABLE_FIELDS


class TestMain(unittest.TestCase):
    @patch('src.cron_job.Env')
    @patch('src.cron_job.AppConfig')
    @patch('src.cron_job.DBManager')
    @patch('requests.get')
    def test_main(self, mock_get, mock_db_manager, mock_app_config, mock_env):
        mock_env_instance = mock_env.return_value
        mock_env_instance.read_env.return_value = None
        mock_app_config_instance = mock_app_config.from_env.return_value
        mock_app_config_instance.db_config = "dummy_db_config"
        mock_db_manager_instance = mock_db_manager.return_value
        mock_db_manager_instance.__enter__.return_value = mock_db_manager_instance

        expected_contacts = {
            "resources": [
                {
                    "fields": {
                        "first name": [{"value": "John"}],
                        "last name": [{"value": "Doe"}],
                        "email": [{"value": "john@example.com"}]},
                    "record_type": "person"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_contacts
        mock_get.return_value = mock_response

        logging.basicConfig(level=logging.CRITICAL)
        logger = logging.getLogger(__name__)

        cron_job_main(logger)

        mock_env.assert_called_once()
        mock_app_config.from_env.assert_called_once_with(mock_env_instance)
        mock_db_manager.assert_called_once_with("dummy_db_config")
        mock_db_manager_instance.connect.assert_called_once()
        mock_get.assert_called_once_with(
            mock_app_config_instance.nimble_api_config.NIMBLE_API_URL,
            headers={"Authorization": f"Bearer {mock_app_config_instance.nimble_api_config.NIMBLE_API_KEY}"},
            params={"fields": ', '.join(HUMAN_READABLE_FIELDS)}
        )


if __name__ == '__main__':
    unittest.main()
