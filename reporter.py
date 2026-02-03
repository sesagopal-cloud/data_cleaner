import json
import pandas as pd
import config
import os

class Reporter:
    def __init__(self):
        self.summary_file = config.OUTPUT_DIR / "cleaning_summary.json"
        self.discarded_file = config.OUTPUT_DIR / "discarded_records.csv"
        
        # Initialize stats
        self.stats = {
            "total_processed": 0,
            "total_valid": 0,
            "total_invalid": 0,
            "errors_log": []
        }
        
        # Reset files - Disabled for continuous processing to avoid PermissionErrors and data loss
        # if self.discarded_file.exists():
        #     os.remove(self.discarded_file)

    def update_stats(self, report):
        self.stats["total_processed"] += report['total_rows']
        self.stats["total_valid"] += report['valid_rows']
        self.stats["total_invalid"] += report['invalid_rows']
        self.stats["errors_log"].extend(report['errors'])

    def log_discards(self, invalid_df):
        if not invalid_df.empty:
            # Append header only if file doesn't exist
            header = not self.discarded_file.exists()
            invalid_df.to_csv(self.discarded_file, mode='a', header=header, index=False)

    def save_summary(self):
        with open(self.summary_file, 'w') as f:
            json.dump(self.stats, f, indent=4)
        config.logger.info("Cleaning Summary Saved.")
