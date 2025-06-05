import sqlite3
from validation import validate_zip, validate_phone
from encryption import encrypt_data, decrypt_data

def add_traveller(conn, first_name, last_name, zip_code, mobile_phone):
    if not validate_zip(zip_code):
        print("Invalid zip code format.")
        return False
    if not validate_phone(mobile_phone):
        print("Invalid phone number format.")
        return False
    encrypted_zip = encrypt_data(zip_code)
    encrypted_phone = encrypt_data(mobile_phone)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO travellers (first_name, last_name, zip_code, mobile_phone) VALUES (?, ?, ?, ?)",
        (first_name, last_name, encrypted_zip, encrypted_phone)
    )
    conn.commit()
    print("Traveller added.")
    return True

def search_travellers(conn, key):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM travellers WHERE first_name LIKE ? OR last_name LIKE ?",
        (f"%{key}%", f"%{key}%")
    )
    return cursor.fetchall()

def check_users
# TODO: Add update/delete functions for travellers and similar functions for scooters