from agentspace import Agent, space

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

ChannelFactoryInitialize(0,'eth0')

sport_client = LocoClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

class Mover(Agent):
    
    def __init__(self, nameForward, nameTurn):
        self.nameForward = nameForward
        self.nameTurn = nameTurn
        super().__init__()
        
    def init(self):
        self.attach_timer(0.25)
  
    def senseSelectAct(self):
        forward = space(default=0.0)[self.nameForward]
        turn = space(default=0.0)[self.nameTurn]
        if turn > 0.0:
            sport_client.Move(0,0,0.3) # rotate
        elif turn < 0.0:
            sport_client.Move(0,0,-0.3) # rotate
        elif forward > 0.0:
            sport_client.Move(0.3,0,0) # forward
        elif forward < 0.0:
            sport_client.Move(-0.3,0,0) # backward
        else:
            sport_client.Move(0,0,0) # stop
