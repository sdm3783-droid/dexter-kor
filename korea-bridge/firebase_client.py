import os, time
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'dexter', '.env'))

_db = None

def get_db():
    global _db
    if _db is None:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db

def get_cached(collection: str, doc_id: str, ttl_seconds: int) -> dict | None:
    db = get_db()
    doc = db.collection(collection).document(doc_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if time.time() - data.get("cached_at", 0) > ttl_seconds:
        return None
    return data.get("payload")

def set_cached(collection: str, doc_id: str, payload: dict):
    db = get_db()
    db.collection(collection).document(doc_id).set({
        "payload": payload,
        "cached_at": time.time(),
    })
