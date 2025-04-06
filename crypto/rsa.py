import numpy as np
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class RSACipher:
    def __init__(self):
        """Initialize RSA cipher"""
        pass

    def generate_key_pair(self, key_size=2048):
        """Generate a new RSA key pair"""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        public_key = private_key.public_key()

        return private_key, public_key

    def save_keys(self, private_key, public_key, private_path, public_path):
        """Save keys to files"""
        # Save private key
        with open(private_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # Save public key
        with open(public_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

    def load_public_key(self, path):
        """Load public key from file"""
        with open(path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        return public_key

    def load_private_key(self, path):
        """Load private key from file"""
        with open(path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        return private_key

    def encrypt(self, message, public_key):
        """Encrypt a message using RSA public key"""
        if isinstance(message, str):
            message = message.encode()

        # RSA encryption with OAEP padding
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return ciphertext

    def decrypt(self, ciphertext, private_key):
        """Decrypt a message using RSA private key"""
        if isinstance(ciphertext, bytearray):
            ciphertext = bytes(ciphertext)

        # RSA decryption with OAEP padding
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return plaintext
