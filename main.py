import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import requests

# .env laden (Standard: .env im selben Verzeichnis)
load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")  # Aus deiner .env
BASE_URL = "https://api.capital.com"


@app.get("/")
def home():
    return {"message": "FastAPI-Capital.com-Test-API läuft!"}


@app.get("/test-capital")
def test_capital():
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API-Key nicht konfiguriert!")

    endpoint = f"{BASE_URL}/api/v1/some-endpoint"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return response.json()

