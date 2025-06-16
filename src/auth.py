# auth.py
# Handles user authentication, password hashing, username decryption search, validation, and login flow
import os
import sys
import sqlite3
import re
import bcrypt
import hashlib

_src_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from src.encryption import decrypt_data
except ImportError:
    from encryption import decrypt_data
from database import DATABASE_NAME

SUPER_ADMIN = {"username": "super_admin", "password": "Admin_123?"}

def hash_password(password):
    """
    Hash a password for storage using bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(password, hashed_password):
    """
    Verify a plaintext password against the stored bcrypt hash.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def validate_username(username):
    """
    Validate username rules:
    - length 8-10
    - starts with letter or underscore
    - contains only letters, digits, underscore, apostrophe, period, hyphen
    """
    if not (8 <= len(username) <= 10):
        return False
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_.'-]{7,9}$", username):
        return False
    return True


def validate_password(password):
    """
    Validate password rules:
    - length 12-30
    - at least one uppercase, one lowercase, one digit, one special char
    """
    if not (12 <= len(password) <= 30):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[~!@#$%&_\-+=`|\\(){}\[\]:;'<>,.?/]", password):
        return False
    return True

def get_all_users_from_db():
    """
    Retrieve and decrypt all users from the database for in-memory search.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role, registration_date FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = []
    for enc_username, hashed_pw, enc_role, reg_date in rows:
        try:
            username = decrypt_data(enc_username)
            role = decrypt_data(enc_role)
        except Exception:
            continue
        users.append({
            "username": username,
            "password": hashed_pw,
            "role": role,
            "registration_date": reg_date
        })
    return users

def login():
    """
    Prompt for credentials, authenticate against hardcoded Super Admin or database.
    """
    username_input = input("Username: ").strip()
    password_input = input("Password: ").strip()

    if (username_input == SUPER_ADMIN["username"] and
        password_input == SUPER_ADMIN["password"]):
        print("Super Admin logged in successfully.")
        return {"username": username_input, "role": "Super Admin"}

    all_users = get_all_users_from_db()
    for user in all_users:
        if user["username"].lower() == username_input.lower():
            if verify_password(password_input, user["password"]):
                print(f"Logged in as {user['role']}.")
                return {"username": user["username"], "role": user["role"]}
            else:
                print("Invalid password.")
                return None

    print("User not found.")
    return None
