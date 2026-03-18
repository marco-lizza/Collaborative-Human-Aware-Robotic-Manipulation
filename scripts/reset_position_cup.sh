#!/bin/bash
ign service -s /world/worldCobotta/set_pose --reqtype ignition.msgs.Pose --reptype ignition.msgs.Boolean --req 'name: "Cup", position: {x: -9.05, y: -1.675, z: 1.05}, orientation: {x: 0.0, y: 0.0, z: 0.6442177, w: 0.7648422}' --timeout 2000 
