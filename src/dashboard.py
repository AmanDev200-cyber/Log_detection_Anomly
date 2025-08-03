# src/main.py (Live Monitoring Version)
import time
import os
import csv
import re
from joblib import load
import win32evtlog

# --- Configuration ---
MODEL_PATH = 'models/anomaly_detector.joblib' 
LIVE_ANOMALY_LOG_FILE = 'live_anomalies.csv'
LOG_TO_WATCH = 'System'
CRITICAL_KEYWORDS = r'fatal|crash|failed|exception|unhandled|error'

# --- Global State ---
model = None

def clean_message(message):
    """
    Applies the same cleaning steps used for training data to live data.
    """
    if not isinstance(message, str):
        return ""
    # Convert to lowercase
    cleaned = message.lower()
    # Remove special characters, punctuation, and numbers
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def process_event(event):
    """
    Processes a single event using the hybrid detection model.
    """
    full_message = ""
    if event.StringInserts:
        full_message = ' '.join(str(s).strip() for s in event.StringInserts)
    
    log_line = f"Source: {event.SourceName} | ID: {event.EventID} | Message: {full_message}"
    
    # Preprocess the message before prediction
    cleaned_full_message = clean_message(full_message)
    
    # Get prediction from the model on the cleaned message
    model_prediction = model.predict([cleaned_full_message])[0]
    # Check for keywords in the original, uncleaned message
    keyword_found = re.search(CRITICAL_KEYWORDS, full_message, re.IGNORECASE)

    if model_prediction == -1 or keyword_found:
        reason = "model detected anomaly" if model_prediction == -1 else f"keyword '{keyword_found.group(0)}' found"
        print("\n🚨 ANOMALY DETECTED! 🚨")
        print(f" -> Reason: {reason}.")
        print(f" -> {log_line}\n")
        save_anomaly_to_file(log_line, reason)

def save_anomaly_to_file(log_data, reason):
    """Appends a detected anomaly and the reason to the log CSV."""
    file_exists = os.path.isfile(LIVE_ANOMALY_LOG_FILE)
    with open(LIVE_ANOMALY_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'AnomalousLogMessage', 'DetectionReason'])
        from datetime import datetime
        writer.writerow([datetime.now().isoformat(), log_data, reason])

def start_live_monitoring():
    """
    Continuously monitors the event log for new entries.
    """
    print(f"Initializing live monitoring of the '{LOG_TO_WATCH}' log...")
    
    try:
        log_handle = win32evtlog.OpenEventLog(None, LOG_TO_WATCH)
        last_total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
        win32evtlog.CloseEventLog(log_handle)
        print(f"System log currently has {last_total} records. Monitoring for new ones.")
    except Exception as e:
        print(f"FATAL ERROR: Could not get initial record count: {e}")
        return

    while True:
        try:
            log_handle = win32evtlog.OpenEventLog(None, LOG_TO_WATCH)
            current_total = win32evtlog.GetNumberOfEventLogRecords(log_handle)

            if current_total > last_total:
                print(f"  -> Found {current_total - last_total} new event(s). Analyzing...")
                flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                new_events = win32evtlog.ReadEventLog(log_handle, flags, last_total)
                
                for event in new_events:
                    process_event(event)
                
                last_total = current_total
            
            win32evtlog.CloseEventLog(log_handle)
            time.sleep(5) # Wait 5 seconds before checking again

        except Exception as e:
            print(f"ERROR during monitoring loop: {e}")
            time.sleep(10) # Wait longer after an error

if __name__ == '__main__':
    try:
        model = load(MODEL_PATH)
        print("Model loaded successfully.")
        start_live_monitoring()
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}. Please run src/model.py first.")
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
