"""
This file is responsible for parsing the calib_manager.yaml file from Unimore Racing.
It contains information about the transformations between the various sensors
on the car and about the intrinsic parameters of the cameras.
"""

from collections import defaultdict
import os
from attr import dataclass
import numpy as np
import yaml
from typing import Tuple
from scipy.spatial.transform import Rotation


Vec3f = Tuple[float, float, float]


@dataclass
class CameraIntrinsics:
    width: int
    height: int
    fisheye: bool
    fx: float
    fy: float
    cx: float
    cy: float
    distortion_coeffs: list


@dataclass
class Transformation:
    translation: Vec3f
    rotation: Vec3f


class CalibManagerHandler:
    """
    This class contains useful methods to parse UR calib_manager.yaml file.
    """

    def __init__(self, filepath: str) -> None:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Calib manager file not found: {filepath}")
        self.filepath = filepath
        self.cameras = {}
        self.transformations = {}
        # TF graph is structured like this because a child can have only one parent
        self.tf_graph_fw = defaultdict(list)
        self.tf_graph_bw = {}
        self.tf_tree = {}
        self.load_calib_manager()
        print("[DEBUG] Correctly loaded calib_manager.yaml file.")

    @staticmethod
    def _pose_to_transform(pose):
        """
        Convert [x, y, z, roll, pitch, yaw] to 4x4 transformation matrix
        """
        x, y, z, roll, pitch, yaw = pose

        # Convert degrees to radians for rotation
        roll_rad = np.radians(roll)
        pitch_rad = np.radians(pitch)
        yaw_rad = np.radians(yaw)

        # Create rotation matrix from Euler angles (ZYX convention typical for vehicles)
        rotation = Rotation.from_euler("zyx", [yaw_rad, pitch_rad, roll_rad])
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
            camera = CameraIntrinsics(
                cam_data["width"],
                cam_data["height"],
                cam_data["fisheye"],
                cam_data["K"][0],
                cam_data["K"][1],
                cam_data["K"][2],
                cam_data["K"][3],
                cam_data["D"],
            )
            self.cameras[camera_name] = camera

        # Parse transformations
        tf_entries = data.get("tf_manager", {}).get("tree", {}).get("static_tf", [])
        for tf_data in tf_entries:
            child = tf_data["targetLink"]
            parent = tf_data["baseLink"]
            transformation = Transformation(
                tf_data["tf"][:3],
                tf_data["tf"][3:],
            )
            self.transformations[child] = transformation
            self.tf_graph_fw[parent].append(child)
            self.tf_graph_bw[child] = parent

            # Build tf_tree for easier traversal
            self.tf_tree.setdefault(parent, {})[child] = {
                "transform": self._pose_to_transform(tf_data["tf"])
            }

    def find_transform_path(
        self, start_frame: str, end_frame: str
    ) -> Tuple[list, list]:
        """
        Find the transformation path from start_frame to end_frame.
        Returns two lists of transformations: one for backward and one for forward transformations.
        """
        # Backward: at first I need to find the path to the common ancestor
        current_frame = start_frame
        backward_tfs = [current_frame]
        while current_frame in self.tf_graph_bw:  # While there is a parent
            parent_frame = self.tf_graph_bw[current_frame]
            backward_tfs.append(parent_frame)
            if parent_frame == end_frame:
                return backward_tfs, []
            current_frame = parent_frame

        # Forward: now I need to find the path to the end_frame
        forward_tfs = []
        current_frame = backward_tfs[-1] if backward_tfs else start_frame
        found = True
        while current_frame != end_frame and found:
            found = False
            for child in self.tf_graph_fw[current_frame]:
                forward_tfs.append(self.transformations[child])
                current_frame = child
                found = True
                break

        if not found:
            print(
                f"[ERROR] No transformation path found from {start_frame} to {end_frame}."
            )
            return [], []
        forward_tfs.append(current_frame)

        return backward_tfs, forward_tfs
