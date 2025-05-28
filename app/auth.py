import hashlib
import os
import base64
from sqlalchemy.exc import IntegrityError

from app.database import User, get_session

# simple key for encryption, ниче путного не придумал
ENCRYPTION_KEY = b'ThisIsA16ByteKey'


def encrypt_password(password):
    # encrypting a password using a simple hash
    return hashlib.sha256(password.encode()).hexdigest()


def encrypt_data(data):
    # simple XOR-based method, NOT real secure, but works without dependencies
    if not isinstance(data, str):
        data = str(data)

    # Convert data to bytes
    data_bytes = data.encode('utf-8')

    # Simple XOR with the key (cycled)
    key_len = len(ENCRYPTION_KEY)
    encrypted = bytearray()

    for i, byte in enumerate(data_bytes):
        key_byte = ENCRYPTION_KEY[i % key_len]
        encrypted.append(byte ^ key_byte)

    # encode as base64 for safe storage
    return base64.b64encode(encrypted)


def decrypt_data(encrypted_data):
    # Decode base64
    encrypted = base64.b64decode(encrypted_data)

    key_len = len(ENCRYPTION_KEY)
    decrypted = bytearray()

    for i, byte in enumerate(encrypted):
        key_byte = ENCRYPTION_KEY[i % key_len]
        decrypted.append(byte ^ key_byte)

    # Convert back to string
    return decrypted.decode('utf-8')


def register_user(username, password):
    session = get_session()

    try:
        # Check if exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            session.close()
            return False, "Username already exists"

        # Encrypt password
        encrypted_password = encrypt_password(password)

        # Create new user
        new_user = User(username=username, password=encrypted_password)
        session.add(new_user)
        session.commit()

        # default categories for the new user
        from app.budget import create_default_categories
        create_default_categories(new_user.id)

        session.close()
        return True, "User registered successfully"

    except IntegrityError:
        session.rollback()
        session.close()
        return False, "An error occurred during registration"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An unexpected error occurred: {str(e)}"


def login_user(username, password):
    session = get_session()

    try:
        # Encrypt password
        encrypted_password = encrypt_password(password)

        # Find user
        user = session.query(User).filter_by(username=username, password=encrypted_password).first()

        if user:
            result = (True, user)
        else:
            result = (False, "Invalid username or password")

        session.close()
        return result

    except Exception as e:
        session.close()
        return False, f"An error occurred during login: {str(e)}"