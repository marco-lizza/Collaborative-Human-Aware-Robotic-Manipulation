#!/bin/bash
ign service -s /world/worldCobotta/set_pose --reqtype ignition.msgs.Pose --reptype ignition.msgs.Boolean --req 'name: "Dish", position: {x: -9.38, y: -1.38, z: 1.05}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 0.0}' --timeout 2000 
