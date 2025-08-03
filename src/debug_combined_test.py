# debug_combined_test.py
import win32evtlog
import win32evtlogutil
import win32api
import time
import os

def run_combined_test():
    """
    Writes a test event and then immediately listens for it in the same script.
    This is the definitive test to confirm the monitoring code is working.
    """
    log_type = 'System'
    source_name = "CombinedTestSource" # A fresh source name
    event_id = 888

    # --- PART 1: WRITE THE EVENT ---
    print("--- Step 1: Writing a test event... ---")
    try:
        # Register the event source
        win32evtlogutil.AddSourceToRegistry(source_name, "pywintypes.dll", eventLogType=log_type)
    except win32api.error:
        pass # Source likely already exists, which is fine.

    handle = win32evtlog.OpenEventLog(None, source_name)
    message = ["Test event from combined script.", "Checking for fatal crash."]
    
    try:
        win32evtlog.ReportEvent(handle, win32evtlog.EVENTLOG_ERROR_TYPE, 0, event_id, None, message, None)
        print("✅ Event successfully written to the System Log.")
    except Exception as e:
        print(f"❌ FAILED TO WRITE EVENT. Error: {e}")
        return # Stop if we can't even write the event
    finally:
        win32evtlog.CloseEventLog(handle)

    # --- PART 2: LISTEN FOR THE EVENT ---
    print("\n--- Step 2: Starting listener... Waiting for the event to appear. ---")
    
    try:
        log_handle = win32evtlog.OpenEventLog(None, log_type)
    except Exception as e:
        print(f"ERROR: Could not open event log to listen. {e}")
        return
        
    # Start reading from one position before the end, to be safe
    total_records = win32evtlog.GetNumberOfEventLogRecords(log_handle)
    last_record_read = max(0, total_records - 5) 
    
    found = False
    timeout = 10 # Wait for a maximum of 10 seconds
    start_time = time.time()

    while not found and time.time() - start_time < timeout:
        events = win32evtlog.ReadEventLog(
            log_handle,
            win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ,
            last_record_read
        )
        if not events:
            time.sleep(1)
            continue

        for event in events:
            if event.SourceName == source_name and event.EventID == event_id:
                print("\n\n**************************************************")
                print(">>> ✅ SUCCESS! The listener detected its own event! <<<")
                print("**************************************************")
                print("\nThis confirms the monitoring code works correctly.")
                found = True
                break
        
        last_record_read += len(events)
        if found:
            break
    
    if not found:
        print("\n\n**************************************************")
        print(">>> ❌ FAILURE: The listener did not detect its own event. <<<")
        print("**************************************************")
        print("\nThis points to a fundamental issue with the pywin32 library's ability")
        print("to read all events in real-time on your specific system configuration.")

    win32evtlog.CloseEventLog(log_handle)


if __name__ == "__main__":
    run_combined_test()
    