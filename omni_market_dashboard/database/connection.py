import os
import sqlite3
import logging
from contextlib import contextmanager
from omni_market_dashboard.config import settings

logger = logging.getLogger("DatabaseConnection")

# SQLAlchemy imports (can be uncommented when dependency is installed)
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

def get_pg_connection_string():
    """
    Returns the PostgreSQL connection string.
    """
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

@contextmanager
def get_db_session(use_timeseries=False):
    """
    Context manager for database sessions.
    Falls back to SQLite for local development if PostgreSQL configuration fails
    or if it's not installed.
    """
    # Prototyping/Local fallback mechanism using SQLite
    db_path = settings.SQLITE_DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = None
    try:
        logger.debug(f"Connecting to local SQLite database at {db_path}...")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise e
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")
            
# Prototype PostgreSQL/TimescaleDB connection pool hook:
# engine = create_engine(get_pg_connection_string(), pool_size=10, max_overflow=20)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
