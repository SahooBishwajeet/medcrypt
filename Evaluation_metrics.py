import os
import cv2
import csv
import numpy as np
from main import encrypt_and_hide

# Function to calculate Mean Squared Error (MSE)
def calculate_mse(image1, image2):
    """Calculate MSE based on (R * C)^2 as given in the custom formula."""
    # Make sure both images are same shape
    if image1.shape != image2.shape:
        raise ValueError("Images must be the same size")
    
    R, C = image1.shape[0], image1.shape[1]  # rows and columns
    print(R , C , image1.size)
    squared_error = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    mse = squared_error / ((R * C) ** 2)
    print("Squared Error: ", squared_error)
    print("MSE: ", mse)
    return mse


# Function to calculate Peak Signal-to-Noise Ratio (PSNR)
def calculate_psnr(mse, max_pixel=255.0):
    """Compute Peak Signal-to-Noise Ratio given MSE."""
    if mse == 0:
        return float('inf')
    return 10 * np.log10(max_pixel **2/ mse)

# Function to calculate Structural Similarity Index (SSIM)

def calculate_ssim(image1, image2):
    """
    Calculate SSIM (Structural Similarity Index) between two images.
    Explained simply like telling a baby.
    """
    # 1. Regularization constants (make sure we don't divide by zero)
    C1 = (0.01 * 255) ** 2  # Small number based on max value
    C2 = (0.03 * 255) ** 2

    # 2. Blur the images softly to get the average (mean) brightness
    mu1 = cv2.GaussianBlur(image1.astype(np.float32), (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(image2.astype(np.float32), (11, 11), 1.5)

    # 3. Get the square of the means (brightness squared)
    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    # 4. Now calculate how much the image changes (variance)
    sigma1_sq = cv2.GaussianBlur(image1.astype(np.float32) ** 2, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(image2.astype(np.float32) ** 2, (11, 11), 1.5) - mu2_sq

    # 5. Calculate how much both images change together (covariance)
    sigma12 = cv2.GaussianBlur(image1.astype(np.float32) * image2.astype(np.float32), (11, 11), 1.5) - mu1_mu2

    # 6. Use the big SSIM formula now
    numerator = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
    denominator = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
    ssim_map = numerator / denominator

    # 7. SSIM for the whole image is the average of all the small window SSIMs
    return ssim_map.mean()

# Function to get message length from text file
def get_message_length(text_path):
    """Get the length of the message in bytes."""
    with open(text_path, 'rb') as f:
        return os.path.getsize(text_path)

# Paths
cover_image_path = "test/in/medical_image.png"
public_key_path = "./public_key.pem"
input_dir = "test_texts"
output_dir = "test_out"
csv_file_path = "assessment_metrics.csv"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the original cover image
cover_image = cv2.imread(cover_image_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale directly
if cover_image is None:
    raise FileNotFoundError(f"Cover image not found at {cover_image_path}")

# Prepare CSV file
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = [
        'Input Image', 
        'Message Length (bytes)', 
        'MSE', 
        'PSNR (dB)', 
        'SSIM'
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Process each text file
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
            text_path = os.path.join(input_dir, filename)
            size = filename.split("_")[1].split(".")[0]
            output_path = os.path.join(output_dir, f"stego_{size}.png")
            message_length = get_message_length(text_path)

            # print(f"\n🔐 Embedding text size {size} from {text_path} into image...")
            encrypt_and_hide(text_path, cover_image_path, output_path, public_key_path)

            # Load the stego image
            stego_image = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale directly
            if stego_image is None:
                print(f"Failed to load stego image at {output_path}")
                continue

            # Ensure images have the same dimensions
            if cover_image.shape == stego_image.shape:
                mse_value = calculate_mse(cover_image, stego_image)
                psnr_value = calculate_psnr(mse_value)
                ssim_value = calculate_ssim(cover_image, stego_image)

                # Write metrics to CSV
                writer.writerow({
                    'Input Image': os.path.basename(cover_image_path),
                    'Message Length (bytes)': message_length,
                    'MSE': f"{mse_value:.10f}",
                    'PSNR (dB)': f"{psnr_value:.2f}",
                    'SSIM': f"{ssim_value:.4f}"
                })
                
                # print(f"Metrics for {filename}:")
                # print(f"  MSE: {mse_value:.4f}")
                # print(f"  PSNR: {psnr_value:.2f} dB")
                # print(f"  SSIM: {ssim_value:.4f}")
            else:
                print(f"Skipping {output_path}: Dimension mismatch (Cover: {cover_image.shape}, Stego: {stego_image.shape})")

print(f"\nAssessment metrics have been saved to {csv_file_path}")