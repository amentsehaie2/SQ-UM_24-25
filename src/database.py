import sqlite3  
from datetime import datetime
import os
import sys
import bcrypt

from encryption import _initialize_keys

# --- Conditional import for direct execution vs. package import ---
if __package__ is None or __package__ == '':
    # If run as a script, add the parent directory of 'src' to sys.path
    _src_dir_for_import = os.path.dirname(os.path.abspath(__file__)) 
    _project_root_for_import = os.path.dirname(_src_dir_for_import) 
    if _project_root_for_import not in sys.path:
        sys.path.insert(0, _project_root_for_import)
    from src.encryption import encrypt_data, decrypt_data 
else:
    from .encryption import encrypt_data, decrypt_data
# --- End conditional import ---

# --- Determine project root and output directory for database ---
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")

DATABASE_NAME = os.path.join(_OUTPUT_DIR, "urban_mobility.db")

def get_db_connection():
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def initialize_db():  
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()  
    # Create users table  
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS users (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, -- Encrypted
            password TEXT NOT NULL,        -- Hashed
            role TEXT,                     -- Encrypted
            registration_date DATETIME  
        )  
    """)  

    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS travellers ( 
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            first_name TEXT,          -- Encrypt
            last_name TEXT,           -- Encrypt
            birth_date TEXT,          -- Encrypt if text
            gender TEXT,              -- Encrypt
            street_name TEXT,         -- Encrypt
            house_number TEXT,        -- Encrypt
            zip_code TEXT,            -- Encrypt
            city TEXT,                -- Encrypt
            email TEXT UNIQUE,        -- Encrypt
            phone_number TEXT,        -- Encrypt
            mobile_phone TEXT,        -- Encrypt
            license_number TEXT,      -- Encrypt
            registration_date DATETIME  
        )  
    """)  

    # Create scooters table
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS scooters ( 
            scooter_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            brand TEXT,               -- Encrypt
            model TEXT,               -- Encrypt
            serial_number TEXT UNIQUE,-- Encrypt
            top_speed INTEGER,
            battery_capacity INTEGER,
            state_of_charge INTEGER,
            target_range INTEGER,     
            location TEXT,            -- Encrypt
            out_of_service BOOLEAN,   
            mileage INTEGER,
            last_service_date DATETIME
        )  
    """)  

    # Create system logs
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS logs (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            date DATETIME,
            username TEXT,                     
            description_of_activity TEXT,    
            additional_info TEXT,            
            suspicious_activity BOOLEAN,
            is_read BOOLEAN DEFAULT 0  -- Added is_read column
        )  
    """) 
    conn.commit()  
    conn.close()

def mark_logs_as_read(log_ids):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            UPDATE logs
            SET is_read = 1
            WHERE id IN ({','.join(['?']*len(log_ids))})
        """, log_ids)
        conn.commit()
    except Exception as e:
        print(f"Error marking logs as read: {e}")
    finally:
        conn.close()

def get_unread_suspicious_logs_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM logs
            WHERE suspicious_activity = 1 AND is_read = 0
        """)
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error getting unread suspicious logs count: {e}")
        return 0
    finally:
        conn.close()



# --- Example functions demonstrating encryption/decryption ---

def add_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_username = encrypt_data(username)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    encrypted_role = encrypt_data(role)
    registration_date = datetime.now()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, registration_date)
            VALUES (?, ?, ?, ?)
        """, (encrypted_username, hashed_password, encrypted_role, registration_date))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' might already exist.")
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_search_username = encrypt_data(username) 
    cursor.execute("SELECT id, username, password, role, registration_date FROM users WHERE username = ?", 
                   (encrypted_search_username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_data = {
            "id": row[0],
            "username": decrypt_data(row[1]),
            "password": row[2], # Return the hashed password as is
            "role": decrypt_data(row[3]),
            "registration_date": row[4] 
        }

        # Check for unread suspicious logs if the user is an admin
        if user_data["role"] in ("System Administrator", "Super Administrator"):
            unread_count = get_unread_suspicious_logs_count()
            if unread_count > 0:
                print(f"\nALERT: There are {unread_count} unread suspicious logs. Please check the logs.\n")

        return user_data
    return None

def add_log_entry(username, description, additional_info="", suspicious=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    log_date = datetime.now()
    encrypted_username = encrypt_data(username)
    encrypted_description = encrypt_data(description)
    encrypted_additional_info = encrypt_data(additional_info)
    
    cursor.execute("""
        INSERT INTO logs (date, username, description_of_activity, additional_info, suspicious_activity, is_read)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (log_date, encrypted_username, encrypted_description, encrypted_additional_info, suspicious, 0)) # is_read defaults to 0
    conn.commit()
    conn.close()

def add_traveller(first_name, last_name, birth_date, gender, street_name, house_number, zip_code, city, email, phone_number, mobile_phone, license_number):
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
    encrypted_phone_number = encrypt_data(phone_number)
    encrypted_mobile_phone = encrypt_data(mobile_phone) 
    encrypted_license_number = encrypt_data(license_number)

    try:
        cursor.execute("""
            INSERT INTO travellers (first_name, last_name, birth_date, gender, street_name, 
                                    house_number, zip_code, city, email, phone_number, 
                                    mobile_phone, license_number, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (encrypted_first_name, encrypted_last_name, encrypted_birth_date, encrypted_gender,
              encrypted_street_name, encrypted_house_number, encrypted_zip_code, encrypted_city,
              encrypted_email, encrypted_phone_number, encrypted_mobile_phone, 
              encrypted_license_number, registration_date))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Traveller with email '{email}' might already exist or other integrity constraint failed.")
    finally:
        conn.close()

def get_all_logs(): 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, username, description_of_activity, additional_info, suspicious_activity FROM logs ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    decrypted_logs = []
    for row in rows:
        decrypted_logs.append({
            "id": row[0],
            "date": row[1],
            "username": decrypt_data(row[2]),
            "description_of_activity": decrypt_data(row[3]),
            "additional_info": decrypt_data(row[4]),
            "suspicious_activity": bool(row[5])
        })
    return decrypted_logs
    
if __name__ == '__main__':
    os.makedirs(_OUTPUT_DIR, exist_ok=True) 
    initialize_db()
    print(f"Database initialized in {DATABASE_NAME}.")
    _initialize_keys()
    print("Encryption keys initialized.")