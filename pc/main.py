from mirror_client import MirrorClientAgent 
from viewer import Viewer

ip = '10.195.88.72'
#ip = 'localhost'
MirrorClientAgent(ip,7777,'img')
Viewer('img')
