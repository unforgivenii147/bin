#!/data/data/com.termux/files/usr/bin/python
"""
A utility to encrypt all files in the current directory using AES-256 (CBC mode).
Each file is encrypted with a randomly generated key.
"""

import os
import glob
import secrets
import string
import sys

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: 'cryptography' library is not installed. Run 'pip install cryptography'.")
    sys.exit(1)


def generate_random_key(length=32):
    """
    Generates a cryptographically secure random key.
    
    Args:
        length (int): The length of the key in bytes. Default is 32 (for AES-256).
        
    Returns:
        str: A random string of letters and digits.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def encrypt_file(file_path, key):
    """
    Encrypts a single file using AES-CBC and PKCS7 padding.
    The Initialization Vector (IV) is prepended to the encrypted data.
    
    Args:
        file_path (str): Path to the file to encrypt.
        key (str): The encryption key (must be 16, 24, or 32 bytes for AES).
    """
    backend = default_backend()
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    with open(file_path, "rb") as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open(file_path, "wb") as f:
        # Store IV + ciphertext so decryption is possible
        f.write(iv + encrypted_data)


def main():
    """
    Main entry point for the encryption utility.
    Generates a key and encrypts all files in the current directory.
    """
    key = generate_random_key()
    print(f"Encryption key: {key}")
    print("Keep this key safe! You will need it to decrypt your files.")

    # Get current script name to avoid encrypting itself
    script_name = os.path.basename(__file__)

    for file_path in glob.glob("*"):
        if os.path.isfile(file_path) and file_path != script_name:
            print(f"Encrypting {file_path}...")
            try:
                encrypt_file(file_path, key)
            except Exception as e:
                print(f"Failed to encrypt {file_path}: {e}")


if __name__ == "__main__":
    main()
