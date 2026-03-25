#!/bin/bash
# Nascondi l'immagine 1
ign service -s /world/worldCobotta/set_pose --reqtype ignition.msgs.Pose --reptype ignition.msgs.Boolean --req 'name: "textured_plane_one", position: {z: -10.0}' --timeout 500

# Mostra l'immagine 2
ign service -s /world/worldCobotta/set_pose --reqtype ignition.msgs.Pose --reptype ignition.msgs.Boolean --req 'name: "textured_plane_two", position: {x: -8.0, y: -1.2, z: 1.75}, orientation: {x: 0.0, y: 0.7071068, z: 0.0, w: 0.7071068}' --timeout 500