from auth import login, logout
from operations import (
    add_traveller, update_traveller, delete_traveller, search_travellers,
    add_scooter, update_scooter, delete_scooter, search_scooters,
    add_service_engineer, update_service_engineer_username, update_service_engineer_password,
    delete_service_engineer, reset_service_engineer_password,
    add_system_admin, update_system_admin_username, update_system_admin_password,
    delete_system_admin, reset_system_admin_password,
    make_backup, restore_backup, generate_restore_code, revoke_restore_code,
    list_users
)
from logger import print_logs

def main():
    while True:
        user = login()
        if user is None:
            continue
        main_menu(user)
        logout(user)

def main_menu(current_user):
    role = current_user["role"]
    if role == "super_admin":
        super_admin_menu(current_user)
    elif role == "admin":
        system_admin_menu(current_user)
    elif role == "engineer" or role == "service_engineer":
        service_engineer_menu(current_user)
    else:
        print("Unknown role. Exiting.")

def super_admin_menu(current_user):
    while True:
        print("\n--- Super Administrator Menu ---")
        print("1. User Management")
        print("2. Traveller Management")
        print("3. Scooter Management")
        print("4. System Administration")
        print("5. Reset Service Engineer password")
        print("6. Logout")
        choice = input("Select a category (1-6): ")

        if choice == "1":
            user_management_menu(current_user)
        elif choice == "2":
            traveller_management_menu(current_user)
        elif choice == "3":
            scooter_management_menu(current_user)
        elif choice == "4":
            system_admin_menu(current_user)
        elif choice == "5":
            reset_service_engineer_password(current_user)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def user_management_menu(current_user):
    while True:
        print("\n--- User Management ---")
        print("1. List users")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer username")
        print("4. Delete Service Engineer")
        print("5. Update Service Engineer password")
        print("6. Reset Service Engineer password")
        print("7. Add System Administrator")
        print("8. Update System Administrator username")
        print("9. Delete System Administrator")
        print("10. Update System Administrator password")
        print("11. Reset System Admin password")
        print("12. Back")
        choice = input("Select an option (1-12): ")

        if choice == "1":
            list_users()
        elif choice == "2":
            add_service_engineer(current_user)
        elif choice == "3":
            update_service_engineer_username(current_user)
        elif choice == "4":
            delete_service_engineer(current_user)
        elif choice == "5":
            update_service_engineer_password(current_user)
        elif choice == "6":
            reset_service_engineer_password(current_user)
        elif choice == "7":
            add_system_admin(current_user)
        elif choice == "8":
            update_system_admin_username(current_user)
        elif choice == "9":
            delete_system_admin(current_user)
        elif choice == "10":
            update_system_admin_password(current_user)
        elif choice == "11":
            reset_system_admin_password(current_user)
        elif choice == "12":
            break
        else:
            print("Invalid option. Please try again.")

def traveller_management_menu(current_user):
    while True:
        print("\n--- Traveller Management ---")
        print("1. Add Traveller")
        print("2. Update Traveller information")
        print("3. Delete Traveller")
        print("4. Search/Retrieve Traveller information")
        print("5. Back")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            add_traveller(current_user)
        elif choice == "2":
            update_traveller(current_user)
        elif choice == "3":
            delete_traveller(current_user)
        elif choice == "4":
            search_travellers(current_user)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")

def scooter_management_menu(current_user):
    while True:
        print("\n--- Scooter Management ---")
        print("1. Add Scooter")
        print("2. Update Scooter information")
        print("3. Delete Scooter")
        print("4. Search/Retrieve Scooter information")
        print("5. Back")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            add_scooter(current_user)
        elif choice == "2":
            update_scooter(current_user)
        elif choice == "3":
            delete_scooter(current_user)
        elif choice == "4":
            search_scooters(current_user)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")

def system_admin_menu(current_user):
    while True:
        print("\n--- System Administration ---")
        print("1. View system logs")
        print("2. Make a system backup")
        print("3. Restore a system backup")
        print("4. Generate restore-code for System Administrator")
        print("5. Revoke restore-code for System Administrator")
        print("6. Reset Service Engineer password")
        print("7. Logout")
        choice = input("Select an option (1-7): ")

        if choice == "1":
            print_logs()
        elif choice == "2":
            make_backup(current_user)
        elif choice == "3":
            restore_backup(current_user)
        elif choice == "4":
            generate_restore_code(current_user)
        elif choice == "5":
            revoke_restore_code(current_user)
        elif choice == "6":
            reset_service_engineer_password(current_user)
        elif choice == "7":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def service_engineer_menu(current_user):
    while True:
        print("\n--- Service Engineer Management ---")
        print("1. List users")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer username")
        print("4. Delete Service Engineer")
        print("5. Reset Service Engineer password")
        print("6. Logout")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            list_users()
        elif choice == "2":
            add_service_engineer(current_user)
        elif choice == "3":
            update_service_engineer_username(current_user)
        elif choice == "4":
            delete_service_engineer(current_user)
        elif choice == "5":
            reset_service_engineer_password(current_user)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
