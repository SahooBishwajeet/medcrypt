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
        description="MedCrypt: Hybrid Cryptography-Steganography System for Secure Medical Data Transmission",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Use python main.py {encrypt, decrypt, genkeys} -h for more help specific to each command""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Encrypt command
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a message and hide it in an image",
        description="Encrypts a message with AES+RSA and hides it in an image using DWT steganography",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python main.py encrypt -m message.txt -i cover.png -o stego.png -k public_key.pem",
    )
    encrypt_parser.add_argument(
        "-m", "--message", required=True, help="Path to the message file to encrypt"
    )
    encrypt_parser.add_argument(
        "-i", "--image", required=True, help="Path to the cover image to hide data in"
    )
    encrypt_parser.add_argument(
        "-o", "--output", required=True, help="Path to save the output stego image"
    )
    encrypt_parser.add_argument(
        "-k", "--key", required=True, help="Path to the RSA public key file (.pem)"
    )
    encrypt_parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=0.1,
        help="Embedding strength factor (default: 0.1, range: 0.05-0.2)",
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Extract and decrypt a hidden message",
        description="Extracts hidden data from a stego image and decrypts it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python main.py decrypt -i stego.png -o recovered.txt -k private_key.pem",
    )
    decrypt_parser.add_argument(
        "-i",
        "--image",
        required=True,
        help="Path to the stego image containing hidden data",
    )
    decrypt_parser.add_argument(
        "-o", "--output", required=True, help="Path to save the decrypted output file"
    )
    decrypt_parser.add_argument(
        "-k", "--key", required=True, help="Path to the RSA private key file (.pem)"
    )
    decrypt_parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=0.1,
        help="Embedding strength factor used during encryption (default: 0.1)",
    )

    # Generate keys command
    keys_parser = subparsers.add_parser(
        "genkeys",
        help="Generate RSA key pair",
        description="Generates a new RSA public/private key pair for encryption and decryption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python main.py genkeys -o keys -s 2048",
    )
    keys_parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Directory path to save the generated keys",
    )
    keys_parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=2048,
        choices=[1024, 2048, 3072, 4096],
        help="Key size in bits (default: 2048, options: 1024, 2048, 3072, 4096)",
    )

    return parser.parse_args()


# Update the encrypt_and_hide function
def encrypt_and_hide(
    message_file, cover_image_file, output_file, public_key_file, alpha=0.1
):
    """Encrypt a message and hide it in an image."""
    # Read message
    with open(message_file, "rb") as f:
        message = f.read()

    # Read cover image
    cover_image = cv2.imread(cover_image_file)
    if cover_image is None:
        print(f"Error: Could not read cover image {cover_image_file}")
        sys.exit(1)

    # Convert BGR to RGB
    cover_image = cv2.cvtColor(cover_image, cv2.COLOR_BGR2RGB)

    # Encrypt message
    crypto = HybridCrypto()
    encrypted_data, encrypted_key = crypto.encrypt(message, public_key_file)

    # Combine encrypted data and key for embedding
    # First 4 bytes: length of encrypted key
    key_length = len(encrypted_key).to_bytes(4, byteorder="big")
    combined_data = key_length + encrypted_key + encrypted_data

    print(f"Key length: {len(encrypted_key)} bytes")
    print(f"Data length: {len(encrypted_data)} bytes")
    print(f"Combined data length: {len(combined_data)} bytes")

    # Hide encrypted data in cover image
    stego = DWTSteganography()
    try:
        stego_image = stego.embed(cover_image, combined_data, alpha)

        # Convert RGB back to BGR
        stego_image = cv2.cvtColor(stego_image, cv2.COLOR_RGB2BGR)

        # Determine the output format
        _, ext = os.path.splitext(output_file)
        if ext.lower() in [".jpg", ".jpeg"]:
            # For JPEG, use high quality to minimize data loss
            cv2.imwrite(output_file, stego_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
            print(
                "Warning: JPEG format may cause data loss. Consider using PNG for better results."
            )
        elif ext.lower() == ".png":
            cv2.imwrite(output_file, stego_image)
        else:
            # Default to PNG if extension is unknown
            new_path = output_file + ".png"
            cv2.imwrite(new_path, stego_image)
            print(f"Unknown extension, saved as PNG: {new_path}")
            output_file = new_path

        print(f"Encryption and hiding successful. Stego image saved to {output_file}")

    except ValueError as e:
        print(f"Error during embedding: {e}")
        sys.exit(1)


def extract_and_decrypt(stego_image_file, output_file, private_key_file, alpha=0.1):
    """Extract and decrypt a hidden message from a stego image."""
    # Read stego image
    stego_image = cv2.imread(stego_image_file)
    if stego_image is None:
        print(f"Error: Could not read stego image {stego_image_file}")
        sys.exit(1)

    # Convert BGR to RGB
    stego_image = cv2.cvtColor(stego_image, cv2.COLOR_BGR2RGB)

    # Extract hidden data
    stego = DWTSteganography()
    extracted_data = stego.extract(stego_image, alpha)

    if len(extracted_data) == 0:
        print("Error: Failed to extract data from image")
        sys.exit(1)

    print(f"Extracted data length: {len(extracted_data)} bytes")

    # Ensure we have at least 4 bytes for the key length
    if len(extracted_data) < 4:
        print("Error: Extracted data is too small")
        sys.exit(1)

    # Get key length from first 4 bytes
    key_length = int.from_bytes(extracted_data[:4], byteorder="big")
    print(f"Detected key length from header: {key_length} bytes")

    # Sanity check on key length
    if key_length <= 0 or key_length > len(extracted_data) - 4:
        print(f"Error: Invalid key length: {key_length}")
        sys.exit(1)

    # Get the encrypted key and data
    encrypted_key = bytes(extracted_data[4 : 4 + key_length])
    encrypted_data = bytearray(extracted_data[4 + key_length :])

    print(f"Encrypted key size: {len(encrypted_key)} bytes")
    print(f"Encrypted data size: {len(encrypted_data)} bytes")

    # Decrypt data
    crypto = HybridCrypto()
    try:
        decrypted_data = crypto.decrypt(encrypted_data, encrypted_key, private_key_file)
        print(f"Decrypted data size: {len(decrypted_data)} bytes")
    except Exception as e:
        print(f"Decryption error: {e}")
        sys.exit(1)

    # Write decrypted data to file
    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print(
        f"Extraction and decryption successful. Decrypted message saved to {output_file}"
    )


def generate_keys(output_dir, key_size=2048):
    """Generate RSA key pair."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate keys
    rsa = RSACipher()
    private_key, public_key = rsa.generate_key_pair(key_size)

    # Save keys
    private_path = os.path.join(output_dir, "private_key.pem")
    public_path = os.path.join(output_dir, "public_key.pem")
    rsa.save_keys(private_key, public_key, private_path, public_path)

    print(f"RSA key pair generated.")
    print(f"Private key saved to {private_path}")
    print(f"Public key saved to {public_path}")


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
