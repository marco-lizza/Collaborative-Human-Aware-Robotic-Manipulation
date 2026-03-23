#!/bin/bash

# Trova la cartella dove si trova questo script (la cartella 'scripts')
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Costruiamo il percorso esatto verso il nuovo nascondiglio del file Python
PYTHON_SCRIPT="$SCRIPT_DIR/../src/male_visitor_controll/generate_random_human.py"

echo "Avvio la generazione della traiettoria per l'umano..."

# Lancia lo script Python
python3 "$PYTHON_SCRIPT"

echo "Generazione completata! Ora puoi avviare Gazebo."