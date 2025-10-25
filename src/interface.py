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


def super_admin_menu(user):
    while True:
        print("\n--- Super Administrator Menu ---")
        print("1. User Management")
        print("2. Traveller Management")
        print("3. Scooter Management")
        print("4. System Administration")
        print("5. Logout")
        choice = get_int_input("Select a category (1-5): ", 1, 5, user)
        if choice is None:
            break
        if choice == 1:
            user_management_menu(user)
        elif choice == 2:
            traveller_management_menu(user)
        elif choice == 3:
            scooter_management_menu(user)
        elif choice == 4:
            system_administration_menu(user)
        elif choice == 5:
            print("Logging out...")
            log_activity(user["username"], "Logout", "Logout")
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)
    return None


def user_management_menu(current_user):
    while True:
        print("\n--- User Management ---")
        print("1. List users")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer username")
        print("4. Update Service Engineer password")
        print("5. Update Service Engineer first name")
        print("6. Update Service Engineer last name")
        print("7. Delete Service Engineer")
        print("8. Reset Service Engineer password")

        is_super_admin = current_user["role"] == "super_admin"
        is_system_admin = current_user["role"] == "system_admin"

        if is_super_admin:
            print("9. Add System Administrator")
            print("10. Update System Admin username")
            print("11. Update System Admin password")
            print("12. Update System Admin first name")
            print("13. Update System Admin last name")
            print("14. Delete System Administrator")
            print("15. Reset System Admin password")
            print("16. Back")
            min_opt, max_opt = 1, 16
        else:
            print("9. Update your own profile")
            print("10. Delete your own account")
            print("11. Back")
            min_opt, max_opt = 1, 11

        choice = get_int_input("Select an option: ", min_opt, max_opt, current_user)
        if choice is None:
            break

        if choice == 1:
            list_users()
        elif choice == 2:
            add_service_engineer(current_user)
        elif choice == 3:
            update_service_engineer_username(current_user)
        elif choice == 4:
            update_service_engineer_password(current_user)
        elif choice == 5:
            update_fname_service_engineer(current_user)
        elif choice == 6:
            update_lname_service_engineer(current_user)
        elif choice == 7:
            delete_service_engineer(current_user)
        elif choice == 8:
            reset_service_engineer_password(current_user)
        elif is_super_admin and choice == 9:
            add_system_admin(current_user)
        elif is_super_admin and choice == 10:
            update_system_admin_username(current_user)
        elif is_super_admin and choice == 11:
            update_system_admin_password(current_user)
        elif is_super_admin and choice == 12:
            update_fname_system_admin(current_user)
        elif is_super_admin and choice == 13:
            update_lname_system_admin(current_user)
        elif is_super_admin and choice == 14:
            delete_system_admin(current_user)
        elif is_super_admin and choice == 15:
            reset_system_admin_password(current_user)
        elif is_system_admin and choice == 9:
            update_own_system_admin_profile(current_user)
        elif is_system_admin and choice == 10:
            account_deleted = delete_own_system_admin_account(current_user)
            if account_deleted:
                print("Your account was deleted. Returning to previous menu...")
                log_activity(current_user["username"], "Account deleted", "self-delete")
                return
        elif (is_super_admin and choice == 16) or (is_system_admin and choice == 11):
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(current_user["username"], "Invalid option", "Invalid option", suspicious=True)
    return None


def traveller_management_menu(user):
    while True:
        print("\n--- Traveller Management ---")
        print("1. Add Traveller")
        print("2. Update Traveller")
        print("3. Delete Traveller")
        print("4. Search Traveller")
        print("5. Back")
        choice = get_int_input("Select an option (1-5): ", 1, 5, user)
        if choice is None:
            log_activity(user["username"], "Traveller menu: too many invalid attempts", "return", suspicious=True)
            break

        is_admin = user["role"] in ["super_admin", "system_admin"]

        if choice == 1:
            if is_admin:
                add_traveller(user)
                log_activity(user["username"], "Add Traveller", "")
            else:
                print("Permission denied: Only Admin or Super Admin can add travellers.")
                log_activity(user["username"], "Permission denied", "add traveller", suspicious=True)

        elif choice == 2:
            if is_admin:
                update_traveller(user)
                log_activity(user["username"], "Update Traveller", "")
            else:
                print("Permission denied: Only Admin or Super Admin can update travellers.")
                log_activity(user["username"], "Permission denied", "update traveller", suspicious=True)

        elif choice == 3:
            if is_admin:
                delete_traveller(user)
                log_activity(user["username"], "Delete Traveller", "")
            else:
                print("Permission denied: Only Admin or Super Admin can delete travellers.")
                log_activity(user["username"], "Permission denied", "delete traveller", suspicious=True)

        elif choice == 4:
            search_travellers(user)
            log_activity(user["username"], "Search Traveller", "")

        elif choice == 5:
            log_activity(user["username"], "Traveller menu -> Back", "")
            break

        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "traveller menu invalid option", suspicious=True)
    return None


def scooter_management_menu(current_user):
    while True:
        print("\n--- Scooter Management ---")
        print("1. Add Scooter")
        print("2. Update Scooter")
        print("3. Delete Scooter")
        print("4. Search Scooter")
        print("5. Back")
        choice = get_int_input("Select an option (1-5): ", 1, 5, current_user)
        if choice is None:
            break
        if choice == 1:
            if current_user["role"] in ["super_admin", "system_admin"]:
                add_scooter(current_user)
                log_activity(current_user["username"], "Add Scooter", "")
            else:
                print("Permission denied: Only Admin or Super Admin can add scooters.")
                log_activity(current_user["username"], "Permission denied", "add scooter", suspicious=True)
        elif choice == 2:
            if current_user["role"] in ["super_admin", "system_admin"]:
                update_scooter(current_user)
                log_activity(current_user["username"], "Update Scooter (admin)", "")
            elif current_user["role"] in ["engineer", "service_engineer"]:
                update_scooter_by_engineer(current_user)
                log_activity(current_user["username"], "Update Scooter (engineer)", "")
            else:
                print("Permission denied.")
                log_activity(current_user["username"], "Permission denied", "update scooter", suspicious=True)
        elif choice == 3:
            if current_user["role"] in ["super_admin", "system_admin"]:
                delete_scooter(current_user)
                log_activity(current_user["username"], "Delete Scooter", "")
            else:
                print("Permission denied: Only Admin or Super Admin can delete scooters.")
                log_activity(current_user["username"], "Permission denied", "delete scooter", suspicious=True)
        elif choice == 4:
            search_scooters(current_user)
            log_activity(current_user["username"], "Search Scooter", "")
        elif choice == 5:
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(current_user["username"], "Invalid option", "scooter menu invalid option", suspicious=True)
    return None


def view_suspicious_logs():
    """View and acknowledge suspicious logs."""
    unread_suspicious = show_suspicious_alert()

    if not unread_suspicious:
        print("\n✅ No unread suspicious activities found.")
        return

    print(f"\n🚨 Found some unread suspicious activities:")
    print("-" * 80)

    for log in unread_suspicious:
        print(f"ID: {log['log_id']} | Date: {log['timestamp']} | User: {log['username']}")
        print(f"Description: {log['description']}")
        if log.get('additional_info'):
            print(f"Details: {log['additional_info']}")
        print("-" * 80)

    acknowledge = input("\nAcknowledge these suspicious activities? (yes/no): ").lower()
    if acknowledge == "yes":
        mark_suspicious_logs_as_read()
        print("✅ All suspicious activities marked as read.")
    else:
        print("⚠️  Suspicious activities remain unread.")


def system_admin_menu(user):
    while True:
        print("\n--- System Admin Menu ---")
        print("1. User Management")
        print("2. Traveller Management")
        print("3. Scooter Management")
        print("4. System Administration")
        print("5. Logout")
        choice = get_int_input("Select an option (1-5): ", 1, 5, user)
        if choice is None:
            break
        if choice == 1:
            user_management_menu(user)
        elif choice == 2:
            traveller_management_menu(user)
        elif choice == 3:
            scooter_management_menu(user)
        elif choice == 4:
            system_administration_menu(user)
        elif choice == 5:
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)
    return None


def system_administration_menu(current_user):
    while True:
        print("\n--- System Administration ---")
        print("1. View system logs")
        print("2. Make a system backup")
        print("3. Restore a system backup")
        print("4. View suspicious logs")
        if current_user["role"] == "super_admin":
            print("5. Generate restore-code for System Administrator")
            print("6. Revoke restore-code for System Administrator")
            print("7. Back")
            min_opt, max_opt = 1, 7
        else:
            print("5. Back")
            min_opt, max_opt = 1, 5

        choice = get_int_input(f"Select an option ({min_opt}-{max_opt}): ", min_opt, max_opt, current_user)
        if choice is None:
            log_activity(current_user["username"], "System Admin menu: too many invalid attempts", "return", suspicious=True)
            break

        if choice == 1:
            log_activity(current_user["username"], "View system logs", "")
            print_logs()

        elif choice == 2:
            backup_name = make_backup(current_user)
            log_activity(current_user["username"], "Make backup", f"backup={backup_name}")
            print(f"Backup created: {backup_name}")

        elif choice == 3:
            if current_user["role"] in ["system_admin", "super_admin"]:
                if current_user["role"] == "super_admin":
                    backup_name = input("Enter the exact backup file name to restore: ")
                    if backup_name is None or not isinstance(backup_name, str):
                        print("Backup name cannot be empty.")
                        log_activity(current_user["username"], "Restore backup failed", "empty backup name", suspicious=True)
                        continue
                    if restore_backup_by_name(current_user, backup_name):
                        log_activity(current_user["username"], "Restore backup (super admin)", f"backup={backup_name}")
                        return
                    else:
                        print("Restore failed. Please check the backup name and try again.")
                        log_activity(current_user["username"], "Restore backup failed", f"backup={backup_name}", suspicious=True)
                elif current_user["role"] == "system_admin":
                    restore_code = input("Enter your restore-code: ")
                    if restore_code is None or not isinstance(restore_code, str):
                        print("Restore-code cannot be empty.")
                        log_activity(current_user["username"], "Restore backup failed", "empty restore-code", suspicious=True)
                        continue
                    ok, backup_name = use_restore_code_db( 
                        encrypt_data(current_user["username"]),
                        restore_code,
                        current_user
                    )
                    if not ok:
                        print("Restore-code invalid or not for this user!")
                        log_activity(current_user["username"], "Restore backup failed", "invalid restore-code", suspicious=True)
                    else:
                        restore_backup_by_name(current_user, backup_name)
                        log_activity(current_user["username"], "Restore backup OK", f"backup={backup_name}")
                        return
            else:
                print("Only an Administrator can restore a backup!")
                log_activity(current_user["username"], "Permission denied", "restore backup", suspicious=True)

        elif choice == 4:
            log_activity(current_user["username"], "View suspicious logs", "")
            view_suspicious_logs()

        elif current_user["role"] == "super_admin" and choice == 5:
            max_strikes = 4
            strike_count = 0
            while strike_count < max_strikes:
                target_sysadmin = input("For which Administrator? Username: ")
                if not (isinstance(target_sysadmin, str) and target_sysadmin):
                    print("Username cannot be empty.")
                    strike_count += 1
                    continue
                if get_user_by_username(target_sysadmin) is None:
                    print("User does not exist.")
                    strike_count += 1
                    continue
                break
            else:
                print("Too many invalid attempts. Returning to menu.")
                log_activity(current_user["username"], "Generate restore-code aborted", "username invalid", suspicious=True)
                continue

            strike_count = 0
            while strike_count < max_strikes:
                backup_name = input("Which backup (full file name)? ")
                if not (isinstance(backup_name, str) and backup_name):
                    print("Backup name cannot be empty.")
                    strike_count += 1
                    continue
                backup_path = os.path.join(BACKUP_DIR, backup_name)
                if not os.path.exists(backup_path):
                    print("Backup file does not exist.")
                    strike_count += 1
                    continue
                break
            else:
                print("Too many invalid attempts. Returning to menu.")
                log_activity(current_user["username"], "Generate restore-code aborted", "backup invalid", suspicious=True)
                continue

            generate_restore_code_db(target_sysadmin, backup_name, current_user)
            log_activity(current_user["username"], "Generate restore-code", f"user={target_sysadmin}, backup={backup_name}")

        elif current_user["role"] == "super_admin" and choice == 6:
            strike_count = 0
            while strike_count < 4:
                code = input("Which restore-code to revoke? ")
                if isinstance(code, str) and code:
                    revoke_restore_code_db(code, current_user)
                    log_activity(current_user["username"], "Revoke restore-code", f"code={code}")
                    break
                else:
                    print("Code cannot be empty.")
                    strike_count += 1
            if strike_count >= 4:
                print("Too many invalid attempts. Returning to menu.")
                log_activity(current_user["username"], "Revoke restore-code aborted", "too many invalid attempts", suspicious=True)

        elif (current_user["role"] == "super_admin" and choice == 7) or (current_user["role"] == "system_admin" and choice == 5):
            log_activity(current_user["username"], "System Admin menu -> Back", "")
            break

        else:
            print("Invalid option. Please try again.")
            log_activity(current_user["username"], "Invalid option", "system admin menu invalid option", suspicious=True)
    return None


def service_engineer_menu(user):
    while True:
        print("\n--- Service Engineer Menu ---")
        print("1. Search Scooter")
        print("2. Update Scooter attributes")
        print("3. Update own password")
        print("4. Logout")
        choice = get_int_input("Select an option (1-4): ", 1, 4, user)
        if choice is None:
            break
        if choice == 1:
            search_scooters(user)
            log_activity(user["username"], "Search Scooter", "")
        elif choice == 2:
            update_scooter_by_engineer(user)
            log_activity(user["username"], "Update Scooter (engineer)", "")
        elif choice == 3:
            update_own_password_service_engineer(user)
            log_activity(user["username"], "Update own password (engineer)", "")
        elif choice == 4:
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)
    return None
