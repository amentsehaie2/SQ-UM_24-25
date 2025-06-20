import os
import sys
import sqlite3
import bcrypt
from datetime import datetime
from logger import log_activity, show_suspicious_alert

from database import DATABASE_NAME, get_user_by_username
from encryption import encrypt_data

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

def log_action(username, description, suspicious=False):
    flag = "SUSPICIOUS" if suspicious else "OK"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{now} | {username} | {description} | {flag}\n"
    with open(os.path.join(os.path.dirname(__file__), "activity.log"), "a", encoding="utf-8") as f:
        f.write(log_line)

def get_all_users_from_db():
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
        username_input = input("Username: ").strip()
        if not isinstance(username_input, str) or username_input == "":
            print("Username must be a non-empty string.")
            strike_count += 1
        else:
            break
    else:
        print("Too many invalid attempts for username. Please try again later.")
        return None

    strike_count = 0
    while strike_count < MAX_STRIKES:
        password_input = input("Password: ").strip()
        if not isinstance(password_input, str) or password_input == "":
            print("Password must be a non-empty string.")
            strike_count += 1
        else:
            break
    else:
        print("Too many invalid attempts for password. Please try again later.")
        return None

    # Super Admin login
    if (username_input == SUPER_ADMIN["username"] and password_input == SUPER_ADMIN["password"]):
        log_action(username_input, "Super Admin login", False)
        print("Super Admin logged in successfully.")
        user = {"id": 0, "username": username_input, "role": "super_admin"}
        show_suspicious_alert()
        return user

    # Look up user in database
    user_db = get_user_by_username(username_input)
    if user_db:
        if verify_password(password_input, user_db["password"]):
            log_action(username_input, f"Login as {user_db['role']}", False)
            print(f"Logged in as {user_db['role']}.")
            user_obj = {
                "id": user_db["id"], 
                "username": encrypt_data(user_db["username"]),  # encrypted in memory
                "role": user_db["role"]
            }
            if user_db["role"] in ["admin", "super_admin"]:
                show_suspicious_alert()
            return user_obj
        else:
            log_action(username_input, "Login failed: invalid password", True)
            print("Invalid password.")
            return None

    log_action(username_input, "Login failed: user not found", True)
    print("User not found.")
    return None

def logout(user):
    log_action(user["username"], "User logged out", False)
    print(f"{user['username']} has been logged out.")
