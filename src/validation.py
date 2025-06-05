# Validates user inputs (e.g., zip code, phone number)  
import re  

def validate_zip(zip_code) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{3}(?!SA|SD|SS)[A-Z]{2}$', zip_code))

def validate_phone(phone) -> bool:  
    return bool(re.fullmatch(r'^\+31-6-\d{8}$', phone))

def validate_email(email) -> bool:
    return bool(re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_username(username) -> bool:
    return bool(re.fullmatch(r'^[a-zA-Z0-9_]{3,20}$', username))

def validate_address(address) -> bool:
    return bool(re.fullmatch(r'^[a-zA-Z0-9\s,.-]{5,100}$', address))