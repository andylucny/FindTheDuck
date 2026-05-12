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
            errcode, jpegdata = client.GetImageSample()
            if errcode != 0:
                continue
            jpegdataarray = np.array(jpegdata,np.uint8)
            data = np.frombuffer(jpegdataarray, np.uint8)
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if image is None or (not hasattr(image, "shape")) or len(image.shape) != 3 or image.shape[0] <= 0 or image.shape[1] <= 0:
                continue
            space[self.name] = image    
  
    def senseSelectAct(self):
        pass
