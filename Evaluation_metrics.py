import os
import cv2
import csv
import numpy as np
from main import encrypt_and_hide

# Function to calculate Mean Squared Error (MSE)
def calculate_mse(image1, image2):
    """Compute Mean Squared Error between two images."""
    err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err

# Function to calculate Peak Signal-to-Noise Ratio (PSNR)
def calculate_psnr(mse, max_pixel=255.0):
    """Compute Peak Signal-to-Noise Ratio given MSE."""
    if mse == 0:
        return float('inf')
    return 20 * np.log10(max_pixel / np.sqrt(mse))

# Function to calculate Structural Similarity Index (SSIM)
def calculate_ssim(image1, image2):
    """Compute Structural Similarity Index between two images."""
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    # Compute means
    mu1 = cv2.GaussianBlur(image1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(image2, (11, 11), 1.5)

    # Compute variances and covariance
    sigma1_sq = cv2.GaussianBlur(image1 ** 2, (11, 11), 1.5) - mu1 ** 2
    sigma2_sq = cv2.GaussianBlur(image2 ** 2, (11, 11), 1.5) - mu2 ** 2
    sigma12 = cv2.GaussianBlur(image1 * image2, (11, 11), 1.5) - mu1 * mu2

    # Compute SSIM
    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()

# Paths
cover_image_path = "test/in/medical_image.png"
public_key_path = "./public_key.pem"
input_dir = "test_texts"
output_dir = "test_out"
csv_file_path = "assessment_metrics.csv"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the original cover image
cover_image = cv2.imread(cover_image_path)
if cover_image is None:
    raise FileNotFoundError(f"Cover image not found at {cover_image_path}")

# Convert cover image to grayscale for assessment metrics
cover_image_gray = cv2.cvtColor(cover_image, cv2.COLOR_BGR2GRAY)

# Prepare CSV file
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = ['Stego Image', 'MSE', 'PSNR (dB)', 'SSIM']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Process each text file
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            text_path = os.path.join(input_dir, filename)
            size = filename.split("_")[1].split(".")[0]
            output_path = os.path.join(output_dir, f"stego_{size}.png")

            print(f"\n🔐 Embedding text size {size} from {text_path} into image...")
            encrypt_and_hide(text_path, cover_image_path, output_path, public_key_path)

            # Load the stego image
            stego_image = cv2.imread(output_path)
            if stego_image is None:
                print(f"Failed to load stego image at {output_path}")
                continue

            # Convert stego image to grayscale for assessment metrics
            stego_image_gray = cv2.cvtColor(stego_image, cv2.COLOR_BGR2GRAY)

            # Ensure images have the same dimensions
            if cover_image_gray.shape == stego_image_gray.shape:
                mse_value = calculate_mse(cover_image_gray, stego_image_gray)
                psnr_value = calculate_psnr(mse_value)
                ssim_value = calculate_ssim(cover_image_gray, stego_image_gray)

                # Write metrics to CSV
                writer.writerow({
                    'Stego Image': f"stego_{size}.png",
                    'MSE': f"{mse_value:.2f}",
                    'PSNR (dB)': f"{psnr_value:.2f}",
                    'SSIM': f"{ssim_value:.4f}"
                })
            else:
                print(f"Skipping {output_path}: Dimension mismatch.")

print(f"\nAssessment metrics have been saved to {csv_file_path}")
