# Console menus for each user role  

from operations import (
    add_traveller, update_traveller, delete_traveller, search_travellers,
    add_scooter, update_scooter, delete_scooter, search_scooters,
    list_users_and_roles, add_service_engineer, update_service_engineer_profile,
    delete_service_engineer, reset_service_engineer_password, view_system_logs,
    add_system_admin, update_system_admin_profile, delete_system_admin,
    reset_system_admin_password, make_backup, restore_backup,
    generate_restore_code, revoke_restore_code, update_service_engineer_password,
    update_system_admin_password
)

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
        print("5. Update Service Engineer password")
        print("6. Add System Administrator")
        print("7. Update System Administrator profile")
        print("8. Delete System Administrator")
        print("9. Update System Administrator password")
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
            update_service_engineer_password()
        elif choice == "6":
            add_system_admin()
        elif choice == "7":
            update_system_admin_profile()
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
        print("5. Back")
        choice = input("Select an option (1-5): ")

        if choice == "1":
            # Collect input and call add_traveller
            first_name = input("First name: ")
            last_name = input("Last name: ")
            birth_date = input("Birth date (YYYY-MM-DD): ")
            gender = input("Gender: ")
            street_name = input("Street name: ")
            house_number = input("House number: ")
            zip_code = input("Zip code: ")
            city = input("City: ")
            email = input("Email: ")
            phone_number = input("Phone number: ")
            mobile_phone = input("Mobile phone: ")
            license_number = input("License number: ")
            add_traveller(
                first_name, last_name, birth_date, gender, street_name, house_number,
                zip_code, city, email, phone_number, mobile_phone, license_number
            )
        elif choice == "2":
            customer_id = input("Traveller ID to update: ")
            print("Leave fields blank to skip updating them.")
            fields = {}
            for field in [
                "first_name", "last_name", "birth_date", "gender", "street_name",
                "house_number", "zip_code", "city", "email", "phone_number",
                "mobile_phone", "license_number"
            ]:
                value = input(f"{field.replace('_', ' ').capitalize()}: ")
                if value.strip():
                    fields[field] = value
            if fields:
                update_traveller(customer_id, **fields)
            else:
                print("No fields to update.")
        elif choice == "3":
            customer_id = input("Traveller ID to delete: ")
            delete_traveller(customer_id)
        elif choice == "4":
            key = input("Search key (first or last name): ")
            results = search_travellers(key)
            for row in results:
                print(row)
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
            brand = input("Brand: ")
            model = input("Model: ")
            serial_number = input("Serial number: ")
            top_speed = input("Top speed: ")
            battery_capacity = input("Battery capacity: ")
            state_of_charge = input("State of charge: ")
            target_range = input("Target range: ")
            location = input("Location: ")
            out_of_service = input("Out of service (True/False): ")
            mileage = input("Mileage: ")
            last_service_date = input("Last service date (YYYY-MM-DD): ")
            add_scooter(
                brand, model, serial_number, top_speed, battery_capacity,
                state_of_charge, target_range, location, out_of_service,
                mileage, last_service_date
            )
        elif choice == "2":
            scooter_id = input("Scooter ID to update: ")
            print("Leave fields blank to skip updating them.")
            fields = {}
            for field in [
                "brand", "model", "serial_number", "top_speed", "battery_capacity",
                "state_of_charge", "target_range", "location", "out_of_service",
                "mileage", "last_service_date"
            ]:
                value = input(f"{field.replace('_', ' ').capitalize()}: ")
                if value.strip():
                    fields[field] = value
            if fields:
                update_scooter(scooter_id, **fields)
            else:
                print("No fields to update.")
        elif choice == "3":
            scooter_id = input("Scooter ID to delete: ")
            delete_scooter(scooter_id)
        elif choice == "4":
            key = input("Search key (brand, model, or serial number): ")
            results = search_scooters(key)
            for row in results:
                print(row)
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
