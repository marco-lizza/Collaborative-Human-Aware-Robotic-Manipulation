#!/bin/bash
ign service -s /world/worldCobotta/set_pose \
 --reqtype ignition.msgs.Pose \
 --reptype ignition.msgs.Boolean \
 --req 'name: "Dish", position: {x: -9.36, y: -1.38, z: 1.40}, orientation: {x: 0.0, y: 0.0, z: -0.552554, w: 0.833486}' \
 --timeout 2000