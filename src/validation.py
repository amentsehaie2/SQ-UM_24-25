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

def validate_birth_date(birth_date: str) -> bool:
    """
    Validates if the birth date is a string in the ISO 8601 format 'YYYY-MM-DD'.
    Example: '2000-01-01'
    """
    parsed_date = datetime.date.fromisoformat(birth_date)
    if parsed_date < datetime.date.today():
        return True
    return False

def validate_gender(gender) -> bool:
    """    Validates if the gender is either 'Male' or 'Female'.
    """
    if isinstance(gender, str):
        if gender == "Male" or gender == "male" or gender == "Female" or gender == "female":
            return True
    return False

def validate_house_number(house_number) -> bool:  
    """
    Validates a Dutch house number input.
    """
    if re.fullmatch(r'^[1-9][0-9]{0,3}$', house_number) is not None:
        return True
    return False

def validate_zip(zip_code) -> bool:
    """
    Validates if the zip_code is a string in the Dutch postal code format '1234AB'.  
    """
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
    """
    Validates if the email is in a standard email format.
    """
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
    """
    Validates if the street name is a string of 1 to 50 alphabetic characters and spaces.
    """
    return bool(re.fullmatch(r'^[A-Za-z\s]{1,50}$', street_name))

def validate_license_number(license_number) -> bool:
    """
    Validates if the license number is in one of the two Dutch formats:
    - Two letters followed by seven digits: 'AB1234567'
    - One letter followed by eight digits: 'A12345678'
    """
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
    """
    Validates if the brand is a non-empty string.
    """
    if isinstance(brand, str):
        return True
    return False

def validate_model(model) -> bool:
    """
    Validates if the model is a non-empty string.
    """
    if isinstance(model, str) and bool(model):
        return True
    return False

def validate_serial_number(serial_number) -> bool:
    """
    Validates if the serial number is an alphanumeric string (uppercase letters and digits) of length 10 to 17.
    """
    if isinstance(serial_number, str) and bool(re.fullmatch(r'^[A-Z0-9]{10,17}$', serial_number)):
        return True
    return False

def validate_top_speed(top_speed) -> bool:
    """
    Validates if the top speed is a positive integer.
    """
    if isinstance(top_speed, int) and top_speed > 0:
        return True
    return False

def validate_battery_capacity(battery_capacity) -> bool:
    """
    Validates if the battery capacity is a positive integer.
    """ 
    if isinstance(battery_capacity, int) and battery_capacity > 0 and battery_capacity <= 100:
        return True
    return False

def validate_SoC(SoC) -> bool:
    """
    Validates if the State of Charge (SoC) is an integer between 0 and 100 (inclusive).
    """
    if isinstance(SoC, int) and 0 <= SoC <= 100:
        return True
    return False

def validate_target_range(target_range) -> bool:
    """ 
    Validates if the target range is a positive integer.
    """
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
    """
    Validates if the Out of Service (OoS) status is a boolean value.
    """
    if isinstance(OoS, bool):
        return True
    return False

def validate_mileage(mileage) -> bool:
    """
    Validates if the mileage is a non-negative integer.
    """
    if isinstance(mileage, int) and mileage >= 0:
        return True
    return False

def validate_last_maint(date) -> bool:
    """
    Validates if the last maintenance date is in the format 'YYYY-MM-DD'.
    """
    if  isinstance(date, str) and datetime.date.fromisoformat(date):
        return True
    return False    

# Duplicate?
def valid_phone_number(message, blank=False):
    """
    Validates a Dutch mobile phone number input.
    """
    while True:
        phone = input(message + "31-6-")
        if blank and phone == '':
            return None
        
        if re.match('^[d{0}]', phone) is not None:
            return "+31-6-" + phone
        print("Invalid phone number")


# Duplicate?
def valid_zipcode(blank=False):
    """ 
    Validates a Dutch zipcode input.
    """
    while True:
        print("Enter zipcode (e.g., 1234AB): ")
        zipcode= input("Enter a valid zipcode")
        if blank and zipcode == '':
            return None
        
        if re.fullmatch('^[1-9][0-9]{3}[A-Z]{2}$', zipcode) is not None:
            return zipcode
        print("Invalid zipcode")