import re
import datetime

def validate_password(password) -> bool:
    """ 
    Validates if the password:
    - has a length of at least 12 and at most 30 characters,
    - contains only allowed characters,
    - contains at least one lowercase letter, one uppercase letter, one digit, and one special character.
    """
    allowed_specials = r"~!@#$%&_\-\+=`|\(\)\{\}\[\]:;'<>,\.?/"
    pattern = rf"^[A-Za-z0-9{re.escape(allowed_specials)}]+$"
    if (12 <= len(password) <= 30):
        if all(re.search(r, password) for r in [r'[a-z]', r'[A-Z]', r'\d', f"[{re.escape(allowed_specials)}]"]) and re.fullmatch(pattern, password):
            return True
        return False
    return False

def validate_fname(first_name: str) -> bool:
    """
    Validates if the first name is a string of 1 to 19 alphabetic characters.
    """
    if re.fullmatch(r'^[A-Za-z]{1,19}$', first_name) is not None:
        return True
    return False

def validate_lname(last_name: str) -> bool:
    """
    Validates if the last name is a string of 1 to 19 alphabetic characters.
    """
    if isinstance(last_name, str) and bool(re.fullmatch(r'^[A-Za-z]{1,19}$', last_name)):
        return True
    return False
#################
def validate_birth_date(birth_date: str) -> bool:
    """
    Validates if the birth date is a string in the ISO 8601 format 'YYYY-MM-DD'.
    Example: '2000-01-01'
    """
    if datetime.date.fromisoformat(birth_date):
        if birth_date < datetime.date.today().strftime("%Y-%m-%d"):
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
    if re.fullmatch(r'^[1-9][0-9]{0,3}$', house_number) is not None:
        return True
    return False

def validate_zip(zip_code) -> bool:  
    if re.fullmatch(r'^[1-9][0-9]{3}[A-Z]{2}$', zip_code) is not None:
        return True
    return False

def validate_phone(phone) -> bool:
    """
    Validates if the phone is a string of exactly 8 digits (Dutch mobile number without country code and prefix).
    Example: '12345678'
    """
    if re.fullmatch(r'^\d{8}$', phone) is not None:
        return True
    return False

def validate_email(email: str) -> bool:
    if bool(re.fullmatch(r'^(?!.*\.\.)[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)):
        return True
    return False

def validate_username(username: str) -> bool:
    """
    Validates if the username:
    - has a length of 8 to 10 characters,
    - starts with a letter or underscore,
    - contains only letters, numbers, underscores, apostrophes, and periods,
    - is case-insensitive (validation does not distinguish case).
    """
    pattern = r'^[A-Za-z_][A-Za-z0-9_\'\.]{7,9}$'
    if 8 <= len(username) <= 10:
        if re.fullmatch(pattern, username) is not None:
            return True
    return False

def validate_street_name(street_name) -> bool:
    return bool(re.fullmatch(r'^[A-Za-z\s]{1,50}$', street_name))

def validate_license_number(license_number) -> bool:
    if bool(re.fullmatch(r'^([A-Z]{2}\d{7}|[A-Z]{1}\d{8})$', license_number)):
        return True
    return False

def validate_city(city_name: str) -> bool:
    """
    Validates if the city_name is a non-empty string and one of the 10 predefined Dutch cities.
    """
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

def valid_phone_number(message, blank=False):
    while True:
        phone = input(message + "31-6-")
        if blank and phone == '':
            return None
        
        if re.match('^[d{0}]', phone) is not None:
            return "+31-6-" + phone
        print("Invalid phone number")

def valid_zipcode(blank=False):
    while True:
        print("Enter zipcode (e.g., 1234AB): ")
        zipcode= input("Enter a valid zipcode").upper()
        if blank and zipcode == '':
            return None
        
        if re.fullmatch('^[1-9][0-9]{3}[A-Z]{2}$', zipcode) is not None:
            return zipcode
        print("Invalid zipcode")