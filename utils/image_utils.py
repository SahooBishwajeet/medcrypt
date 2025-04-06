import numpy as np
import cv2


def rgb_to_ycbcr(image):
    """
    Convert RGB image to YCbCr color space

    Args:
        image: RGB image (numpy array)

    Returns:
        YCbCr image (numpy array)
    """
    # Make sure image is float for calculations
    image = image.astype(np.float32)

    # Create transformation matrix
    transform = np.array(
        [[0.299, 0.587, 0.114], [-0.169, -0.331, 0.500], [0.500, -0.419, -0.081]]
    )

    # Create offset
    offset = np.array([0, 128, 128])

    # Reshape image for matrix multiplication
    height, width, channels = image.shape
    reshaped = image.reshape(height * width, channels)

    # Apply transformation
    ycbcr = np.dot(reshaped, transform.T) + offset

    # Reshape back
    return ycbcr.reshape(height, width, channels)


def ycbcr_to_rgb(image):
    """
    Convert YCbCr image to RGB color space

    Args:
        image: YCbCr image (numpy array)

    Returns:
        RGB image (numpy array)
    """
    # Make sure image is float for calculations
    image = image.astype(np.float32)

    # Create transformation matrix
    transform = np.array([[1.0, 0.0, 1.402], [1.0, -0.344, -0.714], [1.0, 1.772, 0.0]])

    # Create offset
    offset = np.array([0, -128, -128])

    # Reshape image for matrix multiplication
    height, width, channels = image.shape
    reshaped = image.reshape(height * width, channels)

    # Apply offset
    reshaped = reshaped + offset

    # Apply transformation
    rgb = np.dot(reshaped, transform.T)

    # Reshape back and clip values to valid range
    return rgb.reshape(height, width, channels)
