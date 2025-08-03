import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogFileHandler(FileSystemEventHandler):
    """Handles new data written to a monitored log file."""
    def __init__(self, filepath, callback):
        self.filepath = filepath
        self.callback = callback
        self.last_pos = 0 # Start reading from the beginning

    def on_modified(self, event):
        if event.src_path == self.filepath:
            with open(self.filepath, 'r') as f:
                f.seek(self.last_pos) # Go to where we left off
                new_lines = f.readlines()
                if new_lines:
                    for line in new_lines:
                        self.callback(line.strip())
                    self.last_pos = f.tell() # Update our position

def start_monitoring(filepath, callback):
    """Starts monitoring a file for changes."""
    event_handler = LogFileHandler(filepath, callback)
    observer = Observer()
    # Schedule monitoring the directory containing the file
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    print(f"Monitoring '{filepath}' for new logs...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # Example usage: print new lines to the console
    def print_new_log(log_line):
        print(f"NEW LOG DETECTED: {log_line}")

    # Create a dummy log file to monitor
    log_file_path = "data/raw_logs/app.log"
    with open(log_file_path, "w") as f:
        f.write("Initial log entry.\n")
    
    start_monitoring(log_file_path, print_new_log)