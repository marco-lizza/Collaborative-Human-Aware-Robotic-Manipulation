#!/bin/bash
source /opt/ros/humble/setup.bash
ros2 launch /home/marco/Desktop/charm_ws/src/robot_description/launch/display.launch.py rvizconfig:=/home/marco/Desktop/charm_ws/src/robot_description/launch/rviz/urdf.rviz model:=/home/marco/Desktop/charm_ws/src/robot_description/Cobotta.urdf
