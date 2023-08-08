import logging
from environs import Env

try:
    from utils import prepare_db
    from app_config import AppConfig
    from db_manager import DBManager
except ModuleNotFoundError:
    from src.utils import prepare_db
    from src.app_config import AppConfig
    from src.db_manager import DBManager


def cron_job_main(logger):
    logger.info("Starting a scheduled update of the 'contacts' database table")
    env = Env()
    app_config = AppConfig.from_env(env)
    db_manager = DBManager(app_config.db_config)

    prepare_db(db_manager, app_config.nimble_api_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    cron_job_main(logger)
