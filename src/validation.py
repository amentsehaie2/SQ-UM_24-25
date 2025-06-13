import re  
from datetime import datetime

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

def validate_brand(brand) -> bool:
    """
    Validates if the brand is a non-empty string and one of the 10 predefined car brands.
    """
    if not isinstance(brand, str) or not brand.strip():
        return False
    brands = {
        "Volkswagen", "BMW", "Audi", "Mercedes-Benz", "Ford",
        "Toyota", "Peugeot", "Fiat", "Renault", "Citroën"
    }
    return brand.strip() in brands

def validate_model(model) -> bool:
    """
    Validates if the model is a non-empty string and one of the 10 predefined car models.
    """
    if not isinstance(model, str) or not model.strip():
        return False
    models = {
        "Golf", "3-serie", "A4", "C-Klasse", "Focus",
        "Corolla", "308", "Panda", "Clio", "C3"
    }
    return model.strip() in models

def validate_serial_number(serial_number) -> bool:
    """
    Validates if the serial number is a non-empty string and matches the format:
    10 to 17 alphanumeric characters.
    """
    if not isinstance(serial_number, str) or not serial_number.strip():
        return False
    return bool(re.fullmatch(r'^[A-Z0-9]{10,17}$', serial_number.strip()))

def validate_top_speed(top_speed) -> bool:
    """
    Validates if the top speed is a positive integer.
    """
    if not isinstance(top_speed, int) or top_speed <= 0:
        return False
    return True

def validate_battery_capacity(battery_capacity) -> bool:
    """
    Validates if the battery capacity is a positive integer.
    """
    if not isinstance(battery_capacity, int) or battery_capacity <= 0:
        return False
    return True

def validate_SoC(SoC) -> bool:
    """
    Validates if the State of Charge (SoC) is a percentage between 0 and 100.
    """
    if not isinstance(SoC, int) or not (0 <= SoC <= 100):
        return False
    return True

def validate_target_range(target_range) -> bool:
    """
    Validates if the target range is a positive integer.
    """
    if not isinstance(target_range, int) or target_range <= 0:
        return False
    return True

def validate_location(location) -> bool:
    """
    Validates if the location is a string in the format 'latitude,longitude' with 5 decimal places.
    Example: '51.92250,4.47917'
    """
    if not isinstance(location, str) or not location.strip():
        return False
    pattern = r'^-?\d{1,2}\.\d{5},-?\d{1,3}\.\d{5}$'
    return bool(re.fullmatch(pattern, location.strip()))

def validate_OoS(OoS) -> bool:
    """
    Validates if the Out of Service (OoS) status is a boolean.
    """
    return isinstance(OoS, bool)

def validate_mileage(mileage) -> bool:
    """
    Validates if the mileage is a positive integer.
    """
    if not isinstance(mileage, int) or mileage < 0:
        return False
    return True

def validate_last_maint(date) -> bool:
    """
    Validates if the last maintenance date is a string in the ISO 8601 format 'YYYY-MM-DD'.
    Example: '2023-10-01'
    """
    if not isinstance(date, str) or not date.strip():
        return False
    if not re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', date.strip()):
        return False
    try:
        datetime.strptime(date.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False