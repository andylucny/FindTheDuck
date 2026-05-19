import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

ChannelFactoryInitialize(0,'eth0')

sport_client = LocoClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

"""
for _ in range(10):
    sport_client.Move(0.3,0,0) # move forward
    time.sleep(0.25)

#sport_client.Move(0,0.3,0) # move to a side
#time.sleep(1)
"""

for _ in range(10):
    sport_client.Move(0,0,0.3) # rotate
    time.sleep(0.25)
