import pandas as pd
import config
import os
from datetime import datetime

class ExcelGenerator:
    def __init__(self, df):
        self.df = df
        self.output_dir = config.OUTPUT_DIR / "daily_reports"
        self.output_dir.mkdir(exist_ok=True)

    def generate_daily_files(self):
        """
        Splits the dataframe by date and saves individual Excel files.
        Files are organized into weekly folders: YYYY-WNN/
        """
        config.logger.info("Starting Daily Excel Generation...")
        
        # Ensure we have a datetime column
        if 'Transaction_Date' not in self.df.columns:
            config.logger.error("Transaction_Date column missing. Cannot generate daily reports.")
            return

        # Ensure datetime type
        self.df['Transaction_Date'] = pd.to_datetime(self.df['Transaction_Date'])

        # Group by Date (YYYY-MM-DD)
        daily_groups = self.df.groupby(self.df['Transaction_Date'].dt.date)

        count = 0
        for date_val, group in daily_groups:
            # Get week number (ISO format: YYYY-WNN)
            week_str = date_val.strftime("%Y-W%W")
            
            # Create weekly folder
            week_dir = self.output_dir / week_str
            week_dir.mkdir(exist_ok=True)
            
            # Create daily file inside weekly folder
            date_str = date_val.strftime("%Y-%m-%d")
            filename = f"Bank_Report_{date_str}.xlsx"
            filepath = week_dir / filename
            
            # Write to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                group.to_excel(writer, index=False, sheet_name="Transactions")
                
            count += 1
            
        config.logger.info(f"Generated {count} daily Excel files in weekly folders")
        print(f"📊 Generated {count} daily Excel files (organized by week).")
