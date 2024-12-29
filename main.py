import os
import base64
import requests

from fastapi import FastAPI, HTTPException
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dotenv import load_dotenv

from encryption import encrypt_password

# .env laden
load_dotenv()

app = FastAPI()

# Demo-Umgebung. Für Live: https://api-capital.backend-capital.com
CAPITAL_BASE_URL = "https://demo-api-capital.backend-capital.com"

# API Key, User (Identifier) und Passwort aus .env
CAPITAL_API_TOKEN = os.getenv("CAPITAL_API_KEY", "DEIN_API_KEY")
CAPITAL_USER = os.getenv("CAPITAL_USER", "DEIN_USER")
CAPITAL_PASSWORD = os.getenv("CAPITAL_PASSWORD", "DEIN_PASSWORT")


@app.get("/")
def home():
    return {
        "message": "FastAPI + Capital.com Demo - AES Encryption Login in nur einem Aufruf"
    }


@app.get("/positions")
def get_positions():
    """
    Führt in EINEM Schritt aus:
    1) /api/v1/session/encryptionKey -> encryptionKey + timeStamp holen
    2) CAPITAL_PASSWORD per AES verschlüsseln
    3) /api/v1/session -> Login (CST, X-SECURITY-TOKEN)
    4) /api/v1/positions -> offene Positionen abfragen
    """

    print("start", CAPITAL_API_TOKEN, CAPITAL_BASE_URL)

    # ----------------------------------------------------
    # 1) ENCRYPTION KEY + TIMESTAMP HOLEN
    # ----------------------------------------------------
    try:
        enc_resp = requests.get(
            f"{CAPITAL_BASE_URL}/api/v1/session/encryptionKey",
            headers={"X-CAP-API-KEY": CAPITAL_API_TOKEN},
            timeout=10,
        )
        enc_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Fehler bei /encryptionKey-Anfrage: {e}"
        )

    enc_data = enc_resp.json()
    encryption_key_b64 = enc_data.get("encryptionKey")
    time_stamp = enc_data.get("timeStamp")

    if not encryption_key_b64 or not time_stamp:
        raise HTTPException(
            status_code=500, detail="encryptionKey oder timeStamp nicht gefunden!"
        )

    encrypted_password_b64 = encrypt_password(
        encryption_key_b64, time_stamp, CAPITAL_PASSWORD
    )

    # print(enc_data)

    # ----------------------------------------------------
    # 3) LOGIN (SESSION) -> CST, X-SECURITY-TOKEN
    # ----------------------------------------------------
    login_payload = {"identifier": CAPITAL_USER, "password": CAPITAL_PASSWORD}

    # print(login_payload)
    try:
        login_resp = requests.post(
            f"{CAPITAL_BASE_URL}/api/v1/session",
            json=login_payload,
            headers={"X-CAP-API-KEY": CAPITAL_API_TOKEN},
            timeout=10,
        )
        login_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Login fehlgeschlagen: {e}")

    cst = login_resp.headers.get("CST")
    x_sec = login_resp.headers.get("X-SECURITY-TOKEN")

    # print("✨", x_sec)

    if not cst or not x_sec:
        raise HTTPException(
            status_code=500, detail="CST oder X-SECURITY-TOKEN nicht vorhanden!"
        )

    # ----------------------------------------------------
    # 4) POSITIONEN ABFRAGEN
    # ----------------------------------------------------
    try:
        pos_resp = requests.get(
            f"{CAPITAL_BASE_URL}/api/v1/accounts",
            headers={
                "CST": cst,
                "X-SECURITY-TOKEN": x_sec,
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        pos_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Positions-Request fehlgeschlagen: {e}"
        )

    return pos_resp.json()

