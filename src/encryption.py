import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")

# --- Key file paths within the output directory ---
_PRIVATE_KEY_FILE = os.path.join(_OUTPUT_DIR, ".private-key")
_PUBLIC_KEY_FILE = os.path.join(_OUTPUT_DIR, ".public-key")
_SYMMETRIC_KEY_FILE = os.path.join(_OUTPUT_DIR, ".key") # Stores the Fernet key, encrypted

privateKey = None
publicKey = None
encryptor = None # This will be the Fernet instance

def _initialize_keys():
    """Ensure encryption keys exist, loading or generating them as needed."""
    global privateKey, publicKey, encryptor

    if encryptor is not None: # Already initialized
        return

    # Ensure output directory exists
    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    try:
        # Try loading the RSA keys
        if os.path.exists(_PRIVATE_KEY_FILE) and os.path.exists(_PUBLIC_KEY_FILE):
            with open(_PRIVATE_KEY_FILE, "rb") as f:
                privateKey = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
            with open(_PUBLIC_KEY_FILE, "rb") as f:
                publicKey = serialization.load_pem_public_key(f.read(), backend=default_backend())
        else:
            # Generate new RSA key pair
            privateKey = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048, 
                backend=default_backend()
            )
            publicKey = privateKey.public_key()
            with open(_PRIVATE_KEY_FILE, "wb") as f:
                f.write(privateKey.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            with open(_PUBLIC_KEY_FILE, "wb") as f:
                f.write(publicKey.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            print(f"Generated new RSA key pair and saved to {_PRIVATE_KEY_FILE} and {_PUBLIC_KEY_FILE}")

        if os.path.exists(_SYMMETRIC_KEY_FILE):
            with open(_SYMMETRIC_KEY_FILE, "rb") as f:
                encrypted_fernet_key = f.read()
            fernet_key = _decrypt_asymmetric(encrypted_fernet_key)
        else:
            fernet_key = Fernet.generate_key()
            encrypted_fernet_key = _encrypt_asymmetric(fernet_key)
            with open(_SYMMETRIC_KEY_FILE, "wb") as f:
                f.write(encrypted_fernet_key)
            print(f"Generated new Fernet key, encrypted it, and saved to {_SYMMETRIC_KEY_FILE}")
        
        encryptor = Fernet(fernet_key)

    except Exception as e:
        print(f"Error during key initialization: {e}")
        raise SystemExit(f"Could not initialize encryption keys: {e}")


def _encrypt_asymmetric(data: bytes) -> bytes:
    """Asymmetrically encrypt data using the RSA public key."""
    if publicKey is None:
        _initialize_keys()
    return publicKey.encrypt(
        data,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def _decrypt_asymmetric(encrypted_data: bytes) -> bytes:
    """Asymmetrically decrypt data using the RSA private key."""
    if privateKey is None:
        _initialize_keys()
    return privateKey.decrypt(
        encrypted_data,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def encrypt_data(data: str) -> str:
    """Symmetrically encrypts a string and returns a string."""
    if encryptor is None:
        _initialize_keys()
    if not isinstance(data, str):
        data = str(data) # Ensure data is a string
    encrypted_bytes = encryptor.encrypt(data.encode('utf-8'))
    return encrypted_bytes.decode('utf-8') # Fernet output is base64, safe for UTF-8 decode

def decrypt_data(encrypted_text_data: str) -> str:
    """Symmetrically decrypts a string."""
    if encryptor is None:
        _initialize_keys()
    encrypted_bytes = encrypted_text_data.encode('utf-8')
    decrypted_bytes = encryptor.decrypt(encrypted_bytes)
    return decrypted_bytes.decode('utf-8')

_initialize_keys()

if __name__ == '__main__':
    print("Encryption module loaded. Keys should be initialized.")
