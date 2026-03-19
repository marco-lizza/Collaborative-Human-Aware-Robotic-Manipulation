#!/bin/bash
cd ~/Scrivania/charm_ws/src/simulation_env || exit
ign gazebo -v 4 worldCobotta.sdf
