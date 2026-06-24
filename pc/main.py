from agentspace import space
from mirror_client import MirrorClientAgent 
from viewer import Viewer
from snapshotter import Snapshotter
# from joystickApi import JoystickAgent
# from joystickControl import JoystickControlAgent
from duck_provider import DuckProvider
from cli import CLI
import time

ip = '10.195.88.72'
#ip = 'localhost'
MirrorClientAgent(ip,7777,['duck'])
time.sleep(2)
DuckProvider("objects/duck/features_00.npy") # duck very big
Viewer('img')
#Snapshotter('img', 'features')
#CLI()

time.sleep(1)

# JoystickAgent('joystick')
# JoystickControlAgent('joystick','forward','turn')


# DEBUG
# import time
# for _ in range(10):
#     time.sleep(1)
#     img = space['img']
#     feat = space['features']
#     print(f"img={'OK' if img is not None else 'None'}  "
#           f"features={'OK' if feat is not None else 'None'}"
#           f"{' shape=' + str(feat.shape) if feat is not None and hasattr(feat, 'shape') else ''}")