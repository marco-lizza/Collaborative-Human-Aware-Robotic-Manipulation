#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

CONFIG_PATH="$SCRIPT_DIR/../src/robot_description/map.yaml"

if [ ! -f "$CONFIG_PATH" ]; then
    echo "Errore: File di configurazione non trovato in $CONFIG_PATH"
    exit 1
fi

ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:="$CONFIG_PATH"