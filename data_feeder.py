import pandas as pd
import numpy as np
import config
from datetime import datetime, timedelta
import random
import os
import json

# --- Configuration ---
STATE_FILE = config.OUTPUT_DIR / "feeder_state.json"
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2024, 12, 31)
ROWS_PER_MONTH = 2000 # Simulated "month" volume (scaled down for mock)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"current_date": START_DATE.strftime("%Y-%m-%d")}

def save_state(current_date):
    with open(STATE_FILE, 'w') as f:
        json.dump({"current_date": current_date.strftime("%Y-%m-%d")}, f)

def generate_chunk():
    """Generates a CSV file representing one month of data."""
    # --- SIMULATE CRASH ---
    crash_file = config.BASE_DIR / "crash.txt"
    if crash_file.exists():
        os.remove(crash_file) # Remove so it doesn't crash forever
        raise RuntimeError("⚠️ SIMULATED CRASH: Data Feeder encountered a critical error!")
    
    state = load_state()
    current_date = datetime.strptime(state["current_date"], "%Y-%m-%d")
    
    if current_date > END_DATE:
        config.logger.info("Data Feeder: Reached end of 14-year period. Resetting to start.")
        current_date = START_DATE

    # Calculate next month for state update
    # Simple logic: increment month.
    # Logic to get next month start
    next_month_val = current_date.month + 1
    next_year_val = current_date.year
    if next_month_val > 12:
        next_month_val = 1
        next_year_val += 1
    
    next_date = datetime(next_year_val, next_month_val, 1)
    
    # Generate Data for the "Current Month"
    # We will spread timestamps across this month
    config.logger.info(f"Data Feeder: Generating data for {current_date.strftime('%Y-%m')}")
    print(f"Feeder: Producing data for {current_date.strftime('%B %Y')}...")

    # Generate random dates within the current month
    days_in_month = (next_date - current_date).days
    
    random_days = np.random.randint(0, days_in_month, ROWS_PER_MONTH)
    random_seconds = np.random.randint(0, 86400, ROWS_PER_MONTH)
    
    dates = []
    for d, s in zip(random_days, random_seconds):
        dates.append(current_date + timedelta(days=int(d), seconds=int(s)))
    
    dates.sort() # Sort by date for realism

    # Other mocked columns
    ids = np.arange(1000, 1000 + ROWS_PER_MONTH) # IDs ideally should strictly increase if global, but for mock per file it's okay maybe? 
    # Better: Use timestamp-based IDs or something unique.
    # Let's use a random offset + row index to ensure some uniqueness if files are merged
    base_id = int(current_date.timestamp())
    ids = [base_id + i for i in range(ROWS_PER_MONTH)]

    amounts = np.round(np.random.uniform(-100, 10000, ROWS_PER_MONTH), 2)
    branches = ['New York', 'London', 'Mumbai', 'Singapore', 'Tokyo']
    types = ['Credit', 'Debit', 'Transfer']
    customers = [f"Customer_{random.randint(1, 1000)}" for _ in range(ROWS_PER_MONTH)]

    df = pd.DataFrame({
        'Transaction_ID': ids,
        'Transaction_Date': dates,
        'Amount': amounts,
        'Branch': [random.choice(branches) for _ in range(ROWS_PER_MONTH)],
        'Transaction_Type': [random.choice(types) for _ in range(ROWS_PER_MONTH)],
        'Customer_Name': customers
    })

    # Save to Incoming Folder
    incoming_dir = config.RAW_DATA_DIR / "incoming"
    incoming_dir.mkdir(parents=True, exist_ok=True)
    
    filename = incoming_dir / f"Bank_Data_{current_date.strftime('%Y-%m')}.xlsx"
    df.to_excel(filename, index=False)
    
    config.logger.info(f"Data Feeder: Saved {filename}")
    
    # Update State
    save_state(next_date)

if __name__ == "__main__":
    generate_chunk()
