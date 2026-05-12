import cv2
import numpy as np
import base64

# ----------------------------
# UNMARSHALL (decode image)
# ----------------------------
def demarshal_image(encoded_str: str) -> np.ndarray:
    """
    Converts base64 string back to OpenCV image (numpy array).
    """

    # decode base64 to bytes
    img_bytes = base64.b64decode(encoded_str)

    # convert bytes to numpy array
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)

    # decode image
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Image decoding failed")

    return image

def demarshal(name, text_data):
    if 'rgb' in name or 'img' in name or 'image' in name:
        return demarshal_image(text_data)
    
    return None