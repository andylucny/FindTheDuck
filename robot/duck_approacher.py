from agentspace import Agent, space
import numpy as np
import time
import math
from collections import deque
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

STOP_DISTANCE = 0.25    # meters - flip to STOP below this
SLOW_DISTANCE = 1.5    # meters - flip to SLOW below this
CONE_X_MIN, CONE_X_MAX = 0.2, 3.0
CONE_Y_HALF = 0.5
CONE_Z_MIN, CONE_Z_MAX = -0.5, 1.0   # ignore floor + above-head

# Duck thresholds                                          
LOCK   = 0.28          # could be a duck in that direction         
ACCEPT = 0.35          # confirm it's the duck         

# Movement
# ChannelFactoryInitialize(0, 'eth0')   # or whatever your interface is
client = LocoClient()
client.SetTimeout(10.0)
client.Init()

WINDOW_SECONDS = 0.8        # rolling window length
TICK_SECONDS   = 0.1        # how long each Move burst lasts

class DuckApproacher(Agent):

    def __init__(self, pts_name):
        self.name = pts_name
        self.mode = 'stop'
        self.history = deque()
        super().__init__()

    def init(self):
        self.max_distance = 1.0
        space.attach_trigger(self.name, self)
        # search state                                     # NEW
        self.turn_dir = 1.0       # +1 / -1 sweep direction
        self.last_sim = None
        self.step = 0.5           # current yaw magnitude while hunting
        self.found = False

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

    def smoothed_distance(self, now, d):
        """Append the new sample, drop expired ones, return the window mean."""
        self.history.append((now, d))
        cutoff = now - WINDOW_SECONDS
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()
        vals = [min(v, 10.0) for _, v in self.history]
        return sum(vals) / len(vals)

    def search_yaw(self):                                  # NEW (whole method)
        """Decide yaw from duck similarity. Returns (vx, vyaw, done)."""
        sim = space['duck_sim']
        if sim is None or self.found:
            return 0.0, 0.0, self.found

        if sim > ACCEPT:                 # confirmed at this heading
            self.found = True
            space['tospeak'] = "Ou, here is the duck!"
            print("IT IS A DUCK!", flush=True)
            return 0.0, 0.0, True

        if sim < LOCK:                   # nothing yet: sweep to scan
            self.last_sim = sim
            return 0.0, self.turn_dir * 0.5, False

        # LOCK <= sim <= ACCEPT: hill-climb toward the peak
        if self.last_sim is not None and sim < self.last_sim:
            self.turn_dir *= -1.0        # overshot: reverse
            self.step = max(0.1, self.step * 0.6)
        self.last_sim = sim
        return 0.0, self.turn_dir * self.step, False

    def senseSelectAct(self):
        pts = space[self.name]
        if pts is None:
            return

        now = time.time()
        d_raw = self.front_distance(pts)
        d = self.smoothed_distance(now, d_raw)

        sim = space['duck_sim']                           
        sim = sim if sim is not None else 0.0              

        if d < STOP_DISTANCE:
            new_mode = 'stop'
            if self.found:                                 
                vx, vyaw = 0.0, 0.0
            elif sim > ACCEPT:
                # the obstacle in front is the duck
                self.found = True
                space['tospeak'] = "Ou, here is the duck!"
                print("IT IS A DUCK!", flush=True)
                vx, vyaw = 0.0, 0.0
            elif sim >= LOCK:
                # duckish but not confirmed don't turn away yet.
                _, vyaw, _ = self.search_yaw()
                vx = 0.0
            else:
                # genuinely not a duck - turn away
                vx, vyaw = 0.0, 0.5
        elif d < SLOW_DISTANCE:
            new_mode = 'slow'
            vx, vyaw = 0.4, 0.0
        else:
            new_mode = 'go'
            vx, vyaw, done = self.search_yaw()             
            if done:
                vx, vyaw = 0.0, 0.0

        client.Move(vx, 0.0, vyaw)
        time.sleep(0.02)

        if new_mode != self.mode:
            self.mode = new_mode
            if new_mode == 'stop':
                space['tospeak'] = "Stop. Obstacle found."
            elif new_mode == 'slow':
                space['tospeak'] = "Slower. Obstacle coming nearer."
            elif new_mode == 'go':
                space['tospeak'] = "Path clear. Going."

        print(f"raw={d_raw:.2f} avg={d:.2f} ({len(self.history)} samples) => {new_mode}",
            flush=True)