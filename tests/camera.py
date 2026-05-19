import time
import numpy as np
import cv2

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

ChannelFactoryInitialize(0,'eth0')

# "width": 1920, "height": 1080, "fps": 15
    
client = VideoClient()
client.SetTimeout(3.0)
client.Init()

errcode, jpegdata = client.GetImageSample()
if errcode != 0:
    print("ERROR", errcode)
else:
    jpegdataarray = np.array(jpegdata,np.uint8)
    data = np.frombuffer(jpegdataarray, np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None or (not hasattr(image, "shape")) or len(image.shape) != 3 or image.shape[0] <= 0 or image.shape[1] <= 0:
        print('BAD FORMAT')
    else:
        filename = f'{int(time.time())}.png'
        cv2.imwrite(filename,image)
        print('successfully written as',filename)
