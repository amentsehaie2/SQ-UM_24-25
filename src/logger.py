import os
from database import get_user_by_username
from auth import login, logout
from logger import mark_suspicious_logs_as_read, print_logs, show_suspicious_alert, log_activity
from encryption import encrypt_data
from backup import (
    restore_backup_by_name, make_backup, generate_restore_code_db,
    revoke_restore_code_db, use_restore_code_db
)
from traveller import (
    add_traveller, update_traveller, delete_traveller, search_travellers
)
from engineer import (
    add_service_engineer, update_service_engineer_username, update_service_engineer_password,
    update_fname_service_engineer, update_lname_service_engineer,
    reset_service_engineer_password, update_scooter_by_engineer, update_own_password_service_engineer
)
from scooter import (
    add_scooter, update_scooter, delete_scooter, search_scooters
)
from admin import (
    add_system_admin, update_system_admin_username, update_system_admin_password,
    update_fname_system_admin, update_lname_system_admin, delete_system_admin, reset_system_admin_password,
    list_users, update_own_system_admin_profile, delete_own_system_admin_account, delete_service_engineer
)

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
BACKUP_DIR = os.path.join(_PROJECT_ROOT, "backup")


def get_int_input(prompt, min_option, max_option, user):
    strike_count = 0
    while strike_count < 4:
        try:
            value = int(input(prompt))
            if min_option <= value <= max_option:
                return value
            else:
                print(f"Please enter a number between {min_option} and {max_option}.")
                log_activity(user["username"], f"Strike count: {strike_count}", "Invalid input", suspicious=True)
                strike_count += 1
        except ValueError:
            print("Invalid input. Please enter a number.")
            log_activity(user["username"], f"Strike count: {strike_count}", "Invalid input", suspicious=True)
            strike_count += 1
    print("Too many invalid attempts. Returning to previous menu.")
    log_activity(user["username"], f"Strike count: {strike_count}", "Too many invalid attempts", suspicious=True)
    return None


def main_menu(user):
    role = user["role"]
    if role == "super_admin":
        return super_admin_menu(user)
    elif role == "system_admin":
        return system_admin_menu(user)
    elif role == "engineer" or role == "service_engineer":
        return service_engineer_menu(user)
    else:
        print("Unknown role. Exiting.")
        log_activity(user["username"], "Unknown role", "Unknown role", suspicious=True)
        return None


if __name__ == '__main__':
    print_logs()
