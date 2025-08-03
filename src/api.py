# Example api.py snippet
from fastapi import FastAPI
from joblib import load

app = FastAPI()
model = load('models/crash_detector.joblib')

@app.post("/predict")
def predict_log(log_entry: dict):
    log_message = log_entry['message']
    prediction = model.predict([log_message])[0]
    return {"log_message": log_message, "is_crash": int(prediction)}