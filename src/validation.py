# Validates user inputs (e.g., zip code, phone number)  
import re  

def validate_zip(zip_code) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{3}(?!SA|SD|SS)[A-Z]{2}$', zip_code))

def validate_phone(phone) -> bool:  
    return bool(re.fullmatch(r'^\+31-6-\d{8}$', phone))