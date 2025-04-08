# MedCrypt : Hybrid Cryptographic-Steganographic Framework for Secure Medical Data Transmission Healthcare Systems

## Overview

MedCrypt is a hybrid cryptography and steganography system designed specifically for secure medical data transmission. The framework leverages both cryptographic techniques (AES and RSA) and steganographic methods (DWT-based image hiding) to provide multi-layered security for sensitive healthcare information.

## Features

- **Hybrid Encryption**:

  - AES-128 for fast symmetric encryption of data
  - RSA-2048 for secure key exchange

- **DWT-based Image Steganography**:

  - Hides encrypted data within medical images using discrete wavelet transform
  - Maintains visual quality of cover images
  - Resistant to basic steganalysis

- **Command Line Interface**:
  - Easy-to-use commands for encryption, decryption, and key generation
  - Support for various image formats

## Requirements

- Python 3.6+
- NumPy
- PyWavelets (pywt)
- OpenCV (cv2)
- cryptography
- PyWavelets (pywt)
- OpenCV (cv2)
- cryptography

## Installation

1. Clone the repository:

```bash
git clone https://github.com/SahooBishwajeet/medcrypt.git
cd medcrypt
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Key Generation

Generate RSA keys for encryption and decryption:

```bash
python main.py genkeys -o directory_path
```

### Encrypt & Hide Data

Encrypt a file and hide it within a cover image:

```bash
python main.py encrypt -m message.txt -i cover_image.png -o stego_image.png -k path_to_public_key.pem
```

Parameters:

- `-m, --message`: Path to the message file to be encrypted and hidden.
- `-i, --image`: Path to the cover image where the message will be hidden.
- `-o, --output`: Path to the output stego image.
- `-k, --key`: Path to the public key file for encryption.
- `-a, --alpha`: (Optional) Embedding strength (default is 0.1). Higher values may reduce image quality.

### Extract & Decrypt Data


Extract hidden data from a stego image and decrypt it:

```bash
python main.py decrypt -i stego_image.png -o extracted_message.txt -k path_to_private_key.pem
```

Parameters:

- `-i, --image`: Path to the stego image from which the message will be extracted.
- `-o, --output`: Path to the output file where the extracted message will be saved.
- `-k, --key`: Path to the private key file for decryption.
- `-a, --alpha`: (Optional) Embedding strength (default is 0.1). Higher values may reduce image quality.

## Best Practices

- Always use PNG format for stego images to avoid lossy compression.
Extract hidden data from a stego image and decrypt it:

```bash
python main.py decrypt -i stego_image.png -o extracted_message.txt -k path_to_private_key.pem
```

Parameters:

- `-i, --image`: Path to the stego image from which the message will be extracted.
- `-o, --output`: Path to the output file where the extracted message will be saved.
- `-k, --key`: Path to the private key file for decryption.
- `-a, --alpha`: (Optional) Embedding strength (default is 0.1). Higher values may reduce image quality.

## Best Practices

- Always use PNG format for stego images to avoid lossy compression.
- Keep the alpha value balanced (0.1-0.2) for good image quality
- Ensure the cover image has sufficient capacity for your message
- Keep private keys secure and never share them

## Limitations

- JPEG compression can destroy hidden data due to lossy compression
- Large messages require proportionally large cover images
- The steganography method focuses on security rather than capacity
