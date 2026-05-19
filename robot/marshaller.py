import cv2
import numpy as np
import base64
import io

# ----------------------------
# MARSHALL (encode image)
# ----------------------------
def marshal_image(image: np.ndarray) -> str:
    """
    Converts OpenCV image (numpy array) to base64 string.
    """
    
    # resize
    image = cv2.resize(image,(480,270))

    # encode image as PNG (lossless)
    success, buffer = cv2.imencode('.png', image)
    if not success:
        raise ValueError("Image encoding failed")

    # convert to base64 string
    encoded = base64.b64encode(buffer).decode('utf-8')
    return encoded
    
def marshal_array(array: np.ndarray) -> str:
    buf = io.BytesIO()
    np.save(buf, array, allow_pickle=False)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def marshal(name,data):
    if isinstance(data,np.ndarray):
        if 'rgb' in name or 'img' in name or 'image' in name:
            return marshal_image(data)
        elif 'features' in name or 'duck' in name:
            return marshal_array(data)
    return ""
