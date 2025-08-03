# src/model.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from joblib import dump
import os

def train_anomaly_model_on_processed_data():
    """
    Trains an Isolation Forest model using the preprocessed log data.
    """
    processed_data_path = 'data/processed/preprocessed_logs.csv'
    model_path = 'models/anomaly_detector.joblib'

    # 1. Load the PREPROCESSED Data
    print(f"📂 Loading preprocessed data from '{processed_data_path}'...")
    try:
        df = pd.read_csv(processed_data_path)
    except FileNotFoundError:
        print(f"❌ ERROR: Preprocessed data file not found at '{processed_data_path}'.")
        print("ℹ️ Please run the preprocess_data.py script first.")
        return

    # Fill missing values
    df['CleanedMessage'] = df['CleanedMessage'].fillna('')
    df['Level'] = df['Level'].fillna('')

    # 2. Filter for "Normal" Data (Information-level)
    normal_df = df[df['Level'] == 'Information']
    if normal_df.empty:
        print("❌ ERROR: No logs with 'Information' level found.")
        return

    print(f"✅ Found {len(normal_df)} normal logs (Level: Information).")

    X_train = normal_df['CleanedMessage']

    # 3. Create and Train Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('clf', IsolationForest(contamination='auto', random_state=42))
    ])

    print("🧠 Training anomaly detection model...")
    pipeline.fit(X_train)
    print("✅ Training complete.")

    # 4. Save model
    os.makedirs('models', exist_ok=True)
    dump(pipeline, model_path)
    print(f"💾 Model saved to: {model_path}")

if __name__ == '__main__':
    train_anomaly_model_on_processed_data()
