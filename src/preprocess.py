import pandas as pd
import re

def preprocess_log_data(input_filepath, output_filepath):
    """
    Loads raw log data, cleans it properly, and saves it to a new file.
    
    Args:
        input_filepath (str): Path to the raw CSV log file.
        output_filepath (str): Path to save the cleaned CSV file.
    """
    print(f"📂 Loading log data from '{input_filepath}'...")

    try:
        col_names = ['Level', 'DateTime', 'Source', 'EventID', 'TaskCategory', 'Message']
        df = pd.read_csv(
            input_filepath,
            encoding='latin1',
            on_bad_lines='skip',
            header=None,
            skiprows=1,
            names=col_names
        )
    except FileNotFoundError:
        print(f"❌ ERROR: File not found at '{input_filepath}'")
        return
    except Exception as e:
        print(f"❌ ERROR loading CSV: {e}")
        return

    # Drop rows without messages or levels
    df = df.dropna(subset=['Message', 'Level'])

    # Clean the message text
    print("🧹 Cleaning log messages...")
    df['CleanedMessage'] = df['Message'].astype(str).str.lower()
    df['CleanedMessage'] = df['CleanedMessage'].apply(lambda x: re.sub(r'[^a-z\s]', '', x))
    df['CleanedMessage'] = df['CleanedMessage'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())

    # Optional: You can drop very short messages (less than 3 words)
    df = df[df['CleanedMessage'].str.split().str.len() >= 3]

    # Save only useful columns for training
    output_df = df[['Level', 'CleanedMessage']]

    try:
        output_df.to_csv(output_filepath, index=False, encoding='utf-8')
        print(f"\n✅ Preprocessing complete.")
        print(f"📁 Saved cleaned data to '{output_filepath}'")
    except Exception as e:
        print(f"❌ ERROR saving file: {e}")

    # Display preview
    print("\n--- Preview of Preprocessed Data ---")
    print(output_df.head(5))

if __name__ == '__main__':
    raw_log_file = 'data/raw_logs/application_log_export.csv'
    processed_log_file = 'data/processed/preprocessed_logs.csv'
    
    preprocess_log_data(raw_log_file, processed_log_file)