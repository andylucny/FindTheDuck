import cv2
import numpy as np
import base64
import io

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

def demarshal_array(encoded_str: str) -> np.ndarray:
    buf = base64.b64decode(encoded_str)
    return np.load(io.BytesIO(buf), allow_pickle=False)
def demarshal(name, text_data):
    if 'rgb' in name or 'img' in name or 'image' in name:
        return demarshal_image(text_data)
    elif 'features' in name or 'duck' in name:
        return demarshal_array(text_data)
    else:
        return float(text_data)
    return None