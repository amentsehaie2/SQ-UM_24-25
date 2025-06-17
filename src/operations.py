import sqlite3
import os
import shutil
import secrets
import bcrypt
from datetime import datetime
from validation import (
    validate_zip, validate_phone, validate_fname, validate_lname, validate_house_number,
    validate_email, validate_username, validate_street_name, validate_license_number, validate_city,
    validate_birth_date, validate_gender, validate_brand, validate_model, validate_serial_number,
    validate_target_range, validate_top_speed, validate_battery_capacity, validate_SoC, validate_location,
    validate_OoS, validate_mileage, validate_last_maint
)
from encryption import encrypt_data, decrypt_data
from logger import log_activity, read_logs

# Use the same DB path logic as database.py
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")
DATABASE_NAME = os.path.join(_OUTPUT_DIR, "urban_mobility.db")
BACKUP_DIR = os.path.join(_PROJECT_ROOT, "backup")
RESTORE_CODE_FILE = os.path.join(_OUTPUT_DIR, "restore_code.txt")

def get_db_connection():
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    return sqlite3.connect(DATABASE_NAME)

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

    while True:
        birth_date = input("Birth date (YYYY-MM-DD): ")
        if validate_birth_date(birth_date):
            break
        print("Invalid birth date. Please try again.")

    while True:
        gender = input("Gender: ")
        if validate_gender(gender):
            break
        print("Invalid gender. Please try again.")

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
        mobile_phone = input("Mobile phone (8 digits): ")
        if validate_phone(mobile_phone):
            break
        print("Invalid mobile phone number. Please try again.")

    while True:
        license_number = input("License number (XXDDDDDDD or XDDDDDDDD): ")
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
        "birth_date": validate_birth_date,
        "gender": validate_gender,
        "street_name": validate_street_name,
        "house_number": validate_house_number,
        "zip_code": validate_zip,
        "city": validate_city,
        "email": validate_email,
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

    while True:
        try:
            top_speed = int(input("Top speed (integer): "))
            if validate_top_speed(top_speed):
                break
            else:
                print("Invalid top speed. Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            battery_capacity = int(input("Battery capacity (integer): "))
            if validate_battery_capacity(battery_capacity):
                break
            else:
                print("Invalid battery capacity. Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            state_of_charge = int(input("State of charge (0-100): "))
            if validate_SoC(state_of_charge):
                break
            else:
                print("Invalid state of charge. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        try:
            target_range = int(input("Target range (integer): "))
            if validate_target_range(target_range):
                break
            else:
                print("Invalid target range. Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        location = input("Location (latitude,longitude): ")
        if validate_location(location):
            break
        print("Invalid location. Please try again.")

    while True:
        out_of_service_input = input("Out of service (True/False): ")
        if out_of_service_input.lower() in {"true", "false"}:
            out_of_service = out_of_service_input.lower() == "true"
            if validate_OoS(out_of_service):
                break
        print("Invalid input. Please enter True or False.")

    while True:
        try:
            mileage = int(input("Mileage (integer): "))
            if validate_mileage(mileage):
                break
            else:
                print("Invalid mileage. Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        last_service_date = input("Last service date (YYYY-MM-DD): ")
        if validate_last_maint(last_service_date):
            break
        print("Invalid date. Please use YYYY-MM-DD format.")

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

# === SYSTEM BACKUP/RESTORE (ZIP-BASIS) ===

def create_backup():
    """Maakt een zip-backup van de hele output directory (incl. DB)."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"urban_mobility_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.make_archive(backup_path.replace(".zip", ""), 'zip', _OUTPUT_DIR)
    log_activity("system", f"Backup gemaakt: {backup_name}", suspicious=False)
    print(f"Backup gemaakt: {backup_name}")
    return backup_name

def restore_backup_by_name(current_user, backup_name):
    """Restore zip-backup, alleen voor System Admin via restore-code."""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        print("Backup niet gevonden!")
        return False
    # Verwijder bestaande .db bestanden
    for file in os.listdir(_OUTPUT_DIR):
        if file.endswith('.db'):
            os.remove(os.path.join(_OUTPUT_DIR, file))
    shutil.unpack_archive(backup_path, _OUTPUT_DIR, 'zip')
    log_activity(current_user, f"Backup gerestored: {backup_name}", suspicious=False)
    print(f"Backup '{backup_name}' succesvol hersteld.")
    return True

# === Restore-code management ===
def generate_restore_code_db(target_system_admin, backup_name):
    """Genereert een restore-code, gekoppeld aan een System Admin en een specifieke backup."""
    code = str(uuid.uuid4())
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    with open(RESTORE_CODES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{code}|{target_system_admin}|{backup_name}|unused\n")
    log_activity("super_admin", f"Restore-code gegenereerd voor {target_system_admin} backup: {backup_name}", suspicious=False)
    print(f"Restore-code voor {target_system_admin}: {code}")
    return code

def use_restore_code_db(current_username, code):
    """
    Valideert een restore-code, koppelt aan de juiste System Admin & backup,
    markeert de code als gebruikt. Returnt (True, backup_name) bij succes, anders (False, None).
    """
    lines = []
    found = False
    backup_name = None
    if not os.path.exists(RESTORE_CODES_FILE):
        return False, None
    with open(RESTORE_CODES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RESTORE_CODES_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            code_line, sysadmin, backup, used = line.strip().split("|")
            if code_line == code and sysadmin == current_username and used == "unused":
                found = True
                backup_name = backup
                f.write(f"{code}|{sysadmin}|{backup}|used\n")
            else:
                f.write(line)
    return found, backup_name

def revoke_restore_code_db(code):
    if not os.path.exists(RESTORE_CODES_FILE):
        print("Restore-codes-bestand niet gevonden!")
        return
    lines = []
    with open(RESTORE_CODES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RESTORE_CODES_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            code_line, sysadmin, backup, used = line.strip().split("|")
            if code_line == code and used == "unused":
                f.write(f"{code}|{sysadmin}|{backup}|revoked\n")
            else:
                f.write(line)
    print(f"Restore-code '{code}' ingetrokken.")
    log_activity("super_admin", f"Restore-code revoked: {code}", suspicious=True)

# === Operationele wrappers voor menu (met rol-check!) ===

def make_backup(current_user):
    if current_user["role"] not in ["super_admin", "system_admin"]:
        print("Permission denied: Alleen Super Admin/System Admin mag backups maken!")
        return
    backup_name = create_backup()
    print(f"Backup gemaakt: {backup_name}")

def generate_restore_code(current_user):
    if current_user["role"] != "super_admin":
        print("Permission denied: Alleen Super Admin mag restore-codes genereren!")
        return
    sysadmin = input("Voor welke System Admin? Username: ").strip()
    backup_name = input("Welke backup (volledige bestandsnaam)? ").strip()
    generate_restore_code_db(sysadmin, backup_name)

def restore_backup(current_user):
    if current_user["role"] != "system_admin":
        print("Alleen System Admin mag een restore uitvoeren!")
        return
    code = input("Voer restore-code in: ").strip()
    ok, backup_name = use_restore_code_db(current_user["username"], code)
    if not ok:
        log_activity(current_user["username"], f"Restore attempt FAILED met code {code}", suspicious=True)
        print("Restore-code ongeldig of niet voor deze gebruiker!")
        return
    restore_backup_by_name(current_user["username"], backup_name)

def revoke_restore_code(current_user):
    if current_user["role"] != "super_admin":
        print("Alleen Super Admin mag restore-codes intrekken!")
        return
    code = input("Welke restore-code intrekken? ").strip()
    revoke_restore_code_db(code)

# list_users()
add_traveller()
# add_scooter()