#!/usr/bin/env python3
"""
Test SQLite database connection for GenX-FX.
- Verifies genxdb_fx.db exists in the project root
- Connects via sqlite3
- Confirms the expected tables are present
- Prints row counts for key tables

Exit codes:
  0 = success
  1 = database file missing
  2 = connection or query failure
"""

import sys
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_FILE = PROJECT_ROOT / 'genxdb_fx.db'

EXPECTED_TABLES = [
    'users',
    'trading_accounts',
    'trading_pairs',
    'market_data',
    'trading_signals',
    'trades',
    'model_predictions',
    'system_logs',
]

KEY_COUNT_TABLES = [
    'users',
    'trading_pairs',
    'trading_signals',
    'trades',
]


def main() -> int:
    if not DB_FILE.exists():
        logger.error(f"Database file not found: {DB_FILE}")
        logger.info("If you have not initialized it yet, run: python setup_database.py (from the project root)")
        return 1

    logger.info(f"Opening SQLite database: {DB_FILE}")

    try:
        conn = sqlite3.connect(str(DB_FILE))
        cur = conn.cursor()

        # Fetch tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        found_tables = {row[0] for row in cur.fetchall()}

        missing = [t for t in EXPECTED_TABLES if t not in found_tables]
        if missing:
            logger.warning(f"Missing expected tables: {', '.join(missing)}")
        else:
            logger.info("All expected tables are present.")

        # Print row counts for key tables
        for table in KEY_COUNT_TABLES:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                logger.info(f"{table}: {count} rows")
            except Exception as e:
                logger.warning(f"Could not count rows in {table}: {e}")

        # Simple sanity query
        try:
            cur.execute("SELECT datetime('now')")
            now = cur.fetchone()[0]
            logger.info(f"SQLite reachable. Current DB time: {now}")
        except Exception as e:
            logger.error(f"Sanity query failed: {e}")
            return 2

        conn.close()
        logger.info("Database connection test: OK")
        return 0

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
