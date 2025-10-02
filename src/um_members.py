# Main entry point for the Urban Mobility backend system  
from auth import login  
from database import initialize_db
from interface import main_menu  

if __name__ == "__main__":  
    current_user = login()  
    if current_user:  
        main_menu(current_user)
        initialize_db()  