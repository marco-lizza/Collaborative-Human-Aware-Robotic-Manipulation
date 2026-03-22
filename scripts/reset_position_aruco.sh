#!/bin/bash
ign service -s /world/worldCobotta/set_pose \
--reqtype ignition.msgs.Pose \
--reptype ignition.msgs.Boolean \
--req 'name: "textured_plane", position: {x: -7, y: -1.2, z: 2.2}, orientation: {x: -0.5, y: 0.5, z: -0.5, w: 0.5}' \
--timeout 2000