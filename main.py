import argparse
import os
import sys
import numpy as np
import cv2
from crypto.hybrid import HybridCrypto
from steganography.dwt import DWTSteganography
from crypto.rsa import RSACipher
from cryptography.hazmat.primitives import serialization


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MedCrypt : Hybrid Cryptography-Steganography System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Encrypt command
    encrypt_parser = subparsers.add_parser(
        "encrypt", help="Encrypt a message and hide it in an image"
    )
    encrypt_parser.add_argument(
        "-m", "--message", required=True, help="Message file to encrypt"
    )
    encrypt_parser.add_argument(
        "-i", "--image", required=True, help="Cover image to hide data in"
    )
    encrypt_parser.add_argument(
        "-o", "--output", required=True, help="Output stego image filename"
    )
    encrypt_parser.add_argument(
        "-k", "--key", required=True, help="RSA public key file"
    )
    encrypt_parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=0.1,
        help="Embedding strength (default: 0.1)",
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Extract and decrypt a hidden message"
    )
    decrypt_parser.add_argument(
        "-i", "--image", required=True, help="Stego image containing hidden data"
    )
    decrypt_parser.add_argument(
        "-o", "--output", required=True, help="Output file for decrypted message"
    )
    decrypt_parser.add_argument(
        "-k", "--key", required=True, help="RSA private key file"
    )
    decrypt_parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=0.1,
        help="Embedding strength (default: 0.1)",
    )

    # Generate keys command
    keys_parser = subparsers.add_parser("genkeys", help="Generate RSA key pair")
    keys_parser.add_argument(
        "-o", "--output", required=True, help="Output directory for keys"
    )
    keys_parser.add_argument(
        "-s", "--size", type=int, default=2048, help="Key size in bits (default: 2048)"
    )

    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    if args.command == "encrypt":
        encrypt_and_hide(args.message, args.image, args.output, args.key, args.alpha)

    elif args.command == "decrypt":
        extract_and_decrypt(args.image, args.output, args.key, args.alpha)

    elif args.command == "genkeys":
        generate_keys(args.output, args.size)

    else:
        print("Please specify a command. Use -h for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
