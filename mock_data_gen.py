import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Settings
NUM_ROWS = 5000
OUTPUT_FILE = "c:/data_cleaner/raw_data/mock_bank_data.csv"

def generate_mock_data():
    print("Generating mock data...")
    
    # Generators
    ids = np.arange(1000, 1000 + NUM_ROWS)
    dates = [datetime.now() - timedelta(days=x) for x in range(NUM_ROWS)]
    amounts = np.round(np.random.uniform(-100, 10000, NUM_ROWS), 2) # Include some negatives for testing
    branches = ['New York', 'London', 'Mumbai', 'Singapore', 'Tokyo']
    types = ['Credit', 'Debit', 'Transfer']
    
    data = {
        'Transaction_ID': ids,
        'Transaction_Date': dates,
        'Amount': amounts,
        'Branch': [random.choice(branches) for _ in range(NUM_ROWS)],
        'Transaction_Type': [random.choice(types) for _ in range(NUM_ROWS)],
        'Customer_Name': [f"Customer_{i}" for i in range(NUM_ROWS)]
    }
    
    df = pd.DataFrame(data)
    
    # Inject some duplicates
    df = pd.concat([df, df.iloc[:100]], ignore_index=True)
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Mock data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_mock_data()
