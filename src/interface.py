# Console menus for each user role  
def main_menu(user):  
    if user["role"] == "super_admin":  
        super_admin_menu()  
    elif user["role"] == "system_admin":  
        system_admin_menu()  
    elif user["role"] == "service_engineer":  
        service_engineer_menu()  

def super_admin_menu():  
    print("\n1. Add System Admin\n2. Generate Restore Code\n3. Exit")  