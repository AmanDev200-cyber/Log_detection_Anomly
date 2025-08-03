# add_new_data.py
import csv

# --- Using a real, misclassified log from your system ---
# This is a much better training example!
new_log_message = "Source: PythonTestEventSource | ID: 777 | Message: A fatal crash has occurred. Application failed unexpectedly.  "

# --- SCRIPT TO APPEND THE DATA ---
new_row = {
    'Level': 'Warning',  # The original level was likely a Warning or Error
    'Date and Time': '',
    'Source': 'Microsoft-Windows-DNS-Client',
    'Event ID': '1014',
    'Message': new_log_message,
    'is_crash': 1  # The CORRECT label
}

try:
    with open('data/raw_logs/labeled_application_logs.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_row.keys())
        # If the file is empty, write the header first
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(new_row)
    
    print("✅ Successfully added the new DNS error log to your dataset.")
    print("You are now ready to retrain your model.")

except Exception as e:
    print(f"An error occurred: {e}")