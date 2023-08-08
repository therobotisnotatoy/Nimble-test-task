import logging
import time
from fastapi import FastAPI, Query, HTTPException
from environs import Env
from psycopg2 import OperationalError

from src.app_config import AppConfig
from src.db_manager import DBManager
from src.utils import prepare_db, search_contacts, get_valid_fields


app = FastAPI()
env = Env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app_config = AppConfig.from_env(env)
time.sleep(30)
db_manager = DBManager(app_config.db_config)


@app.on_event("startup")
async def startup_init():
    """Perform initialization tasks on application startup."""
    max_retries = 10
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            with db_manager.connect() as _:
                break
        except OperationalError as exc:
            logger.warning(f"Failed to connect to the database (Attempt {attempt + 1}/{max_retries}): {exc}")
            time.sleep(retry_delay)
    else:
        logger.error("Failed to connect to the database after multiple attempts. Exiting...")
        exit(1)
    prepare_db(db_manager, app_config.nimble_api_config)


@app.get('/search')
async def search_handler(
    query: str = Query("", min_length=1),
    fields: str = Query(""),
):
    """Handle the search request."""
    valid_fields = get_valid_fields(fields)
    try:
        contacts = search_contacts(db_manager, query, valid_fields)
        return contacts
    except Exception as exc:
        logger.error(f"Failed to perform full-text search: {exc}")
        raise HTTPException(status_code=500, detail="Failed to perform full-text search.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
