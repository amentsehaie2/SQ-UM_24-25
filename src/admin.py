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
        print("Invalid password format. Please use 12-30 characters with at least one uppercase letter, one lowercase letter, and one special character.")
        return
    encrypted_username = encrypt_data(username)
    encrypted_fname = encrypt_data(first_name)
    encrypted_lname = encrypt_data(last_name)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    encrypted_role = encrypt_data("system_admin")

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

        if user_role != "system_admin":
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
    try:
        user_id = int(input("Enter the ID of the system administrator you want to update: "))
    except ValueError:
        log_activity(current_user["username"], "Failed to update system admin password - invalid ID format", suspicious=True)
        print("Invalid ID format. Please enter a number.")
        return

    old_password = input("Current Password: ")
    new_password = input("New Password: ")
    if not validate_password(old_password):
        log_activity(current_user["username"], f"Failed to update system admin password - invalid current password format for user: {user_id}", suspicious=True)
        print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
        return
    if not validate_password(new_password):
        log_activity(current_user["username"], f"Failed to update system admin password - invalid new password format for user: {user_id}", suspicious=True)
        print("Invalid password format. Please use 12-30 alphanumeric characters, with at least one uppercase letter, one lowercase letter, and one special character.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            log_activity(current_user["username"], f"Failed to update system admin password - user ID '{user_id}' not found", suspicious=True)
            print("User with that ID not found.")
            return

        user_id, current_password_hash, role_encrypted = result
        role = decrypt_data(role_encrypted)
        if role != "system_admin":
            log_activity(current_user["username"], f"Failed to update password - user '{user_id}' is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            return

        if not bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - incorrect current password for user: {user_id}", suspicious=True)
            print("Incorrect current password.")
            return

        if bcrypt.checkpw(new_password.encode('utf-8'), current_password_hash):
            log_activity(current_user["username"], f"Failed to update system admin password - new password same as current for user: {user_id}")
            print("New password cannot be the same as the current password.")
            return

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            log_activity(current_user["username"], f"Successfully updated system admin password for user '{user_id}' (ID: {user_id})")
            print("Password updated successfully.")
        else:
            log_activity(current_user["username"], f"Failed to update system admin password - no rows affected for user: {user_id}", suspicious=True)
            print("Failed to update password - no changes made to database.")
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to update system admin password - database error for user '{user_id}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        log_activity(current_user["username"], f"Failed to update system admin password - unexpected error for user '{user_id}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

def delete_system_admin(current_user):
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

        if user_role != "system_admin":
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

def delete_own_system_admin(current_user):
    """Allows a system administrator to delete their own account."""
    username = decrypt_data(current_user["username"])
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (current_user["username"],))
        result = cursor.fetchone()

        if not result:
            log_activity(current_user["username"], f"Failed to delete own system admin account - username '{username}' not found")
            print("User account not found.")
            conn.close()
            return False

        user_id = result[0]
        current_username_encrypted = result[1]
        current_username = decrypt_data(current_username_encrypted)
        current_password_hash = result[2]
        user_role_encrypted = result[3]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "admin":
            log_activity(current_user["username"], f"Failed to delete own account - user '{username}' is not a system administrator", suspicious=True)
            print("User is not a System Administrator.")
            conn.close()
            return False

        print(f"⚠️  WARNING: You are about to delete your own account '{current_username}'")
        print("This action cannot be undone and you will be logged out immediately.")
        
        confirmation = input("Are you sure you want to delete your own account? Type yes/no to confirm: ")
        if confirmation != "yes":
            log_activity(current_user["username"], f"Own system admin account deletion cancelled for user {current_username} (ID: {user_id})")
            print("Account deletion cancelled.")
            conn.close()
            return False
        if confirmation == "no":
            log_activity(current_user["username"], f"Own system admin account deletion cancelled for user {current_username} (ID: {user_id})")
            print("Account deletion cancelled.")
            conn.close()
            return False
        
        elif confirmation == "yes":

            # # Require password confirmation for security
            # current_password_input = input("Enter your current password to confirm deletion: ")
            # if not validate_password(current_password_input):
            #     log_activity(current_user["username"], f"Failed to delete own system admin account - invalid password format", suspicious=True)
            #     print("Invalid password format.")
            #     conn.close()
            #     return False

            # if not bcrypt.checkpw(current_password_input.encode('utf-8'), current_password_hash):
            #     log_activity(current_user["username"], f"Failed to delete own system admin account - incorrect password for ID {user_id}", suspicious=True)
            #     print("Incorrect password. Account deletion cancelled.")
            #     conn.close()
            #     return False

            # Final confirmation
            final_confirmation = input("Final confirmation - type 'yes' to permanently delete your account: ")
            if final_confirmation != "yes":
                log_activity(current_user["username"], f"Own system admin account deletion cancelled at final confirmation for user {current_username} (ID: {user_id})")
                print("Account deletion cancelled.")
                conn.close()
                return False
            
            if final_confirmation == "yes":
                # Perform the deletion
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    log_activity(current_user["username"], f"Successfully deleted own system administrator account {current_username} (ID: {user_id})")
                    print("✅ Your account has been successfully deleted.")
                    print("You will now be logged out.")
                    conn.close()
                    return True
                else:
                    log_activity(current_user["username"], f"Failed to delete own system admin account - no rows affected for ID {user_id}", suspicious=True)
                    print("Failed to delete account - no changes made to database.")
                    conn.close()
                    return False
            
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete own system admin account - database error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
        return False
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete own system admin account - unexpected error for username '{username}'", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        return False
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

        if user_role != "system_admin":
            log_activity(current_user["username"], f"Failed to update first name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_fname = input("Enter the new first name: ")
        if not validate_fname(new_fname):
            log_activity(current_user["username"], f"Failed to update service admin first name - invalid format: {new_fname}", suspicious=True)
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

        if user_role != "system_admin":
            log_activity(current_user["username"], f"Failed to update last name - user ID {user_id} is not a system administrator", suspicious=True)
            print("User with that ID is not a System Administrator.")
            conn.close()
            return

        new_lname = input("Enter the new last name: ")
        if not validate_lname(new_lname):
            log_activity(current_user["username"], f"Failed to update service admin last name - invalid format: {new_lname}", suspicious=True)
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

        if user_role != "system_admin":
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

        if user_role != "system_admin":
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

def update_own_system_admin_profile(current_user):
    """Allows a system admin to update their own profile (username, password, first name, last name)."""
    if current_user["role"] != "system_admin" and current_user["role"] != "admin":
        print("Only a system administrator can update their own profile.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user['id']

    # --- Update username ---
    strike_count = 0
    while strike_count < 4:
        new_username = input("New username (leave empty to skip): ").strip()
        if new_username == "":
            break
        if not isinstance(new_username, str) or not validate_username(new_username):
            print("Invalid username format.")
            strike_count += 1
            continue
        # Check uniqueness
        cursor.execute("SELECT id, username FROM users WHERE id != ?", (user_id,))
        usernames = [decrypt_data(row[1]) for row in cursor.fetchall()]
        if new_username in usernames:
            print("Username is already taken.")
            strike_count += 1
            continue
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (encrypt_data(new_username), user_id))
        current_user["username"] = new_username  # Update session
        print("Username updated.")
        break
    if strike_count >= 4:
        print("Too many invalid attempts for username.")
        conn.close()
        return

    # --- Update first name ---
    strike_count = 0
    while strike_count < 4:
        new_fname = input("New first name (leave empty to skip): ").strip()
        if new_fname == "":
            break
        if not isinstance(new_fname, str) or not validate_fname(new_fname):
            print("Invalid first name format.")
            strike_count += 1
            continue
        cursor.execute("UPDATE users SET first_name = ? WHERE id = ?", (encrypt_data(new_fname), user_id))
        print("First name updated.")
        break
    if strike_count >= 4:
        print("Too many invalid attempts for first name.")
        conn.close()
        return

    # --- Update last name ---
    strike_count = 0
    while strike_count < 4:
        new_lname = input("New last name (leave empty to skip): ").strip()
        if new_lname == "":
            break
        if not isinstance(new_lname, str) or not validate_lname(new_lname):
            print("Invalid last name format.")
            strike_count += 1
            continue
        cursor.execute("UPDATE users SET last_name = ? WHERE id = ?", (encrypt_data(new_lname), user_id))
        print("Last name updated.")
        break
    if strike_count >= 4:
        print("Too many invalid attempts for last name.")
        conn.close()
        return

    # --- Update password ---
    strike_count = 0
    while strike_count < 4:
        old_password = input("Current password (leave empty to skip): ").strip()
        if old_password == "":
            break
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result or not bcrypt.checkpw(old_password.encode('utf-8'), result[0]):
            print("Current password is incorrect.")
            strike_count += 1
            continue
        # Ask for new password
        pw_strike = 0
        while pw_strike < 4:
            new_password = input("New password: ").strip()
            if not isinstance(new_password, str) or not validate_password(new_password):
                print("Invalid password format.")
                pw_strike += 1
                continue
            if bcrypt.checkpw(new_password.encode('utf-8'), result[0]):
                print("New password cannot be the same as the old password.")
                pw_strike += 1
                continue
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
            print("Password updated.")
            break
        if pw_strike >= 4:
            print("Too many invalid attempts for password.")
            conn.close()
            return
        break
    if strike_count >= 4:
        print("Too many invalid attempts for password.")
        conn.close()
        return

    conn.commit()
    conn.close()
    print("Your profile has been updated.")

def delete_own_system_admin_account(current_user):
    """Allows a system admin to delete their own account after password confirmation."""
    if current_user["role"] != "system_admin" and current_user["role"] != "admin":
        print("Only a system administrator can delete their own account.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user['id']

    strike_count = 0
    while strike_count < 4:
        password = input("Enter your password to confirm: ").strip()
        if not isinstance(password, str) or password == "":
            print("Password cannot be empty.")
            strike_count += 1
            continue
        cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result or not bcrypt.checkpw(password.encode('utf-8'), result[0]):
            print("Password is incorrect.")
            strike_count += 1
            continue
        break
    if strike_count >= 4:
        print("Too many invalid attempts. Account will NOT be deleted.")
        conn.close()
        return False

    strike_count = 0
    while strike_count < 4:
        confirmation = input("Are you sure you want to delete your account? Type 'yes' to confirm: ").strip().lower()
        if confirmation == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            print("Your account has been deleted. You will now be logged out.")
            conn.close()
            return True  # ACCOUNT DELETED!
        else:
            print("Deletion not confirmed. Type 'yes' to proceed.")
            strike_count += 1
    if strike_count >= 4:
        print("Too many invalid attempts. Account will NOT be deleted.")
    conn.close()
    return False

def delete_service_engineer(current_user):
    strike_count = 0
    service_engineer_id = None
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

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, role FROM users WHERE id = ?", (service_engineer_id,))
        result = cursor.fetchone()
        if not result:
            log_activity(current_user["username"], f"Failed to delete service engineer - user ID {service_engineer_id} not found")
            print("User with that ID not found.")
            conn.close()
            return False

        current_username_encrypted = result[0]
        current_username = decrypt_data(current_username_encrypted)
        user_role_encrypted = result[1]
        user_role = decrypt_data(user_role_encrypted)

        if user_role != "engineer":
            log_activity(current_user["username"], f"Failed to delete - user ID {service_engineer_id} is not a service engineer", suspicious=True)
            print("User with that ID is not a Service Engineer.")
            conn.close()
            return False

        confirmation = input(f"Are you sure you want to delete service engineer with ID {service_engineer_id}? (yes/no): ")
        if confirmation.lower() == "yes":
            cursor.execute("DELETE FROM users WHERE id = ?", (service_engineer_id,))
            conn.commit()
            if cursor.rowcount > 0:
                log_activity(current_user["username"], f"Successfully deleted service engineer {current_username} (ID: {service_engineer_id})")
                print("Service engineer deleted successfully.")
                conn.close()
                return True
            else:
                log_activity(current_user["username"], f"Failed to delete service engineer - no rows affected for ID {service_engineer_id}", suspicious=True)
                print("Failed to delete service engineer - no changes made to database.")
                conn.close()
                return False
        else:
            log_activity(current_user["username"], f"Service engineer deletion cancelled for user {current_username} (ID: {service_engineer_id})")
            print("Deletion cancelled.")
            conn.close()
            return False
    except sqlite3.Error as e:
        log_activity(current_user["username"], f"Failed to delete service engineer - database error for ID {service_engineer_id}", f"Error: {str(e)}", suspicious=True)
        print(f"Database error occurred: {str(e)}")
        conn.close()
        return False
    except Exception as e:
        log_activity(current_user["username"], f"Failed to delete service engineer - unexpected error for ID {service_engineer_id}", f"Error: {str(e)}", suspicious=True)
        print(f"An unexpected error occurred: {str(e)}")
        conn.close()
        return False
    