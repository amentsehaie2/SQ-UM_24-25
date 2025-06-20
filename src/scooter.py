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

def add_scooter(current_user):
    conn = get_db_connection()
    print("Enter scooter details:")
    username = current_user["username"] if current_user and "username" in current_user else "unknown"

    # Format descriptions for each field
    field_formats = {
        "brand": "Any string.",
        "model": "Non-empty string.",
        "serial_number": "10–17 uppercase letters or digits.",
        "top_speed": "In km/h (e.g., 45, 100).",
        "battery_capacity": "Positive integer (Wh).",
        "state_of_charge": "Integer between 0 and 100.",
        "target_range": "Positive integer (e.g., 15000).",
        "location": "Latitude,longitude both with exactly 5 decimal places. Example: 51.92250,4.47917",
        "out_of_service": "True or false",
        "mileage": "In kilometres",
        "last_service_date": "Date in format YYYY-MM-DD."
    }

    def get_valid_input(prompt_text, validate_func, log_field, cast_func=None, format_hint=None):
        strikes = 0
        if format_hint:
            print(f"Format: {format_hint}")
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

    brand = get_valid_input("Brand: ", validate_brand, "brand", format_hint=field_formats["brand"])
    if brand is None:
        return
    model = get_valid_input("Model: ", validate_model, "model", format_hint=field_formats["model"])
    if model is None:
        return
    serial_number = get_valid_input("Serial number: ", validate_serial_number, "serial number", format_hint=field_formats["serial_number"])
    if serial_number is None:
        return
    top_speed = get_valid_input("Top speed (integer): ", validate_top_speed, "top speed", int, field_formats["top_speed"])
    if top_speed is None:
        return
    battery_capacity = get_valid_input("Battery capacity (integer): ", validate_battery_capacity, "battery capacity", int, field_formats["battery_capacity"])
    if battery_capacity is None:
        return
    state_of_charge = get_valid_input("State of charge (0-100): ", validate_SoC, "state of charge", int, field_formats["state_of_charge"])
    if state_of_charge is None:
        return
    target_range = get_valid_input("Target range (integer): ", validate_target_range, "target range", int, field_formats["target_range"])
    if target_range is None:
        return
    location = get_valid_input("Location (latitude,longitude): ", validate_location, "location", format_hint=field_formats["location"])
    if location is None:
        return
    out_of_service_input = get_valid_input("Out of service (True/False): ", lambda x: x.lower() in {"true", "false"}, "out of service", format_hint=field_formats["out_of_service"])
    if out_of_service_input is None:
        return
    out_of_service = out_of_service_input.lower() == "true"
    if not validate_OoS(out_of_service):
        print("Invalid out of service value. Returning to previous menu.")
        log_activity(username, "add_scooter", "Invalid out_of_service value", suspicious=True)
        return
    mileage = get_valid_input("Mileage (integer): ", validate_mileage, "mileage", int, field_formats["mileage"])
    if mileage is None:
        return
    last_service_date = get_valid_input("Last service date (YYYY-MM-DD): ", validate_last_maint, "last service date", format_hint=field_formats["last_service_date"])
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
        log_activity(current_user["username"], "search_scooters", f"Scooter ID: {r[0]}", suspicious=False)
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
