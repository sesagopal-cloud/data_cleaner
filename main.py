"""
Data Cleaner - Main Entry Point
================================
Processes Excel files from raw_data/incoming/ folder.

Usage:
    python main.py
    OR
    data_cleaner.exe (after PyInstaller build)
"""

import pandas as pd
import glob
import os
import shutil
from pathlib import Path

# Use relative paths for portability
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "raw_data"
INCOMING_DIR = RAW_DATA_DIR / "incoming"
PROCESSED_DIR = RAW_DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
INCOMING_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Import cleaning modules
from validators import validate_chunk
from cleaners import clean_data
from reporter import Reporter


def get_incoming_files():
    """Get all Excel files from incoming directory."""
    xlsx_files = list(INCOMING_DIR.glob("*.xlsx"))
    xls_files = list(INCOMING_DIR.glob("*.xls"))
    return xlsx_files + xls_files


def process_file(filepath, reporter):
    """Process a single Excel file."""
    print(f"   📄 Processing: {filepath.name}")
    
    try:
        df = pd.read_excel(filepath)
        
        # Clean column names
        df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
        
        # Validate
        valid_df, invalid_df, report = validate_chunk(df)
        reporter.update_stats(report)
        reporter.log_discards(invalid_df)
        
        # Clean
        if not valid_df.empty:
            clean_df = clean_data(valid_df)
            return clean_df
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"   ❌ Error processing {filepath.name}: {e}")
        return pd.DataFrame()


def move_to_processed(filepath):
    """Move processed file to processed folder."""
    dest = PROCESSED_DIR / filepath.name
    shutil.move(str(filepath), str(dest))
    print(f"   ➡️  Moved to processed/")


def main():
    print("=" * 50)
    print("🏦 DATA CLEANER - Processing Pipeline")
    print("=" * 50)
    
    # Get files to process
    files = get_incoming_files()
    
    if not files:
        print("\n💤 No files found in raw_data/incoming/")
        print("   Place Excel files there or run: python pg_fetcher.py --table <name>")
        return
    
    print(f"\n📂 Found {len(files)} file(s) to process:")
    for f in files:
        print(f"   • {f.name}")
    
    reporter = Reporter()
    all_clean_data = []
    
    print("\n🔄 Processing...")
    
    for filepath in files:
        clean_df = process_file(filepath, reporter)
        
        if not clean_df.empty:
            all_clean_data.append(clean_df)
        
        # Move to processed
        move_to_processed(filepath)
    
    # Compile results
    print("\n✅ Processing Complete!")
    
    if all_clean_data:
        final_df = pd.concat(all_clean_data, ignore_index=True)
        
        # Save Master CSV
        output_path = OUTPUT_DIR / "master_clean_data.csv"
        final_df.to_csv(output_path, index=False)
        print(f"\n💾 Output saved: {output_path}")
        print(f"   Total rows: {len(final_df)}")
        
        # Generate Excel output
        from excel_generator import ExcelGenerator
        excel_gen = ExcelGenerator(final_df)
        excel_gen.generate_daily_files()
        
        # Package if needed
        from temporal_packager import TemporalPackager
        packager = TemporalPackager()
        packager.package_by_month()
    
    # Save report
    reporter.save_summary()
    print("📋 Audit report saved.")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
