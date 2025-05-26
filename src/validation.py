# Validates user inputs (e.g., zip code, phone number)  
import re  

def validate_zip(zip_code):  
    return re.match(r"^\d{4}[A-Z]{2}$", zip_code)  

def validate_phone(phone):  
    return re.match(r"^\+31-6-\d{9}$", phone)  