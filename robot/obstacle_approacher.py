from agentspace import Agent, space
import numpy as np
import time
import math
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

STOP_DISTANCE = 1.0    # meters - flip to STOP below this
SLOW_DISTANCE = 1.5    # meters - flip to SLOW below this
CONE_X_MIN, CONE_X_MAX = 0.2, 3.0
CONE_Y_HALF = 0.5
CONE_Z_MIN, CONE_Z_MAX = -0.5, 1.0   # ignore floor + above-head

# Movement
# ChannelFactoryInitialize(0, 'eth0')   # or whatever your interface is
client = LocoClient()
client.SetTimeout(10.0)
client.Init()

class ObstacleApproacher(Agent): 

    def __init__(self, pts_name):
        self.name = pts_name
        self.mode = 'stop'
        super().__init__()
        
    def init(self):
        self.max_distance = 1.0
        space.attach_trigger(self.name, self)

    def front_distance(self, pts):
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        mask = (
            (x > CONE_X_MIN) & (x < CONE_X_MAX) &
            (np.abs(y) < CONE_Y_HALF) &
            (z > CONE_Z_MIN) & (z < CONE_Z_MAX)
        )
        front = pts[mask]
        if front.shape[0] == 0:
            return float("inf")
        return float(np.linalg.norm(front[:, :2], axis=1).min())
    
    def walk_forward(self, client, distance_m, speed=0.3):
        duration = distance_m / speed
        t_end = time.time() + duration
        while time.time() < t_end:
            client.Move(speed, 0, 0)
            time.sleep(0.05)
        client.StopMove()

    def walk_forward_slowly(self, client, distance_m, speed=0.1):
        duration = distance_m / speed
        t_end = time.time() + duration
        while time.time() < t_end:
            client.Move(speed, 0, 0)
            time.sleep(0.05)
        client.StopMove()

    def turn(self, client, angle_rad, rate=0.5):
        """Positive angle = counterclockwise (left turn)."""
        direction = 1 if angle_rad >= 0 else -1
        duration = abs(angle_rad) / rate
        t_end = time.time() + duration
        while time.time() < t_end:
            client.Move(0, 0, direction * rate)
            time.sleep(0.05)
        client.StopMove()

    def senseSelectAct(self):
        pts = space[self.name]
        if pts is None:
            return
        d = self.front_distance(pts)
        if d < STOP_DISTANCE:
            self.mode = 'stop'
            #self.turn(client, math.pi)
            space['tospeak'] = "Stop. Obstacle found."
        elif d < SLOW_DISTANCE:
            self.mode = 'slow'
            #self.walk_forward_slowly(client, d)
            space['tospeak'] = "Slower. Obstacle coming nearer."
        else:
            self.mode = 'go'
            #self.walk_forward(client, d)
            
        print(f"obstacle at {d:.2f} m => {self.mode}", flush=True)
        
