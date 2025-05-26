# Encrypts sensitive data using AES (Fernet)  
from cryptography.fernet import Fernet  

KEY = Fernet.generate_key()  # Store this key securely in config.py  

def encrypt_data(data):  
    return Fernet(KEY).encrypt(data.encode())  

def decrypt_data(encrypted_data):  
    return Fernet(KEY).decrypt(encrypted_data).decode()  