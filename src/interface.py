from auth import login, logout
from operations import (
    add_traveller, update_traveller, delete_traveller, search_travellers,
    add_scooter, update_scooter, delete_scooter, search_scooters, add_service_engineer,
    delete_service_engineer, reset_service_engineer_password, update_service_engineer_username,
    add_system_admin, delete_system_admin,
    update_system_admin_username, make_backup, restore_backup,
    generate_restore_code, revoke_restore_code, update_service_engineer_password,
    update_system_admin_password, list_users
)

def main():
    while True:
        user = login()
        if user is None:
            continue
        main_menu(user)
        logout(user)  # wordt aangeroepen als menu klaar is

def main_menu(user):  
    if user["role"] == "super_admin":  
        super_admin_menu()  
    elif user["role"] == "system_admin":  
        system_admin_menu()  
    elif user["role"] == "service_engineer":  
        service_engineer_menu()  

def super_admin_menu():
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
            system_admin_menu()
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
        print("4. Delete Service Engineer")
        print("5. Update Service Engineer password")
        print("6. Add System Administrator")
        print("7. Update System Administrator username")
        print("8. Delete System Administrator")
        print("9. Update System Administrator password")
        print("10. Terug")
        choice = input("Select an option (1-10): ")

        if choice == "1":
            list_users()
        elif choice == "2":
            add_service_engineer()
        elif choice == "3":
            update_service_engineer_username()
        elif choice == "4":
            delete_service_engineer()
        elif choice == "5":
            update_service_engineer_password()
        elif choice == "6":
            add_system_admin()
        elif choice == "7":
            update_system_admin_username()
        elif choice == "8":
            delete_system_admin()
        elif choice == "9":
            update_system_admin_password()
        elif choice == "10":
            break
        else:
            print("Invalid option. Please try again.")

def traveller_management_menu():
    while True:
        print("\n--- Traveller Management ---")
        print("1. Add Traveller")
        print("2. Update Traveller information")
        print("3. Delete Traveller")
        print("4. Search/Retrieve Traveller information")
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
        print("2. Update Scooter information")
        print("3. Delete Scooter")
        print("4. Search/Retrieve Scooter information")
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

def system_admin_menu():
    while True:
        print("\n--- System Administration ---")
        print("1. View system logs")
        print("2. Make a system backup")
        print("3. Restore a system backup")
        print("4. Generate restore-code for System Administrator")
        print("5. Revoke restore-code for System Administrator")
        print("6. Uitloggen")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            view_system_logs()
        elif choice == "2":
            make_backup()
        elif choice == "3":
            restore_backup()
        elif choice == "4":
            generate_restore_code()
        elif choice == "5":
            revoke_restore_code()
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def service_engineer_menu():
    while True:
        print("\n--- Service Engineer Management ---")
        print("1. List users")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer username")
        print("4. Delete Service Engineer")
        print("5. Reset Service Engineer password")
        print("6. Uitloggen")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            list_users()
        elif choice == "2":
            add_service_engineer()
        elif choice == "3":
            update_service_engineer_profile()
        elif choice == "4":
            delete_service_engineer()
        elif choice == "5":
            reset_service_engineer_password()
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
