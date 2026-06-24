from agentspace import Agent, space
import numpy as np
import time
from collections import deque
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

STOP_DISTANCE = 0.5
SLOW_DISTANCE = 1.5
CONE_X_MIN, CONE_X_MAX = 0.2, 3.0
CONE_Y_HALF = 0.5
CONE_Z_MIN, CONE_Z_MAX = -0.5, 1.0

LOCK = 0.28            # could be a duck
ACCEPT = 0.35          # confirmed duck

SCAN_YAW = 0.5         # turn speed while searching
APPROACH_VX = 0.2      # forward speed toward a candidate
WIGGLE_YAW = 0.3       # turn speed during angle check
INVESTIGATE_T = 4.0    # sec driving before forcing a wiggle
WIGGLE_T = 1.2         # sec per wiggle half
LOST_GRACE = 0.5       # sec below LOCK before giving up

client = LocoClient()
client.SetTimeout(10.0)
client.Init()

WINDOW_SECONDS = 0.8

class DuckApproacher(Agent):

    def __init__(self, pts_name):
        self.name = pts_name
        self.mode = 'stop'
        self.history = deque()
        super().__init__()

    def init(self):
        space.attach_trigger(self.name, self)
        self.state = 'SCAN'        # SCAN | INVESTIGATE | WIGGLE | DONE
        self.turn_dir = 1.0
        self.state_t0 = time.time()
        self.wiggle_phase = 0      # 0 = left, 1 = right
        self.lost_t0 = None
        self.found = False
        self.celebrated = False

    def front_distance(self, pts):
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        mask = (x > CONE_X_MIN) & (x < CONE_X_MAX) & (np.abs(y) < CONE_Y_HALF) & (z > CONE_Z_MIN) & (z < CONE_Z_MAX)
        front = pts[mask]
        if front.shape[0] == 0:
            return float("inf")
        return float(np.linalg.norm(front[:, :2], axis=1).min())

    def smoothed_distance(self, now, d):
        self.history.append((now, d))
        cutoff = now - WINDOW_SECONDS
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()
        vals = [min(v, 10.0) for _, v in self.history]
        return sum(vals) / len(vals)

    def wave(self):
        if self.celebrated:
            return
        client.Move(0.0, 0.0, 0.0)
        time.sleep(0.3)
        try:
            client.WaveHand(False)
        except TypeError:
            client.WaveHand()
        except Exception as e:
            print("wave failed:", e, flush=True)
        self.celebrated = True

    def senseSelectAct(self):
        pts = space[self.name]
        if pts is None:
            return

        now = time.time()
        d_raw = self.front_distance(pts)
        d = self.smoothed_distance(now, d_raw)

        sim = space['duck_sim']
        if sim is None:
            sim = 0.0

        vx = 0.0
        vyaw = 0.0

        # confirmed earlier: stand still in front of the duck
        if self.found:
            new_mode = 'stop'

        # obstacle very close
        elif d < STOP_DISTANCE:
            new_mode = 'stop'
            if sim > ACCEPT:
                # the thing in front is the duck
                self.found = True
                self.state = 'DONE'
                space['tospeak'] = "Ou, here is the duck!"
                print("IT IS A DUCK!", flush=True)
                self.wave()
            elif sim >= LOCK:
                # close to a candidate: wiggle to check angles, don't push in
                if self.state != 'WIGGLE':
                    self.state = 'WIGGLE'
                    self.wiggle_phase = 0
                    self.state_t0 = now
                if self.wiggle_phase == 0:
                    if now - self.state_t0 > WIGGLE_T:
                        self.wiggle_phase = 1
                        self.state_t0 = now
                    vyaw = WIGGLE_YAW
                else:
                    if now - self.state_t0 > WIGGLE_T:
                        self.turn_dir = -self.turn_dir
                        self.state = 'SCAN'
                    vyaw = -WIGGLE_YAW
            else:
                # not a duck: turn away
                vyaw = 0.5

        # obstacle getting near: keep hunting but slow
        elif d < SLOW_DISTANCE:
            new_mode = 'slow'
            if sim > ACCEPT:
                self.found = True
                self.state = 'DONE'
                space['tospeak'] = "Ou, here is the duck!"
                print("IT IS A DUCK!", flush=True)
                self.wave()
            elif sim >= LOCK:
                vx = 0.2
            else:
                vyaw = self.turn_dir * SCAN_YAW

        # path clear: full search state machine
        else:
            new_mode = 'go'

            if sim > ACCEPT:
                self.found = True
                self.state = 'DONE'
                space['tospeak'] = "Ou, here is the duck!"
                print("IT IS A DUCK!", flush=True)
                self.wave()

            elif self.state == 'SCAN':
                if sim >= LOCK:
                    self.state = 'INVESTIGATE'
                    self.state_t0 = now
                    self.lost_t0 = None
                    vx = APPROACH_VX
                else:
                    vyaw = self.turn_dir * SCAN_YAW

            elif self.state == 'INVESTIGATE':
                if sim < LOCK:
                    # candidate fading: short grace, then give up
                    if self.lost_t0 is None:
                        self.lost_t0 = now
                    if now - self.lost_t0 > LOST_GRACE:
                        self.turn_dir = -self.turn_dir
                        self.state = 'SCAN'
                        self.lost_t0 = None
                    else:
                        vx = APPROACH_VX
                else:
                    self.lost_t0 = None
                    if now - self.state_t0 > INVESTIGATE_T:
                        # driven long enough: check angles
                        self.state = 'WIGGLE'
                        self.wiggle_phase = 0
                        self.state_t0 = now
                    else:
                        vx = APPROACH_VX

            elif self.state == 'WIGGLE':
                if self.wiggle_phase == 0:
                    if now - self.state_t0 > WIGGLE_T:
                        self.wiggle_phase = 1
                        self.state_t0 = now
                    vyaw = WIGGLE_YAW
                else:
                    if now - self.state_t0 > WIGGLE_T:
                        # nothing found: turn the other way and rescan
                        self.turn_dir = -self.turn_dir
                        self.state = 'SCAN'
                    vyaw = -WIGGLE_YAW

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

        print(f"raw={d_raw:.2f} avg={d:.2f} state={self.state} sim={sim:.3f} => {new_mode}", flush=True)