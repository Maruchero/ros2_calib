"""
This file is responsible for parsing the calib_manager.yaml file from Unimore Racing.
It contains information about the transformations between the various sensors
on the car and about the intrinsic parameters of the cameras.
"""

import os
import numpy as np
import yaml
from typing import Dict, Tuple
from scipy.spatial.transform import Rotation as R
from ros2_calib.ros_utils import CameraInfo, Header


Vec3f = Tuple[float, float, float]


class CalibManagerHandler:
    """
    This class contains useful methods to parse UR calib_manager.yaml file.
    """

    def __init__(self, filepath: str) -> None:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Calib manager file not found: {filepath}")
        self.filepath = filepath
        self.cameras: Dict[str, CameraInfo] = {}
        self.tf_tree = {}
        self.load_calib_manager()
        print("[DEBUG] Correctly loaded calib_manager.yaml file.")

    @staticmethod
    def _pose_to_transform(pose):
        """
        Convert [x, y, z, roll, pitch, yaw] to 4x4 transformation matrix
        """
        x, y, z, roll, pitch, yaw = pose

        # Create rotation matrix from Euler angles
        rotation = R.from_euler("xyz", [roll, pitch, yaw], degrees=True)
        rot_matrix = rotation.as_matrix()

        # Create transformation matrix
        transform = np.eye(4)
        transform[:3, :3] = rot_matrix
        transform[:3, 3] = [x, y, z]

        return transform

    def load_calib_manager(self):
        """
        Load and parse the calib_manager file.
        """
        with open(self.filepath, "r") as file:
            data = yaml.safe_load(file)

        # Parse camera intrinsics
        cam_entries = data.get("tf_manager", {}).get("tree", {}).get("calibs", [])
        for cam_data in cam_entries:
            camera_name = cam_data["frameId"]
            fx, fy, cx, cy = cam_data["K"]
            k = [
                fx, 0.0, cx,
                0.0, fy, cy,
                0.0, 0.0, 1.0,
            ]
            camera = CameraInfo(
                header=Header(
                    stamp=0,
                    frame_id=camera_name,
                ),
                height=cam_data["height"],
                width=cam_data["width"],
                distortion_model="fisheye" if cam_data["fisheye"] else "plumb_bob",
                d=cam_data["D"][:5],  # Take only first 5 distortion coefficients
                k=k,
                r=[],
                p=[],
            )
            self.cameras[camera_name] = camera

        # Parse transformations
        tf_entries = data.get("tf_manager", {}).get("tree", {}).get("static_tf", [])
        for tf_data in tf_entries:
            child = tf_data["targetLink"]
            parent = tf_data["baseLink"]
            self.tf_tree.setdefault(parent, {})[child] = {
                "transform": self._pose_to_transform(tf_data["tf"])
            }
