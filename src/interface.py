# Console menus for each user role  
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
        print("5. Exit to main menu")
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
            print("Returning to main menu...")
            break
        else:
            print("Invalid option. Please try again.")

def user_management_menu():
    while True:
        print("\n--- User Management ---")
        print("1. List users and roles")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer profile")
        print("4. Delete Service Engineer")
        print("5. Reset Service Engineer password")
        print("6. Add System Administrator")
        print("7. Update System Administrator profile")
        print("8. Delete System Administrator")
        print("9. Reset System Administrator password")
        print("10. Back")
        choice = input("Select an option (1-10): ")

        if choice == "1":
            list_users_and_roles()
        elif choice == "2":
            add_service_engineer()
        elif choice == "3":
            update_service_engineer_profile()
        elif choice == "4":
            delete_service_engineer()
        elif choice == "5":
            reset_service_engineer_password()
        elif choice == "6":
            add_system_admin()
        elif choice == "7":
            update_system_admin_profile()
        elif choice == "8":
            delete_system_admin()
        elif choice == "9":
            reset_system_admin_password()
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
        print("5. Back")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            add_traveller()
        elif choice == "2":
            update_traveller()
        elif choice == "3":
            delete_traveller()
        elif choice == "4":
            search_traveller()
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
        print("5. Back")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            add_scooter()
        elif choice == "2":
            update_scooter()
        elif choice == "3":
            delete_scooter()
        elif choice == "4":
            search_scooter()
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
        print("6. Back")
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
            break
        else:
            print("Invalid option. Please try again.")

def service_engineer_menu():
    while True:
        print("\n--- Service Engineer Management ---")
        print("1. List users and roles")
        print("2. Add Service Engineer")
        print("3. Update Service Engineer profile")
        print("4. Delete Service Engineer")
        print("5. Reset Service Engineer password")
        print("6. Back")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            list_users_and_roles()
        elif choice == "2":
            add_service_engineer()
        elif choice == "3":
            update_service_engineer_profile()
        elif choice == "4":
            delete_service_engineer()
        elif choice == "5":
            reset_service_engineer_password()
        elif choice == "6":
            break
        else:
            print("Invalid option. Please try again.")

# Placeholder functions for menu actions
def list_users_and_roles():
    print("Listing users and roles...")

def add_service_engineer():
    print("Adding a new Service Engineer...")

def update_service_engineer_profile():
    print("Updating Service Engineer profile...")

def delete_service_engineer():
    print("Deleting Service Engineer account...")

def reset_service_engineer_password():
    print("Resetting Service Engineer password...")

def add_traveller():
    print("Adding a new Traveller...")

def update_traveller():
    print("Updating Traveller information...")

def delete_traveller():
    print("Deleting Traveller...")

def search_traveller():
    print("Searching/Retrieving Traveller information...")

def add_scooter():
    print("Adding a new Scooter...")

def update_scooter():
    print("Updating Scooter information...")

def delete_scooter():
    print("Deleting Scooter...")

def search_scooter():
    print("Searching/Retrieving Scooter information...")

def view_system_logs():
    print("Viewing system logs...")

def add_system_admin():
    print("Adding a new System Administrator...")

def update_system_admin_profile():
    print("Updating System Administrator profile...")

def delete_system_admin():
    print("Deleting System Administrator account...")

def reset_system_admin_password():
    print("Resetting System Administrator password...")

def make_backup():
    print("Making a system backup...")

def restore_backup():
    print("Restoring a system backup...")

def generate_restore_code():
    print("Generating restore-code for System Administrator...")

def revoke_restore_code():
    print("Revoking restore-code for System Administrator...")