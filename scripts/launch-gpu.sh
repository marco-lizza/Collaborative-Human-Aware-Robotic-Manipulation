#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR/../src/simulation_env" || { echo "Percorso non trovato"; exit 1; }

# Forzo l'uso della GPU NVIDIA
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia

ign gazebo -v 4 worldCobotta.sdf