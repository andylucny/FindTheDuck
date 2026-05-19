import numpy as np
import cv2

# --- config ---
CONE_X_MIN, CONE_X_MAX = 0.2, 3.0
CONE_Y_HALF = 0.5
CONE_Z_MIN, CONE_Z_MAX = -0.5, 1.0

# top-down view config
VIEW_RANGE_M = 4.0      # show points within +/- 4 m
VIEW_SIZE_PX = 600      # window is 600x600
PX_PER_M = VIEW_SIZE_PX / (2 * VIEW_RANGE_M)

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

if __name__ == '__main__':

    i=3
    pts = np.loadtxt(f'pts{i}.npy')
    
    """
    img, dist, num_pts = render_topdown(pts)
    print(num_pts)
    print(dist)
    cv2.imwrite(f'img{i}.png',img)
    """
    
    """
    import plotly.express as px
    import numpy as np
    fig = px.scatter_3d(x=pts[:, 0], y=pts[:, 1], z=pts[:, 2])
    fig.update_traces(marker=dict(size=2))
    fig.update_layout(scene=dict(aspectmode='data'))
    fig.show()
    """
    