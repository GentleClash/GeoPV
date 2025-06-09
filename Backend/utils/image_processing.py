import cv2
import numpy as np

def preprocess_image(image, sharpen_method='standard', amount=1.5, radius=1, threshold=0) -> np.ndarray:
    """
    Preprocess the image with different sharpening methods.

    Args:
        image (numpy.ndarray): Input image
        sharpen_method (str): 'standard' for kernel-based or 'unsharp_mask' for unsharp masking
        amount (float): Strength of sharpening effect
        radius (int): Radius for Gaussian blur in unsharp mask
        threshold (int): Threshold for applying unsharp mask

    Returns:
        numpy.ndarray: Preprocessed image
    """
    if sharpen_method == 'standard':
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, kernel)

        return cv2.addWeighted(image, 2 - amount, sharpened, amount - 1, 0)

    elif sharpen_method == 'unsharp_mask':
        blurred = cv2.GaussianBlur(image, (0, 0), radius)

        high_pass = cv2.addWeighted(image, 1.0, blurred, -1.0, 0)

        sharpened = cv2.addWeighted(image, 1.0, high_pass, amount, 0)

        if threshold > 0:
            mask = cv2.subtract(image, blurred)
            _, mask = cv2.threshold(mask, threshold, 255, cv2.THRESH_BINARY)

            return cv2.bitwise_and(sharpened, sharpened, mask=mask)

        return sharpened

    else:
        return image