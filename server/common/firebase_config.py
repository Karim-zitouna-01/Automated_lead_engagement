import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials only once
cred = credentials.Certificate("server/utils/firebase_cred.json")


def get_firestore_db():
    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    # Expose Firestore DB
    db = firestore.client()
    return db
