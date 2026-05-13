from mirror_client import MirrorClientAgent 
from viewer import Viewer
from snapshotter import Snapshotter
from cli import CLI
from agentspace import space

ip = '10.195.88.72'
#ip = 'localhost'
MirrorClientAgent(ip,7777,'img')
MirrorClientAgent(ip, 7778, 'features')
Viewer('img')
Snapshotter('img', 'features')
CLI()



# DEBUG
# import time
# for _ in range(10):
#     time.sleep(1)
#     img = space['img']
#     feat = space['features']
#     print(f"img={'OK' if img is not None else 'None'}  "
#           f"features={'OK' if feat is not None else 'None'}"
#           f"{' shape=' + str(feat.shape) if feat is not None and hasattr(feat, 'shape') else ''}")