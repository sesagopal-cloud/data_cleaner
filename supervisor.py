import time
import subprocess
import config
import sys
import os
from datetime import datetime

import pandas as pd
from datetime import datetime

# --- Settings ---
FEEDER_INTERVAL = 60  # 1 minute
PROCESSOR_INTERVAL = 60 # 1 minute
AUDIT_FILE = config.OUTPUT_DIR / "supervisor_audit.xlsx"

def log_audit(event_type, script_name, details):
    """Logs supervisor events to an Excel file."""
    new_entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Event": event_type,
        "Script": script_name,
        "Details": details
    }
    
    try:
        if AUDIT_FILE.exists():
            df = pd.read_excel(AUDIT_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])
            
        df.to_excel(AUDIT_FILE, index=False)
    except Exception as e:
        print(f"⚠️  Failed to write to audit log: {e}")

def run_script(script_name):
    """Runs a script and waits for it to finish."""
    script_path = config.BASE_DIR / script_name
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Supervisor: Starting {script_name}...")
    config.logger.info(f"Supervisor: Starting {script_name}")
    log_audit("START", script_name, "Attempting run")
    
    try:
        # Use sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {script_name} finished successfully.")
            config.logger.info(f"Supervisor: {script_name} success.")
            log_audit("SUCCESS", script_name, "Completed with exit code 0")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {script_name} failed!")
            print(f"Error Output:\n{result.stderr}")
            config.logger.error(f"Supervisor: {script_name} failed. Error: {result.stderr}")
            log_audit("FAILURE", script_name, f"Error: {result.stderr[:200]}...") # Truncate error for excel

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💥 Supervisor: Critical Error running {script_name}: {e}")
        config.logger.critical(f"Supervisor: Critical Error running {script_name}: {e}")
        log_audit("CRITICAL_ERROR", script_name, str(e))

def supervisor_loop():
    print("👮 Supervisor System Started.")
    print(f"   Feeder Interval: {FEEDER_INTERVAL}s")
    print(f"   Processor Interval: {PROCESSOR_INTERVAL}s")
    print("   Press Ctrl+C to stop.")
    
    last_feeder_run = 0
    last_processor_run = 0
    
    while True:
        try:
            now = time.time()
            
            # Check Feeder
            if now - last_feeder_run >= FEEDER_INTERVAL:
                run_script("data_feeder.py")
                last_feeder_run = time.time()
            
            # Check Processor
            # We check time again to avoid drifting if feeder takes long
            now = time.time() 
            if now - last_processor_run >= PROCESSOR_INTERVAL:
                run_script("data_processor.py")
                last_processor_run = time.time()
                
            # Sleep briefly to avoid CPU spin
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Supervisor stopped by user.")
            break
        except Exception as e:
            print(f"⚠️  Supervisor Loop Error: {e}")
            config.logger.error(f"Supervisor Loop Error: {e}")
            time.sleep(5) # Wait a bit before retrying loop

if __name__ == "__main__":
    supervisor_loop()
