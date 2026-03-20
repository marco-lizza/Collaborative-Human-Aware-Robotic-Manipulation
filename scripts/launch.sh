#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR/../src/simulation_env" || { echo "Percorso non trovato"; exit 1; }

ign gazebo -v 4 worldCobotta.sdf