import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def encrypt_password(encryption_key: str, timestamp: int, password: str) -> str:
    """
    Entspricht grob dem Java-Code:

    public static String encryptPassword(String encryptionKey, Long timestamp, String password)
    {
        // ...
    }

    Ablauf:
    1) Erzeugt aus 'password|timestamp' Bytes.
    2) Base64-kodiert diese Bytes.
    3) Dekodiert das übergebene encryption_key (Base64 -> DER-codierte X.509).
    4) Erstellt daraus ein RSA-PublicKey-Objekt.
    5) Verschlüsselt die Base64-kodierten Passwort-Daten mit RSA/PKCS1.
    6) Base64-kodiert das Ergebnis und gibt es als String zurück.
    """
    try:
        # 1) 'password|timestamp' als Bytes
        combined = f"{password}|{timestamp}".encode("utf-8")

        # 2) Base64-kodieren
        b64_input = base64.b64encode(combined)

        # 3) encryption_key ist Base64-codiert -> Dekodieren zu bytes (DER/X.509)
        public_key_bytes = base64.b64decode(encryption_key)

        # 4) PublicKey via X.509 DER laden
        public_key = serialization.load_der_public_key(
            public_key_bytes, backend=default_backend()
        )

        # 5) RSA-Verschlüsselung mit PKCS#1 v1.5 Padding (entspricht "RSA/ECB/PKCS1Padding")
        encrypted_bytes = public_key.encrypt(b64_input, padding.PKCS1v15())

        # 6) Ergebnis Base64-kodieren und zurückgeben
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    except Exception as e:
        raise RuntimeError(f"Encryption failed: {e}")
