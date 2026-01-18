# MIT License
#
# Copyright (c) 2025 Institute for Automotive Engineering (ika), RWTH Aachen University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import time

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .dataload.calib_manager_handler import CalibManagerHandler


def validate_args(window: MainWindow):
    if len(sys.argv) != 6:
        print("[ERROR] Invalid number of arguments. Switching to GUI mode.")
        return
    
    arg_mode, arg_bag_path, arg_calib_manager_path, arg_lidar_topic, arg_camera_topic = sys.argv[1:6]
    
    if arg_mode != "--lidar2cam":
        print("[ERROR] Unsupported/Invalid mode argument. Switching to GUI mode.")
        return
    
    window.select_calibration_type("LiDAR2Cam")
    window.load_bag_from_path(arg_bag_path)
    window.load_camerainfo_from_path(arg_calib_manager_path)
    window.update_proceed_button_state()
    if not window.proceed_button.isEnabled():
        print("[ERROR] Invalid arguments. Switching to GUI mode.")
        return
    
    if arg_lidar_topic not in [
        window.pointcloud_topic_combo.itemText(i)
        for i in range(window.pointcloud_topic_combo.count())
    ]:
        print(f"[ERROR] Invalid lidar topic: {arg_lidar_topic}. Switching to GUI mode.")
        return
    window.pointcloud_topic_combo.setCurrentText(arg_lidar_topic)
    
    if arg_camera_topic not in [
        window.image_topic_combo.itemText(i)
        for i in range(window.image_topic_combo.count())
    ]:
        print(f"[ERROR] Invalid camera topic: {arg_camera_topic}. Switching to GUI mode.")
        return
    window.image_topic_combo.setCurrentText(arg_camera_topic)
    window.process_rosbag_data()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    validate_args(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
