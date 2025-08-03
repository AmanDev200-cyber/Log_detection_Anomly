# src/windows_event_monitor.py

import win32evtlog
import win32evtlogutil
import win32api
import time

def start_monitoring(callback, log_type='System', server='localhost'):
    """
    Monitors the Windows Event Log for new entries.
    This version is resilient to errors from events that don't have a registered message file.
    """
    print(f"Attempting to monitor the '{log_type}' Windows Event Log...")
    
    try:
        log_handle = win32evtlog.OpenEventLog(server, log_type)
    except Exception as e:
        print(f"Error opening event log: {e}")
        print("Please ensure you are running this script with Administrator privileges.")
        return

    total_records = win32evtlog.GetNumberOfEventLogRecords(log_handle)
    last_record_read = total_records

    print(f"Monitoring started. Current records: {total_records}. Waiting for new events...")

    try:
        while True:
            current_total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
            
            if current_total > last_record_read:
                events = win32evtlog.ReadEventLog(
                    log_handle, 
                    win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ, 
                    last_record_read
                )

                for event in events:
                    full_message = ""
                    try:
                        # **TRY** the robust method first
                        full_message = win32evtlogutil.FormatMessage(event, log_type)
                    except win32api.error:
                        # **FALLBACK** if the message file is missing
                        if event.StringInserts:
                            full_message = ' '.join(str(s).strip() for s in event.StringInserts)
                        else:
                            full_message = "No message string available."
                    
                    # Create a single string for the model
                    formatted_log = f"Source: {event.SourceName} | ID: {event.EventID} | Message: {full_message.strip()}"
                    callback(formatted_log)
                
                last_record_read = current_total

            time.sleep(2) 
            
    except KeyboardInterrupt:
        print("Stopping monitor.")
    finally:
        win32evtlog.CloseEventLog(log_handle)