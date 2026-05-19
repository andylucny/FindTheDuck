from agentspace import Agent, space
import numpy as np
import cv2

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_

ChannelFactoryInitialize(0,'eth0')

class Lidar(Agent): 
    
    def __init__(self,name="pts"):
        self.name = name
        super().__init__()
        
    def on_cloud(self, msg: PointCloud2_):
        raw = np.frombuffer(bytes(msg.data), dtype=np.uint8)
        n = msg.width * msg.height
        if n == 0 or raw.size < n * msg.point_step:
            return
        raw = raw.reshape(n, msg.point_step)
        xyz = raw[:, :12].copy().view(np.float32).reshape(n, 3)
        space(validity=0.5)[self.name] = xyz[np.isfinite(xyz).all(axis=1)]
        
    def init(self):
        sub = ChannelSubscriber("rt/utlidar/cloud_livox_mid360", PointCloud2_)
        sub.Init(self.on_cloud, 10)
  
    def senseSelectAct(self):
        pass

