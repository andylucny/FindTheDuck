from agentspace import space
from camera import Camera
from perception import Perception
from mirror_server import MirrorServerAgent

Camera('img')
Perception('img','features')
MirrorServerAgent(7777,'img')
MirrorServerAgent(7778,'features')