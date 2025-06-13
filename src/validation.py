import re  

def validate_fname(first_name) -> bool:  
    return bool(re.fullmatch(r'^[A-Z][a-z]{1,19}$', first_name))

def validate_lname(last_name) -> bool:
    return bool(re.fullmatch(r'^[A-Z][a-z]{1,19}$', last_name))

def validate_house_number(house_number) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{0,3}$', house_number))

def validate_zip(zip_code) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{3}[A-Z]{2}$', zip_code))

def validate_phone(phone) -> bool:  
    return bool(re.fullmatch(r'^\+31-6-\d{8}$', phone))

def validate_email(email) -> bool:
    return bool(re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_username(username) -> bool:
    return bool(re.fullmatch(r'^[a-zA-Z0-9_]{3,20}$', username))

def validate_street_name(street_name) -> bool:
    if not isinstance(street_name, str) or not street_name.strip():
        return False
    return bool(re.fullmatch(r'^[A-Za-z\s]{1,50}$', street_name.strip()))

def validate_license_number(license_number) -> bool:
    return bool(re.fullmatch(r'^([A-Z]{2}\d{7}|[A-Z]{1}\d{8})$', license_number))

def validate_city(city_name) -> bool:
    """
    Validates if the city_name is a non-empty string and one of the 10 predefined Dutch cities.
    """
    if not isinstance(city_name, str) or not city_name.strip():
        return False
    cities = {
        "Rotterdam", "Amsterdam", "Den Bosch", "Groningen", "Den Haag",
        "Maastricht", "Lelystad", "Utrecht", "Haarlem", "Breda"
    }
    return city_name.strip() in cities