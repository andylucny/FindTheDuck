from agentspace import Agent, space
import numpy as np
import cv2

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

ChannelFactoryInitialize(0,'eth0')

class Camera(Agent): # "width": 1920, "height": 1080, "fps": 15
    
    def __init__(self,name):
        self.name = name
        super().__init__()
        
    def init(self):
            client = VideoClient()
            client.SetTimeout(3.0)
            client.Init()
            while True:
                try:
                    errcode, jpegdata = client.GetImageSample()
                    if errcode != 0:
                        continue
                    if jpegdata is None or len(jpegdata) == 0:   # empty frame: skip
                        continue
                    data = np.frombuffer(np.array(jpegdata, np.uint8), np.uint8)
                    if data.size == 0:                            # guard before decode
                        continue
                    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
                    if image is None or image.ndim != 3 or image.shape[0] <= 0 or image.shape[1] <= 0:
                        continue
                    space[self.name] = image
                except Exception as e:
                    print("camera frame error:", e, flush=True)
                    continue
