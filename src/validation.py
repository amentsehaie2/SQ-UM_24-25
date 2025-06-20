import re  
from datetime import datetime

def validate_password(password) -> bool:
    """
    Validates if the password:
    - has a length of at least 12 and at most 30 characters,
    - contains only allowed characters,
    - contains at least one lowercase letter, one uppercase letter, one digit, and one special character.
    """
    if not isinstance(password, str):
        return False
    if not (12 <= len(password) <= 30):
        return False
    allowed_specials = r"~!@#$%&_\-\+=`|\(\)\{\}\[\]:;'<>,\.?/"
    pattern = rf"^[A-Za-z0-9{re.escape(allowed_specials)}]+$"
    if not re.fullmatch(pattern, password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[~!@#$%&_\-\+=`|\(\)\{\}\[\]:;\'<>,\.?/]', password):
        return False
    return True

def validate_fname(first_name) -> bool:
    """
    Validates if the first name is a string of 1 to 19 alphabetic characters.
    """
    if not isinstance(first_name, str):
        return False
    return bool(re.fullmatch(r'^[A-Za-z]{1,19}$', first_name))

def validate_lname(last_name) -> bool:
    """
    Validates if the last name is a string of 1 to 19 alphabetic characters.
    """
    if not isinstance(last_name, str):
        return False
    return bool(re.fullmatch(r'^[A-Za-z]{1,19}$', last_name))

def validate_birth_date(birth_date) -> bool:
    """
    Validates if the birth date is a string in the ISO 8601 format 'YYYY-MM-DD'.
    Example: '2000-01-01'
    """
    if not isinstance(birth_date, str) or not birth_date.strip():
        return False
    if not re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', birth_date.strip()):
        return False
    try:
        datetime.strptime(birth_date.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def validate_gender(gender) -> bool:
    """    Validates if the gender is either 'Male' or 'Female'.
    """
    if not isinstance(gender, str) or not gender.strip():
        return False
    return gender.strip().lower() in {"male", "female"}

def validate_house_number(house_number) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{0,3}$', house_number))

def validate_zip(zip_code) -> bool:  
    return bool(re.fullmatch(r'^[1-9][0-9]{3}[A-Z]{2}$', zip_code))

def validate_phone(phone) -> bool:
    """
    Validates if the phone is a string of exactly 8 digits (Dutch mobile number without country code and prefix).
    Example: '12345678'
    """
    return bool(re.fullmatch(r'^\d{8}$', phone))

def validate_email(email) -> bool:
    return bool(re.fullmatch(r'^(?!.*\.\.)[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_username(username) -> bool:
    """
    Validates if the username:
    - has a length of 8 to 10 characters,
    - starts with a letter or underscore,
    - contains only letters, numbers, underscores, apostrophes, and periods,
    - is case-insensitive (validation does not distinguish case).
    """
    if not isinstance(username, str):
        return False
    username = username.strip()
    if not (8 <= len(username) <= 10):
        return False
    pattern = r'^[A-Za-z_][A-Za-z0-9_\'\.]{7,9}$'
    return bool(re.fullmatch(pattern, username))

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

def validate_brand(brand) -> bool:
    return isinstance(brand, str)

def validate_model(model) -> bool:
    return isinstance(model, str) and bool(model.strip())

def validate_serial_number(serial_number) -> bool:
    return isinstance(serial_number, str) and bool(re.fullmatch(r'^[A-Z0-9]{10,17}$', serial_number.strip()))

def validate_top_speed(top_speed) -> bool:
    return isinstance(top_speed, int) and top_speed > 0

def validate_battery_capacity(battery_capacity) -> bool:
    return isinstance(battery_capacity, int) and battery_capacity > 0

def validate_SoC(SoC) -> bool:
    return isinstance(SoC, int) and 0 <= SoC <= 100

def validate_target_range(target_range) -> bool:
    return isinstance(target_range, int) and target_range > 0

def validate_location(location) -> bool:
    """
    Validates if the location is a string in the format 'latitude,longitude' with exactly 5 decimal places.
    Example: '51.92250,4.47917'
    """
    if not isinstance(location, str):
        return False
    try:
        lat_str, lon_str = location.strip().split(',')
        lat = float(lat_str)
        lon = float(lon_str)
        pattern = r'^-?\d{1,2}\.\d{5},-?\d{1,3}\.\d{5}$'
        return (
            -90 <= lat <= 90 and
            -180 <= lon <= 180 and
            re.fullmatch(pattern, location.strip()) is not None
        )
    except (ValueError, AttributeError):
        return False

def validate_OoS(OoS) -> bool:
    return isinstance(OoS, bool)

def validate_mileage(mileage) -> bool:
    return isinstance(mileage, int) and mileage >= 0

def validate_last_maint(date) -> bool:
    if not isinstance(date, str) or not date.strip():
        return False
    try:
        datetime.strptime(date.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_password(password):
    """
    Validates if the password:
    - has a length of at least 12 and at most 30 characters,
    - contains only allowed characters,
    - contains at least one lowercase letter, one uppercase letter, one digit, and one special character.
    """
    if not isinstance(password, str):
        return False
    if not (12 <= len(password) <= 30):
        return False
    allowed_specials = r"~!@#$%&_\-\+=`|\(\)\{\}\[\]:;'<>,\.?/"
    pattern = rf"^[A-Za-z0-9{re.escape(allowed_specials)}]+$"
    if not re.fullmatch(pattern, password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(f"[{re.escape(allowed_specials)}]", password):
        return False
    return True