"""
PostgreSQL Data Fetcher
=======================
Connects to PostgreSQL, fetches table data, and exports to Excel.

Usage:
    python pg_fetcher.py                    # Uses table from .env
    python pg_fetcher.py --table my_table   # Specify table name
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration from Environment ---
PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "database": os.getenv("PG_DATABASE", ""),
    "user": os.getenv("PG_USER", ""),
    "password": os.getenv("PG_PASSWORD", "")
}

# Output directory (relative to script location)
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "raw_data" / "incoming"


def connect_postgres():
    """Establish connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=PG_CONFIG["host"],
            port=PG_CONFIG["port"],
            database=PG_CONFIG["database"],
            user=PG_CONFIG["user"],
            password=PG_CONFIG["password"]
        )
        print(f"✅ Connected to PostgreSQL: {PG_CONFIG['database']}@{PG_CONFIG['host']}")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def fetch_table(conn, table_name):
    """Fetch all data from specified table."""
    query = f"SELECT * FROM {table_name}"
    print(f"📥 Fetching data from table: {table_name}...")
    
    try:
        df = pd.read_sql_query(query, conn)
        print(f"   Retrieved {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"❌ Error fetching table: {e}")
        return pd.DataFrame()


def export_to_excel(df, table_name):
    """Export DataFrame to Excel in the incoming folder."""
    # Ensure directory exists
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = RAW_DATA_DIR / f"{table_name}_{timestamp}.xlsx"
    
    # Save to Excel
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"💾 Saved Excel file: {filename}")
    return filename


def list_tables(conn):
    """List all available tables in the database."""
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """
    cursor = conn.cursor()
    cursor.execute(query)
    tables = cursor.fetchall()
    
    print("\n📋 Available Tables:")
    for i, (table,) in enumerate(tables, 1):
        print(f"   {i}. {table}")
    return [t[0] for t in tables]


def main():
    parser = argparse.ArgumentParser(description="Fetch PostgreSQL table to Excel")
    parser.add_argument("--table", "-t", help="Table name to fetch")
    parser.add_argument("--list", "-l", action="store_true", help="List available tables")
    args = parser.parse_args()
    
    # Get table name
    table_name = args.table or os.getenv("PG_TABLE", "")
    
    # Connect
    conn = connect_postgres()
    
    # List tables if requested
    if args.list:
        list_tables(conn)
        conn.close()
        return
    
    # Validate table name
    if not table_name:
        print("❌ No table specified. Use --table <name> or set PG_TABLE in .env")
        list_tables(conn)
        conn.close()
        sys.exit(1)
    
    # Fetch and export
    df = fetch_table(conn, table_name)
    
    if not df.empty:
        output_file = export_to_excel(df, table_name)
        print(f"\n✅ SUCCESS! Data ready for processing.")
        print(f"   Run: python main.py")
        print(f"   Or:  .\\dist\\data_cleaner.exe")
    
    conn.close()


if __name__ == "__main__":
    main()
