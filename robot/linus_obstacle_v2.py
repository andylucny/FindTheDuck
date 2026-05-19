# lidar_plus_video.py
import sys, time, threading
import numpy as np
import cv2

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_

# --- config ---
CAM_DEVICE     = "/dev/video0"   # change as needed
STOP_DISTANCE  = 1.0
SLOW_DISTANCE  = 1.5
CONE_X_MIN, CONE_X_MAX = 0.2, 3.0
CONE_Y_HALF    = 0.5
CONE_Z_MIN, CONE_Z_MAX = -0.5, 1.0

# top-down view config
VIEW_RANGE_M   = 4.0      # show points within +/- 4 m
VIEW_SIZE_PX   = 600      # window is 600x600
PX_PER_M       = VIEW_SIZE_PX / (2 * VIEW_RANGE_M)

latest = {"pts": None}

def on_cloud(msg: PointCloud2_):
    raw = np.frombuffer(bytes(msg.data), dtype=np.uint8)
    n = msg.width * msg.height
    if n == 0 or raw.size < n * msg.point_step:
        return
    raw = raw.reshape(n, msg.point_step)
    xyz = raw[:, :12].copy().view(np.float32).reshape(n, 3)
    latest["pts"] = xyz[np.isfinite(xyz).all(axis=1)]

def world_to_px(x, y):
    """Lidar +X forward, +Y left → image: forward = up, left = left."""
    px = (VIEW_SIZE_PX // 2 - y * PX_PER_M).astype(np.int32)
    py = (VIEW_SIZE_PX // 2 - x * PX_PER_M).astype(np.int32)
    return px, py

def render_topdown(pts):
    img = np.zeros((VIEW_SIZE_PX, VIEW_SIZE_PX, 3), dtype=np.uint8)

    # grid + axes
    for r in range(1, int(VIEW_RANGE_M) + 1):
        cv2.circle(img, (VIEW_SIZE_PX//2, VIEW_SIZE_PX//2),
                   int(r * PX_PER_M), (40, 40, 40), 1)
        cv2.putText(img, f"{r}m",
                    (VIEW_SIZE_PX//2 + 5, VIEW_SIZE_PX//2 - int(r*PX_PER_M)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)

    # cone outline (in world coords) → 4 corners
    cone_world = np.array([
        [CONE_X_MIN, +CONE_Y_HALF],
        [CONE_X_MAX, +CONE_Y_HALF],
        [CONE_X_MAX, -CONE_Y_HALF],
        [CONE_X_MIN, -CONE_Y_HALF],
    ])
    cx, cy = world_to_px(cone_world[:, 0], cone_world[:, 1])
    cv2.polylines(img, [np.stack([cx, cy], axis=1)], True, (0, 255, 255), 1)

    # robot at center
    cv2.circle(img, (VIEW_SIZE_PX//2, VIEW_SIZE_PX//2), 5, (0, 200, 255), -1)
    cv2.line(img, (VIEW_SIZE_PX//2, VIEW_SIZE_PX//2),
             (VIEW_SIZE_PX//2, VIEW_SIZE_PX//2 - 20), (0, 200, 255), 2)

    if pts is None or pts.size == 0:
        return img, float("inf"), 0

    # filter to a Z slab so the top-down isn't dominated by floor/ceiling
    z = pts[:, 2]
    slab = pts[(z > CONE_Z_MIN) & (z < CONE_Z_MAX)]

    # in-cone mask for highlighting + distance
    x, y = slab[:, 0], slab[:, 1]
    in_cone = ((x > CONE_X_MIN) & (x < CONE_X_MAX) &
               (np.abs(y) < CONE_Y_HALF))

    # draw all slab points dim white, in-cone points red
    if slab.shape[0]:
        px_all, py_all = world_to_px(slab[:, 0], slab[:, 1])
        valid = (px_all >= 0) & (px_all < VIEW_SIZE_PX) & \
                (py_all >= 0) & (py_all < VIEW_SIZE_PX)
        img[py_all[valid & ~in_cone], px_all[valid & ~in_cone]] = (180, 180, 180)
        img[py_all[valid & in_cone],  px_all[valid & in_cone]]  = (0, 0, 255)

    front = slab[in_cone]
    if front.shape[0] == 0:
        return img, float("inf"), 0
    d = float(np.sqrt(front[:, 0]**2 + front[:, 1]**2).min())
    return img, d, int(front.shape[0])

def main():
    iface = sys.argv[1] if len(sys.argv) > 1 else "eth0"
    ChannelFactoryInitialize(0, iface)
    sub = ChannelSubscriber("rt/utlidar/cloud_livox_mid360", PointCloud2_)
    sub.Init(on_cloud, 10)

    cap = cv2.VideoCapture(CAM_DEVICE)
    if not cap.isOpened():
        print(f"warning: cannot open {CAM_DEVICE} -- camera pane will be black")

    print("Press q in a window to quit.")
    while True:
        # --- camera frame ---
        ok, frame = (cap.read() if cap.isOpened() else (False, None))
        if not ok:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "no camera", (20, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # --- lidar top-down ---
        topdown, dist, n_pts = render_topdown(latest["pts"])

        # status bar
        if dist < STOP_DISTANCE:
            state, color = "STOP", (0, 0, 255)
        elif dist < SLOW_DISTANCE:
            state, color = "SLOW", (0, 165, 255)
        else:
            state, color = "GO",   (0, 255, 0)
        d_str = f"{dist:.2f} m" if dist != float("inf") else "inf"
        for img in (frame, topdown):
            cv2.rectangle(img, (0, 0), (img.shape[1], 30), (30, 30, 30), -1)
            cv2.putText(img, f"{state}  front: {d_str}  ({n_pts} pts)",
                        (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # combine side-by-side, normalize heights
        h = max(frame.shape[0], topdown.shape[0])
        def pad(img):
            if img.shape[0] == h: return img
            out = np.zeros((h, img.shape[1], 3), dtype=np.uint8)
            out[:img.shape[0]] = img
            return out
        combined = np.hstack([pad(frame), pad(topdown)])
        cv2.imshow("camera | lidar (top-down)", combined)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()