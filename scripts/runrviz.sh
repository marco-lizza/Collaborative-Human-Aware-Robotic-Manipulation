#!/bin/bash
source /opt/ros/humble/setup.bash
ros2 launch /home/nicolas/Scrivania/charm_ws/src/robot_description/launch/display.launch.py rvizconfig:=/home/nicolas/Scrivania/charm_ws/src/robot_description/launch/rviz/urdf.rviz model:=/home/nicolas/Scrivania/charm_ws/src/robot_description/Cobotta.urdf
