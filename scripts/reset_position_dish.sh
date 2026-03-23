#!/bin/bash

# Reset posizione e orientamento per "Plate"
ign service -s /world/worldCobotta/set_pose \
 --reqtype ignition.msgs.Pose \
 --reptype ignition.msgs.Boolean \
 --req 'name: "Plate", position: {x: -9.40, y: -1.38, z: 1.25}, orientation: {x: 0.0, y: 0.0, z: -0.602554, w: 0.833486}' \
 --timeout 2000

