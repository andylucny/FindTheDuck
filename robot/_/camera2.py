from agentspace import Agent, space
import numpy as np
import cv2

import pyrealsense2 as rs

class Camera(Agent):
    
    def __init__(self,name):
        self.name = name
        super().__init__()
        
    def init(self):
        width = 640
        height = 480
        fps = 30
        jpeg_quality = 90
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        pipeline.start(config)

        for _ in range(10):
            pipeline.wait_for_frames()

        enc_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)]
        print('JPG params',env_params)

        while not self.stopped:
            frames = pipeline.wait_for_frames()
            color = frames.get_color_frame()
            if not color:
                continue

            image = np.asanyarray(color.get_data())
            space[self.name] = image    
        
        pipeline.stop()
        store.stop()
  
    def senseSelectAct(self):
        pass
