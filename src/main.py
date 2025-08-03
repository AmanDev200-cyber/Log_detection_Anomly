import time
import os
import csv
import re
from joblib import load
import win32evtlog
from collections import deque

# --- Configuration ---
MODEL_PATH = 'models/anomaly_detector.joblib'
LIVE_ANOMALY_LOG_FILE = 'live_anomalies.csv'
LOG_TO_WATCH = 'Application'
CRITICAL_KEYWORDS = r'fatal|crash|failed|exception|unhandled|error'

# --- Global State ---
model = None

def clean_message(message):
    if not isinstance(message, str):
        return ""
    cleaned = message.lower()
    cleaned = re.sub(r'[^a-z\s]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def process_event(event, seen_records):
    if event.RecordNumber in seen_records:
        return False

    seen_records.add(event.RecordNumber)

    try:
        full_message = ""
        if event.StringInserts:
            full_message = ' '.join(str(s).strip() for s in event.StringInserts)

        cleaned_full_message = clean_message(full_message)

        model_prediction = model.predict([cleaned_full_message])[0]
        keyword_found = re.search(CRITICAL_KEYWORDS, full_message, re.IGNORECASE)

        if model_prediction == -1 or keyword_found:
            reason = "Model detected anomaly" if model_prediction == -1 else f"Keyword match: '{keyword_found.group(0)}'"

            log_line = f"Source: {event.SourceName} | ID: {event.EventID} | Message: {full_message}"
            print(f"\n🚨 ANOMALY DETECTED!")
            print(f"🔍 Reason: {reason}")
            print(f"🧾 Event: {log_line}\n")
            save_anomaly_to_file(event, full_message, reason)
            return True

    except Exception as e:
        print(f"⚠️ Failed to process event from '{event.SourceName}'. Error: {e}")

    return False

def save_anomaly_to_file(event, message, reason):
    with open(LIVE_ANOMALY_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            event.TimeGenerated.Format(),
            event.SourceName,
            event.EventID,
            message,
            reason
        ])

def start_live_monitoring():
    global model
    print("📡 Initializing live monitoring...")

    try:
        model = load(MODEL_PATH)
        print("✅ Model loaded.")
    except FileNotFoundError:
        print(f"❌ Model file not found at {MODEL_PATH}.")
        return

    if not os.path.exists(LIVE_ANOMALY_LOG_FILE):
        with open(LIVE_ANOMALY_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Source', 'EventID', 'Message', 'DetectionReason'])

    log_handle = None
    try:
        log_handle = win32evtlog.OpenEventLog(None, LOG_TO_WATCH)

        seen_records = set()
        print(f"📖 Watching Windows '{LOG_TO_WATCH}' event log for anomalies...")

        processed_event_count = 0
        MAX_EVENTS = 10
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        while True:
            events = win32evtlog.ReadEventLog(log_handle, flags, 0, 20)
            if not events:
                time.sleep(2)
                continue

            for event in events:
                new_anomaly = process_event(event, seen_records)
                if new_anomaly:
                    processed_event_count += 1
                    if processed_event_count >= MAX_EVENTS:
                        print(f"\n⏸️ Processed {MAX_EVENTS} anomalies. Pausing for new events...\n")
                        processed_event_count = 0
                        time.sleep(5)

            time.sleep(1)

    except Exception as e:
        print(f"❌ ERROR during monitoring: {e}")
    finally:
        if log_handle:
            win32evtlog.CloseEventLog(log_handle)
            print("ℹ️ Event log handle closed.")

if __name__ == '__main__':
    try:
        start_live_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user.")
