# 🏦 Data Cleaner - Server Deployment Guide

## Step-by-Step Setup on Company System

---

## STEP 1: Copy Files to Server/VM

Copy these files to your server (e.g., `C:\data_cleaner\`):

```
data_cleaner/
├── pg_fetcher.py          # Fetches data from PostgreSQL
├── main.py                # Main processing pipeline
├── config.py              # Configuration
├── validators.py          # Data validation
├── cleaners.py            # Data cleaning
├── reporter.py            # Report generation
├── excel_generator.py     # Excel output
├── temporal_packager.py   # Archive packaging
├── requirements.txt       # Dependencies
├── .env.template          # Credentials template
├── raw_data/
│   └── incoming/          # Place Excel files here
│   └── processed/         # Files move here after processing
└── output/                # Cleaned output files appear here
```

---

## STEP 2: Install Python & Dependencies

```powershell
# Check Python is installed
python --version

# Install dependencies
cd C:\data_cleaner
pip install -r requirements.txt
```

---

## STEP 3: Configure PostgreSQL Connection

1. **Copy template:**
   ```powershell
   copy .env.template .env
   ```

2. **Edit `.env` with your credentials:**
   ```
   PG_HOST=192.168.1.100        # Your PostgreSQL server IP
   PG_PORT=5432                  # Default PostgreSQL port
   PG_DATABASE=company_db        # Your database name
   PG_USER=your_username         # Your username
   PG_PASSWORD=your_password     # Your password
   PG_TABLE=transactions         # Default table (optional)
   ```

---

## STEP 4: Fetch Data from PostgreSQL

```powershell
# List available tables
python pg_fetcher.py --list

# Fetch a specific table to Excel
python pg_fetcher.py --table your_table_name
```

**Result:** Excel file saved in `raw_data/incoming/`

---

## STEP 5: Run Data Cleaner

**Option A - Python Script:**
```powershell
python main.py
```

**Option B - Executable:**
```powershell
.\dist\data_cleaner.exe
```

**Result:** Cleaned data saved in `output/`

---

## STEP 6: Build Executable (Optional)

If you need to rebuild the `.exe`:

```powershell
pip install pyinstaller
python -m PyInstaller --onefile --name data_cleaner main.py
```

Executable created at: `dist\data_cleaner.exe`

---

## Complete Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     WORKFLOW DIAGRAM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [PostgreSQL]  ──pg_fetcher.py──►  [Excel in incoming/]    │
│                                            │                │
│                                            ▼                │
│                                   [data_cleaner.exe]        │
│                                            │                │
│                                            ▼                │
│                                    [Cleaned Output]         │
│                                      output/                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Daily Usage:**
```powershell
# Step 1: Fetch fresh data
python pg_fetcher.py --table daily_transactions

# Step 2: Process it
.\dist\data_cleaner.exe
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check firewall, ensure PostgreSQL allows remote connections |
| Authentication failed | Verify username/password in `.env` |
| No files found | Ensure Excel files are in `raw_data/incoming/` |
| Missing module error | Run `pip install -r requirements.txt` |

---

## Files Output

After processing, check these locations:

| File | Location |
|------|----------|
| Cleaned CSV | `output/master_clean_data.csv` |
| Daily Excel | `output/daily/` |
| Monthly Archives | `output/archives/` |
| Audit Report | `output/audit_summary.csv` |
