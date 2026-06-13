import os
from pathlib import Path

# Base Directory of the Project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Configs (Defaults to SQLite for local development convenience if Postgres is not configured)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "digital_family_office")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# SQLite fallback path
SQLITE_DB_PATH = os.path.join(BASE_DIR, "database", "local_vault.db")

# API Keys & URLs
BCB_SGS_API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados"
CDI_SERIES_CODE = 12  # Daily CDI rate from Banco Central SGS

# Broker shelves scraper details
MIN_CDB_RENTABILITY_TARGET = 110.0  # Min % of CDI to trigger alerts (e.g. 110% CDI)

# Risk & Rebalancing Parameters
# Suggest rebalancing if day trading profits exceed target
DAY_TRADE_PROFIT_TRIGGER_PCT = 15.0  # 15% profit target to trigger auto-treasury sweep
TREASURY_ALLOCATION_TARGET = 40.0   # Target 40% of family portfolio in risk-free CDBs

# Logging Config
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
