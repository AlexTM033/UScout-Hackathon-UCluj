"""
Utility script to manage API Keys for U Cluj Scout AI.

Usage:
  python add_key.py                     # List all existing keys
  python add_key.py add scout_pro       # Generate a new key with role 'scout_pro'
  python add_key.py add admin           # Generate a new key with role 'admin'
  python add_key.py revoke <key>        # Deactivate a key
"""

import sys
import secrets
from database import SessionLocal, APIKey, init_db

init_db()
db = SessionLocal()

def list_keys():
    keys = db.query(APIKey).all()
    if not keys:
        print("No API keys found.")
        return
    print(f"\n{'KEY':<40} {'ROLE':<15} {'ACTIVE'}")
    print("-" * 60)
    for k in keys:
        status = "YES" if k.is_active else "NO"
        print(f"{k.key:<40} {k.role:<15} {status}")
    print()

def add_key(role: str):
    new_key = secrets.token_hex(24)  # 48-char secure random key
    record = APIKey(key=new_key, role=role, is_active=True)
    db.add(record)
    db.commit()
    print(f"\n  New API Key created!")
    print(f"  Key:  {new_key}")
    print(f"  Role: {role}")
    print(f"\n  Save this key! It cannot be recovered.\n")

def revoke_key(key: str):
    record = db.query(APIKey).filter(APIKey.key == key).first()
    if not record:
        print(f"Key not found: {key}")
        return
    record.is_active = False
    db.commit()
    print(f"Key revoked successfully: {key}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_keys()
    elif sys.argv[1] == "add" and len(sys.argv) >= 3:
        add_key(sys.argv[2])
    elif sys.argv[1] == "revoke" and len(sys.argv) >= 3:
        revoke_key(sys.argv[2])
    else:
        print(__doc__)

db.close()
