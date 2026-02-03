import sqlite3
import pandas as pd
import config

class BankingDatabase:
    def __init__(self):
        self.db_path = config.DB_PATH

    def connect(self):
        """Establish connection to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            config.logger.error(f"Database connection failed: {e}")
            raise

    def get_total_count(self):
        """Get total number of rows efficiently."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {config.TABLE_NAME}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def fetch_chunk(self, offset, limit):
        """
        Fetch a specific chunk of data.
        This mimics 'Server-Side Paging' used in big banking systems.
        """
        conn = self.connect()
        query = f"SELECT * FROM {config.TABLE_NAME} LIMIT {limit} OFFSET {offset}"
        try:
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            config.logger.error(f"Error fetching chunk (Offset: {offset}): {e}")
            return pd.DataFrame() # Return empty on error
        finally:
            conn.close()
