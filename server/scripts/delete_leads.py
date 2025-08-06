# scripts/delete_all_leads.py

from server.common.firebase_config import get_firestore_db
import firebase_admin

def delete_all_leads(collection_ref, batch_size):
    """
    Deletes all documents from a Firestore collection in batches.
    
    Args:
        collection_ref (google.cloud.firestore.CollectionReference): The collection to delete from.
        batch_size (int): The number of documents to delete per batch.
    """
    docs = collection_ref.limit(batch_size).stream()
    deleted_count = 0

    while True:
        # Stream documents in batches.
        docs = collection_ref.limit(batch_size).stream()
        batch_has_docs = False
        
        for doc in docs:
            print(f"Deleting document {doc.id}")
            doc.reference.delete()
            deleted_count += 1
            batch_has_docs = True

        # If the batch was empty, we're done.
        if not batch_has_docs:
            print(f"✅ Finished. Deleted {deleted_count} documents.")
            break

# The main execution block
if __name__ == "__main__":
    db=get_firestore_db()
    # Assuming 'db' is your initialized Firestore client from firebase_config.
    leads_collection_ref = db.collection("Leads")
    print("Starting deletion of all leads...")
    delete_all_leads(leads_collection_ref, 10)