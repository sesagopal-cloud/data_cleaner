import os
import logging
from pathlib import Path

# --- Project Paths ---
BASE_DIR = Path("c:/data_cleaner")
RAW_DATA_DIR = BASE_DIR / "raw_data"
OUTPUT_DIR = BASE_DIR / "output"
DB_PATH = BASE_DIR / "banking.db"

# --- Database Settings ---
TABLE_NAME = "banking_transactions"
CHUNK_SIZE = 1000  # Number of rows to fetch per "chunk" (Interview Key Point)

# Ensure directories exist BEFORE logging setup
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Logging Configuration ---
LOG_FILE = OUTPUT_DIR / "system.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'), # Changed to 'a' (append) to avoid sharing conflicts or overwriting locks
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("System")
