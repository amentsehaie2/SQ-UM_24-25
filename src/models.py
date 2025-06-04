from datetime import datetime

class User:
    def __init__(self, id: int, username: str, password: str, role: str, registration_date: datetime):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.registration_date = registration_date



class Traveller:
    def __init__(self, customer_id: int, first_name: str, last_name: str, birth_date: str, 
                 gender: str, street_name: str, house_number: str, zip_code: str, 
                 city: str, email: str, phone_number: str, mobile_phone: str, 
                 license_number: str, registration_date: datetime):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email = email
        self.phone_number = phone_number
        self.mobile_phone = mobile_phone
        self.license_number = license_number
        self.registration_date = registration_date



class Scooter:
    def __init__(self, customer_id: int, brand: str, model: str, serial_number: str, 
                 top_speed: int, battery_capacity: int, state_of_charge: int, 
                 target_range: int, location: str, out_of_service: bool, 
                 mileage: int, last_service_date: datetime):
        self.customer_id = customer_id
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.top_speed = top_speed
        self.battery_capacity = battery_capacity
        self.state_of_charge = state_of_charge
        self.target_range = target_range
        self.location = location
        self.out_of_service = out_of_service
        self.mileage = mileage
        self.last_service_date = last_service_date



class Log:
    def __init__(self, id: int, date: datetime, username: str, 
                 description_of_activity: str, additional_info: str, 
                 suspicious_activity: bool):
        self.id = id
        self.date = date
        self.username = username
        self.description_of_activity = description_of_activity
        self.additional_info = additional_info
        self.suspicious_activity = suspicious_activity