import csv
import logging
import requests
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

try:
    from app_config import NimbleAPIConfig
    from db_manager import DBManager
except ModuleNotFoundError:
    from src.app_config import NimbleAPIConfig
    from src.db_manager import DBManager


logger = logging.getLogger(__name__)

CSV_FILE_PATH = "src/Nimble Contacts - Sheet1.csv"
VALID_FIELDS = ["first_name", "last_name", "email"]
HUMAN_READABLE_FIELDS = [field.replace('_', ' ') for field in VALID_FIELDS]


def get_from_csv(file_path) -> list():
    """Read data from a CSV file and return a list of contacts."""
    contacts_data = list()
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            first_name, last_name, email = row
            contacts_data.append((first_name, last_name, email))
    return contacts_data


def init_db_with_csv(db_manager: DBManager, file_path: str) -> None:
    """Initialize the 'contacts' database table with data from a CSV file."""
    contacts_data = get_from_csv(file_path)
    if contacts_data:
        try:
            with db_manager.connect() as conn:
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO contacts (first_name, last_name, email) VALUES (%s, %s, %s);",
                        contacts_data,
                    )
                    conn.commit()
            logger.info("Database initialized with data from CSV.")
        except OperationalError as exc:
            logger.error(f"Failed to initialize the database with csv file: {exc}")


def get_contacts(nimble_api_config: NimbleAPIConfig) -> dict:
    """Get contacts from the Nimble API."""
    headers = {"Authorization": f"Bearer {nimble_api_config.NIMBLE_API_KEY}"}
    fields_to_get = ', '.join(HUMAN_READABLE_FIELDS)
    params = {"fields": fields_to_get}
    response = requests.get(nimble_api_config.NIMBLE_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    logger.error(f"Failed to get contacts from Nimble API. Status code: {response.status_code}")


def update_db(db_manager: DBManager, nimble_contacts: dict) -> None:
    """Update the 'contacts' database table with data from the Nimble API."""
    with db_manager.connect() as conn:
        with conn.cursor() as cur:
            conn.autocommit = False
            try:
                cur.execute("DELETE FROM contacts;")
                empty_value = [{"value": None}]
                contacts_data = [
                    (
                        contact["fields"].get("first name", empty_value)[0].get("value", ""),
                        contact["fields"].get("last name", empty_value)[0].get("value", ""),
                        contact["fields"].get("email", empty_value)[0].get("value", ""),
                    ) for contact in nimble_contacts["resources"] if contact["record_type"] == "person"
                ]
                cur.executemany(
                    "INSERT INTO contacts (first_name, last_name, email) VALUES (%s, %s, %s);",
                    contacts_data,
                )
                logger.info("Successfully updated contacts from Nimble API.")
            except Exception as exc:
                conn.rollback()
                logger.error(f"Failed to update contacts: {exc}")
            else:
                create_query = """
                    CREATE INDEX IF NOT EXISTS contacts_fulltext_idx ON contacts
                    USING GIN (to_tsvector('english', first_name || ' ' || last_name || ' ' || email));
                """
                cur.execute(create_query)
                conn.commit()
                logger.info("Successfully created index on contacts table.")


def prepare_db(
    db_manager: DBManager,
    nimble_api_config: NimbleAPIConfig,
    init: bool = False,
) -> None:
    """Prepare the database by initializing it with CSV data (optionl)
    and updating it with Nimble API data."""
    if init:
        init_db_with_csv(db_manager, CSV_FILE_PATH)
    nimble_contacts = get_contacts(nimble_api_config)
    if not nimble_contacts:
        logger.warning("Failed to get contacts from Nimble API. Using default data from csv file.")
        return
    try:
        update_db(db_manager, nimble_contacts)
    except Exception as exc:
        logger.error(f"Failed to connect to the database: {exc}")


def get_valid_fields(fields: str) -> list:
    """Extract and validate the list of fields for searching."""
    if fields:
        fields = fields.split(',')
        search_fields = [field.strip() for field in fields if field.strip() in VALID_FIELDS + HUMAN_READABLE_FIELDS]
        if len(search_fields) > 0:
            return [field.replace(' ', '_') for field in search_fields]
    return VALID_FIELDS


def get_search_condition(search_fields: list) -> str:
    """Create a condition for full-text search based on the search fields."""
    return " || ' ' || ".join(f'COALESCE({field}, \'\')' for field in search_fields)


def search_contacts(db_manager: DBManager, query: str, search_fields: list):
    """Perform a full-text search in the 'contacts' database table."""
    fields_condition = get_search_condition(search_fields)
    search_query = """
        SELECT *
        FROM contacts
        WHERE to_tsvector('english', {fields_condition}) @@ plainto_tsquery('english', %s);
    """
    with db_manager.connect() as conn:
        pass
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(search_query.format(fields_condition=fields_condition), (query,))
            contacts = cur.fetchall()
    return contacts


if __name__ == "__main__":
    pass
