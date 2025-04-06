import numpy as np
import pywt
import cv2
from utils.image_utils import rgb_to_ycbcr, ycbcr_to_rgb


class DWTSteganography:
    def __init__(self):
        """Initialize DWT-based steganography"""
        self.wavelet = "haar"  # Using Haar wavelet

    def embed(self, cover_image, secret_data, alpha=0.1):
        """
        Embeds secret data into cover image using DWT

        Args:
            cover_image: The cover image (RGB)
            secret_data: The secret data (byte array)
            alpha: Embedding strength factor (higher = more visible, more robust)

        Returns:
            Stego image with embedded data
        """
        print(f"Secret data length: {len(secret_data)} bytes")

        # Convert RGB to YCbCr
        ycbcr_img = rgb_to_ycbcr(cover_image)

        # Work with Y channel (luminance)
        y_channel = ycbcr_img[:, :, 0].copy()

        # Apply 2D DWT to Y channel
        coeffs = pywt.dwt2(y_channel, self.wavelet)
        cA, (cH, cV, cD) = coeffs

        # Calculate embedding capacity (in bytes)
        # Only cH for simplicity and reliability
        capacity = cH.size // 8  # 1 bit per coefficient, 8 bits per byte
        print(f"Embedding capacity: {capacity} bytes")

        if len(secret_data) > capacity:
            raise ValueError(
                f"Secret data too large: {len(secret_data)} bytes, capacity: {capacity} bytes"
            )

        # Add a simple marker header to help with extraction
        # Format: [magic number (4 bytes)][data length (4 bytes)][data]
        magic = b"STEG"
        data_len = len(secret_data).to_bytes(4, byteorder="big")
        full_data = magic + data_len + secret_data
        print(f"Full data length with header: {len(full_data)} bytes")

        # Convert data to bit array
        bit_array = []
        for byte in full_data:
            for i in range(7, -1, -1):  # MSB first
                bit_array.append((byte >> i) & 1)

        print(f"Bit array length: {len(bit_array)} bits")

        # Flatten cH for embedding
        cH_flat = cH.flatten()

        # Embed bits
        for i in range(len(bit_array)):
            if bit_array[i] == 1:
                # Set coefficient to have a positive phase
                cH_flat[i] = abs(cH_flat[i]) + alpha
            else:
                # Set coefficient to have a negative phase
                cH_flat[i] = -abs(cH_flat[i]) - alpha

        # Reshape cH back to original shape
        cH_modified = cH_flat.reshape(cH.shape)

        # Reconstruct Y channel
        coeffs_modified = (cA, (cH_modified, cV, cD))
        y_modified = pywt.idwt2(coeffs_modified, self.wavelet)

        # Ensure dimensions match
        h, w = y_channel.shape
        y_modified = y_modified[:h, :w]

        # Replace Y channel in YCbCr image
        stego_ycbcr = ycbcr_img.copy()
        stego_ycbcr[:, :, 0] = np.clip(y_modified, 0, 255)

        # Convert back to RGB
        stego_img_rgb = ycbcr_to_rgb(stego_ycbcr)
        stego_img_rgb = np.clip(stego_img_rgb, 0, 255).astype(np.uint8)

        return stego_img_rgb

    def extract(self, stego_image, alpha=0.1):
        """
        Extract secret data from stego image

        Args:
            stego_image: The stego image with hidden data
            alpha: The embedding strength factor used

        Returns:
            Extracted secret data as byte array
        """
        # Convert RGB to YCbCr
        ycbcr_img = rgb_to_ycbcr(stego_image)

        # Work with Y channel
        y_channel = ycbcr_img[:, :, 0]

        # Apply 2D DWT
        coeffs = pywt.dwt2(y_channel, self.wavelet)
        cA, (cH, cV, cD) = coeffs

        # Flatten cH for bit extraction
        cH_flat = cH.flatten()

        # Extract bits based on coefficient sign
        extracted_bits = []
        for i in range(len(cH_flat)):
            bit = 1 if cH_flat[i] > 0 else 0
            extracted_bits.append(bit)

        print(f"Extracted {len(extracted_bits)} bits total")

        # Convert bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 8 <= len(extracted_bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | extracted_bits[i + j]
                extracted_bytes.append(byte)

        print(f"Extracted {len(extracted_bytes)} bytes")

        # Look for the magic number (STEG)
        if len(extracted_bytes) < 8:
            print("Error: Extracted data too small to contain header")
            return bytearray()

        magic = extracted_bytes[0:4]
        if magic != b"STEG":
            print(f"Error: Invalid magic number: {magic} (expected: STEG)")
            return bytearray()

        # Get data length
        data_len = int.from_bytes(extracted_bytes[4:8], byteorder="big")
        print(f"Data length from header: {data_len} bytes")

        # Validate data length
        if data_len <= 0 or data_len > len(extracted_bytes) - 8:
            print(f"Error: Invalid data length: {data_len}")
            return bytearray()

        # Extract actual data
        secret_data = extracted_bytes[8 : 8 + data_len]
        print(f"Successfully extracted {len(secret_data)} bytes of secret data")

        return secret_data

    def _bytes_to_bits(self, data):
        """Convert bytes to bit array"""
        result = []
        for byte in data:
            # Convert each byte to 8 bits
            for i in range(7, -1, -1):
                result.append((byte >> i) & 1)
        return result

    def _bits_to_bytes(self, bits):
        """Convert bit array to bytes"""
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(min(8, len(bits) - i)):
                byte = (byte << 1) | bits[i + j]
            result.append(byte)
        return result

    def _int_to_bits(self, n, bits_count=32):
        """Convert integer to bit array"""
        result = []
        for i in range(bits_count - 1, -1, -1):
            result.append((n >> i) & 1)
        return result

    def _bits_to_int(self, bits):
        """Convert bit array to integer"""
        n = 0
        for bit in bits:
            n = (n << 1) | bit
        return n
