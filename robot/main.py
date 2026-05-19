from agentspace import space
from camera import Camera
from perception import Perception
from namer import Namer
from speaker import Speaker
from lidar import Lidar
from mover import Mover
from mirror_server import MirrorServerAgent
import time

Camera('img')
Lidar('pts')
Perception('img','features')
Namer('features')
Speaker('tospeak')
Mover('forward','turn')
MirrorServerAgent(7777,['img','features'])
while (True):
    print(space['pts'])
    time.sleep(1)
