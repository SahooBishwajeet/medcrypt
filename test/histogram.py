
import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
from pathlib import Path


def plot_image_with_histogram(img1_path, img2_path, output_path=None, titles=None):
    """
    Plot two images side by side with their histograms below them.

    Args:
        img1_path: Path to the first image
        img2_path: Path to the second image
        output_path: Path to save the output figure (optional)
        titles: List of two titles for the images (optional)
    """
    # Read images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None:
        raise ValueError(f"Could not read the first image: {img1_path}")
    if img2 is None:
        raise ValueError(f"Could not read the second image: {img2_path}")

    # Convert from BGR to RGB for display
    img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    # Set default titles if not provided
    if titles is None:
        titles = [Path(img1_path).name, Path(img2_path).name]

    # Create figure
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Plot images
    axs[0, 0].imshow(img1_rgb)
    axs[0, 0].set_title(titles[0])
    axs[0, 0].axis('off')

    axs[0, 1].imshow(img2_rgb)
    axs[0, 1].set_title(titles[1])
    axs[0, 1].axis('off')

    # Calculate and plot histograms
    colors = ('r', 'g', 'b')

    # Histogram for first image
    for i, color in enumerate(colors):
        hist = cv2.calcHist([img1], [i], None, [256], [0, 256])
        axs[1, 0].plot(hist, color=color, alpha=0.7)

    axs[1, 0].set_xlim([0, 256])
    axs[1, 0].set_title(f'Histogram: {titles[0]}')
    axs[1, 0].set_xlabel('Pixel Value')
    axs[1, 0].set_ylabel('Frequency')
    axs[1, 0].grid(True, alpha=0.3)

    # Histogram for second image
    for i, color in enumerate(colors):
        hist = cv2.calcHist([img2], [i], None, [256], [0, 256])
        axs[1, 1].plot(hist, color=color, alpha=0.7)

    axs[1, 1].set_xlim([0, 256])
    axs[1, 1].set_title(f'Histogram: {titles[1]}')
    axs[1, 1].set_xlabel('Pixel Value')
    axs[1, 1].set_ylabel('Frequency')
    axs[1, 1].grid(True, alpha=0.3)

    # Add a legend
    lines = [plt.Line2D([0], [0], color=c) for c in colors]
    labels = ['Blue', 'Green', 'Red']  # Reversed since OpenCV uses BGR
    fig.legend(lines, labels, loc='upper center', ncol=3)

    plt.tight_layout()

    # Save figure if output path is provided
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {output_path}")

    # Show plot
    plt.show()


def calculate_metrics(img1_path, img2_path):
    """
    Calculate similarity metrics between two images.

    Args:
        img1_path: Path to the first image
        img2_path: Path to the second image

    Returns:
        Dictionary of metrics
    """
    # Read images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        raise ValueError("Could not read one or both images")

    # Check if images have the same dimensions
    if img1.shape != img2.shape:
        raise ValueError(f"Images have different dimensions: {img1.shape} vs {img2.shape}")

    # Calculate MSE (Mean Squared Error)
    mse = np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)

    # Calculate PSNR (Peak Signal-to-Noise Ratio)
    if mse == 0:  # Images are identical
        psnr = float('inf')
    else:
        psnr = 10 * np.log10((255.0 ** 2) / mse)

    # Calculate histogram correlation for each channel
    hist_corr = []
    for i in range(3):  # BGR channels
        hist1 = cv2.calcHist([img1], [i], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [i], None, [256], [0, 256])

        # Normalize histograms
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        # Calculate correlation
        corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        hist_corr.append(corr)

    metrics = {
        'MSE': mse,
        'PSNR (dB)': psnr,
        'Hist_Correlation_B': hist_corr[0],
        'Hist_Correlation_G': hist_corr[1],
        'Hist_Correlation_R': hist_corr[2],
        'Hist_Correlation_Avg': np.mean(hist_corr)
    }

    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Compare two images and their histograms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
        python histogram.py --image1 cover.png --image2 stego.png --title1 "Original Image" --title2 "Modified Image" --output comparison.png"""
    )

    parser.add_argument("--image1", required=True, help="Path to the first image")
    parser.add_argument("--image2", required=True, help="Path to the second image")
    parser.add_argument("--title1", help="Title for the first image")
    parser.add_argument("--title2", help="Title for the second image")
    parser.add_argument("--output", help="Path to save the output figure")
    parser.add_argument("--metrics", action="store_true", help="Calculate similarity metrics")

    args = parser.parse_args()

    # Set titles if provided
    titles = None
    if args.title1 and args.title2:
        titles = [args.title1, args.title2]

    # Calculate and print metrics if requested
    if args.metrics:
        try:
            metrics = calculate_metrics(args.image1, args.image2)
            print("Image Similarity Metrics:")
            print("-" * 40)
            for key, value in metrics.items():
                print(f"{key}: {value:.6f}")
            print("-" * 40)
        except Exception as e:
            print(f"Error calculating metrics: {e}")

    # Plot images with histograms
    try:
        plot_image_with_histogram(args.image1, args.image2, args.output, titles)
    except Exception as e:
        print(f"Error plotting images: {e}")


if __name__ == "__main__":
    main()


"""
Usage :

1. Basic usage
python histogram.py --image1 cover.png --image2 stego.png

2. With titles
python histogram.py --image1 cover.png --image2 stego.png --title1 "Original Image" --title2 "Modified Image"

3. Save output
python histogram.py --image1 cover.png --image2 stego.png --output comparison.png

4. Calculate metrics
python histogram.py --image1 cover.png --image2 stego.png --metrics

5. All options
python histogram.py --image1 cover.png --image2 stego.png --title1 "Original Image" --title2 "Modified Image" --output comparison.png --metrics

"""

