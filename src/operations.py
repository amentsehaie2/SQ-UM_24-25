import sqlite3
import os
import shutil
import secrets
from datetime import datetime
from validation import (
    validate_zip, validate_phone, validate_fname, validate_lname, validate_house_number,
    validate_email, validate_username, validate_street_name, validate_license_number, validate_city
)
from encryption import encrypt_data, decrypt_data
import bcrypt
from logger import log_activity, read_logs

# Use the same DB path logic as database.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DB_PATH = os.path.join(OUTPUT_DIR, "urban_mobility.db")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backup")
RESTORE_CODE_FILE = os.path.join(OUTPUT_DIR, "restore_code.txt")

def get_db_connection():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

# === Traveller Operations ===
def add_traveller(first_name, last_name, birth_date, gender, street_name, house_number, zip_code, city, email, phone_number, mobile_phone, license_number):
    if not (validate_fname(first_name) and validate_lname(last_name) and validate_house_number(house_number)
            and validate_zip(zip_code) and validate_email(email) and validate_phone(phone_number)
            and validate_phone(mobile_phone) and validate_license_number(license_number) and validate_city(city)):
        print("Validation failed for one or more fields.")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    registration_date = datetime.now()
    encrypted_first_name = encrypt_data(first_name)
    encrypted_last_name = encrypt_data(last_name)
    encrypted_birth_date = encrypt_data(birth_date)
    encrypted_gender = encrypt_data(gender)
    encrypted_street_name = encrypt_data(street_name)
    encrypted_house_number = encrypt_data(house_number)
    encrypted_zip_code = encrypt_data(zip_code)
    encrypted_city = encrypt_data(city)
    encrypted_email = encrypt_data(email)
    encrypted_mobile_phone = encrypt_data(mobile_phone)
    encrypted_license_number = encrypt_data(license_number)
    try:
        cursor.execute("""
            INSERT INTO travellers (first_name, last_name, birth_date, gender, street_name, 
                                    house_number, zip_code, city, email, mobile_phone, 
                                    license_number, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (encrypted_first_name, encrypted_last_name, encrypted_birth_date, encrypted_gender,
              encrypted_street_name, encrypted_house_number, encrypted_zip_code, encrypted_city,
              encrypted_email, encrypted_mobile_phone, encrypted_license_number, registration_date))
        conn.commit()
        print("Traveller added.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Traveller with email '{email}' might already exist or other integrity constraint failed.")
        return False
    finally:
        conn.close() #WERKT VOLLEDIG

def search_travellers(key):
    conn = get_db_connection()
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
    conn.close()
    return results

def update_traveller(customer_id, **kwargs):
    # kwargs: any updatable field, must be validated and encrypted
    allowed_fields = {
        "first_name": validate_fname,
        "last_name": validate_lname,
        "birth_date": lambda x: True,
        "gender": lambda x: True,
        "street_name": validate_street_name,
        "house_number": validate_house_number,
        "zip_code": validate_zip,
        "city": validate_city,
        "email": validate_email,
        "phone_number": validate_phone,
        "mobile_phone": validate_phone,
        "license_number": validate_license_number
    }
    updates = []
    values = []
    for field, value in kwargs.items():
        if field in allowed_fields and allowed_fields[field](value):
            updates.append(f"{field}=?")
            values.append(encrypt_data(value))
        else:
            print(f"Invalid value for {field}.")
            return False
    if not updates:
        print("No valid fields to update.")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"UPDATE travellers SET {', '.join(updates)} WHERE customer_id=?"
    values.append(customer_id)
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()
    print("Traveller updated.")
    return True

def delete_traveller(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM travellers WHERE customer_id=?", (customer_id,))
    conn.commit()
    conn.close()
    print("Traveller deleted.")
    return True



# === Scooter Operations ===
def add_scooter(brand, model, serial_number, top_speed, battery_capacity, state_of_charge, target_range, location, out_of_service, mileage, last_service_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_brand = encrypt_data(brand)
    encrypted_model = encrypt_data(model)
    encrypted_serial = encrypt_data(serial_number)
    encrypted_location = encrypt_data(location)
    try:
        cursor.execute("""
            INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity, state_of_charge, target_range, location, out_of_service, mileage, last_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (encrypted_brand, encrypted_model, encrypted_serial, top_speed, battery_capacity, state_of_charge, target_range, encrypted_location, out_of_service, mileage, last_service_date))
        conn.commit()
        print("Scooter added.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Scooter with serial number '{serial_number}' might already exist.")
        return False
    finally:
        conn.close()

def search_scooters(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scooter_id, brand, model, serial_number, location FROM scooters")
    results = []
    for row in cursor.fetchall():
        decrypted_brand = decrypt_data(row[1])
        decrypted_model = decrypt_data(row[2])
        decrypted_serial = decrypt_data(row[3])
        decrypted_location = decrypt_data(row[4])
        if (key.lower() in decrypted_brand.lower() or key.lower() in decrypted_model.lower() or key.lower() in decrypted_serial.lower()):
            results.append((row[0], decrypted_brand, decrypted_model, decrypted_serial, decrypted_location))
    conn.close()
    return results

def update_scooter(scooter_id, **kwargs):
    allowed_fields = {
        "brand": lambda x: True,
        "model": lambda x: True,
        "serial_number": lambda x: True,
        "top_speed": lambda x: True,
        "battery_capacity": lambda x: True,
        "state_of_charge": lambda x: True,
        "target_range": lambda x: True,
        "location": lambda x: True,
        "out_of_service": lambda x: True,
        "mileage": lambda x: True,
        "last_service_date": lambda x: True
    }
    updates = []
    values = []
    for field, value in kwargs.items():
        if field in allowed_fields and allowed_fields[field](value):
            if field in {"brand", "model", "serial_number", "location"}:
                updates.append(f"{field}=?")
                values.append(encrypt_data(value))
            else:
                updates.append(f"{field}=?")
                values.append(value)
        else:
            print(f"Invalid value for {field}.")
            return False
    if not updates:
        print("No valid fields to update.")
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f"UPDATE scooters SET {', '.join(updates)} WHERE scooter_id=?"
    values.append(scooter_id)
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()
    print("Scooter updated.")
    return True

def delete_scooter(scooter_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scooters WHERE scooter_id=?", (scooter_id,))
    conn.commit()
    conn.close()
    print("Scooter deleted.")
    return True



# === User/System Admin Functions ===
def list_users(): #WERKT VOLLEDIG   
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, registration_date FROM users")
    users = cursor.fetchall()
    print("Users:")
    for user in users:
        print(f"ID: {user[0]}  |  Username: {decrypt_data(user[1])}  |  Password: [Hidden]  |  Role: {decrypt_data(user[3])}  |  Registration Date: {user[4]}")
    conn.close()

def _set_user_password(conn, username, password): # ADRIAN 
    encrypted_username = encrypt_data(username)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, encrypted_username))
    conn.commit()

def add_service_engineer():# WERKT VOLLEDIG
    conn = get_db_connection ()
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

def update_service_engineer_username(): # WERKT VOLLEDIG
    """Updates the username of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the user you want to update: "))
    except ValueError:
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        print("User with that ID not found.")
        conn.close()
        return

    current_username_encrypted = result[0]
    current_username = decrypt_data(current_username_encrypted)

    current_username_input = input(f"Enter the current username for user ID {user_id}: ")
    if current_username_input != current_username:
        print("Incorrect current username.")
        conn.close()
        return

    new_username = input("Enter the new username: ")
    if new_username == current_username:
        print("New username cannot be the same as the current username.")
        log_activity("test_user", f"Attempted to update username to {new_username}", "Username already exists", False)
        conn.close()
        return

    if not validate_username(new_username):
        print("Invalid username format. Please use 3-20 alphanumeric characters or underscores.")
        log_activity("test_user", f"Attempted to update username to {new_username}", "Invalid username format", False)
        conn.close()
        return

    cursor.execute("SELECT id FROM users WHERE username = ?", (encrypt_data(new_username),))
    if cursor.fetchone():
        print("This username is already taken.")
        conn.close()
        log_activity("test_user", f"Attempted to update username to {new_username}", "Username already exists", False)
        return

    encrypted_new_username = encrypt_data(new_username)
    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
    conn.commit()
    print("Username updated successfully.")
    conn.close()

def delete_service_engineer(): # WERKT NIET
    conn = get_db_connection()
    username = input("Username to delete: ")
    #CONFIRM DELETE
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=? AND role=?", (encrypt_data(username), encrypt_data("engineer")))
    conn.commit()
    conn.close()
    print("Engineer deleted.")

def reset_service_engineer_password(): # set user moet nog af
    conn = get_db_connection()
    username = input("Username: ")
    new_password = secrets.token_urlsafe(8)
    _set_user_password(conn, username, new_password)
    conn.close()
    print(f"Temporary password: {new_password}")

def update_service_engineer_password(): # set user moet nog af
    conn = get_db_connection()
    username = input("Username: ")
    password = input("New Password: ")
    _set_user_password(conn, username, password)
    conn.close()
    print("Password updated.")

def add_system_admin(): # MOET NOG VALIDATED WORDEN
    conn = get_db_connection()
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

def update_system_admin_username(): # WERKT VOLLEDIG
    """Updates the username of a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        print("User with that ID not found.")
        conn.close()
        return

    current_username_encrypted = result[0]
    current_username = decrypt_data(current_username_encrypted)
    user_role_encrypted = result[1]
    user_role = decrypt_data(user_role_encrypted)

    if user_role != "admin":
        print("User with that ID is not a System Administrator.")
        conn.close()
        return

    current_username_input = input(f"Enter the current username for system administrator ID {user_id}: ")
    if current_username_input != current_username:
        print("Incorrect current username.")
        conn.close()
        return

    new_username = input("Enter the new username: ")
    if new_username == current_username:
        print("New username cannot be the same as the current username.")
        conn.close()
        return

    if not validate_username(new_username):
        print("Invalid username format. Please use 3-20 alphanumeric characters or underscores.")

        conn.close()
        return

    cursor.execute("SELECT id FROM users WHERE username = ?", (encrypt_data(new_username),))
    if cursor.fetchone():
        print("This username is already taken.")
        conn.close()
        return

    encrypted_new_username = encrypt_data(new_username)
    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
    conn.commit()
    print("Username updated successfully.")
    conn.close()

def update_system_admin_password():# set user moet nog af
    conn = get_db_connection()
    username = input("Username: ")
    old_password = input("Current Password: ")
    new_password = input("New Password: ")
    #NIEUWE NOG VALIDATEN
    _set_user_password(conn, username, new_password)
    conn.close()
    print("Password updated.")

def delete_system_admin():#WERKT NIET DOOR QUERY
    conn = get_db_connection()
    username = input("Username to delete: ")
    #CONFIRM DELETE
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=? AND role=?", (encrypt_data(username), encrypt_data("admin")))
    conn.commit()
    conn.close()
    print("Admin deleted.")

def reset_system_admin_password():#set user moet nog af
    conn = get_db_connection()
    username = input("Username: ")
    new_password = secrets.token_urlsafe(8)
    _set_user_password(conn, username, new_password)
    conn.close()
    print(f"Temporary password: {new_password}")

def view_system_logs():# niet nodig, gebruik logger.py
    log_path = os.path.join(OUTPUT_DIR, "system.log")
    if os.path.exists(log_path):
        with open(log_path) as log:
            print(log.read())
    else:
        print("No logs found.")

def make_backup(): #jayden
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_file = os.path.join(BACKUP_DIR, f"urban_mobility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(DB_PATH, backup_file)
    print(f"Backup created at {backup_file}")

def restore_backup(): #jayden
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

def generate_restore_code(): #jayden
    code = secrets.token_urlsafe(16)
    with open(RESTORE_CODE_FILE, "w") as f:
        f.write(code)
    print(f"Restore code generated and saved.")

def revoke_restore_code(): #jayden
    if os.path.exists(RESTORE_CODE_FILE):
        os.remove(RESTORE_CODE_FILE)
        print("Restore code revoked.")
    else:
        print("No restore code to revoke.")


if __name__ == "__main__":

    ###TRAVELLER OPERATIONS
    # add_traveller("John", "Doe", "1990-01-01", "Male", "Main Street", "123", "1234AB", "Rotterdam", "test@example.com", "+31-6-12345678", "+31-6-12345678", "AB1234567")
    # delete_traveller(1)
    # update_traveller(1, first_name="Jane", last_name="Doe", birth_date="1990-01-01", gender="Female", street_name="New Street", house_number="456", zip_code="5678CD", city="Amsterdam", email="jane.doe@example.com", mobile_phone="+31-6-87654321", license_number="CD9876543")
    # search_travellers("Jane")

    ###SCOOTER OPERATIONS
    # add_vehicle("John", "Doe", "1990-01-01", "Male", "Main Street", "123", "12345", "City", "8Fg6y@example.com", "1234567890", "1234567890", "1234567890")
    # update_vehicle("John", "Doe", "1990-01-01", "Male", "Main Street", "123", "12345", "City", "8Fg6y@example.com", "1234567890", "1234567890", "1234567890")   
    # delete_vehicle("John", "Doe")
    # search_vehicles("John", "Doe", "1990-01-01", "Male", "Main Street", "123", "12345", "City", "8Fg6y@example.com", "1234567890", "1234567890", "1234567890")


    list_users()

    ###SYSTEM ADMIN FUNCTIONS
    # add_system_admin()
    # update_system_admin_username()
    # update_system_admin_password()   
    # delete_system_admin()
    # reset_system_admin_password()

    ###SERVICE ENGINEER FUNCTIONS
    # add_service_engineer()
    #update_service_engineer_username()
    # logs = read_logs()
    # for log in logs:
    #     print("\nLogs")
    #     print(f"ID: {log['log_id']}  |  Date: {log['timestamp']}  |  User: {log['username']}  |  Desc: {log['description']}  |  Info: {log['additional_info']}  |  Suspicious: {log['suspicious']}")

    # update_service_engineer_password()
    # delete_service_engineer()
    # reset_service_engineer_password()