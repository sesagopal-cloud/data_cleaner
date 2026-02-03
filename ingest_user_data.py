import pandas as pd
import sqlite3
import config
import glob
import os

def ingest_data():
    """
    Scans the raw_data directory for files, reads them,
    standardizes columns, and loads them into SQLite.
    """
    config.logger.info("Starting Data Ingestion Process...")
    
    # 1. Find file
    files = glob.glob(str(config.RAW_DATA_DIR / "*.*"))
    validation_files = [f for f in files if f.endswith(('.csv', '.xlsx', '.xls'))]
    
    if not validation_files:
        config.logger.error(f"No CSV or Excel files found in {config.RAW_DATA_DIR}")
        print(f"❌ ERROR: Please place your banking data file in {config.RAW_DATA_DIR}")
        return

    file_path = validation_files[0]
    config.logger.info(f"Found file: {file_path}")
    
    try:
        # 2. Read File
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        config.logger.info(f"Loaded {len(df)} rows from file.")
        
        # 3. Basic Standardization (Optional: Map columns if needed)
        # For now, we assume the user's columns are roughly correct or we clean them later.
        # We replace spaces in column names with underscores for DB safety.
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]
        
        # 4. Save to Database
        conn = sqlite3.connect(config.DB_PATH)
        df.to_sql(config.TABLE_NAME, conn, if_exists='replace', index=False)
        conn.close()
        
        config.logger.info(f"Successfully saved data to {config.TABLE_NAME} table in {config.DB_PATH}")
        print(f"✅ Success! Data loaded into Database. Ready for Chunk Processing.")
        
    except Exception as e:
        config.logger.error(f"Failed to ingest data: {e}")
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    ingest_data()
