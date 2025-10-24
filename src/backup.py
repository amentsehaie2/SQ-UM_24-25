import sqlite3
import os
import shutil
import secrets
import bcrypt
import uuid
from datetime import datetime
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
        log_activity(current_user.get("username") if isinstance(current_user, dict) else str(current_user), f"Backup FAILED: {backup_name}", suspicious=True)
        return False

    # Unpack into a temporary directory first, validate, then swap in if OK
    temp_dir = os.path.join(BACKUP_DIR, f"tmp_restore_{uuid.uuid4().hex}")
    try:
        os.makedirs(temp_dir, exist_ok=True)
        shutil.unpack_archive(backup_path, temp_dir, 'zip')

        # Locate .db inside the unpacked archive
        restored_db = None
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.endswith('.db'):
                    restored_db = os.path.join(root, f)
                    break
            if restored_db:
                break

        if not restored_db:
            print("No database file found inside the backup archive.")
            log_activity(current_user.get("username") if isinstance(current_user, dict) else str(current_user), f"Restore aborted: no DB in {backup_name}", suspicious=True)
            return False

        # Validate the current user exists in the restored DB (or allow super_admin)
        if not valid_curr_sys(current_user, backup_name, db_path=restored_db):
            print("Restored backup does not contain the current user. Restore aborted.")
            log_activity(current_user.get("username") if isinstance(current_user, dict) else str(current_user), f"Restore aborted: user not in {backup_name}", suspicious=True)
            return False

        # At this point validation succeeded. Replace current DB files with the restored ones.
        # Back up current DB files first
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_current = os.path.join(BACKUP_DIR, f"pre_restore_backup_{timestamp}")
        os.makedirs(backup_current, exist_ok=True)
        for file in os.listdir(_OUTPUT_DIR):
            if file.endswith('.db'):
                shutil.move(os.path.join(_OUTPUT_DIR, file), os.path.join(backup_current, file))

        # Copy restored files into _OUTPUT_DIR
        for root, _, files in os.walk(temp_dir):
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(_OUTPUT_DIR, f)
                shutil.copy2(src_file, dst_file)

        # Optionally remove the restore code backup file so it cannot be reused
        try:
            os.remove(backup_path)
        except Exception:
            pass

        log_activity(current_user.get("username") if isinstance(current_user, dict) else str(current_user), f"Backup restored: {backup_name}", suspicious=False)
        print(f"Backup '{backup_name}' succesfully restored.")
        return True

    finally:
        # Clean up temporary extraction directory
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass

def valid_curr_sys(current_user, backup, db_path: str = None) -> bool:
    """
    Checks if the current username exists in the provided database path (if given)
    or in the live DATABASE_NAME if db_path is None. Returns True if found.
    Super admins are always allowed.
    """
    current_username = current_user["username"] if isinstance(current_user, dict) else str(current_user)

    if isinstance(current_user, dict) and current_user.get("role") == "super_admin":
        print("Super admin detected: skipping user existence check in backup.")
        log_activity(current_username, f"Super admin restored backup '{backup}' (no user check)", suspicious=False)
        return True

    # Choose which DB to inspect
    conn = None
    try:
        if db_path:
            conn = sqlite3.connect(db_path)
        else:
            conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        all_users = cursor.fetchall()
        found = False
        for (encrypted_username,) in all_users:
            try:
                if decrypt_data(encrypted_username) == current_username:
                    found = True
                    break
            except Exception:
                # Skip entries that cannot be decrypted
                continue

        if found:
            print(f"Username '{current_username}' exists in the database.")
            log_activity(current_username, f"Restored backup '{backup}' contains current user", suspicious=False)
        else:
            print(f"Username '{current_username}' does NOT exist in the database.")
            log_activity(current_username, f"Restored backup '{backup}' does not contain current user", suspicious=True)

        log_activity(current_username, f"Validating current user in restored backup '{backup}': {found}", suspicious=not found)
        return found
    finally:
        if conn:
            conn.close()

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
                log_activity(current_username, f"Restore code used: {code}", suspicious=False)
            else:
                f.write(line)
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
