#!/bin/bash
ign service -s /world/worldCobotta/set_pose \
--reqtype ignition.msgs.Pose \
--reptype ignition.msgs.Boolean \
--req 'name: "Cup", position: {x: -8.52, y: -1.2, z: 1.14}, orientation: {x: 0.0, y: 0.0, z: 1.0, w: 0.0}' \
--timeout 2000