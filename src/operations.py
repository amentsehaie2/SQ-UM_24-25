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
from logger import log_activity, print_logs

# Use the same DB path logic as database.py
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")
DATABASE_NAME = os.path.join(_OUTPUT_DIR, "urban_mobility.db")
BACKUP_DIR = os.path.join(_PROJECT_ROOT, "backup")
RESTORE_CODE_FILE = os.path.join(_OUTPUT_DIR, "restore_code.txt")

strike_count = 0

def get_db_connection():
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    return sqlite3.connect(DATABASE_NAME)

# === Traveller Operations ===
def add_traveller(current_user):
    conn = get_db_connection()
    print("Enter traveller details:\n")

    while strike_count < 4:
        first_name = input("First name: ")
        if validate_fname(first_name):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid first name", suspicious=True)   
        print("Invalid first name. Please try again.")

    while strike_count < 4:
        last_name = input("Last name: ")
        if validate_lname(last_name):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid last name", suspicious=True)
        print("Invalid last name. Please try again.")

    while strike_count < 4:
        birth_date = input("Birth date (YYYY-MM-DD): ")
        if validate_birth_date(birth_date):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid birth date", suspicious=True)
        print("Invalid birth date. Please try again.")

    while strike_count < 4:
        gender = input("Gender: ")
        if validate_gender(gender):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid gender", suspicious=True)
        print("Invalid gender. Please try again.")

    while strike_count < 4:
        street_name = input("Street name: ")
        if validate_street_name(street_name):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid street name", suspicious=True)
        print("Invalid street name. Please try again.")

    while strike_count < 4:
        house_number = input("House number: ")
        if validate_house_number(house_number):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid house number", suspicious=True)
        print("Invalid house number. Please try again.")

    while strike_count < 4:
        zip_code = input("Zip code: ")
        if validate_zip(zip_code):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid zip code", suspicious=True)
        print("Invalid zip code. Please try again.")

    while strike_count < 4:
        city = input("City: ")
        if validate_city(city):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid city", suspicious=True)
        print("Invalid city. Please try again.")

    while strike_count < 4:
        email = input("Email: ")
        if validate_email(email):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid email", suspicious=True)
        print("Invalid email. Please try again.")

    while strike_count < 4:
        mobile_phone = input("Mobile phone (8 digits): ")
        if validate_phone(mobile_phone):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid mobile phone number", suspicious=True)
        print("Invalid mobile phone number. Please try again.")

    while strike_count < 4:
        license_number = input("License number (XXDDDDDDD or XDDDDDDDD): ")
        if validate_license_number(license_number):
            break
        strike_count += 1
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid license number", suspicious=True)
        print("Invalid license number. Please try again.")

    if strike_count >= 4:
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Too many incorrect inputs", suspicious=True)
        print("Too many incorrect inputs. Please try again later.")
        return None
    
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

        if cursor.rowcount > 0:
            log_activity(decrypt_data(current_user["username"]), "Added a new traveller", "Success", suspicious=False)
            print("Traveller added.")
            return True
    except sqlite3.IntegrityError:
        print(f"Error: Traveller with email '{email}' might already exist or other integrity constraint failed.")
        return False
    finally:
        conn.close() 

def search_travellers(current_user):
    """
    Prompt the user for a search key and display matching travellers.
    Search is case-insensitive and matches substrings in:
    traveller_id, first_name, last_name, zip_code, mobile_phone, email, city.
    """
    key = input("Enter search key for travellers: ").strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT traveller_id, first_name, last_name, zip_code, mobile_phone, email, city
            FROM travellers
        """)
        results = []
        for row in cursor.fetchall():
            traveller_id = str(row[0])
            decrypted_first = decrypt_data(row[1])
            decrypted_last = decrypt_data(row[2])
            decrypted_zip = decrypt_data(row[3])
            decrypted_phone = decrypt_data(row[4])
            decrypted_email = decrypt_data(row[5])
            decrypted_city = decrypt_data(row[6])
            if (
                key in traveller_id.lower()
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
                log_activity(current_user["username"], "Searched for travellers", "Success", suspicious=False)
        else:
            print("No matching travellers found.")
            log_activity(current_user["username"], "Searched for travellers", "Success", suspicious=False)
        return results
    except sqlite3.Error as e:
        print(f"Database error occurred: {str(e)}")
        log_activity(current_user["username"], "Searched for travellers", "Database error", suspicious=True)
        return None
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update traveller - unexpected error", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        return False

def update_traveller(current_user):
    try:
        traveller_id = int(input("Enter the ID of the traveller you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update traveller - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    

    try:
        cursor.execute("SELECT 1 FROM travellers WHERE traveller_id=?", (traveller_id,))
        if not cursor.fetchone():
            print("Traveller ID does not exist.")
            log_activity(current_user["username"], "Failed to update traveller - traveller ID does not exist", suspicious=True)
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
                    log_activity(current_user["username"], "Failed to update traveller - invalid value for field", suspicious=True)
                    conn.close()
                    return False
        if not updates:
            print("No valid fields to update.")
            log_activity(current_user["username"], "Failed to update traveller - no valid fields to update", suspicious=True)
            conn.close()
            return False

        sql = f"UPDATE travellers SET {', '.join(updates)} WHERE traveller_id=?"
        values.append(traveller_id)
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount == 0:
            print("Traveller ID does not exist.")
            log_activity(current_user["username"], "Failed to update traveller - traveller ID does not exist", suspicious=True)
            conn.close()
            return False
        if cursor.rowcount > 0:
            print("Traveller updated.")
            log_activity(current_user["username"], "Updated traveller", "Success", suspicious=False)
            conn.close()
            return False
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update traveller - database error for ID {traveller_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
        return False
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update traveller - unexpected error for ID {traveller_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        return False
    finally:
        conn.close()
    

def delete_traveller(current_user):

    while strike_count < 4:
        try:
            traveller_id = int(input("Enter the ID of the traveller you want to delete: "))
            break
        except ValueError:
            strike_count += 1
            log_activity(current_user["username"], f"Strike count: {strike_count}", "Invalid ID format", suspicious=True)
            print("Invalid ID format. Please enter a number.")  
    if strike_count == 4:
        print("You have reached the maximum number of strikes. Please try again later.")
        log_activity(current_user["username"], f"Strike count: {strike_count}", "Maximum number of strikes reached", suspicious=True)
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM travellers WHERE traveller_id=?", (traveller_id,))
        if not cursor.fetchone():
            print("Traveller ID does not exist.")
            conn.close()
            return False

        confirm = input("Are you sure you want to delete this traveller? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Deletion cancelled.")
            conn.close()
            return False
        if confirm == "yes":
            cursor.execute("DELETE FROM travellers WHERE traveller_id=?", (traveller_id,))
            conn.commit()

            if cursor.rowcount == 0:
                print("Traveller ID does not exist.")
                log_activity(current_user["username"], "Failed to delete traveller - traveller ID does not exist", suspicious=True)
                conn.close()
                return False

            if cursor.rowcount > 0:
                print("Traveller deleted.")
                log_activity(current_user["username"], "Deleted traveller", "Success", suspicious=False)
                conn.close()
                return True
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete traveller - database error for ID {traveller_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
        return False
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete traveller - unexpected error for ID {traveller_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        return False


# === Scooter Operations ===
def add_scooter(current_user):
    conn = get_db_connection()
    print("Enter scooter details:")
    username = current_user["username"] if current_user and "username" in current_user else "unknown"

    def get_valid_input(prompt_text, validate_func, log_field, cast_func=None):
        strikes = 0
        while strikes < 3:
            value = input(prompt_text)
            try:
                if cast_func:
                    value_cast = cast_func(value)
                else:
                    value_cast = value
                if validate_func(value_cast):
                    return value_cast
            except Exception as e:
                print(f"Validation error: {e}")
            print(f"Invalid {log_field.replace('_', ' ')}. Please try again.")
            log_activity(username, "add_scooter", f"Invalid {log_field}", suspicious=True)
            strikes += 1
        print("Too many strikes. Returning to previous menu.")
        log_activity(username, "add_scooter", f"Too many strikes for {log_field}", suspicious=True)
        return None

    brand = get_valid_input("Brand: ", validate_brand, "brand")
    if brand is None:
        return
    model = get_valid_input("Model: ", validate_model, "model")
    if model is None:
        return
    serial_number = get_valid_input("Serial number: ", validate_serial_number, "serial number")
    if serial_number is None:
        return
    top_speed = get_valid_input("Top speed (integer): ", validate_top_speed, "top speed", int)
    if top_speed is None:
        return
    battery_capacity = get_valid_input("Battery capacity (integer): ", validate_battery_capacity, "battery capacity", int)
    if battery_capacity is None:
        return
    state_of_charge = get_valid_input("State of charge (0-100): ", validate_SoC, "state of charge", int)
    if state_of_charge is None:
        return
    target_range = get_valid_input("Target range (integer): ", validate_target_range, "target range", int)
    if target_range is None:
        return
    location = get_valid_input("Location (latitude,longitude): ", validate_location, "location")
    if location is None:
        return
    out_of_service_input = get_valid_input("Out of service (True/False): ", lambda x: x.lower() in {"true", "false"}, "out of service")
    if out_of_service_input is None:
        return
    out_of_service = out_of_service_input.lower() == "true"
    if not validate_OoS(out_of_service):
        print("Invalid out of service value. Returning to previous menu.")
        log_activity(username, "add_scooter", "Invalid out_of_service value", suspicious=True)
        return
    mileage = get_valid_input("Mileage (integer): ", validate_mileage, "mileage", int)
    if mileage is None:
        return
    last_service_date = get_valid_input("Last service date (YYYY-MM-DD): ", validate_last_maint, "last service date")
    if last_service_date is None:
        return

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
        log_activity(username, "add_scooter", "Scooter added successfully")
        return True
    except Exception as e:
        print(f"Error: {e}")
        log_activity(username, "add_scooter", f"Failed to add scooter: {e}", suspicious=True)
        return

def search_scooters(current_user):
    key = input("Enter search key for scooters: ").strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT scooter_id, brand, model, serial_number, top_speed, battery_capacity, state_of_charge, 
               target_range, location, out_of_service, mileage, last_service_date
        FROM scooters
    """)
    results = []
    for row in cursor.fetchall():
        scooter_id = row[0]
        decrypted_brand = decrypt_data(row[1])
        decrypted_model = decrypt_data(row[2])
        decrypted_serial = decrypt_data(row[3])
        top_speed = row[4]
        battery_capacity = row[5]
        state_of_charge = row[6]
        target_range = row[7]
        decrypted_location = decrypt_data(row[8])
        out_of_service = row[9]
        mileage = row[10]
        last_service_date = row[11]
        # Search in decrypted/encrypted fields as appropriate
        if (
            key in decrypted_brand.lower()
            or key in decrypted_model.lower()
            or key in decrypted_serial.lower()
            or key in str(top_speed).lower()
            or key in str(battery_capacity).lower()
            or key in str(state_of_charge).lower()
            or key in str(target_range).lower()
            or key in decrypted_location.lower()
            or key in str(out_of_service).lower()
            or key in str(mileage).lower()
            or (last_service_date and key in str(last_service_date).lower())
        ):
            results.append((
                scooter_id, decrypted_brand, decrypted_model, decrypted_serial, top_speed,
                battery_capacity, state_of_charge, target_range, decrypted_location,
                out_of_service, mileage, last_service_date
            ))
    conn.close()
    if results:
        print("Matching scooters:")
        for r in results:
            print(
                f"ID: {r[0]}, Brand: {r[1]}, Model: {r[2]}, Serial: {r[3]}, Top Speed: {r[4]}, "
                f"Battery: {r[5]}, SoC: {r[6]}, Range: {r[7]}, Location: {r[8]}, "
                f"Out of Service: {r[9]}, Mileage: {r[10]}, Last Service: {r[11]}"
            )
            log_activity(current_user["username"], "search_scooters", f"Scooter ID: {r[0]}")
    else:
        print("No matching scooters found.")
        log_activity(current_user["username"], "search_scooters", "No matching scooters found", suspicious=True)
    return results
    
def update_scooter(current_user):
    try:
        scooter_id = int(input("Enter the ID of the scooter you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update scooter - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT 1 FROM scooters WHERE scooter_id=?", (scooter_id,))
        if not cursor.fetchone():
            print("Scooter ID does not exist.")
            log_activity(current_user["username"], "Failed to update scooter - scooter ID does not exist", suspicious=True)
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
                        log_activity(current_user["username"], f"Failed to update scooter - invalid value for {field}", suspicious=True)
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
    
    except sqlite3.Error as e:
        print(f"Database error occurred: {str(e)}")
        log_activity(current_user["username"], "Failed to update scooter - database error", f"Error: {str(e)}", suspicious=True)
        return False
    except Exception as e:
        log_activity(current_user["username"], "Failed to update scooter - unexpected error", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        return False

def update_scooter_by_engineer(current_user):
    scooter_id = input("Enter the Scooter ID to update: ").strip()
    if not scooter_id.isdigit():
        print("Invalid Scooter ID format.")
        log_activity(current_user["username"], "Failed to update scooter by engineer - invalid ID format", suspicious=True)
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM scooters WHERE scooter_id=?", (scooter_id,))
    if not cursor.fetchone():
        print("Scooter ID does not exist.")
        log_activity(current_user["username"], "Failed to update scooter by engineer - scooter ID does not exist", suspicious=True)
        conn.close()
        return False

    print("Leave fields blank to skip updating them.")
    allowed_fields = {
        "state_of_charge": (validate_SoC, False),
        "out_of_service": (validate_OoS, False),
        "mileage": (validate_mileage, False),
        "last_service_date": (validate_last_maint, False)
    }
    updates = []
    values = []

    for field, (validator, should_encrypt) in allowed_fields.items():
        value = input(f"{field.replace('_', ' ').capitalize()} (leave blank to skip): ").strip()
        if value:
            if field in {"state_of_charge", "mileage"}:
                try:
                    value = int(value)
                except ValueError:
                    print(f"Invalid value for {field}. Must be an integer.")
                    log_activity(current_user["username"], f"Failed to update scooter by engineer - invalid value for {field}", suspicious=True)
                    conn.close()
                    return False
            if field == "out_of_service":
                if value.lower() in {"true", "false"}:
                    value = value.lower() == "true"
                else:
                    print("Invalid value for out_of_service. Must be True or False.")
                    log_activity(current_user["username"], "Failed to update scooter by engineer - invalid value for out_of_service", suspicious=True)  
                    conn.close()
                    return False
            if validator(value):
                processed_value = encrypt_data(value) if should_encrypt else value
                updates.append(f"{field}=?")
                values.append(processed_value)
            else:
                print(f"Invalid value for {field}. Update cancelled.")
                log_activity(current_user["username"], f"Failed to update scooter by engineer - invalid value for {field}", suspicious=True)
                conn.close()
                return False

    if not updates:
        print("No valid fields to update.")
        log_activity(current_user["username"], "Failed to update scooter by engineer - no valid fields to update", suspicious=True)
        conn.close()
        return False

    sql = f"UPDATE scooters SET {', '.join(updates)} WHERE scooter_id=?"
    values.append(scooter_id)
    cursor.execute(sql, tuple(values))
    conn.commit()
    if cursor.rowcount == 0:
        print("Scooter ID does not exist.")
        log_activity(current_user["username"], "Failed to update scooter by engineer - scooter ID does not exist", suspicious=True)
        conn.close()
        return False
    if cursor.rowcount > 0:
        print("Scooter updated.")
        log_activity(current_user["username"], "Successfully updated scooter by engineer", f"Scooter ID: {scooter_id}", suspicious=False)
        conn.close()
        return True


    while strike_count < 4:
        try:
            scooter_id = int(input("Enter the ID of the scooter you want to delete: "))
            break
        except ValueError:
            strike_count += 1
            log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Invalid ID format", suspicious=True)
            print("Invalid ID format. Please enter a number.")  
    if strike_count == 4:
        print("You have reached the maximum number of strikes. Please try again later.")
        log_activity(decrypt_data(current_user["username"]), f"Strike count: {strike_count}", "Maximum number of strikes reached", suspicious=True)
        return False

def delete_scooter(current_user):
    conn = get_db_connection()
    username = current_user["username"] if current_user and "username" in current_user else "unknown"

    strikes = 0
    while strikes < 4:
        scooter_id = input("Enter the Scooter ID to delete: ")
        try:
            scooter_id_int = int(scooter_id)
            cursor = conn.cursor()
            cursor.execute("SELECT scooter_id FROM scooters WHERE scooter_id=?", (scooter_id_int,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM scooters WHERE scooter_id=?", (scooter_id_int,))
                conn.commit()
                if cursor.rowcount == 0:
                    print("Scooter ID not found. Please try again.")
                    log_activity(username, "delete_scooter", f"Scooter ID {scooter_id} not found", suspicious=True)
                    conn.close()
                    strikes += 1
                    continue    
                if cursor.rowcount > 0:
                    print("Scooter deleted.")
                    log_activity(username, "delete_scooter", f"Scooter ID {scooter_id_int} deleted successfully")
                    conn.close()
                    return True
            else:
                print("Scooter ID not found. Please try again.")
                log_activity(username, "delete_scooter", f"Scooter ID {scooter_id} not found", suspicious=True)
                strikes += 1
        except ValueError:
            print("Invalid input. Scooter ID must be an integer.")
            log_activity(username, "delete_scooter", "Invalid scooter ID input (not integer)", suspicious=True)
            strikes += 1
        except Exception as e:
            print(f"Error: {e}")
            log_activity(username, "delete_scooter", f"Error while deleting scooter: {e}", suspicious=True)
            strikes += 1

        if strikes >= 4:
            print("You have reached the maximum number of strikes. Please try again later.")
            log_activity(username, "delete_scooter", "Maximum number of strikes reached", suspicious=True)
            conn.close()
            return False

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
def add_service_engineer(current_user):# WERKT VOLLEDIG
    """Adds a new service engineer to the database."""
    username = input("\nUsername: ")
    if not validate_username(username):
        log_activity(current_user["username"], f"Failed to add service engineer - invalid username format: {username}", suspicious=True)
        print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
        return

    first_name = input("First Name: ")
    if not validate_fname(first_name):
        log_activity(current_user["username"], f"Failed to add service engineer - invalid first name format: {first_name}", suspicious=True)
        print("Invalid first name format. Please use 1-19 alphabetic characters.")
        return

    last_name = input("Last Name: ")
    if not validate_lname(last_name):
        log_activity(current_user["username"], f"Failed to add service engineer - invalid last name format: {last_name}", suspicious=True)
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
        log_activity(current_user["username"], f"Failed to add service engineer - username already exists: {username}")
        print("This username is already taken.")
        conn.close()
        return

    password = input("Password: ")
    if not validate_password(password):
        log_activity(current_user["username"], f"Failed to add service engineer - invalid password format: {password}", suspicious=True)
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
            log_activity(current_user["username"], f"Successfully added service engineer: {username}")
            print("Service Engineer added.")
        else:
            log_activity(current_user["username"], f"Failed to add service engineer - no rows affected: {username}", suspicious=True)
            print("Failed to add service engineer - no changes made to database.")
    except sqlite3.IntegrityError as e:
        log_activity(current_user["username"], f"Failed to add service engineer - database integrity error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"Failed to add service engineer due to database constraint: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to add service engineer - unexpected error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_service_engineer_username(current_user): # WERKT VOLLEDIG
    """Updates the username of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update service engineer username - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update service engineer username - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to update username - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        current_username_input = input(f"Enter the current username for service engineer ID {user_id}: ")
        if not validate_username(current_username_input):
            log_activity(current_user["username"], f"Failed to update service engineer username - invalid format: {current_username_input}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return

        if current_username_input != current_username:
            log_activity(current_user["username"], f"Failed to update service engineer username - incorrect current username for ID {user_id}", suspicious=True)
            print("Incorrect current username.")
            conn.close()
            return

        new_username = input("Enter the new username: ")
        if not validate_username(new_username):
            log_activity(current_user["username"], f"Failed to update service engineer username - invalid format: {new_username}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return
        if new_username == current_username:
            log_activity(current_user["username"], f"Failed to update service engineer username - new username same as current for ID {user_id}")
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
            log_activity(current_user["username"], f"Failed to update service engineer username - username already exists: {new_username}")
            print("This username is already taken.")
            conn.close()
            return

        encrypted_new_username = encrypt_data(new_username)
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated service engineer username from {current_username} to {new_username} for ID {user_id}")
            print("Username updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update service engineer username - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update username - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update service engineer username - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update service engineer username - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_service_engineer_password(current_user): # WERKT VOLLEDIG
    """Updates the password of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update service engineer password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, password, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update service engineer password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        current_password_hash = result[1]
        user_role_encrypted = result[2]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to update password - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        current_password_input = input(f"Enter the current password for service engineer ID {user_id}: ")
        if not validate_password(current_password_input):
            log_activity(current_user["username"], f"Failed to update service engineer password - invalid format: {current_password_input}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return

        if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update service engineer password - incorrect current password for ID {user_id}", suspicious=True)
            print("Incorrect current password.")
            conn.close()
            return

        new_password = input("Enter the new password: ")
        if not validate_password(new_password):
            log_activity(current_user["username"], f"Failed to update service engineer password - invalid format: {new_password}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return
        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update service engineer password - new password same as current for ID {user_id}")
            print("New password cannot be the same as the current password.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated service engineer password for user {current_username} (ID: {user_id})")
            print("Password updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update service engineer password - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update password - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update service engineer password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update service engineer password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_service_engineer(current_user):

    while strike_count < 4:
        try:
            service_engineer_id = int(input("Enter the ID of the service engineer you want to delete: "))
            break
        except ValueError:
            strike_count += 1
            log_activity(current_user["username"], f"Strike count: {strike_count}", "Invalid ID format", suspicious=True)
            print("Invalid ID format. Please enter a number.")  
    if strike_count == 4:
        print("You have reached the maximum number of strikes. Please try again later.")
        log_activity(current_user["username"], f"Strike count: {strike_count}", "Maximum number of strikes reached", suspicious=True)
        return False
def update_fname_service_engineer(current_user): # WERKT VOLLEDIG
    """Updates the first name of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update service engineer first name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update service engineer first name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to update first name - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        new_fname = input("Enter the new first name: ")
        if not validate_fname(new_fname):
            log_activity(current_user["username"], f"Failed to update service engineer first name - invalid format: {new_fname}", suspicious=True)
            print("Invalid first name format. Please use 1-19 alphabetic characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET first_name = ? WHERE id = ?", (encrypt_data(new_fname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated service engineer first name for user {current_username} (ID: {user_id})")
            print("First name updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update service engineer first name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update first name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update service engineer first name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update service engineer first name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_lname_service_engineer(current_user): # WERKT VOLLEDIG
    """Updates the last name of a service engineer."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update service engineer last name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update service engineer last name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)    

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to update last name - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        new_lname = input("Enter the new last name: ")
        if not validate_lname(new_lname):
            log_activity(current_user["username"], f"Failed to update service engineer last name - invalid format: {new_lname}", suspicious=True)
            print("Invalid last name format. Please use 1-19 alphabetic characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET last_name = ? WHERE id = ?", (encrypt_data(new_lname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated service engineer last name for user {current_username} (ID: {user_id})")
            print("Last name updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update service engineer last name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update last name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update service engineer last name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update service engineer last name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_service_engineer(current_user): # WERKT VOLLEDIG
    """Deletes a service engineer by their ID."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to delete: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to delete service engineer - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to delete service engineer - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to delete - user ID {user_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to delete service engineer with ID {user_id}? (yes/no): ")
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return False
        if confirm == "yes":
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()

            if cursor.rowcount == 0:
                print("Service Engineer ID does not exist.")
                log_activity(current_user["username"], "Failed to delete service engineer - service engineer ID does not exist", suspicious=True)
                conn.close()
                return False

            if cursor.rowcount > 0:
                print("Service engineer deleted.")
                log_activity(current_user["username"], "Deleted service engineer", "Success", suspicious=False)
                conn.close()
                return True
            else:
                log_activity(current_user["username"], f"Failed to delete service engineer - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to delete service engineer - no changes made to database.")
        elif confirmation.lower() != "yes":
            log_activity(current_user["username"], f"Service engineer deletion cancelled for user {current_username} (ID: {user_id})")
            print("Deletion cancelled.")
            conn.close()
            return

    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete service engineer - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete service engineer - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()
    
def reset_service_engineer_password(current_user): # WERKT VOLLEDIG
    """Resets the password of a service engineer with a temporary password."""
    try:
        user_id = int(input("Enter the ID of the service engineer you want to reset password for: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to reset service engineer password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to reset service engineer password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to reset password - user ID {user_id} is not a service engineer", suspicious=True)
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
                log_activity(current_user["username"], f"Successfully reset service engineer password for user {current_username} (ID: {user_id})")
                print(f"Password reset successfully for service engineer '{current_username}'.")
                print(f"Temporary password: {temp_password}")
                print("Please share this password securely and ask the user to change it immediately.")
            else:
                log_activity(current_user["username"], f"Failed to reset service engineer password - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to reset password - no changes made to database.")
        
        elif confirmation.lower() != "yes":
            log_activity(current_user["username"], f"Service engineer password reset cancelled for user {current_username} (ID: {user_id})")
            print("Password reset cancelled.")
            conn.close()
            return
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to reset service engineer password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to reset service engineer password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()




# === System Admin Functions === 
def add_system_admin(current_user): # WERKT VOLLEDIG
    """Adds a new system administrator to the database."""
    username = input("Username: ")
    if not validate_username(username):
        log_activity(current_user["username"], f"Failed to add system admin - invalid username format: {username}", suspicious=True)
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
        log_activity(current_user["username"], f"Failed to add system admin - username already exists: {username}")
        print("This username is already taken.")
        conn.close()
        return


    first_name = input("First Name: ")
    if not validate_fname(first_name):
        log_activity(current_user["username"], f"Failed to add system admin - invalid first name format: {first_name}", suspicious=True)
        print("Invalid first name format. Please use 1-19 alphabetic characters.")
        return
            
    last_name = input("Last Name: ")
    if not validate_lname(last_name):
        log_activity(current_user["username"], f"Failed to add system admin - invalid last name format: {last_name}", suspicious=True)
        print("Invalid last name format. Please use 1-19 alphabetic characters.")
        return
    
    password = input("Password: ")
    if not validate_password(password):
        log_activity(current_user["username"], f"Failed to add system admin - invalid password format: {password}", suspicious=True)
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
            log_activity(current_user["username"], f"Successfully added system admin: {username}")
            print("System Admin added.")
        else:
            log_activity("system", f"Failed to add system admin - no rows affected: {username}", suspicious=True)
            print("Failed to add system admin - no changes made to database.")
    except sqlite3.IntegrityError as e:
        log_activity(current_user["username"], f"Failed to add system admin - database integrity error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"Failed to add system admin due to database constraint: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to add system admin - unexpected error: {username}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_system_admin_username(current_user):
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update system admin username - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update system admin username - user ID {user_id} not found", suspicious=True)
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to update username - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        current_username_input = input(f"Enter the current username for system administrator ID {user_id}: ")
        if not validate_username(current_username_input):
            log_activity(current_user["username"], f"Failed to update system admin username - invalid format: {current_username_input}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return

        if current_username_input != current_username:
            log_activity(current_user["username"], f"Failed to update system admin username - incorrect current username for ID {user_id}", suspicious=True)
            print("Incorrect current username.")
            conn.close()
            return

        new_username = input("Enter the new username: ")
        if not validate_username(new_username):
            log_activity(current_user["username"], f"Failed to update system admin username - invalid format: {new_username}", suspicious=True)
            print("Invalid username format. Please use 8-10 alphanumeric characters or underscores.")
            conn.close()
            return
        
        if new_username == current_username:
            log_activity(current_user["username"], f"Failed to update system admin username - new username same as current for ID {user_id}")
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
            log_activity(current_user["username"], f"Failed to update system admin username - username already exists: {new_username}")
            print("This username is already taken.")
            conn.close()
            return

        encrypted_new_username = encrypt_data(new_username)
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypted_new_username, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated system admin username from {current_username} to {new_username} for ID {user_id}")
            print("Username updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update system admin username - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update username - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update system admin username - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update system admin username - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_system_admin_password(current_user):
    """Updates the password of a system administrator."""
    username = input("Username: ")
    if not validate_username(username):
        log_activity(current_user["username"], f"Failed to update system admin password - invalid username format: {username}", suspicious=True)
        print("Invalid username format.")
        return

    old_password = input("Current Password: ")
    new_password = input("New Password: ")
    if not validate_password(new_password):
        log_activity(current_user["username"], f"Failed to update system admin password - invalid new password format for user: {username}", suspicious=True)
        print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        encrypted_username = encrypt_data(username)
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (encrypted_username,))
        result = cursor.fetchone()
        if not result:
            log_activity(current_user["username"], f"Failed to update system admin password - username '{username}' not found", suspicious=True)
            print("User with that username not found.")
            return

        user_id, current_password_hash, role_encrypted = result
        role = decrypt_data(role_encrypted)
        if role != "admin":
            log_activity(current_user["username"], f"Failed to update password - user '{username}' is not a system administrator", suspicious=True)
            print("User with that username is not a System Administrator.")
            return

        if not bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - incorrect current password for user: {username}", suspicious=True)
            print("Incorrect current password.")
            return

        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - new password same as current for user: {username}")
            print("New password cannot be the same as the current password.")
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated system admin password for user '{username}' (ID: {user_id})")
            print("Password updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update system admin password - no rows affected for user: {username}", suspicious=True)
            print("Failed to update password - no changes made to database.")
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update system admin password - database error for user '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update system admin password - unexpected error for user '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_system_admin(current_user):
    username = input("Username to delete: ")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        encrypted_username = encrypt_data(username)
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (encrypted_username,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to delete system admin - username '{username}' not found")
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
            log_activity(current_user["username"], f"Failed to delete - user '{username}' is not a system administrator", suspicious=True)
            print("User with that username is not a System Administrator.")
            conn.close()
            return

        current_password_input = input(f"Enter the current password for system administrator ID {user_id}: ")
        if not validate_password(current_password_input):
            log_activity(current_user["username"], f"Failed to update system admin password - invalid format: {current_password_input}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters or special characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return

        if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - incorrect current password for ID {user_id}", suspicious=True)
            print("Incorrect current password.")
            conn.close()
            return

        new_password = input("Enter the new password: ")
        if not validate_password(new_password):
            log_activity(current_user["username"], f"Failed to update system admin password - invalid format: {new_password}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters or special characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return
        
        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - new password same as current for ID {user_id}")
            print("New password cannot be the same as the current password.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully deleted system administrator {current_username} (ID: {user_id})")
            print("System administrator deleted successfully.")
        else:
            log_activity(current_user["username"], f"Failed to delete system admin - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to delete system admin - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete system admin - database error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete system admin - unexpected error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_fname_system_admin(current_user): # WERKT VOLLEDIG
    """Updates the first name of a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update system admin first name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update system admin first name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to update system admin first name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_fname = input("Enter the new first name: ")
        if not validate_fname(new_fname):
            log_activity(current_user["username"], f"Failed to update system admin first name - invalid format: {new_fname}", suspicious=True)
            print("Invalid first name format. Please use 2-30 alphanumeric characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET first_name = ? WHERE id = ?", (encrypt_data(new_fname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated system admin first name for user {current_username} (ID: {user_id})")
            print("First name updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update system admin first name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update first name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update system admin first name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update system admin first name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def update_lname_system_admin(current_user): # WERKT VOLLEDIG
    """Updates the last name of a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update system admin last name - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update system admin last name - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to update system admin last name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_lname = input("Enter the new last name: ")
        if not validate_lname(new_lname):
            log_activity(current_user["username"], f"Failed to update system admin last name - invalid format: {new_lname}", suspicious=True)
            print("Invalid last name format. Please use 2-30 alphanumeric characters.")
            conn.close()
            return

        cursor.execute("UPDATE users SET last_name = ? WHERE id = ?", (encrypt_data(new_lname), user_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated system admin last name for user {current_username} (ID: {user_id})")
            print("Last name updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update system admin last name - no rows affected for ID {user_id}", suspicious=True)
            print("Failed to update last name - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update system admin last name - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update system admin last name - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_system_admin(current_user): # WERKT VOLLEDIG
    """Deletes a system administrator."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to delete: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to delete system admin - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to delete system admin - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to delete - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        confirmation = input(f"Are you sure you want to delete system administrator with ID {user_id}? (yes/no): ")
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        
            if cursor.rowcount > 0:
                log_activity(current_user["username"], f"Successfully deleted system administrator {current_username} (ID: {user_id})")
                print("System administrator deleted successfully.")
            else:
                log_activity(current_user["username"], f"Failed to delete system admin - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to delete system admin - no changes made to database.")

        elif confirmation.lower() != "yes":
            log_activity(current_user["username"], f"System admin deletion cancelled for user {current_username} (ID: {user_id})")
            print("Deletion cancelled.")
            conn.close()
            return

    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete system admin - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete system admin - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def reset_system_admin_password(current_user): # WERKT VOLLEDIG
    """Resets the password of a system administrator with a temporary password."""
    try:
        user_id = int(input("Enter the ID of the system administrator you want to reset password for: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to reset system admin password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to reset system admin password - user ID {user_id} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to reset password - user ID {user_id} is not a system administrator", suspicious=True)
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
                log_activity(current_user["username"], f"Successfully reset system admin password for user {current_username} (ID: {user_id})")
                print(f"Password reset successfully for system administrator '{current_username}'.")
                print(f"Temporary password: {temp_password}")
                print("Please share this password securely and ask the user to change it immediately.")
            else:
                log_activity(current_user["username"], f"Failed to reset system admin password - no rows affected for ID {user_id}", suspicious=True)
                print("Failed to reset password - no changes made to database.")

        if confirmation.lower() != "yes":
            log_activity(current_user["username"], f"System admin password reset cancelled for user {current_username} (ID: {user_id})")
            print("Password reset cancelled.")
            conn.close()
            return
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to reset system admin password - database error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to reset system admin password - unexpected error for ID {user_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

# === Backup Functions ===
def make_backup(current_user):
    """Makes a backup of the database."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"urban_mobility_backup_{timestamp}.zip"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.make_archive(backup_path.replace(".zip", ""), 'zip', _OUTPUT_DIR)
    if os.path.exists(backup_path):
        log_activity(current_user["username"], f"Backup created: {backup_name}", suspicious=False)
        print(f"Backup created: {backup_name}")
        return backup_name
    else:
        log_activity(current_user["username"], f"Backup FAILED: {backup_name}", suspicious=True)
        print(f"Backup FAILED: {backup_name}")
        return None

def restore_backup_by_name(current_user, backup_name):
    """Restore zip-backup, only system admins can do this, through a code."""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        print("Backup niet gevonden!")
        log_activity(current_user, f"Backup FAILED: {backup_name}", suspicious=True)
        return False
    # Verwijder bestaande .db bestanden
    for file in os.listdir(_OUTPUT_DIR):
        if file.endswith('.db'):
            os.remove(os.path.join(_OUTPUT_DIR, file))
    shutil.unpack_archive(backup_path, _OUTPUT_DIR, 'zip')
    if os.path.exists(backup_path):
        os.remove(backup_path)
        log_activity(current_user, f"Backup gerestored: {backup_name}", suspicious=False)
        print(f"Backup '{backup_name}' succesvol hersteld.")
        return True
    else:
        log_activity(current_user, f"Backup FAILED: {backup_name}", suspicious=True)
        print(f"Backup FAILED: {backup_name}")
        return False

# === Restore-code management ===
def generate_restore_code_db(target_system_admin, backup_name, current_user):
    """Genereert een restore-code, gekoppeld aan een System Admin en een specifieke backup."""
    code = str(uuid.uuid4())
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    with open(RESTORE_CODE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{code}|{target_system_admin}|{backup_name}|unused\n")
    log_activity("super_admin", f"Restore-code gegenereerd voor {target_system_admin}", suspicious=False)
    print(f"Restore-code voor {target_system_admin}: {code}")
    return code

def use_restore_code_db(current_username, code, current_user):
    """
    Valideert een restore-code, koppelt aan de juiste System Admin & backup,
    markeert de code als gebruikt. Returnt (True, backup_name) bij succes, anders (False, None).
    """
    lines = []
    found = False
    backup_name = None
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore-codes-bestand niet gevonden!")
        log_activity(current_username, "use_restore_code_db", "Restore-codes-bestand niet gevonden", suspicious=True)
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

def revoke_restore_code_db(code, current_user):
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore-codes-bestand niet gevonden!")
        log_activity("super_admin", "revoke_restore_code_db", "Restore-codes-bestand niet gevonden", suspicious=True)
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
    log_activity("super_admin", f"Restore-code revoked: {code}", suspicious=False)

# === Operationele wrappers voor menu (met rol-check!) ===

# def make_backup(current_user):
#     if current_user["role"] not in ["super_admin", "system_admin"]:
#         print("Permission denied: Alleen Super Admin/System Admin mag backups maken!")
#         return
#     backup_name = create_backup()
#     print(f"Backup gemaakt: {backup_name}")

# def generate_restore_code(current_user):
#     if current_user["role"] != "super_admin":
#         print("Permission denied: Alleen Super Admin mag restore-codes genereren!")
#         return
#     sysadmin = input("Voor welke System Admin? Username: ").strip()
#     backup_name = input("Welke backup (volledige bestandsnaam)? ").strip()
#     generate_restore_code_db(sysadmin, backup_name)

# def restore_backup(current_user):
#     if current_user["role"] != "system_admin":
#         print("Alleen System Admin mag een restore uitvoeren!")
#         return
#     code = input("Voer restore-code in: ").strip()
#     ok, backup_name = use_restore_code_db(current_user["username"], code)
#     if not ok:
#         log_activity(current_user["username"], f"Restore attempt FAILED met code {code}", suspicious=True)
#         print("Restore-code ongeldig of niet voor deze gebruiker!")
#         return
#     restore_backup_by_name(current_user["username"], backup_name)

# def revoke_restore_code(current_user):
#     if current_user["role"] != "super_admin":
#         print("Alleen Super Admin mag restore-codes intrekken!")
#         return
#     code = input("Welke restore-code intrekken? ").strip()
#     revoke_restore_code_db(code)

if __name__ == "__main__":

    ###TRAVELLER OPERATIONS
    # add_traveller()
    # delete_traveller()
    # update_traveller()
    # search_travellers()

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
