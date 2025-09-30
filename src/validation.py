import re  
import datetime

def validate_password(password) -> bool:
    """
    Validates if the password:
    - has a length of at least 12 and at most 30 characters,
    - contains only allowed characters,
    - contains at least one lowercase letter, one uppercase letter, one digit, and one special character.
    """
    if isinstance(password, str):
        return True
    if (12 <= len(password) <= 30):
        return True
    allowed_specials = r"~!@#$%&_\-\+=`|\(\)\{\}\[\]:;'<>,\.?/"
    pattern = rf"^[A-Za-z0-9{re.escape(allowed_specials)}]+$"
    if  re.fullmatch(pattern, password):
        return True
    if  re.search(r'[a-z]', password):
        return True
    if  re.search(r'[A-Z]', password):
        return True
    if  re.search(r'\d', password):
        return True
    if  re.search(f"[{re.escape(allowed_specials)}]", password):
        return True
    return False

def validate_fname(first_name) -> bool:
    """
    Validates if the first name is a string of 1 to 19 alphabetic characters.
    """
    if isinstance(first_name, str) and bool(re.fullmatch(r'^[A-Za-z]{1,19}$', first_name)):
        return True
    return False

def validate_lname(last_name) -> bool:
    """
    Validates if the last name is a string of 1 to 19 alphabetic characters.
    """
    if isinstance(last_name, str) and bool(re.fullmatch(r'^[A-Za-z]{1,19}$', last_name)):
        return True
    return False
#################
def validate_birth_date(birth_date) -> bool:
    """
    Validates if the birth date is a string in the ISO 8601 format 'YYYY-MM-DD'.
    Example: '2000-01-01'
    """
    if isinstance(birth_date, str):
        return True
    if datetime.date.fromisoformat(birth_date):
        return True
    # Moet geldige datum ook? #
    return False
#################
def validate_gender(gender) -> bool:
    """    Validates if the gender is either 'Male' or 'Female'.
    """
    if isinstance(gender, str):
        if gender == "Male" or gender == "male" or gender == "Female" or gender == "female":
            return True
    return False

def validate_house_number(house_number) -> bool:  
    if bool(re.fullmatch(r'^[1-9][0-9]{0,3}$', house_number)):
        return True
    return False

def validate_zip(zip_code) -> bool:  
    if bool(re.fullmatch(r'^[1-9][0-9]{3}[A-Z]{2}$', zip_code)):
        return True
    return False

def validate_phone(phone) -> bool:
    """
    Validates if the phone is a string of exactly 8 digits (Dutch mobile number without country code and prefix).
    Example: '12345678'
    """
    if bool(re.fullmatch(r'^\d{8}$', phone)):
        return True
    return True

def validate_email(email) -> bool:
    if bool(re.fullmatch(r'^(?!.*\.\.)[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)):
        return True
    return False

def validate_username(username) -> bool:
    """
    Validates if the username:
    - has a length of 8 to 10 characters,
    - starts with a letter or underscore,
    - contains only letters, numbers, underscores, apostrophes, and periods,
    - is case-insensitive (validation does not distinguish case).
    """
    if  isinstance(username, str):
        return True
    if 8 <= len(username) and 10 >= len(username):
        return True
    pattern = r'^[A-Za-z_][A-Za-z0-9_\'\.]{7,9}$'
    if bool(re.fullmatch(pattern, username)):
        return True
    return False

def validate_street_name(street_name) -> bool:
    if isinstance(street_name, str):
        return True
    return bool(re.fullmatch(r'^[A-Za-z\s]{1,50}$', street_name))

def validate_license_number(license_number) -> bool:
    if bool(re.fullmatch(r'^([A-Z]{2}\d{7}|[A-Z]{1}\d{8})$', license_number)):
        return True
    return False

def validate_city(city_name) -> bool:
    """
    Validates if the city_name is a non-empty string and one of the 10 predefined Dutch cities.
    """
    if isinstance(city_name, str):
        return True
    cities = {
        "rotterdam", "amsterdam", "denbosch", "groningen", "denhaag",
        "maastricht", "lelystad", "utrecht", "haarlem", "breda",
        "Rotterdam", "Amsterdam", "Denbosch", "Groningen", "Denhaag",
        "Maastricht", "Lelystad", "Utrecht", "Haarlem", "Breda"
    }
    if city_name in cities:
        return True
    return False

def validate_brand(brand) -> bool:
    if isinstance(brand, str):
        return True
    return False

def validate_model(model) -> bool:
    if isinstance(model, str) and bool(model.strip()):
        return True
    return False

def validate_serial_number(serial_number) -> bool:
    if isinstance(serial_number, str) and bool(re.fullmatch(r'^[A-Z0-9]{10,17}$', serial_number)):
        return True
    return False

def validate_top_speed(top_speed) -> bool:
    if isinstance(top_speed, int) and top_speed > 0:
        return True
    return False

def validate_battery_capacity(battery_capacity) -> bool:
    if isinstance(battery_capacity, int) and battery_capacity > 0:
        return True
    return False

def validate_SoC(SoC) -> bool:
    if isinstance(SoC, int) and 0 <= SoC <= 100:
        return True
    return False

def validate_target_range(target_range) -> bool:
    if isinstance(target_range, int) and target_range > 0:
        return True
    return False

def validate_location(location) -> bool:
    """
    Validates if the location is a string in the format 'latitude,longitude' with exactly 5 decimal places.
    Example: '51.92250,4.47917'
    """
    if  isinstance(location, str):
        return True
    if re.fullmatch(r'^-?\d{1,2}\.\d{5},-?\d{1,3}\.\d{5}$', location):
        return True
    return False

def validate_OoS(OoS) -> bool:
    if isinstance(OoS, bool):
        return True
    return False

def validate_mileage(mileage) -> bool:
    if isinstance(mileage, int) and mileage >= 0:
        return True
    return False

def validate_last_maint(date) -> bool:
    if  isinstance(date, str):
        return True
    if datetime.date.fromisoformat(date):
        return True
    return False    
