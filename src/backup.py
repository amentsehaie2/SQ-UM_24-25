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
        print("Backup not found!")
        log_activity(current_user, f"Backup FAILED: {backup_name}", suspicious=True)
        return False
    # Verwijder bestaande .db bestanden
    for file in os.listdir(_OUTPUT_DIR):
        if file.endswith('.db'):
            os.remove(os.path.join(_OUTPUT_DIR, file))
    shutil.unpack_archive(backup_path, _OUTPUT_DIR, 'zip')
    if os.path.exists(backup_path):
        os.remove(backup_path)
        log_activity(current_user, f"Backup restored: {backup_name}", suspicious=False)
        print(f"Backup '{backup_name}' succesfully restored.")
        return True
    else:
        log_activity(current_user, f"Backup FAILED: {backup_name}", suspicious=True)
        print(f"Backup FAILED: {backup_name}")
        return False

def generate_restore_code_db(target_system_admin, backup_name, current_user):
    code = str(uuid.uuid4())
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    with open(RESTORE_CODE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{code}|{target_system_admin}|{backup_name}|unused\n")
    log_activity("super_admin", f"Restore-code generated for {target_system_admin} backup: {backup_name}", suspicious=False)
    print(f"Restore-code for {target_system_admin}: {code}")
    return code

def use_restore_code_db(current_username, code, current_user):
    """
    Validates a restore code, links it to the correct System Admin & backup,
    marks the code as used. Returns (True, backup_name) on success, otherwise (False, None).
    """
    lines = []
    found = False
    backup_name = None
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore codes file not found!")
        log_activity(current_username, "use_restore_code_db", "Restore codes file not found", suspicious=True)
        return False, None
    with open(RESTORE_CODE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RESTORE_CODE_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            code_line, sysadmin, backup, used = line.strip().split("|")
            if code_line == code and sysadmin == decrypt_data(current_username) and used == "unused":
                found = True
                backup_name = backup
                f.write(f"{code}|{sysadmin}|{backup}|used\n")
            else:
                f.write(line)
    print(current_username)
    print(sysadmin)
    return found, backup_name

def revoke_restore_code_db(code, current_user):
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore codes file not found!")
        log_activity("super_admin", "revoke_restore_code_db", "Restore codes file not found", suspicious=True)
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
    print(f"Restore code '{code}' has been revoked.")
    log_activity("super_admin", f"Restore code revoked: {code}", suspicious=False)

    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore-codes-bestand niet gevonden!")
        log_activity("super_admin", "revoke_restore_code_db", "Restore-codes-file not found", suspicious=True)
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
    print(f"Restore-code '{code}' revoked.")
    log_activity("super_admin", f"Restore-code revoked: {code}", suspicious=False)
