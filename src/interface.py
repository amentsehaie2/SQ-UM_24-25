from auth import login, logout
from operations import (
    add_traveller, update_traveller, delete_traveller, search_travellers,
    add_scooter, update_scooter, delete_scooter, search_scooters,
    add_service_engineer, update_service_engineer_username, update_service_engineer_password,
    update_fname_service_engineer, update_lname_service_engineer, delete_service_engineer,
    reset_service_engineer_password,
    add_system_admin, update_system_admin_username, update_system_admin_password,
    update_fname_system_admin, update_lname_system_admin, delete_system_admin, reset_system_admin_password,
    make_backup, restore_backup, generate_restore_code, revoke_restore_code,
    list_users
)
from logger import mark_suspicious_logs_as_read, print_logs, show_suspicious_alert

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
        
def super_admin_menu(user):
    while True:
        print("\n--- Super Administrator Menu ---")
        print("1. User Management")
        print("2. Traveller Management")
        print("3. Scooter Management")
        print("4. System Administration")
        print("5. Uitloggen")
        choice = input("Select a category (1-5): ")
        if choice == "1":
            user_management_menu()
        elif choice == "2":
            traveller_management_menu()
        elif choice == "3":
            scooter_management_menu()
        elif choice == "4":
            system_administration_menu(user)
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def user_management_menu():
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
        print("9. Add System Administrator")
        print("10. Update System Admin username")
        print("11. Update System Admin password")
        print("12. Update System Admin first name")
        print("13. Update System Admin last name")
        print("14. Delete System Administrator")
        print("15. Reset System Admin password")
        print("16. Terug")
        choice = input("Select an option (1-16): ")
        if choice == "1":
            list_users()
        elif choice == "2":
            add_service_engineer()
        elif choice == "3":
            update_service_engineer_username()
        elif choice == "4":
            update_service_engineer_password()
        elif choice == "5":
            update_fname_service_engineer()
        elif choice == "6":
            update_lname_service_engineer()
        elif choice == "7":
            delete_service_engineer()
        elif choice == "8":
            reset_service_engineer_password()
        elif choice == "9":
            add_system_admin()
        elif choice == "10":
            update_system_admin_username()
        elif choice == "11":
            update_system_admin_password()
        elif choice == "12":
            update_fname_system_admin()
        elif choice == "13":
            update_lname_system_admin()
        elif choice == "14":
            delete_system_admin()
        elif choice == "15":
            reset_system_admin_password()
        elif choice == "16":
            break
        else:
            print("Invalid option. Please try again.")

def traveller_management_menu():
    while True:
        print("\n--- Traveller Management ---")
        print("1. Add Traveller")
        print("2. Update Traveller")
        print("3. Delete Traveller")
        print("4. Search Traveller")
        print("5. Terug")
        choice = input("Select an option (1-5): ")
        if choice == "1":
            add_traveller()
        elif choice == "2":
            update_traveller()
        elif choice == "3":
            delete_traveller()
        elif choice == "4":
            search_travellers()
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")

def scooter_management_menu():
    while True:
        print("\n--- Scooter Management ---")
        print("1. Add Scooter")
        print("2. Update Scooter")
        print("3. Delete Scooter")
        print("4. Search Scooter")
        print("5. Terug")
        choice = input("Select an option (1-5): ")
        if choice == "1":
            add_scooter()
        elif choice == "2":
            update_scooter()
        elif choice == "3":
            delete_scooter()
        elif choice == "4":
            search_scooters()
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")

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

def system_administration_menu(user):
    while True:
        print("\n--- System Administration ---")
        print("1. View system logs")
        print("2. View suspicious activities")  
        print("3. Make a system backup")
        print("4. Restore a system backup")
        print("5. Generate restore-code for System Administrator")
        print("6. Revoke restore-code for System Administrator")
        print("7. Terug")
        choice = input("Select an option (1-7): ")
        if choice == "1":
            print_logs()
        elif choice == "2":
            view_suspicious_logs()
        elif choice == "3":
            make_backup(user)
        elif choice == "4":
            restore_backup(user)
        elif choice == "5":
            generate_restore_code(user)
        elif choice == "6":
            revoke_restore_code(user)
        elif choice == "7":
            break
        else:
            print("Invalid option. Please try again.")

def service_engineer_menu(user):
    while True:
        print("\n--- Service Engineer Menu ---")
        print("1. Traveller Management")
        print("2. Scooter Management")
        print("3. Update own username")
        print("4. Update own password")
        print("5. Update own first name")
        print("6. Update own last name")
        print("7. Uitloggen")
        choice = input("Select an option (1-7): ")
        if choice == "1":
            traveller_management_menu()
        elif choice == "2":
            scooter_management_menu()
        elif choice == "3":
            update_service_engineer_username()
        elif choice == "4":
            update_service_engineer_password()
        elif choice == "5":
            update_fname_service_engineer()
        elif choice == "6":
            update_lname_service_engineer()
        elif choice == "7":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
