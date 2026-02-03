import shutil
import os
import config
from datetime import datetime
import glob
from pathlib import Path

class TemporalPackager:
    def __init__(self):
        self.source_dir = config.OUTPUT_DIR / "daily_reports"
        self.weekly_archive_dir = config.OUTPUT_DIR / "weekly_archives"
        self.monthly_archive_dir = config.OUTPUT_DIR / "monthly_archives"
        self.weekly_archive_dir.mkdir(exist_ok=True)
        self.monthly_archive_dir.mkdir(exist_ok=True)

    def package_by_week(self):
        """
        Creates ZIP archives for each weekly folder.
        Structure: daily_reports/2024-W01/ -> weekly_archives/Weekly_Report_2024-W01.zip
        """
        config.logger.info("Starting Weekly Packaging...")
        
        # Find all weekly folders
        week_folders = [d for d in self.source_dir.iterdir() if d.is_dir()]
        
        if not week_folders:
            print("⚠️  No weekly folders to package.")
            return []

        count = 0
        packaged_weeks = []
        
        for week_dir in week_folders:
            week_name = week_dir.name  # e.g., "2024-W01"
            zip_name = self.weekly_archive_dir / f"Weekly_Report_{week_name}"
            
            # Create ZIP of the week folder
            shutil.make_archive(str(zip_name), 'zip', week_dir)
            packaged_weeks.append(week_name)
            count += 1
            
        config.logger.info(f"Packaged {count} weekly archives.")
        print(f"📦 Created {count} Weekly ZIP Packages.")
        return packaged_weeks

    def package_by_month(self):
        """
        Groups weekly ZIPs by month and creates monthly archives.
        Structure: weekly_archives/Weekly_Report_2024-W01.zip -> monthly_archives/Monthly_Report_2024-01.zip
        
        Hierarchy: Day files → Weekly folders → Weekly ZIPs → Monthly ZIPs
        """
        # First, package weeks
        self.package_by_week()
        
        config.logger.info("Starting Monthly Packaging...")
        
        # Find all weekly ZIPs
        weekly_zips = list(self.weekly_archive_dir.glob("Weekly_Report_*.zip"))
        
        if not weekly_zips:
            print("⚠️  No weekly archives to package into months.")
            return

        # Group by month
        zips_by_month = {}
        for zip_path in weekly_zips:
            # Extract week string: "Weekly_Report_2024-W01.zip" -> "2024-W01"
            week_str = zip_path.stem.replace("Weekly_Report_", "")
            
            try:
                # Parse year and week number
                year = int(week_str[:4])
                week_num = int(week_str.split("W")[1])
                
                # Convert week to approximate month
                # Week 1-4 ≈ January, Week 5-8 ≈ February, etc.
                month = min(12, max(1, (week_num - 1) // 4 + 1))
                month_key = f"{year}-{month:02d}"
                
                if month_key not in zips_by_month:
                    zips_by_month[month_key] = []
                zips_by_month[month_key].append(zip_path)
            except (ValueError, IndexError):
                continue

        # Create monthly archives
        count = 0
        for month, zip_list in zips_by_month.items():
            # Create temp folder for this month
            temp_month_dir = self.monthly_archive_dir / f"temp_{month}"
            temp_month_dir.mkdir(exist_ok=True)
            
            # Copy weekly ZIPs there
            for z in zip_list:
                shutil.copy(z, temp_month_dir)
            
            # Create monthly ZIP
            zip_name = self.monthly_archive_dir / f"Monthly_Report_{month}"
            shutil.make_archive(str(zip_name), 'zip', temp_month_dir)
            
            # Cleanup temp folder
            shutil.rmtree(temp_month_dir)
            count += 1
            
        config.logger.info(f"Packaged {count} monthly archives.")
        print(f"📦 Created {count} Monthly ZIP Packages (containing weekly ZIPs).")


# Backwards compatibility
def package_all():
    """Run full packaging pipeline: days → weeks → months"""
    packager = TemporalPackager()
    packager.package_by_month()
