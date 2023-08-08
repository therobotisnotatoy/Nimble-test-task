import logging
import psycopg2.pool

try:
    from app_config import DBConfig
except ModuleNotFoundError:
    from src.app_config import DBConfig


logger = logging.getLogger(__name__)


class DBManager:
    """Manage the database connections."""

    def __init__(self, db_config: DBConfig, minconn=1, maxconn=10):
        self.conn_pool = None
        try:
            self.conn_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                host=db_config.DB_HOST,
                port=db_config.DB_PORT,
                dbname=db_config.DB_NAME,
                user=db_config.DB_USER,
                password=db_config.DB_PASSWORD,
            )
            logger.info("Successfully created connection pool using host.")
        except Exception:
            logger.warning("Failed to create connection pool using host.")

        if not self.conn_pool:
            try:
                self.conn_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=minconn,
                    maxconn=maxconn,
                    host=db_config.DB_CONTAINER_NAME,
                    port=db_config.DB_PORT,
                    dbname=db_config.DB_NAME,
                    user=db_config.DB_USER,
                    password=db_config.DB_PASSWORD,
                )
                logger.info("Successfully created connection pool using container name.")
            except Exception:
                logger.warning("Failed to create connection pool using container name.")

        if not self.conn_pool:
            try:
                self.conn_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=minconn,
                    maxconn=maxconn,
                    host=db_config.DB_SERVICE_NAME,
                    port=db_config.DB_PORT,
                    dbname=db_config.DB_NAME,
                    user=db_config.DB_USER,
                    password=db_config.DB_PASSWORD,
                )
                logger.info("Successfully created connection pool using service name.")
            except Exception as exc:
                logger.warning("Failed to create connection pool using service name.")
                logger.error(f"Failed to create connection pool: {exc}")
                raise exc

    def connect(self):
        return _DBContextManager(self.conn_pool)


class _DBContextManager:
    """Context manager for the database connection."""

    def __init__(self, conn_pool: psycopg2.pool.SimpleConnectionPool):
        self.conn_pool = conn_pool

    def __enter__(self):
        self.conn = self.conn_pool.getconn()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn_pool.putconn(self.conn)
