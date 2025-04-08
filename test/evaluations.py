
import os
import cv2
import csv
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import encrypt_and_hide

# Function to calculate Mean Squared Error (MSE)
def calculate_mse(image1, image2):
    """Calculate MSE between two images."""
    # Make sure both images are same shape
    if image1.shape != image2.shape:
        raise ValueError("Images must be the same size")

    squared_error = np.sum((image1.astype("float") - image2.astype("float")) ** 2)

    # Standard MSE calculation
    mse = squared_error / (image1.shape[0] * image1.shape[1])

    if len(image1.shape) > 2:  # If the image has multiple channels
        mse /= image1.shape[2]

    return mse

# Function to calculate Peak Signal-to-Noise Ratio (PSNR)
def calculate_psnr(mse, max_pixel=255.0):
    """Compute Peak Signal-to-Noise Ratio given MSE."""
    if mse == 0:
        return float('inf')
    return 10 * np.log10(max_pixel**2 / mse)

# Function to calculate Structural Similarity Index (SSIM)
def calculate_ssim(image1, image2):
    """Calculate SSIM between two images."""
    # Convert images to grayscale if they're not already
    if len(image1.shape) > 2:
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    else:
        gray1 = image1
        gray2 = image2

    # Manual implementation of SSIM
    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2

    # Compute means
    mu1 = cv2.GaussianBlur(gray1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(gray2, (11, 11), 1.5)

    # Compute mean square
    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    # Compute variances and covariance
    sigma1_sq = cv2.GaussianBlur(gray1 * gray1, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(gray2 * gray2, (11, 11), 1.5) - mu2_sq
    sigma12 = cv2.GaussianBlur(gray1 * gray2, (11, 11), 1.5) - mu1_mu2

    # SSIM formula
    num = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
    den = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)

    ssim_map = num / den
    ssim_index = np.mean(ssim_map)

    return ssim_index

# Function to extract text of specific length from a file
def extract_text_with_length(file_path, byte_length):
    """Extract text of specified byte length from a file."""
    with open(file_path, 'rb') as f:
        content = f.read()

    # Ensure we don't exceed the file size
    if byte_length > len(content):
        print(f"Warning: Requested {byte_length} bytes but file only has {len(content)} bytes")
        return content

    return content[:byte_length]

# Function to save text to a temporary file
def save_temp_text(content, output_path):
    """Save content to a temporary file."""
    with open(output_path, 'wb') as f:
        f.write(content)

# Main evaluation function
def run_comprehensive_evaluation():
    # Paths
    cover_image_path = "./in/medical_image.png"
    public_key_path = "../keys/public_key.pem"
    secret_message_path = "./in/secret_message.txt"
    temp_message_dir = "./eval_text"
    output_dir = "./eval_out"
    csv_file_path = "./comprehensive_metrics.csv"

    # Message sizes to evaluate (in bytes)
    message_sizes = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    # Create necessary directories
    os.makedirs(temp_message_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Generate RSA keys if they don't exist
    keys_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'keys'))
    if not os.path.exists(os.path.join(keys_dir, "public_key.pem")):
        os.makedirs(keys_dir, exist_ok=True)
        print("Generating RSA keys...")
        from crypto.rsa import RSACipher
        rsa = RSACipher()
        private_key, public_key = rsa.generate_key_pair(2048)
        private_path = os.path.join(keys_dir, "private_key.pem")
        public_path = os.path.join(keys_dir, "public_key.pem")
        rsa.save_keys(private_key, public_key, private_path, public_path)
        public_key_path = public_path

    # Load the cover image
    cover_image = cv2.imread(cover_image_path)
    if cover_image is None:
        raise FileNotFoundError(f"Cover image not found at {cover_image_path}")

    # Create CSV file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        fieldnames = [
            'Message Size (bytes)',
            'MSE',
            'PSNR (dB)',
            'SSIM'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Process each message size
        for size in message_sizes:
            print(f"\nProcessing message size: {size} bytes")

            # Extract message of specified length
            message_content = extract_text_with_length(secret_message_path, size)
            temp_message_path = os.path.join(temp_message_dir, f"message_{size}.txt")
            save_temp_text(message_content, temp_message_path)

            # Set output path for stego image
            output_path = os.path.join(output_dir, f"stego_{size}.png")

            try:
                # Encrypt and hide the message
                print(f"Embedding message of {size} bytes in image...")
                encrypt_and_hide(temp_message_path, cover_image_path, output_path, public_key_path)

                # Load the stego image
                stego_image = cv2.imread(output_path)
                if stego_image is None:
                    print(f"Failed to load stego image at {output_path}")
                    continue

                # Calculate metrics
                mse_value = calculate_mse(cover_image, stego_image)
                psnr_value = calculate_psnr(mse_value)
                ssim_value = calculate_ssim(cover_image, stego_image)

                # Write metrics to CSV
                writer.writerow({
                    'Message Size (bytes)': size,
                    'MSE': f"{mse_value:.10f}",
                    'PSNR (dB)': f"{psnr_value:.2f}",
                    'SSIM': f"{ssim_value:.4f}"
                })

                print(f"Metrics for message size {size} bytes:")
                print(f"  MSE: {mse_value:.10f}")
                print(f"  PSNR: {psnr_value:.2f} dB")
                print(f"  SSIM: {ssim_value:.4f}")

            except Exception as e:
                print(f"Error processing message size {size}: {e}")
                # Still write to CSV but with error
                writer.writerow({
                    'Message Size (bytes)': size,
                    'MSE': "ERROR",
                    'PSNR (dB)': "ERROR",
                    'SSIM': "ERROR"
                })

    print(f"\nComprehensive assessment metrics have been saved to {csv_file_path}")
    print(f"Message files saved in {temp_message_dir}")
    print(f"Stego images saved in {output_dir}")

if __name__ == "__main__":
    run_comprehensive_evaluation()

