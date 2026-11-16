import os
from google.cloud import firestore

# 1. Tell Python to use our local practice database instead of the real cloud
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

# 2. Connect to the database (any fake project name works locally)
db = firestore.Client(project="classroom-demo")

# --- STEP A: CREATE (Save Data) ---
print("1. Saving a student record...")
# Think of 'students' as a folder, and 'student_01' as a specific file inside it
doc_ref = db.collection("students").document("student_01")
doc_ref.set({
    "name": "Alex",
    "grade": 92,
    "passed": True
})

# --- STEP B: READ (Get Data Back) ---
print("2. Reading the record back...")
doc = doc_ref.get()
if doc.exists:
    print("   Found data:", doc.to_dict())

# --- STEP C: UPDATE (Change Part of the Data) ---
print("3. Updating Alex's grade...")
doc_ref.update({
    "grade": 98
})
print("   Updated data:", doc_ref.get().to_dict())

# --- STEP D: DELETE (Remove Data) ---
print("4. Deleting the record...")
doc_ref.delete()
print("   Does record still exist?", doc_ref.get().exists)
