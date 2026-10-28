from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model/final_model.joblib")

class UserInput(BaseModel):
    age: float
    sex: str
    education: str
    income_level: str
    bmi: Optional[float] = None
    waist_cm: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    total_cholesterol: Optional[float] = None
    told_high_bp: str
    family_diabetes: str
    smoked_100_cigs: str
    vigorous_activity: str
    moderate_activity: str

@app.post("/predict")
def predict(data: UserInput):

    row = {k: (np.nan if v is None else v) for k, v in data.model_dump().items()}
    row["cholesterol_ratio"] = row["total_cholesterol"] / row["hdl_cholesterol"] if row["hdl_cholesterol"] > 0 else np.nan

    df = pd.DataFrame([row])

    names = ["Normal", "Prediabetes", "Diabetes"]
    prediction = int(model.predict(df)[0])
    proba = model.predict_proba(df)[0]

    return {
        "result": names[prediction],
        "normal_probability": round(float(proba[0]), 4),
        "prediabetes_probability": round(float(proba[1]), 4),
        "diabetes_probability": round(float(proba[2]), 4)
    }