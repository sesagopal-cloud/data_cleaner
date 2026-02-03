import pandas as pd
import sqlite3
import config
import glob
import os
import json
import shutil
from db_connector import BankingDatabase
from validators import validate_chunk
from cleaners import clean_data
from reporter import Reporter
from excel_generator import ExcelGenerator
from temporal_packager import TemporalPackager

# --- Configuration ---
PROCESSOR_STATE_FILE = config.OUTPUT_DIR / "processor_state.json"

def load_state():
    if PROCESSOR_STATE_FILE.exists():
        with open(PROCESSOR_STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_processed_offset": 0}

def save_state(offset):
    with open(PROCESSOR_STATE_FILE, 'w') as f:
        json.dump({"last_processed_offset": offset}, f)

def ingest_new_files():
    """Ingests files from incoming/ to DB and moves them to processed/."""
    incoming_dir = config.RAW_DATA_DIR / "incoming"
    processed_dir = config.RAW_DATA_DIR / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    files = glob.glob(str(incoming_dir / "*.xlsx"))
    if not files:
        return 0 # No new files

    count = 0
    conn = sqlite3.connect(config.DB_PATH)
    
    for f in files:
        try:
            config.logger.info(f"Processor: Ingesting {f}...")
            df = pd.read_excel(f)
            # Basic clean of columns
            df.columns = [c.strip().replace(" ", "_") for c in df.columns]
            
            # Append to DB
            df.to_sql(config.TABLE_NAME, conn, if_exists='append', index=False)
            
            # Move to processed
            shutil.move(f, processed_dir / os.path.basename(f))
            count += 1
        except Exception as e:
            config.logger.error(f"Failed to ingest {f}: {e}")
            
    conn.close()
    return count

def process_new_data():
    """Processes only new rows from the DB."""
    # 1. Ingest any waiting files
    ingested_count = ingest_new_files()
    if ingested_count > 0:
        config.logger.info(f"Processor: Ingested {ingested_count} new files.")

    # 2. Setup processing
    state = load_state()
    start_offset = state["last_processed_offset"]
    
    db = BankingDatabase()
    reporter = Reporter()
    
    total_rows = db.get_total_count()
    
    if start_offset >= total_rows:
        print("💤 No new rows to process.")
        return

    print(f"Processing new rows: {start_offset} to {total_rows}...")
    
    processed_count = start_offset
    new_clean_data = []

    # 3. Process Chunk Loop
    while processed_count < total_rows:
        df_chunk = db.fetch_chunk(offset=processed_count, limit=config.CHUNK_SIZE)
        if df_chunk.empty:
            break
            
        # Validate
        valid_df, invalid_df, report = validate_chunk(df_chunk)
        reporter.update_stats(report)
        reporter.log_discards(invalid_df)
        
        # Clean
        if not valid_df.empty:
            clean_df = clean_data(valid_df)
            new_clean_data.append(clean_df)
        
        processed_count += len(df_chunk)

    # 4. Save Results (Append)
    if new_clean_data:
        final_df = pd.concat(new_clean_data, ignore_index=True)
        
        # Append to Master CSV
        final_output_path = config.OUTPUT_DIR / "master_clean_data.csv"
        header = not final_output_path.exists()
        final_df.to_csv(final_output_path, mode='a', header=header, index=False)
        print(f"💾 Appended {len(final_df)} rows to Master Clean Data.")

        # Generate Reports (Only for this batch)
        # Note: Excel Generator creates daily files. We can just pass the new data.
        # Ideally, we should merge with existing daily data if partial, 
        # but for now we assume chunks align or overwriting daily files for the same day is acceptable
        # OR we just generate reports for the new data.
        excel_gen = ExcelGenerator(final_df)
        excel_gen.generate_daily_files()

        # Archive (Triggered periodically or here?)
        # Let's run it here to be safe
        packager = TemporalPackager()
        packager.package_by_month()
    
    reporter.save_summary() # Resets/Updates summary stats
    
    # 5. Update State
    save_state(processed_count)
    print(f"✅ Batch Complete. Next offset: {processed_count}")

if __name__ == "__main__":
    process_new_data()
