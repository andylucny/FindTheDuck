from agentspace import Agent, space
import os
import cv2
import numpy as np


class Snapshotter(Agent):
    def __init__(self, img_name, feature_name, command_name="snapshot_cmd"):
        self.img_name = img_name
        self.feature_name = feature_name
        self.command_name = command_name
        super().__init__()

    def init(self):
        space.attach_trigger(self.command_name, self)

    def senseSelectAct(self):
        object_name = space[self.command_name]
        if not object_name:
            return

        image = space[self.img_name]
        features = space[self.feature_name]
        if image is None:
            print("[Snapshotter] No image yet.")
            return
        if features is None:
            print("[Snapshotter] No features yet.")
            return

        obj_dir = os.path.join("objects", object_name)
        os.makedirs(obj_dir, exist_ok=True)

        existing = [f for f in os.listdir(obj_dir)
                    if f.startswith("image_") and f.endswith(".png")]
        idx = len(existing)
        while os.path.exists(os.path.join(obj_dir, f"image_{idx:02d}.png")):
            idx += 1

        cv2.imwrite(os.path.join(obj_dir, f"image_{idx:02d}.png"), image)
        np.save(os.path.join(obj_dir, f"features_{idx:02d}.npy"), features)
        print(f"[Snapshotter] Saved {object_name} #{idx:02d}")

        space[self.command_name] = None