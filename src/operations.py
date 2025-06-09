# operations.py
import sqlite3
from validation import validate_zip, validate_phone
from encryption import encrypt_data, decrypt_data

# === Traveller Operations ===
def add_traveller(conn, first, last, zipc, phone):
    if not validate_zip(zipc):
        print("Invalid zip code format.")
        return False
    if not validate_phone(phone):
        print("Invalid phone number format.")
        return False
    encrypted_zip = encrypt_data(zipc)
    encrypted_phone = encrypt_data(phone)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO travellers (first_name, last_name, zip_code, mobile_phone) VALUES (?, ?, ?, ?)",
        (first, last, encrypted_zip, encrypted_phone)
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
    encrypted_zip = encrypt_data(zipc)
    encrypted_phone = encrypt_data(phone)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE travellers SET first_name=?, last_name=?, zip_code=?, mobile_phone=? WHERE customer_id=?",
        (first, last, encrypted_zip, encrypted_phone, tid)
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
    cursor.execute(
        "SELECT customer_id, first_name, last_name, zip_code, mobile_phone FROM travellers WHERE first_name LIKE ? OR last_name LIKE ?",
        (f"%{key}%", f"%{key}%")
    )
    results = []
    for row in cursor.fetchall():
        # Decrypt sensitive fields before returning
        decrypted_zip = decrypt_data(row[3])
        decrypted_phone = decrypt_data(row[4])
        results.append((row[0], row[1], row[2], decrypted_zip, decrypted_phone))
    return results

# === Scooter Operations ===
def add_scooter(conn, sid, model, status):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scooters (serial_number, model, status) VALUES (?, ?, ?)",
        (sid, model, status)
    )
    conn.commit()
    print("Scooter added.")
    return True

def update_scooter(conn, sid, model, status):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scooters SET model=?, status=? WHERE serial_number=?",
        (model, status, sid)
    )
    conn.commit()
    print("Scooter updated.")
    return True

def delete_scooter(conn, sid):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scooters WHERE serial_number=?", (sid,))
    conn.commit()
    print("Scooter deleted.")
    return True

def search_scooters(conn, key):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT serial_number, model, status FROM scooters WHERE serial_number LIKE ? OR model LIKE ?",
        (f"%{key}%", f"%{key}%")
    )
    return cursor.fetchall()

# === User/System/Engineer/Admin Operations ===
def list_users_and_roles():
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()
    print("Users and roles:")
    for user in users:
        print(f"Username: {user[0]}, Role: {user[1]}")
    conn.close()

def add_service_engineer():
    print("Adding a new Service Engineer...")
    # Placeholder: Implement actual logic

def update_service_engineer_profile():
    print("Updating Service Engineer profile...")
    # Placeholder: Implement actual logic

def delete_service_engineer():
    print("Deleting Service Engineer account...")
    # Placeholder: Implement actual logic

def reset_service_engineer_password():
    print("Resetting Service Engineer password...")
    # Placeholder: Implement actual logic

def update_service_engineer_password():
    print("Updating Service Engineer password...")
    # Placeholder: Implement actual logic

def add_system_admin():
    print("Adding a new System Administrator...")
    # Placeholder: Implement actual logic

def update_system_admin_profile():
    print("Updating System Administrator profile...")
    # Placeholder: Implement actual logic

def delete_system_admin():
    print("Deleting System Administrator account...")
    # Placeholder: Implement actual logic

def reset_system_admin_password():
    print("Resetting System Administrator password...")
    # Placeholder: Implement actual logic

def update_system_admin_password():
    print("Updating System Administrator password...")
    # Placeholder: Implement actual logic

def view_system_logs():
    print("Viewing system logs...")
    # Placeholder: Implement actual logic

def make_backup():
    print("Making a system backup...")
    # Placeholder: Implement actual logic

def restore_backup():
    print("Restoring a system backup...")
    # Placeholder: Implement actual logic

def generate_restore_code():
    print("Generating restore-code for System Administrator...")
    # Placeholder: Implement actual logic

def revoke_restore_code():
    print("Revoking restore-code for System Administrator...")
    # Placeholder: Implement actual logic
