from auth import login, logout
from encryption import decrypt_data
from operations import (
    add_traveller, update_traveller, delete_traveller, search_travellers,
    add_scooter, update_scooter, delete_scooter, search_scooters,
    add_service_engineer, update_service_engineer_username, update_service_engineer_password,
    update_fname_service_engineer, update_lname_service_engineer, delete_service_engineer,
    reset_service_engineer_password, update_scooter_by_engineer,
    add_system_admin, update_system_admin_username, update_system_admin_password,
    update_fname_system_admin, update_lname_system_admin, delete_system_admin, reset_system_admin_password,
    make_backup, restore_backup_by_name, generate_restore_code_db, revoke_restore_code_db, use_restore_code_db,
    list_users,
)
from logger import mark_suspicious_logs_as_read, print_logs, show_suspicious_alert, log_activity

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

def main():
    while True:
        user = login()
        if user is None:
            continue
        main_menu(user)
        logout(user)

def main_menu(user):
    role = user["role"]
    if role == "super_admin":
        super_admin_menu(user)
    elif role == "system_admin":
        system_administration_menu(user)
    elif role == "engineer" or role == "service_engineer":
        service_engineer_menu(user)
    else:
        print("Unknown role. Exiting.")
        log_activity(user["username"], "Unknown role", "Unknown role", suspicious=True)
        return

def super_admin_menu(user):
    while True:
        print("\n--- Super Administrator Menu ---")
        print("1. User Management")
        print("2. Traveller Management")
        print("3. Scooter Management")
        print("4. System Administration")
        print("5. Uitloggen")
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
        if is_super_admin:
            print("9. Add System Administrator")
            print("10. Update System Admin username")
            print("11. Update System Admin password")
            print("12. Update System Admin first name")
            print("13. Update System Admin last name")
            print("14. Delete System Administrator")
            print("15. Reset System Admin password")
            print("16. Terug")
            min_opt, max_opt = 1, 16
        else:
            print("9. Terug")
            min_opt, max_opt = 1, 9
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
        elif (is_super_admin and choice == 16) or (not is_super_admin and choice == 9):
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(current_user["username"], "Invalid option", "Invalid option", suspicious=True)

def traveller_management_menu(user):
    while True:
        print("\n--- Traveller Management ---")
        print("1. Add Traveller")
        print("2. Update Traveller")
        print("3. Delete Traveller")
        print("4. Search Traveller")
        print("5. Terug")
        choice = get_int_input("Select an option (1-5): ", 1, 5, user)
        if choice is None:
            break
        if choice == 1:
            add_traveller(user)
        elif choice == 2:
            update_traveller(user)
        elif choice == 3:
            delete_traveller(user)
        elif choice == 4:
            search_travellers(user)
        elif choice == 5:
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)

def scooter_management_menu(current_user):
    while True:
        print("\n--- Scooter Management ---")
        print("1. Add Scooter")
        print("2. Update Scooter")
        print("3. Delete Scooter")
        print("4. Search Scooter")
        print("5. Terug")
        choice = get_int_input("Select an option (1-5): ", 1, 5, current_user)
        if choice is None:
            break
        if choice == 1:
            if current_user["role"] in ["super_admin", "system_admin"]:
                add_scooter(current_user)
            else:
                print("Permission denied: Only System Admin or Super Admin can add scooters.")
                log_activity(current_user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 2:
            if current_user["role"] in ["super_admin", "system_admin"]:
                update_scooter()
            elif current_user["role"] in ["engineer", "service_engineer"]:
                update_scooter_by_engineer(current_user)
            else:
                print("Permission denied.")
                log_activity(current_user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 3:
            if current_user["role"] in ["super_admin", "system_admin"]:
                delete_scooter(current_user)
            else:
                print("Permission denied: Only System Admin or Super Admin can delete scooters.")
                log_activity(current_user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 4:
            search_scooters(current_user)
        elif choice == 5:
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(current_user["username"], "Invalid option", "Invalid option", suspicious=True)

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
    
    acknowledge = input("\nAcknowledge these suspicious activities? (yes/no): ").strip().lower()
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
        print("5. Uitloggen")
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

def system_administration_menu(current_user):
    while True:
        print("\n--- System Administration ---")
        print("1. View system logs")
        print("2. Make a system backup")
        print("3. Restore a system backup")
        print("4. Generate restore-code for System Administrator")
        print("5. Revoke restore-code for System Administrator")
        print("6. Terug")
        choice = get_int_input("Select an option (1-6): ", 1, 6, user)
        if choice is None:
            break

        if choice == 1:
            print_logs()
        elif choice == 2:
            backup_name = make_backup(current_user)
            print(f"Backup gemaakt: {backup_name}")
        elif choice == 3:
            if current_user["role"] == "system_admin":
                strike_count = 0
                while strike_count < 4:
                    restore_code = input("Voer je restore-code in: ").strip()
                    if isinstance(restore_code, str) and restore_code:
                        ok, backup_name = use_restore_code_db(decrypt_data(current_user["username"]), restore_code, current_user)
                        if not ok:
                            print("Restore-code ongeldig of niet voor deze gebruiker!")
                            strike_count += 1
                        else:
                            restore_backup_by_name(current_user, backup_name)
                            break
                    else:
                        print("Restore-code mag niet leeg zijn.")
                        strike_count += 1
                if strike_count >= 4:
                    print("Te veel ongeldige pogingen. Keer terug naar menu.")
            else:
                print("Only a System Administrator can restore a backup!")
                log_activity(user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 4:
            if current_user["role"] == "super_admin":
                strike_count = 0
                while strike_count < 4:
                    target_sysadmin = input("Voor welke System Admin? Username: ").strip()
                    if isinstance(target_sysadmin, str) and target_sysadmin:
                        break
                    else:
                        print("Gebruikersnaam mag niet leeg zijn.")
                        strike_count += 1
                if strike_count >= 4:
                    print("Te veel ongeldige pogingen. Keer terug naar menu.")
                    continue
                strike_count = 0
                while strike_count < 4:
                    backup_name = input("Welke backup (volledige bestandsnaam)? ").strip()
                    if isinstance(backup_name, str) and backup_name:
                        break
                    else:
                        print("Backupnaam mag niet leeg zijn.")
                        strike_count += 1
                if strike_count >= 4:
                    print("Te veel ongeldige pogingen. Keer terug naar menu.")
                    continue
                generate_restore_code_db(target_sysadmin, backup_name,current_user)
            else:
                print("Only a Super Administrator can generate a restore-code!")
                log_activity(user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 5:
            if current_user["role"] == "super_admin":
                strike_count = 0
                while strike_count < 4:
                    code = input("Welke restore-code intrekken? ").strip()
                    if isinstance(code, str) and code:
                        revoke_restore_code_db(code,current_user)
                        break
                    else:
                        print("Code mag niet leeg zijn.")
                        strike_count += 1
                if strike_count >= 4:
                    print("Te veel ongeldige pogingen. Keer terug naar menu.")
            else:
                print("Only a Super Administrator can revoke a restore-code!")
                log_activity(user["username"], "Permission denied", "Permission denied", suspicious=True)
        elif choice == 6:
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)


def service_engineer_menu(current_user):
    while True:
        print("\n--- Service Engineer Menu ---")
        print("1. Search Scooter")
        print("2. Update Scooter attributes")
        print("3. Update own password")
        print("4. Uitloggen")
        choice = get_int_input("Select an option (1-4): ", 1, 4)
        if choice is None:
            break
        if choice == 1:
            search_scooters(current_user)
        elif choice == 2:
            update_scooter_by_engineer(current_user)
        elif choice == 3:
            update_service_engineer_password(current_user)
        elif choice == 4:
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")
            log_activity(user["username"], "Invalid option", "Invalid option", suspicious=True)

if __name__ == "__main__":
    main()
