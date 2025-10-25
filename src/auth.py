import os
import sys
import sqlite3
import bcrypt
from datetime import datetime
from logger import log_activity, show_suspicious_alert

from database import DATABASE_NAME, get_user_by_username
try:
    from src.encryption import decrypt_data
except ImportError:
    from encryption import decrypt_data
try:
    from src.validation import validate_username, validate_password
except ImportError:
    from validation import validate_username, validate_password

SUPER_ADMIN = {"username": "super_admin", "password": "Admin_123?"}

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def get_all_users_from_db():
    """
    Let op: hier lees je rechtstreeks uit de DB, dus moet je zelf decrypten.
    In database.py zijn usernames/rollen versleuteld opgeslagen.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, registration_date FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = []
    for user_id, enc_username, hashed_pw, enc_role, reg_date in rows:
        try:
            username = decrypt_data(enc_username)
            role = decrypt_data(enc_role)
        except Exception:
            continue

        users.append({
            "id": user_id,
            "username": username,     
            "password": hashed_pw,
            "role": role,             
            "registration_date": reg_date
        })
    return users

def login():
    MAX_STRIKES = 4
    strike_count = 0
    while strike_count < MAX_STRIKES:
        username_input = input("Username: ")
        # Allow hardcoded super admin username to pass validation
        if username_input == SUPER_ADMIN["username"]:
            break
        if not isinstance(username_input, str) or username_input == "":
            print("Username must be a non-empty string.")
            log_activity("unknown user", "Invalid username input", suspicious=True)
            strike_count += 1
            continue
        if not validate_username(username_input):
            print("Invalid username format.")
            log_activity("unknown user", "Invalid username format", suspicious=True)
            strike_count += 1
            continue
        break
    else:
        print("Too many invalid attempts for username. Please try again later.")
        log_activity("unknown user", "Unsuccessful login attempt", f"Strike Count: {strike_count}, Maximum reached.", suspicious=True)
        return None

    strike_count = 0
    while strike_count < MAX_STRIKES:
        password_input = input("Password: ")
        if password_input == SUPER_ADMIN["password"]:
            break
        if not isinstance(password_input, str) or password_input == "":
            print("Password must be a non-empty string.")
            strike_count += 1
            continue
        if not validate_password(password_input):
            print("Invalid password format.")
            strike_count += 1
            continue
        break
    else:
        print("Too many invalid attempts for password. Please try again later.")
        return None
    
    if (username_input == SUPER_ADMIN["username"] and password_input == SUPER_ADMIN["password"]):
        log_activity(username_input, "Super Admin login", False)
        print("Super Admin logged in successfully.")
        user = {"id": 0, "username": username_input, "role": "super_admin"}
        show_suspicious_alert()
        return user

    user_db = get_user_by_username(username_input)
    if user_db:
        if verify_password(password_input, user_db["password"]):
            log_activity(username_input, f"Login as {user_db['role']}", False)
            print(f"Logged in as {user_db['role']}.")
            user_obj = {
                "id": user_db["id"],
                "username": user_db["username"], 
                "role": user_db["role"]
            }
            if user_db["role"] in ["system_admin", "super_admin"]:
                show_suspicious_alert()
            return user_obj
        else:
            log_activity(username_input, "Login failed: invalid password", True)
            print("Invalid password.")
            return None

    log_activity(username_input, "Login failed: user not found", True)
    print("User not found.")
    return None


def logout(user):
    log_activity(user["username"], "User logged out", False)
    print(f"{user['username']} has been logged out.")
