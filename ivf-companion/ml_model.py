# ml_model.py
import numpy as np
import joblib

# Example function (you can train your own model later and replace this)
def predict_success(age, bmi, cycles, stress_level):
    if age < 30 and bmi < 25 and stress_level < 5 and cycles < 2:
        return "High"
    elif age < 35 and cycles < 4:
        return "Moderate"
    else:
        return "Low"