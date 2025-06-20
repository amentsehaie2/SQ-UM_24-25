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

def add_traveller(current_user=None):
    conn = get_db_connection()
    print("Enter traveller details:")
    username = current_user["username"] if current_user and "username" in current_user else "unknown"

    def get_valid_input(prompt_text, validate_func, log_field):
        strikes = 0
        while strikes < 3:
            value = input(prompt_text)
            try:
                if validate_func(value):
                    return value
            except Exception as e:
                print(f"Validation error: {e}")
            print(f"Invalid {log_field.replace('_', ' ')}. Please try again.")
            log_activity(username, "add_traveller", f"Invalid {log_field}", suspicious=True)
            strikes += 1
        print("Too many strikes. Returning to previous menu.")
        log_activity(username, "add_traveller", f"Too many strikes for {log_field}", suspicious=True)
        return None
    first_name = get_valid_input("First name: ", validate_fname, "first name")
    if first_name is None:
        return
    last_name = get_valid_input("Last name: ", validate_lname, "last name")
    if last_name is None:
        return
    birth_date = get_valid_input("Birth date (YYYY-MM-DD): ", validate_birth_date, "birth date")
    if birth_date is None:
        return
    gender = get_valid_input("Gender: ", validate_gender, "gender")
    if gender is None:
        return
    street_name = get_valid_input("Street name: ", validate_street_name, "street name")
    if street_name is None:
        return
    house_number = get_valid_input("House number: ", validate_house_number, "house number")
    if house_number is None:
        return
    zip_code = get_valid_input("Zip code: ", validate_zip, "zip code")
    if zip_code is None:
        return
    city = get_valid_input("City: ", validate_city, "city")
    if city is None:
        return
    email = get_valid_input("Email: ", validate_email, "email")
    if email is None:
        return
    mobile_phone = get_valid_input("Mobile phone (8 digits): ", validate_phone, "mobile phone")
    if mobile_phone is None:
        return
    license_number = get_valid_input("License number (XXDDDDDDD or XDDDDDDDD): ", validate_license_number, "license number")
    if license_number is None:
        return
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
        log_activity(username, "add_traveller", "Traveller added successfully")
        return True
    except Exception as e:
        print(f"Error: {e}")
        log_activity(username, "add_traveller", f"Failed to add traveller: {e}", suspicious=True)
        return

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
    

def delete_traveller(current_user=None):
    conn = get_db_connection()
    username = current_user["username"] if current_user and "username" in current_user else "unknown"

    strikes = 0
    while strikes < 3:
        traveller_id = input("Enter the Traveller ID to delete: ")
        try:
            traveller_id_int = int(traveller_id)
            cursor = conn.cursor()
            cursor.execute("SELECT traveller_id FROM travellers WHERE traveller_id=?", (traveller_id_int,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM travellers WHERE traveller_id=?", (traveller_id_int,))
                conn.commit()
                print("Traveller deleted.")
                log_activity(username, "delete_traveller", f"Traveller ID {traveller_id_int} deleted successfully")
                conn.close()
                return True
            else:
                print("Traveller ID not found. Please try again.")
                log_activity(username, "delete_traveller", f"Traveller ID {traveller_id} not found", suspicious=True)
        except ValueError:
            print("Invalid input. Traveller ID must be an integer.")
            log_activity(username, "delete_traveller", "Invalid traveller ID input (not integer)", suspicious=True)
        except Exception as e:
            print(f"Error: {e}")
            log_activity(username, "delete_traveller", f"Error while deleting traveller: {e}", suspicious=True)
        strikes += 1

    print("Too many strikes. Returning to previous menu.")
    log_activity(username, "delete_traveller", "Too many strikes for traveller ID", suspicious=True)
    conn.close()
