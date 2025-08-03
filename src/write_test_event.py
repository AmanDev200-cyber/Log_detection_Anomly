# write_test_event.py (Corrected)
import win32evtlog
import win32evtlogutil
import win32api

def create_test_event():
    """Writes a test event directly to the Windows Application Log."""
    print("Attempting to write a test event...")
    
    log_type = 'Application'
    source_name = "MyCrashTestApp" 
    event_id = 1001
    message = [
        "This is a test CRASH log from the writer script.",
        "Faulting module name: KERNELBASE.dll",
        "The application has failed and encountered an unhandled exception."
    ]
    
    try:
        # Register the source name if it doesn't exist
        win32evtlogutil.AddSourceToRegistry(source_name, "pywintypes.dll", eventLogType=log_type)
    except win32api.error:
        pass # Source already exists, which is fine.

    handle = win32evtlog.OpenEventLog(None, source_name)

    try:
        win32evtlog.ReportEvent(
            handle,
            win32evtlog.EVENTLOG_ERROR_TYPE,
            0,
            event_id,
            None,
            message,
            None
        )
        print("✅ Event successfully written to the 'Application' Log.")
        print("The live monitor should detect this shortly.")

    except Exception as e:
        print(f"❌ ERROR: Failed to write event: {e}")
    finally:
        win32evtlog.CloseEventLog(handle)

if __name__ == "__main__":
    create_test_event()
