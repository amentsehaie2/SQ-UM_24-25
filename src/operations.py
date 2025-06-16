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
def add_traveller():
    conn = get_db_connection()
    print("Enter traveller details:")

    while True:
        first_name = input("First name: ")
        if validate_fname(first_name):
            break
        print("Invalid first name. Please try again.")

    while True:
        last_name = input("Last name: ")
        if validate_lname(last_name):
            break
        print("Invalid last name. Please try again.")

    birth_date = input("Birth date (YYYY-MM-DD): ")
    gender = input("Gender: ")

    while True:
        street_name = input("Street name: ")
        if validate_street_name(street_name):
            break
        print("Invalid street name. Please try again.")

    while True:
        house_number = input("House number: ")
        if validate_house_number(house_number):
            break
        print("Invalid house number. Please try again.")

    while True:
        zip_code = input("Zip code: ")
        if validate_zip(zip_code):
            break
        print("Invalid zip code. Please try again.")

    while True:
        city = input("City: ")
        if validate_city(city):
            break
        print("Invalid city. Please try again.")

    while True:
        email = input("Email: ")
        if validate_email(email):
            break
        print("Invalid email. Please try again.")

    while True:
        phone_number = input("Phone number: ")
        if validate_phone(phone_number):
            break
        print("Invalid phone number. Please try again.")

    while True:
        mobile_phone = input("Mobile phone: ")
        if validate_phone(mobile_phone):
            break
        print("Invalid mobile phone. Please try again.")

    while True:
        license_number = input("License number: ")
        if validate_license_number(license_number):
            break
        print("Invalid license number. Please try again.")

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
def add_scooter():
    conn = get_db_connection()
    print("Enter scooter details:")

    while True:
        brand = input("Brand: ")
        if validate_brand(brand):
            break
        print("Invalid brand. Please try again.")

    while True:
        model = input("Model: ")
        if validate_model(model):
            break
        print("Invalid model. Please try again.")

    while True:
        serial_number = input("Serial number: ")
        if validate_serial_number(serial_number):
            break
        print("Invalid serial number. Please try again.")

    top_speed = input("Top speed: ")
    battery_capacity = input("Battery capacity: ")
    state_of_charge = input("State of charge: ")
    target_range = input("Target range: ")

    while True:
        location = input("Location: ")
        if validate_street_name(location):
            break
        print("Invalid location. Please try again.")

    out_of_service = input("Out of service (True/False): ")
    mileage = input("Mileage: ")
    last_service_date = input("Last service date (YYYY-MM-DD): ")

    encrypted_brand = encrypt_data(brand)
    encrypted_model = encrypt_data(model)
    encrypted_serial = encrypt_data(serial_number)
    encrypted_location = encrypt_data(location)
    try:
        cursor = conn.cursor()
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


# list_users_and_roles()
add_traveller()
