# debug_monitor.py
import win32evtlog
import time

def run_debug_monitor():
    log_type = 'System'
    source_to_watch = "PythonTestEventSource"
    
    print("--- Starting Focused Debug Monitor ---")
    print(f"Watching for events from source: {source_to_watch}")

    try:
        log_handle = win32evtlog.OpenEventLog(None, log_type)
    except Exception as e:
        print(f"\nERROR: Could not open event log. Run as Administrator.")
        return

    last_total = win32evtlog.GetNumberOfEventLogRecords(log_handle)

    while True:
        current_total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
        if current_total > last_total:
            events = win32evtlog.ReadEventLog(
                log_handle,
                win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ,
                last_total
            )
            for event in events:
                if event.SourceName == source_to_watch:
                    print("\n\n>>> ✅ SUCCESS: Detected the Python test event! <<<")
                    print("This confirms the entire monitoring pipeline is working.")
            
            last_total = current_total
        time.sleep(1)

if __name__ == "__main__":
    run_debug_monitor()