from environs import Env
import unittest
from unittest.mock import MagicMock, patch

from src.app_config import NimbleAPIConfig
from src.utils import (get_from_csv, init_db_with_csv, get_contacts, update_db, prepare_db, get_valid_fields,
                       get_search_condition, search_contacts, CSV_FILE_PATH,)


class TestMainUtils(unittest.TestCase):
    def test_get_from_csv(self):
        file_path = "tests/test.csv"
        with open(file_path, "w", newline='', encoding='utf-8') as csvfile:
            csvfile.write("first name,last name,Email\nJohn,Doe,john@example.com\nJane,Smith,jane@example.com")

        contacts_data = get_from_csv(file_path)

        self.assertEqual(contacts_data, [("John", "Doe", "john@example.com"), ("Jane", "Smith", "jane@example.com")])

    def test_init_db_with_csv(self):
        db_manager = MagicMock()
        file_path = "tests/test.csv"
        contacts_data = [("John", "Doe", "john@example.com"), ("Jane", "Smith", "jane@example.com")]

        with patch("src.utils.get_from_csv", return_value=contacts_data) as mock_read_csv:
            init_db_with_csv(db_manager, file_path)

        mock_read_csv.assert_called_once_with(file_path)
        db_manager.connect.assert_called_once()
        db_manager.connect.return_value.__enter__.return_value.cursor.assert_called_once()

    def test_get_contacts(self):
        env = Env()
        env.read_env(".env", False)
        nimble_api_config = NimbleAPIConfig.from_env(env)

        contacts = get_contacts(nimble_api_config)

        self.assertIsNotNone(contacts)
        self.assertIsNotNone(contacts.get("resources"))
        self.assertIsNotNone(contacts["resources"][0].get("record_type"))

    def test_update_db(self):
        db_manager = MagicMock()
        nimble_contacts = {
            "resources": [
                {
                    "fields": {
                        "first name": [{"value": "John"}],
                        "last name": [{"value": "Doe"}],
                        "email": [{"value": "john@example.com"}]
                    },
                    "record_type": "person"
                }
            ]
        }

        with patch("src.db_manager.DBManager", return_value=db_manager) as _:
            update_db(db_manager, nimble_contacts)

        db_manager.connect.assert_called_once()
        db_manager.connect.return_value.__enter__.return_value.cursor.assert_called_once()

    def test_prepare_db_with_csv(self):
        db_manager = MagicMock()
        nimble_api_config = NimbleAPIConfig(
            NIMBLE_API_KEY="api_key",
            NIMBLE_API_URL="http://example.com/api",
        )

        with patch("src.utils.init_db_with_csv") as mock_init_db_with_csv, \
            patch("src.utils.get_contacts") as mock_get_contacts, \
            patch("src.utils.update_db") as mock_update_db:

            mock_get_contacts_instance = MagicMock()
            mock_get_contacts.return_value = mock_get_contacts_instance

            prepare_db(db_manager, nimble_api_config, init=True)

        mock_init_db_with_csv.assert_called_once_with(db_manager, CSV_FILE_PATH)
        mock_get_contacts.assert_called_once_with(nimble_api_config)
        mock_update_db.assert_called_once_with(db_manager, mock_get_contacts_instance)

    def test_prepare_db_with_api(self):
        db_manager = MagicMock()
        nimble_api_config = NimbleAPIConfig(
            NIMBLE_API_KEY="api_key",
            NIMBLE_API_URL="http://example.com/api",
        )

        nimble_contacts = {
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

        with patch("src.utils.init_db_with_csv") as mock_init_db_with_csv, \
            patch("src.utils.get_contacts", return_value=nimble_contacts) as mock_get_contacts, \
            patch("src.utils.update_db") as mock_update_db:

            prepare_db(db_manager, nimble_api_config)

        mock_init_db_with_csv.assert_not_called()
        mock_get_contacts.assert_called_once_with(nimble_api_config)
        mock_update_db.assert_called_once_with(db_manager, nimble_contacts)

        with patch("src.utils.init_db_with_csv") as mock_init_db_with_csv, \
            patch("src.utils.get_contacts", return_value=nimble_contacts) as mock_get_contacts, \
            patch("src.utils.update_db") as mock_update_db:

            prepare_db(db_manager, nimble_api_config, init=True)

        mock_init_db_with_csv.assert_called_once_with(db_manager, CSV_FILE_PATH)
        mock_get_contacts.assert_called_once_with(nimble_api_config)
        mock_update_db.assert_called_once_with(db_manager, nimble_contacts)

    def test_get_valid_fields(self):
        fields = "first_name,last name,invalid_field"
        valid_fields = get_valid_fields(fields)

        self.assertEqual(valid_fields, ["first_name", "last_name"])

    def test_get_search_condition(self):
        search_fields = ["first_name", "last_name"]
        search_condition = get_search_condition(search_fields)

        self.assertEqual(search_condition, "COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')")

    def test_search_contacts(self):
        db_manager = MagicMock()
        query = "John"
        search_fields = ["first_name", "last_name"]
        expected_query = """
        SELECT *
        FROM contacts
        WHERE to_tsvector('english', COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) @@ plainto_tsquery('english', %s);
    """

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # Assuming you expect an empty result

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        db_manager.connect.return_value.__enter__.return_value = mock_connection

        contacts = search_contacts(db_manager, query, search_fields)

        db_manager.connect.assert_called_once()
        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(expected_query, (query,))
        mock_cursor.fetchall.assert_called_once()

        self.assertEqual(contacts, [])


if __name__ == "__main__":
    unittest.main()
