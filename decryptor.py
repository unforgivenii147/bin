#!/data/data/com.termux/files/usr/bin/python
"""
A file encryption/decryption tool using AES-256 CBC mode.
Processes all files in the current directory, excluding itself.
Warning: This tool modifies files in place.
"""

import os
import glob
import secrets
import string
import argparse
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

AES_BLOCK_SIZE = 16 # bytes
KEY_SIZE = 32 # bytes for AES-256


def generate_secure_key(length: int = 32) -> str:
    """
    Generates a cryptographically secure random alphanumeric key.

    Args:
        length: Length of the key in characters.

    Returns:
        A random string of alphanumeric characters.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def encrypt_file(file_path: str, key: str) -> None:
    """
    Encrypts a file in place using AES-CBC.

    Args:
        file_path: Path to the file to encrypt.
        key: Encryption key (string).
    """
    backend = default_backend()
    iv = os.urandom(AES_BLOCK_SIZE)

    # Ensure key is exactly 32 bytes for AES-256
    encoded_key = key.encode().ljust(KEY_SIZE)[:KEY_SIZE]
    cipher = Cipher(algorithms.AES(encoded_key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        with open(file_path, "wb") as f:
            # prepend IV so decryption can recover it
            f.write(iv + encrypted_data)
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {e}")


def decrypt_file(file_path: str, key: str) -> None:
    """
    Decrypts a file in place using AES-CBC.

    Args:
        file_path: Path to the file to decrypt.
        key: Decryption key (string).
    """
    backend = default_backend()

    try:
        with open(file_path, "rb") as f:
            raw = f.read()

        if len(raw) < AES_BLOCK_SIZE:
            print(f"Skipping {file_path}: File too small to be encrypted.")
            return

        iv = raw[:AES_BLOCK_SIZE]
        ciphertext = raw[AES_BLOCK_SIZE:]

        encoded_key = key.encode().ljust(KEY_SIZE)[:KEY_SIZE]
        cipher = Cipher(algorithms.AES(encoded_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()

        decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

        with open(file_path, "wb") as f:
            f.write(data)
    except Exception as e:
        print(f"Failed to decrypt {file_path}: {e}. Possibly wrong key or corrupted file.")


def main() -> None:
    """
    Orchestrates encryption or decryption of files in the current directory.
    """
    parser = argparse.ArgumentParser(description="AES File Encryptor/Decryptor")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt files")
    parser.add_argument("--decrypt", action="store_true", help="Decrypt files")
    parser.add_argument("--key", help="Key for encryption/decryption")
    args = parser.parse_args()

    if args.encrypt:
        key = args.key if args.key else generate_secure_key()
        print(f"Using key: {key}")
        action = encrypt_file
    elif args.decrypt:
        if not args.key:
            print("Error: Decryption requires --key")
            sys.exit(1)
        key = args.key
        action = decrypt_file
    else:
        parser.print_help()
        sys.exit(1)

    # Get current script name to avoid encrypting/decrypting itself
    script_name = os.path.basename(__file__)

    for file_path in glob.glob("*"):
        if os.path.isfile(file_path) and file_path != script_name:
            print(f"Processing {file_path}...")
            action(file_path, key)


if __name__ == "__main__":
    main()
