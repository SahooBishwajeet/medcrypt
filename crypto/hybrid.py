import os
from .aes import AESCipher
from .rsa import RSACipher


class HybridCrypto:
    def __init__(self):
        """Initialize hybrid cryptography system"""
        self.aes = AESCipher()
        self.rsa = RSACipher()

    def encrypt(self, data, rsa_public_key_path):
        """
        Encrypt data using hybrid encryption:
        1. Generate random AES key
        2. Encrypt data with AES key
        3. Encrypt AES key with RSA public key
        4. Return encrypted data and encrypted key
        """
        # Generate random 16-byte (128-bit) AES key
        aes_key = os.urandom(16)

        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode()

        # Pad data to make its length a multiple of 16 bytes (AES block size)
        pad_length = 16 - (len(data) % 16)
        data = data + bytes([pad_length]) * pad_length

        # Encrypt data with AES
        encrypted_data = bytearray()
        for i in range(0, len(data), 16):
            block = data[i : i + 16]
            encrypted_block = self.aes.encrypt(block, aes_key)
            encrypted_data.extend(encrypted_block)

        # Load RSA public key
        rsa_public_key = self.rsa.load_public_key(rsa_public_key_path)

        # Encrypt AES key with RSA
        encrypted_key = self.rsa.encrypt(aes_key, rsa_public_key)

        return encrypted_data, encrypted_key

    def decrypt(self, encrypted_data, encrypted_key, rsa_private_key_path):
        """
        Decrypt data using hybrid decryption:
        1. Decrypt AES key with RSA private key
        2. Decrypt data with AES key
        3. Return decrypted data
        """
        # Load RSA private key
        rsa_private_key = self.rsa.load_private_key(rsa_private_key_path)

        # Decrypt AES key with RSA
        aes_key = self.rsa.decrypt(encrypted_key, rsa_private_key)

        # Decrypt data with AES
        decrypted_data = bytearray()

        # Make sure encrypted_data length is a multiple of 16
        if len(encrypted_data) % 16 != 0:
            print(
                f"Warning: Encrypted data length ({len(encrypted_data)}) is not a multiple of 16."
            )
            # Padding to 16 bytes if necessary
            padding_needed = 16 - (len(encrypted_data) % 16)
            encrypted_data.extend([0] * padding_needed)

        # Decrypt block by block
        for i in range(0, len(encrypted_data), 16):
            block = encrypted_data[i : i + 16]
            if len(block) == 16:  # Ensure we have a complete block
                decrypted_block = self.aes.decrypt(block, aes_key)
                decrypted_data.extend(decrypted_block)

        # Remove padding
        if decrypted_data:
            pad_length = decrypted_data[-1]
            if pad_length < 16 and all(
                b == pad_length for b in decrypted_data[-pad_length:]
            ):
                return decrypted_data[:-pad_length]

        return decrypted_data
