import sqlite3
import os
import shutil
import secrets
from datetime import datetime
from validation import validate_zip, validate_phone
from encryption import encrypt_data, decrypt_data
import bcrypt

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "urban_mobility.db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backup")
RESTORE_CODE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "restore_code.txt")

# === Traveller Operations ===
def add_traveller(conn, first, last, zipc, phone):
    if not validate_zip(zipc):
        print("Invalid zip code format.")
        return False
    if not validate_phone(phone):
        print("Invalid phone number format.")
        return False
    encrypted_first = encrypt_data(first)
    encrypted_last = encrypt_data(last)
    encrypted_zip = encrypt_data(zipc)
    encrypted_phone = encrypt_data(phone)
    registration_date = datetime.now()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO travellers (first_name, last_name, zip_code, mobile_phone, registration_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (encrypted_first, encrypted_last, encrypted_zip, encrypted_phone, registration_date)
    )
    conn.commit()
    print("Traveller added.")
    return True

def update_traveller(conn, tid, first, last, zipc, phone):
    if not validate_zip(zipc):
        print("Invalid zip code format.")
        return False
    if not validate_phone(phone):
        print("Invalid phone number format.")
        return False
    encrypted_first = encrypt_data(first)
    encrypted_last = encrypt_data(last)
    encrypted_zip = encrypt_data(zipc)
    encrypted_phone = encrypt_data(phone)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE travellers 
        SET first_name=?, last_name=?, zip_code=?, mobile_phone=? 
        WHERE customer_id=?
        """,
        (encrypted_first, encrypted_last, encrypted_zip, encrypted_phone, tid)
    )
    conn.commit()
    print("Traveller updated.")
    return True

def delete_traveller(conn, tid):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM travellers WHERE customer_id=?", (tid,))
    conn.commit()
    print("Traveller deleted.")
    return True

def search_travellers(conn, key):
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, first_name, last_name, zip_code, mobile_phone FROM travellers")
    results = []
    for row in cursor.fetchall():
        decrypted_first = decrypt_data(row[1])
        decrypted_last = decrypt_data(row[2])
        if key.lower() in decrypted_first.lower() or key.lower() in decrypted_last.lower():
            decrypted_zip = decrypt_data(row[3])
            decrypted_phone = decrypt_data(row[4])
            results.append((row[0], decrypted_first, decrypted_last, decrypted_zip, decrypted_phone))
    return results

# === Scooter Operations ===
def add_scooter(conn, serial_number, model, out_of_service):
    encrypted_model = encrypt_data(model)
    encrypted_serial = encrypt_data(serial_number)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scooters (serial_number, model, out_of_service) 
        VALUES (?, ?, ?)
        """,
        (encrypted_serial, encrypted_model, out_of_service)
    )
    conn.commit()
    print("Scooter added.")
    return True

def update_scooter(conn, serial_number, model, out_of_service):
    encrypted_model = encrypt_data(model)
    encrypted_serial = encrypt_data(serial_number)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE scooters SET model=?, out_of_service=? WHERE serial_number=?
        """,
        (encrypted_model, out_of_service, encrypted_serial)
    )
    conn.commit()
    print("Scooter updated.")
    return True

def delete_scooter(conn, serial_number):
    encrypted_serial = encrypt_data(serial_number)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scooters WHERE serial_number=?", (encrypted_serial,))
    conn.commit()
    print("Scooter deleted.")
    return True

def search_scooters(conn, key):
    cursor = conn.cursor()
    cursor.execute("SELECT serial_number, model, out_of_service FROM scooters")
    results = []
    for row in cursor.fetchall():
        decrypted_serial = decrypt_data(row[0])
        decrypted_model = decrypt_data(row[1])
        if key.lower() in decrypted_serial.lower() or key.lower() in decrypted_model.lower():
            results.append((decrypted_serial, decrypted_model, row[2]))
    return results

# === User/System Admin Functions ===
def list_users_and_roles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    print("Users and roles:")
    for user in users:
        print(f"Username: {decrypt_data(user[0])}, Role: {decrypt_data(user[1])}")
    conn.close()

def _set_user_password(conn, username, password):
    encrypted_username = encrypt_data(username)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, encrypted_username))
    conn.commit()

def add_service_engineer():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    password = input("Password: ")
    encrypted_username = encrypt_data(username)
    encrypted_role = encrypt_data("engineer")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role, registration_date) VALUES (?, ?, ?, ?)",
                   (encrypted_username, hashed_password, encrypted_role, datetime.now()))
    conn.commit()
    print("Service Engineer added.")
    conn.close()

def update_service_engineer_profile():
    conn = sqlite3.connect(DB_PATH)
    old_username = input("Current Username: ")
    new_username = input("New Username: ")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=? WHERE username=?", (encrypt_data(new_username), encrypt_data(old_username)))
    conn.commit()
    conn.close()
    print("Profile updated.")

def delete_service_engineer():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username to delete: ")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=? AND role=?", (encrypt_data(username), encrypt_data("engineer")))
    conn.commit()
    conn.close()
    print("Engineer deleted.")

def reset_service_engineer_password():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    new_password = secrets.token_urlsafe(8)
    _set_user_password(conn, username, new_password)
    conn.close()
    print(f"Temporary password: {new_password}")

def update_service_engineer_password():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    password = input("New Password: ")
    _set_user_password(conn, username, password)
    conn.close()
    print("Password updated.")

def add_system_admin():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    password = input("Password: ")
    encrypted_username = encrypt_data(username)
    encrypted_role = encrypt_data("admin")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role, registration_date) VALUES (?, ?, ?, ?)",
                   (encrypted_username, hashed_password, encrypted_role, datetime.now()))
    conn.commit()
    conn.close()
    print("System Admin added.")

def update_system_admin_profile():
    conn = sqlite3.connect(DB_PATH)
    old_username = input("Current Username: ")
    new_username = input("New Username: ")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=? WHERE username=?", (encrypt_data(new_username), encrypt_data(old_username)))
    conn.commit()
    conn.close()
    print("Profile updated.")

def delete_system_admin():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username to delete: ")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=? AND role=?", (encrypt_data(username), encrypt_data("admin")))
    conn.commit()
    conn.close()
    print("Admin deleted.")

def reset_system_admin_password():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    new_password = secrets.token_urlsafe(8)
    _set_user_password(conn, username, new_password)
    conn.close()
    print(f"Temporary password: {new_password}")

def update_system_admin_password():
    conn = sqlite3.connect(DB_PATH)
    username = input("Username: ")
    password = input("New Password: ")
    _set_user_password(conn, username, password)
    conn.close()
    print("Password updated.")

def view_system_logs():
    log_path = os.path.join(os.path.dirname(DB_PATH), "system.log")
    if os.path.exists(log_path):
        with open(log_path) as log:
            print(log.read())
    else:
        print("No logs found.")

def make_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_file = os.path.join(BACKUP_DIR, f"urban_mobility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(DB_PATH, backup_file)
    print(f"Backup created at {backup_file}")

def restore_backup():
    backups = sorted(os.listdir(BACKUP_DIR))
    if not backups:
        print("No backup available.")
        return
    print("Available backups:")
    for i, f in enumerate(backups):
        print(f"[{i}] {f}")
    idx = int(input("Choose backup number to restore: "))
    backup_file = os.path.join(BACKUP_DIR, backups[idx])
    shutil.copy2(backup_file, DB_PATH)
    print("Backup restored.")

def generate_restore_code():
    code = secrets.token_urlsafe(16)
    with open(RESTORE_CODE_FILE, "w") as f:
        f.write(code)
    print(f"Restore code generated and saved.")

def revoke_restore_code():
    if os.path.exists(RESTORE_CODE_FILE):
        os.remove(RESTORE_CODE_FILE)
        print("Restore code revoked.")
    else:
        print("No restore code to revoke.")