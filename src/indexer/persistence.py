# src/indexer/persistence.py
import sys
import os
import shutil
import sqlite3

def verify_db_integrity(db_path: str) -> bool:
    full_path = os.path.join(db_path, "chroma.sqlite3")
    # Ensure it exists
    os.makedirs(db_path, exist_ok=True)

    if not os.path.exists(full_path):
        return True
    
    try:
        connection = sqlite3.connect(full_path)
        cursor = connection.cursor()

        # INTEGRITY CHECK
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        connection.close()

        if result and result[0] == "ok":
            return True
        else:
            print(f"DB corrupted: {result}")
            return False
    except sqlite3.Error as e:
        print(f"SQLite3 error: {e}")
        return False

def reset_db(db_path: str):
    if os.path.exists(db_path):
        print(f"Deleting database: {db_path}")
        shutil.rmtree(db_path) # Recursively delete