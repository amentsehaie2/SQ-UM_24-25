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
from database import get_user_by_username

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
        print("Invalid password format. Please use 12-30 characters with at least one uppercase letter, one lowercase letter, and one special character.")
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

def update_own_password_service_engineer(current_user): # CHECK
    """Updates the password of the current service engineer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username, password, role FROM users WHERE id = ?", (current_user['id'],))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to update service engineer password - user ID {current_user['id']} not found")
            print("User with that ID not found.")
            conn.close()
            return

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        current_password_hash = result[1]
        user_role_encrypted = result[2]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to update password - user ID {current_user['id']} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return
        current_password_input = input(f"Enter the current password for service engineer ID {current_user['id']}: ")
        if not validate_password(current_password_input):
            log_activity(current_user["username"], f"Failed to update service engineer password - invalid format: {current_password_input}", suspicious=True)
            print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
            conn.close()
            return

        if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update service engineer password - incorrect current password for ID {current_user['id']}", suspicious=True)
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
            log_activity(current_user["username"], f"Failed to update service engineer password - new password same as current for ID {current_user['id']}")
            print("New password cannot be the same as the current password.")
            conn.close()
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, current_user['id']))
        conn.commit()

        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated service engineer password for user {current_username} (ID: {current_user['id']})")
            print("Password updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update service engineer password - no rows affected for ID {current_user['id']}", suspicious=True)
            print("Failed to update password - no changes made to database.")
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update service engineer password - database error for ID {current_user['id']}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update service engineer password - unexpected error for ID {current_user['id']}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()