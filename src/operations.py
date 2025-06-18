import sqlite3
import os
import shutil
import secrets
import bcrypt
import uuid
from datetime import datetime
from validation import (
    validate_password, validate_zip, validate_phone, validate_fname, validate_lname, validate_house_number,
    validate_email, validate_username, validate_street_name, validate_license_number, validate_city,
    validate_birth_date, validate_gender, validate_brand, validate_model, validate_serial_number,
    validate_target_range, validate_top_speed, validate_battery_capacity, validate_SoC, validate_location,
    validate_OoS, validate_mileage, validate_last_maint
)
from encryption import encrypt_data, decrypt_data
import bcrypt
from logger import log_activity, print_logs

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

def search_travellers():
    """
    Prompt the user for a search key and display matching travellers.
    Search is case-insensitive and matches substrings in:
    customer_id, first_name, last_name, zip_code, mobile_phone, email, city.
    """
    key = input("Enter search key for travellers: ").strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT customer_id, first_name, last_name, zip_code, mobile_phone, email, city
        FROM travellers
    """)
    results = []
    for row in cursor.fetchall():
        customer_id = str(row[0])
        decrypted_first = decrypt_data(row[1])
        decrypted_last = decrypt_data(row[2])
        decrypted_zip = decrypt_data(row[3])
        decrypted_phone = decrypt_data(row[4])
        decrypted_email = decrypt_data(row[5])
        decrypted_city = decrypt_data(row[6])
        if (
            key in customer_id.lower()
            or key in decrypted_first.lower()
            or key in decrypted_last.lower()
            or key in decrypted_zip.lower()
            or key in decrypted_phone.lower()
            or key in decrypted_email.lower()
            or key in decrypted_city.lower()
        ):
            results.append((
                row[0], decrypted_first, decrypted_last, decrypted_zip, decrypted_phone, decrypted_email, decrypted_city
            ))
    conn.close()
    if results:
        print("Matching travellers:")
        for r in results:
            print(f"ID: {r[0]}, Name: {r[1]} {r[2]}, Zip: {r[3]}, Phone: {r[4]}, Email: {r[5]}, City: {r[6]}")
    else:
        print("No matching travellers found.")
    return results

def update_traveller():
    customer_id = input("Enter the Traveller ID to update: ").strip()
    
    if not customer_id.isdigit():
        print("Invalid Traveller ID format.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM travellers WHERE customer_id=?", (customer_id,))
    if not cursor.fetchone():
        print("Traveller ID does not exist.")
        conn.close()
        return False

    print("Leave fields blank to skip updating them.")
    allowed_fields = {
        "first_name": (validate_fname, True),
        "last_name": (validate_lname, True),
        "birth_date": (validate_birth_date, True),
        "gender": (validate_gender, True),
        "street_name": (validate_street_name, True),
        "house_number": (validate_house_number, False),
        "zip_code": (validate_zip, False),
        "city": (validate_city, False),
        "email": (validate_email, True),
        "mobile_phone": (validate_phone, True),
        "license_number": (validate_license_number, True)
    }

    updates = []
    values = []

    for field, (validator, should_encrypt) in allowed_fields.items():
        value = input(f"{field.replace('_', ' ').capitalize()} (leave blank to skip): ").strip()
        if value:
            if validator(value):
                processed_value = encrypt_data(value) if should_encrypt else value
                updates.append(f"{field}=?")
                values.append(processed_value)
            else:
                print(f"Invalid value for {field}. Update cancelled.")
                conn.close()
                return False
    if not updates:
        print("No valid fields to update.")
        conn.close()
        return False

    sql = f"UPDATE travellers SET {', '.join(updates)} WHERE customer_id=?"
    values.append(customer_id)
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()
    print("Traveller updated.")
    return True


def delete_traveller():
    customer_id = input("Enter the Traveller ID to delete: ").strip()
    
    if not customer_id.isdigit():
        print("Invalid Traveller ID format.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM travellers WHERE customer_id=?", (customer_id,))
    if not cursor.fetchone():
        print("Traveller ID does not exist.")
        conn.close()
        return False

    confirm = input("Are you sure you want to delete this traveller? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.")
        conn.close()
        return False

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

def search_scooters():
    key = input("Enter search key for scooters: ").strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scooter_id, brand, model, serial_number, location FROM scooters")
    results = []
    for row in cursor.fetchall():
        decrypted_brand = decrypt_data(row[1])
        decrypted_model = decrypt_data(row[2])
        decrypted_serial = decrypt_data(row[3])
        decrypted_location = decrypt_data(row[4])
        if (key in decrypted_brand.lower() or key in decrypted_model.lower() or key in decrypted_serial.lower()):
            results.append((row[0], decrypted_brand, decrypted_model, decrypted_serial, decrypted_location))
    conn.close()
    if results:
        print("Matching scooters:")
        for r in results:
            print(f"ID: {r[0]}, Brand: {r[1]}, Model: {r[2]}, Serial: {r[3]}, Location: {r[4]}")
    else:
        print("No matching scooters found.")
    return results

def update_scooter():
    scooter_id = input("Enter the Scooter ID to update: ").strip()
    if not scooter_id.isdigit():
        print("Invalid Scooter ID format.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM scooters WHERE scooter_id=?", (scooter_id,))
    if not cursor.fetchone():
        print("Scooter ID does not exist.")
        conn.close()
        return False

    print("Leave fields blank to skip updating them.")
    allowed_fields = {
        "brand": (validate_brand, True),
        "model": (validate_model, True),
        "serial_number": (validate_serial_number, True),
        "top_speed": (validate_top_speed, False),
        "battery_capacity": (validate_battery_capacity, False),
        "state_of_charge": (validate_SoC, False),
        "target_range": (validate_target_range, False),
        "location": (validate_location, True),
        "out_of_service": (validate_OoS, False),
        "mileage": (validate_mileage, False),
        "last_service_date": (validate_last_maint, False)
    }
    updates = []
    values = []

    for field, (validator, should_encrypt) in allowed_fields.items():
        value = input(f"{field.replace('_', ' ').capitalize()} (leave blank to skip): ").strip()
        if value:
            # Convert to correct type for numeric fields
            if field in {"top_speed", "battery_capacity", "state_of_charge", "target_range", "mileage"}:
                try:
                    value = int(value)
                except ValueError:
                    print(f"Invalid value for {field}. Must be an integer.")
                    conn.close()
                    return False
            if field == "out_of_service":
                if value.lower() in {"true", "false"}:
                    value = value.lower() == "true"
                else:
                    print("Invalid value for out_of_service. Must be True or False.")
                    conn.close()
                    return False
            if validator(value):
                processed_value = encrypt_data(value) if should_encrypt else value
                updates.append(f"{field}=?")
                values.append(processed_value)
            else:
                print(f"Invalid value for {field}. Update cancelled.")
                conn.close()
                return False

    if not updates:
        print("No valid fields to update.")
        conn.close()
        return False

    sql = f"UPDATE scooters SET {', '.join(updates)} WHERE scooter_id=?"
    values.append(scooter_id)
    cursor.execute(sql, tuple(values))
    conn.commit()
    conn.close()
    print("Scooter updated.")
    return True

def delete_scooter():
    scooter_id = input("Enter the Scooter ID to delete: ")
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
    cursor.execute("SELECT id, username, first_name, last_name, password, role, registration_date FROM users")
    users = cursor.fetchall()
    print("\nUsers:")
    for user in users:
        try:
            username = decrypt_data(user[1]) if user[1] else "N/A"
            first_name = decrypt_data(user[2]) if user[2] else "N/A"
            last_name = decrypt_data(user[3]) if user[3] else "N/A"
            role = decrypt_data(user[5]) if user[5] else "N/A"
            
            print(f"ID: {user[0]}  |  Username: {username}  |  First Name: {first_name}  |  Last Name: {last_name}  |  Password: [Hidden]  |  Role: {role}  |  Registration Date: {user[6]}")
        except Exception as e:
            print(f"ID: {user[0]}  |  Error decrypting user data: {str(e)}")
    conn.close()


# === Service Engineer Functions === 
def add_service_engineer():# WERKT VOLLEDIG
    """Adds a new service engineer to the database."""
    username = input("\nUsername: ")
    if not validate_username(username):
        log_activity("system", f"Failed to add service engineer - invalid username format: {username}", suspicious=True)
        print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
        return

    first_name = input("First Name: ")
    if not validate_fname(first_name):
        log_activity("system", f"Failed to add service engineer - invalid first name format: {first_name}", suspicious=True)
        print("Invalid first name format. Please use 1-19 alphabetic characters.")
        return

    last_name = input("Last Name: ")
    if not validate_lname(last_name):
        log_activity("system", f"Failed to add service engineer - invalid last name format: {last_name}", suspicious=True)
        print("Invalid last name format. Please use 1-19 alphabetic characters.")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    all_users = cursor.fetchall()
    username_exists = False
    for other_id, other_encrypted_username in all_users:
        if decrypt_data(other_encrypted_username) == username:
            username_exists = True
            break
    
    if username_exists:
        log_activity("system", f"Failed to add service engineer - username already exists: {username}")
        print("This username is already taken.")
        conn.close()
        return

    password = input("Password: ")
    if not validate_password(password):
        log_activity("system", f"Failed to add service engineer - invalid password format: {password}", suspicious=True)
        print("Invalid password format. Please use 8-20 alphanumeric characters.")
        return
    encrypted_username = encrypt_data(username)
    encrypted_role = encrypt_data("engineer")
    encrypt_fname = encrypt_data(first_name)
    encrypt_lname = encrypt_data(last_name)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, first_name, last_name, password, role, registration_date) VALUES (?, ?, ?, ?, ?, ?)",
                       (encrypted_username,encrypt_fname, encrypt_lname, hashed_password, encrypted_role, datetime.now().isoformat()))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully added service engineer: {username}")
            print("Service Engineer added.")
        else:
            log_activity("system", f"Failed to add service engineer - no rows affected: {username}", suspicious=True)
            print("Failed to add service engineer - no changes made to database.")
    except sqlite3.IntegrityError as e:
        log_activity("system", f"Failed to add service engineer - database integrity error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"Failed to add service engineer due to database constraint: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to add service engineer - unexpected error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_service_engineer_username(): # WERKT VOLLEDIG
    """Updates the username of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update service engineer username - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update service engineer username - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity("system", f"Failed to update username - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        current_username_input = input(f"Enter the current username for service engineer ID {user_id}: ")
        if not validate_username(current_username_input):
            log_activity("system", f"Failed to update service engineer username - invalid format: {current_username_input}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return

        if current_username_input != current_username:
            log_activity("system", f"Failed to update service engineer username - incorrect current username for ID {user_id}", suspicious=True)
            print("Incorrect current username.")
            conn.close()
            return

        new_username = input("Enter the new username: ")
        if not validate_username(new_username):
            log_activity("system", f"Failed to update service engineer username - invalid format: {new_username}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return
        if new_username == current_username:
            log_activity("system", f"Failed to update service engineer username - new username same as current for ID {user_id}")
            print("New username cannot be the same as the current username.")
            conn.close()
            return


        cursor.execute("SELECT id, username FROM users")
        all_users = cursor.fetchall()
        username_exists = False
        for other_id, other_encrypted_username in all_users:
            if other_id != user_id:
                if decrypt_data(other_encrypted_username) == new_username:
                    username_exists = True
                    break
        
        if username_exists:
            log_activity("system", f"Failed to update service engineer username - username already exists: {new_username}")
            print("This username is already taken.")
            conn.close()
            return

        encrypted_new_username = encrypt_data(new_username)
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated service engineer username from {current_username} to {new_username} for ID {user_id}")
            print("Username updated successfully.")
        else:
            log_activity("system", f"Failed to update service engineer username - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update username - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update service engineer username - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update service engineer username - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_service_engineer_password(): # WERKT VOLLEDIG
    """Updates the password of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update service engineer password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, password, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update service engineer password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        current_password_hash = result[1]
        user_role_encrypted = result[2]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity("system", f"Failed to update password - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        current_password_input = input(f"Enter the current password for service engineer ID {user_id}: ")
        if not validate_password(current_password_input):
            log_activity("system", f"Failed to update service engineer password - invalid format: {current_password_input}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return

        if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update service engineer password - incorrect current password for ID {user_id}", suspicious=True)
            print("Incorrect current password.")
            conn.close()
            return

        new_password = input("Enter the new password: ")
        if not validate_password(new_password):
            log_activity("system", f"Failed to update service engineer password - invalid format: {new_password}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return
        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update service engineer password - new password same as current for ID {user_id}")
            print("New password cannot be the same as the current password.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated service engineer password for user {current_username} (ID: {user_id})")
            print("Password updated successfully.")
        else:
            log_activity("system", f"Failed to update service engineer password - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update password - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update service engineer password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update service engineer password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_fname_service_engineer(): # WERKT VOLLEDIG
    """Updates the first name of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update service engineer first name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update service engineer first name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity("system", f"Failed to update first name - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        new_fname = input("Enter the new first name: ")
        if not validate_fname(new_fname):
            log_activity("system", f"Failed to update service engineer first name - invalid format: {new_fname}", suspicious=True)
            print("Invalid first name format. Please use 1-19 alphabetic characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET first_name = ? WHERE id = ?", (encrypt_data(new_fname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated service engineer first name for user {current_username} (ID: {user_id})")
            print("First name updated successfully.")
        else:
            log_activity("system", f"Failed to update service engineer first name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update first name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update service engineer first name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update service engineer first name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_lname_service_engineer(): # WERKT VOLLEDIG
    """Updates the last name of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update service engineer last name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update service engineer last name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)    

        if user_role != "engineer":
            log_activity("system", f"Failed to update last name - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        new_lname = input("Enter the new last name: ")
        if not validate_lname(new_lname):
            log_activity("system", f"Failed to update service engineer last name - invalid format: {new_lname}", suspicious=True)
            print("Invalid last name format. Please use 1-19 alphabetic characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET last_name = ? WHERE id = ?", (encrypt_data(new_lname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated service engineer last name for user {current_username} (ID: {user_id})")
            print("Last name updated successfully.")
        else:
            log_activity("system", f"Failed to update service engineer last name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update last name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update service engineer last name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update service engineer last name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_service_engineer(): # WERKT VOLLEDIG
    """Deletes a service engineer by their ID."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to delete: "))
    except ValueError:
        log_activity("system", "Failed to delete service engineer - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to delete service engineer - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity("system", f"Failed to delete - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to delete service engineer with ID {user_id}? (yes/no): ")
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                log_activity("system", f"Successfully deleted service engineer {current_username} (ID: {user_id})")
                print("Service engineer deleted successfully.")
            else:
                log_activity("system", f"Failed to delete service engineer - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to delete service engineer - no changes made to database.")
        elif confirmation.lower() != "yes":
            log_activity("system", f"Service engineer deletion cancelled for user {current_username} (ID: {user_id})")
            print("Deletion cancelled.")
            conn.close()
            return

    except sqlite3.Error as e:
        log_activity("system", f"Failed to delete service engineer - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to delete service engineer - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()
    
def reset_service_engineer_password(): # WERKT VOLLEDIG
    """Resets the password of a service engineer with a temporary password."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to reset password for: "))
    except ValueError:
        log_activity("system", "Failed to reset service engineer password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to reset service engineer password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity("system", f"Failed to reset password - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to reset the password for service engineer '{current_username}' (ID: {user_id})? (yes/no): ")
        if confirmation.lower() == "yes":
            temp_password = secrets.token_urlsafe(12)
            hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                log_activity("system", f"Successfully reset service engineer password for user {current_username} (ID: {user_id})")
                print(f"Password reset successfully for service engineer '{current_username}'.")
                print(f"Temporary password: {temp_password}")
                print("Please share this password securely and ask the user to change it immediately.")
            else:
                log_activity("system", f"Failed to reset service engineer password - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to reset password - no changes made to database.")
        
        elif confirmation.lower() != "yes":
            log_activity("system", f"Service engineer password reset cancelled for user {current_username} (ID: {user_id})")
            print("Password reset cancelled.")
            conn.close()
            return
        
    except sqlite3.Error as e:
        log_activity("system", f"Failed to reset service engineer password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to reset service engineer password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()




# === System Admin Functions === 
def add_system_admin(): # WERKT VOLLEDIG
    """Adds a new system administrator to the database."""
    username = input("Username: ")
    if not validate_username(username):
        log_activity("system", f"Failed to add system admin - invalid username format: {username}", suspicious=True)
        print("Invalid username format. Please use 8-10 alphanumeric characters.")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    all_users = cursor.fetchall()
    username_exists = False
    for other_id, other_encrypted_username in all_users:
        if decrypt_data(other_encrypted_username) == username:
            username_exists = True
            break
    
    if username_exists:
        log_activity("system", f"Failed to add system admin - username already exists: {username}")
        print("This username is already taken.")
        conn.close()
        return


    first_name = input("First Name: ")
    if not validate_fname(first_name):
        log_activity("system", f"Failed to add system admin - invalid first name format: {first_name}", suspicious=True)
        print("Invalid first name format. Please use 1-19 alphabetic characters.")
        return
            
    last_name = input("Last Name: ")
    if not validate_lname(last_name):
        log_activity("system", f"Failed to add system admin - invalid last name format: {last_name}", suspicious=True)
        print("Invalid last name format. Please use 1-19 alphabetic characters.")
        return
    
    password = input("Password: ")
    if not validate_password(password):
        log_activity("system", f"Failed to add system admin - invalid password format: {password}", suspicious=True)
        print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
        return
    encrypted_username = encrypt_data(username)
    encrypted_fname = encrypt_data(first_name)
    encrypted_lname = encrypt_data(last_name)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    encrypted_role = encrypt_data("admin")

    try:
        cursor.execute("INSERT INTO users (username, first_name, last_name, password, role, registration_date) VALUES (?, ?, ?, ?, ?, ?)",
                       (encrypted_username, encrypted_fname, encrypted_lname, hashed_password, encrypted_role, datetime.now().isoformat()))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully added system admin: {username}")
            print("System Admin added.")
        else:
            log_activity("system", f"Failed to add system admin - no rows affected: {username}", suspicious=True)
            print("Failed to add system admin - no changes made to database.")
    except sqlite3.IntegrityError as e:
        log_activity("system", f"Failed to add system admin - database integrity error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"Failed to add system admin due to database constraint: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to add system admin - unexpected error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_system_admin_username():
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update system admin username - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update system admin username - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to update username - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        current_username_input = input(f"Enter the current username for system administrator ID {user_id}: ")
        if not validate_username(current_username_input):
            log_activity("system", f"Failed to update system admin username - invalid format: {current_username_input}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return

        if current_username_input != current_username:
            log_activity("system", f"Failed to update system admin username - incorrect current username for ID {user_id}", suspicious=True)
            print("Incorrect current username.")
            conn.close()
            return

        new_username = input("Enter the new username: ")
        if not validate_username(new_username):
            log_activity("system", f"Failed to update system admin username - invalid format: {new_username}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return
        
        if new_username == current_username:
            log_activity("system", f"Failed to update system admin username - new username same as current for ID {user_id}")
            print("New username cannot be the same as the current username.")
            conn.close()
            return

        cursor.execute("SELECT id, username FROM users")
        all_users = cursor.fetchall()
        username_exists = False
        for other_id, other_encrypted_username in all_users:
            if other_id != user_id:
                if decrypt_data(other_encrypted_username) == new_username:
                    username_exists = True
                    break
        
        if username_exists:
            log_activity("system", f"Failed to update system admin username - username already exists: {new_username}")
            print("This username is already taken.")
            conn.close()
            return

        encrypted_new_username = encrypt_data(new_username)
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated system admin username from {current_username} to {new_username} for ID {user_id}")
            print("Username updated successfully.")
        else:
            log_activity("system", f"Failed to update system admin username - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update username - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update system admin username - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update system admin username - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_system_admin_password():
    """Updates the password of a system administrator."""
    username = input("Username: ")
    if not validate_username(username):
        log_activity("system", f"Failed to update system admin password - invalid username format: {username}", suspicious=True)
        print("Invalid username format.")
        return

    old_password = input("Current Password: ")
    new_password = input("New Password: ")
    if not validate_password(new_password):
        log_activity("system", f"Failed to update system admin password - invalid new password format for user: {username}", suspicious=True)
        print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        encrypted_username = encrypt_data(username)
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (encrypted_username,))
        result = cursor.fetchone()
        if not result:
            log_activity("system", f"Failed to update system admin password - username '{username}' not found", suspicious=True)
            print("User with that username not found.")
            return

        user_id, current_password_hash, role_encrypted = result
        role = decrypt_data(role_encrypted)
        if role != "admin":
            log_activity("system", f"Failed to update password - user '{username}' is not a system administrator", suspicious=True)
            print("User with that username is not a System Administrator.")
            return

        if not bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update system admin password - incorrect current password for user: {username}", suspicious=True)
            print("Incorrect current password.")
            return

        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update system admin password - new password same as current for user: {username}")
            print("New password cannot be the same as the current password.")
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated system admin password for user '{username}' (ID: {user_id})")
            print("Password updated successfully.")
        else:
            log_activity("system", f"Failed to update system admin password - no rows affected for user: {username}", suspicious=True)
            print("Failed to update password - no changes made to database.")
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update system admin password - database error for user '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update system admin password - unexpected error for user '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_system_admin():
    username = input("Username to delete: ")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        encrypted_username = encrypt_data(username)
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (encrypted_username,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to delete system admin - username '{username}' not found")
            print("User with that username not found.")
            conn.close()
            return

        user_id = result[0]
        current_username_encrypted = result[1]
        current_username = decrypt_data(current_username_encrypted)
        current_password_hash = result[2]
        user_role_encrypted = result[3]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to delete - user '{username}' is not a system administrator", suspicious=True)
            print("User with that username is not a System Administrator.")
            conn.close()
            return

        current_password_input = input(f"Enter the current password for system administrator ID {user_id}: ")
        if not validate_password(current_password_input):
            log_activity("system", f"Failed to update system admin password - invalid format: {current_password_input}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters or special characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return

        if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update system admin password - incorrect current password for ID {user_id}", suspicious=True)
            print("Incorrect current password.")
            conn.close()
            return

        new_password = input("Enter the new password: ")
        if not validate_password(new_password):
            log_activity("system", f"Failed to update system admin password - invalid format: {new_password}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters or special characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return
        
        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity("system", f"Failed to update system admin password - new password same as current for ID {user_id}")
            print("New password cannot be the same as the current password.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully deleted system administrator {current_username} (ID: {user_id})")
            print("System administrator deleted successfully.")
        else:
            log_activity("system", f"Failed to delete system admin - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to delete system admin - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to delete system admin - database error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to delete system admin - unexpected error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_fname_system_admin(): # WERKT VOLLEDIG
    """Updates the first name of a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update system admin first name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update system admin first name - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to update system admin first name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_fname = input("Enter the new first name: ")
        if not validate_fname(new_fname):
            log_activity("system", f"Failed to update system admin first name - invalid format: {new_fname}", suspicious=True)
            print("Invalid first name format. Please use 2-30 alphanumeric characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET first_name = ? WHERE id = ?", (encrypt_data(new_fname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated system admin first name for user {current_username} (ID: {user_id})")
            print("First name updated successfully.")
        else:
            log_activity("system", f"Failed to update system admin first name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update first name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update system admin first name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update system admin first name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_lname_system_admin(): # WERKT VOLLEDIG
    """Updates the last name of a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity("system", "Failed to update system admin last name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to update system admin last name - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to update system admin last name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_lname = input("Enter the new last name: ")
        if not validate_lname(new_lname):
            log_activity("system", f"Failed to update system admin last name - invalid format: {new_lname}", suspicious=True)
            print("Invalid last name format. Please use 2-30 alphanumeric characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET last_name = ? WHERE id = ?", (encrypt_data(new_lname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity("system", f"Successfully updated system admin last name for user {current_username} (ID: {user_id})")
            print("Last name updated successfully.")
        else:
            log_activity("system", f"Failed to update system admin last name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update last name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to update system admin last name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to update system admin last name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_system_admin(): # WERKT VOLLEDIG
    """Deletes a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to delete: "))
    except ValueError:
        log_activity("system", "Failed to delete system admin - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to delete system admin - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to delete - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to delete system administrator with ID {user_id}? (yes/no): ")
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        
            if cursor.rowcount > 0:
                log_activity("system", f"Successfully deleted system administrator {current_username} (ID: {user_id})")
                print("System administrator deleted successfully.")
            else:
                log_activity("system", f"Failed to delete system admin - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to delete system admin - no changes made to database.")

        elif confirmation.lower() != "yes":
            log_activity("system", f"System admin deletion cancelled for user {current_username} (ID: {user_id})")
            print("Deletion cancelled.")
            conn.close()
            return

    except sqlite3.Error as e:
        log_activity("system", f"Failed to delete system admin - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to delete system admin - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def reset_system_admin_password(): # WERKT VOLLEDIG
    """Resets the password of a system administrator with a temporary password."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to reset password for: "))
    except ValueError:
        log_activity("system", "Failed to reset system admin password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity("system", f"Failed to reset system admin password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity("system", f"Failed to reset password - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to reset the password for system administrator '{current_username}' (ID: {user_id})? (yes/no): ")
        if confirmation.lower() == "yes":
            temp_password = secrets.token_urlsafe(12)
            hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
        
            if cursor.rowcount > 0:
                log_activity("system", f"Successfully reset system admin password for user {current_username} (ID: {user_id})")
                print(f"Password reset successfully for system administrator '{current_username}'.")
                print(f"Temporary password: {temp_password}")
                print("Please share this password securely and ask the user to change it immediately.")
            else:
                log_activity("system", f"Failed to reset system admin password - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to reset password - no changes made to database.")

        if confirmation.lower() != "yes":
            log_activity("system", f"System admin password reset cancelled for user {current_username} (ID: {user_id})")
            print("Password reset cancelled.")
            conn.close()
            return
            
    except sqlite3.Error as e:
        log_activity("system", f"Failed to reset system admin password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity("system", f"Failed to reset system admin password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()



# === Backup Functions ===
def make_backup(): #jayden
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
    with open(RESTORE_CODE_FILE, "a", encoding="utf-8") as f:
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
    if not os.path.exists(RESTORE_CODE_FILE):
        return False, None
    with open(RESTORE_CODE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RESTORE_CODE_FILE, "w", encoding="utf-8") as f:
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
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore-codes-bestand niet gevonden!")
        return
    lines = []
    with open(RESTORE_CODE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RESTORE_CODE_FILE, "w", encoding="utf-8") as f:
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


    # list_users()
    print_logs()

    ###SYSTEM ADMIN FUNCTIONS
    # add_system_admin()
    # update_system_admin_username()
    # update_system_admin_password()  
    # update_fname_system_admin()
    # update_lname_system_admin() 
    # delete_system_admin()
    # reset_system_admin_password()

    
    ###SERVICE ENGINEER FUNCTIONS   
    # add_service_engineer()
    # update_service_engineer_username()
    # update_service_engineer_password()
    # update_fname_service_engineer()
    # update_lname_service_engineer()
    # delete_service_engineer()
    # reset_service_engineer_password()
