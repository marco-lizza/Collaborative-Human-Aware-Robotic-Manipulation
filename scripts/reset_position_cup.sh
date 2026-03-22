#!/bin/bash
ign service -s /world/worldCobotta/set_pose \
--reqtype ignition.msgs.Pose \
--reptype ignition.msgs.Boolean \
--req 'name: "Cup", position: {x: -9.36, y: -1.02, z: 1.14}, orientation: {x: 0.0, y: 0.0, z: -0.1986693, w: 0.9800666}' \
--timeout 2000