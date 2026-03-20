#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

WS_ROOT="$SCRIPT_DIR/.."

LAUNCH_FILE="$WS_ROOT/src/robot_description/launch/display.launch.py"
RVIZ_CONFIG="$WS_ROOT/src/robot_description/launch/rviz/urdf.rviz"
MODEL_URDF="$WS_ROOT/src/robot_description/Cobotta.urdf"

source /opt/ros/humble/setup.bash

ros2 launch "$LAUNCH_FILE" \
    rvizconfig:="$RVIZ_CONFIG" \
    model:="$MODEL_URDF"