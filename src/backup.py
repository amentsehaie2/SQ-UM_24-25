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
        return backup_name
    else:
        log_activity(current_user["username"], f"Backup FAILED: {backup_name}", suspicious=True)
        print(f"Backup FAILED: {backup_name}")
        return None

def restore_backup_by_name(current_user, backup_name):
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        if not os.path.exists(backup_path):
            print(f"Backup file '{backup_name}' does not exist.")
            log_activity(current_user["username"], "Restore backup failed", f"File not found: {backup_name}", suspicious=True)
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
            print(f"Backup '{backup_name}' restored successfully.")
            return True

        finally:
            # Clean up temporary extraction directory
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception:
                pass
    except Exception as e:
        print(f"Error restoring backup: {e}")
        log_activity(current_user["username"], "Restore backup failed", str(e), suspicious=True)
        return False

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
    # encrypt each field before writing (including the flag)
    encrypted_code = encrypt_data(code)
    encrypted_admin = encrypt_data(target_system_admin)
    encrypted_backup = encrypt_data(backup_name)
    encrypted_flag = encrypt_data("unused")
    with open(RESTORE_CODE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{encrypted_code}|{encrypted_admin}|{encrypted_backup}|{encrypted_flag}\n")
    log_activity("super_admin", f"Restore-code generated for {target_system_admin} backup: {backup_name}", suspicious=False)
    print(f"Restore-code for {target_system_admin}: {code}")
    return code

def use_restore_code_db(current_username, code, current_user):
    """
    Validates a restore code, links it to the correct System Admin & backup,
    marks the code as used. Returns (True, backup_name) on success, otherwise (False, None).
    This function tolerates older/plaintext lines and will rewrite them encrypted.
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
            try:
                raw_code, raw_sysadmin, raw_backup, raw_flag = line.strip().split("|")
            except ValueError:
                # malformed line: keep as-is
                f.write(line)
                continue

            # Try to get plaintext values; if decryption fails assume the raw value is plaintext
            try:
                dec_code = decrypt_data(raw_code)
                enc_code = raw_code
            except Exception:
                dec_code = raw_code
                enc_code = encrypt_data(dec_code)

            try:
                dec_sysadmin = decrypt_data(raw_sysadmin)
                enc_sysadmin = raw_sysadmin
            except Exception:
                dec_sysadmin = raw_sysadmin
                enc_sysadmin = encrypt_data(dec_sysadmin)

            try:
                dec_backup = decrypt_data(raw_backup)
                enc_backup = raw_backup
            except Exception:
                dec_backup = raw_backup
                enc_backup = encrypt_data(dec_backup)

            try:
                dec_flag = decrypt_data(raw_flag)
                enc_flag = raw_flag
            except Exception:
                dec_flag = raw_flag
                enc_flag = encrypt_data(dec_flag)

            # current_username is expected encrypted in callers; keep existing behavior
            try:
                current_username_plain = decrypt_data(current_username)
            except Exception:
                current_username_plain = current_username

            try:
                if dec_code == code and dec_sysadmin == current_username_plain and dec_flag == "unused":
                    found = True
                    backup_name = dec_backup
                    # write same encrypted fields but mark used (encrypted)
                    f.write(f"{enc_code}|{enc_sysadmin}|{enc_backup}|{encrypt_data('used')}\n")
                    log_activity(current_username, f"Restore code used: {code}", suspicious=False)
                else:
                    # ensure we write the encrypted form (convert plaintext flags/fields)
                    f.write(f"{enc_code}|{enc_sysadmin}|{enc_backup}|{enc_flag}\n")
            except Exception:
                # on any error, keep the original line
                f.write(line)
    return found, backup_name

def revoke_restore_code_db(code, current_user):
    """
    Marks an existing encrypted restore-code as revoked.
    The restore_code.txt file stores only encrypted fields; this function
    tolerates plaintext legacy lines and rewrites them encrypted.
    """
    if not os.path.exists(RESTORE_CODE_FILE):
        print("Restore codes file not found!")
        log_activity("super_admin", "revoke_restore_code_db", "Restore codes file not found", suspicious=True)
        return

    try:
        with open(RESTORE_CODE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Could not read restore codes file: {e}")
        log_activity("super_admin", "revoke_restore_code_db", f"Read error: {e}", suspicious=True)
        return

    try:
        with open(RESTORE_CODE_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) != 4:
                    # malformed line: keep as-is
                    f.write(line + "\n")
                    continue

                raw_code, raw_sysadmin, raw_backup, raw_flag = parts

                try:
                    dec_code = decrypt_data(raw_code)
                    enc_code = raw_code
                except Exception:
                    dec_code = raw_code
                    enc_code = encrypt_data(dec_code)

                try:
                    dec_flag = decrypt_data(raw_flag)
                    enc_flag = raw_flag
                except Exception:
                    dec_flag = raw_flag
                    enc_flag = encrypt_data(dec_flag)

                # Match the provided plaintext code; only change the flag if unused
                if dec_code == code and dec_flag == "unused":
                    f.write(f"{enc_code}|{raw_sysadmin if raw_sysadmin.startswith('gAAAA') else encrypt_data(raw_sysadmin)}|{raw_backup if raw_backup.startswith('gAAAA') else encrypt_data(raw_backup)}|{encrypt_data('revoked')}\n")
                else:
                    # ensure we write encrypted flag/fields for consistency
                    try:
                        # normalize sysadmin/backup to encrypted versions if they were plaintext
                        try:
                            # if already decryptable, keep raw; else encrypt plaintext
                            _ = decrypt_data(raw_sysadmin)
                            enc_sysadmin = raw_sysadmin
                        except Exception:
                            enc_sysadmin = encrypt_data(raw_sysadmin)

                        try:
                            _ = decrypt_data(raw_backup)
                            enc_backup = raw_backup
                        except Exception:
                            enc_backup = encrypt_data(raw_backup)
                    except Exception:
                        enc_sysadmin = raw_sysadmin
                        enc_backup = raw_backup

                    f.write(f"{enc_code}|{enc_sysadmin}|{enc_backup}|{enc_flag}\n")

        print(f"Restore code '{code}' has been revoked.")
        log_activity("super_admin", f"Restore code revoked: {code}", suspicious=False)
    except Exception as e:
        print(f"Error updating restore codes file: {e}")
        log_activity("super_admin", "revoke_restore_code_db", f"Write error: {e}", suspicious=True)