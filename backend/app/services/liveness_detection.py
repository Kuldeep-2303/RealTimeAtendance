import cv2
import numpy as np
from fastapi import HTTPException

def is_live_person(image_file):
    """
    Perform liveness detection using texture analysis.
    This function checks if the input image is likely to be a real person or a spoof (e.g., photo or video).
    """
    try:
        # Load the image
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Laplacian operator to detect edges
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Threshold for liveness detection (adjust based on testing)
        if laplacian_var < 15:  # Low variance indicates a flat surface (e.g., photo)
            return False

        # Additional checks (e.g., eye blink detection) can be added here
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liveness detection error: {str(e)}")
