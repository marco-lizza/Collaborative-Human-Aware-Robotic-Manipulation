# Progetto di Robotica Collaborativa (ROS 2 Humble + Gazebo Fortress)

Questo repository contiene il workspace ROS 2 per la simulazione di un task collaborativo uomo-robot. Il progetto è sviluppato per essere eseguito su **Ubuntu 22.04** con **ROS 2 Humble**.

## Struttura del Workspace

    charm_ws/
    ├── .gitignore               # Impedisce di caricare file pesanti/compilati su Git
    ├── README.md                # Questo file
    ├── scripts/                 # Script di automazione per l'avvio del sistema
    │   ├── bridge.sh
    │   ├── launch.sh
    │   └── runrviz.sh
    │   └── ...
    └── src/
        ├── robot_description/   
        ├── simulation_env/    
        ├── robot_control/   
        └── human_control/   

Tutto il codice sorgente si trova all'interno della cartella `src/`, divisa in quattro pacchetti principali:

### I Pacchetti nel Dettaglio

#### 1. robot_description (Robot & Motion Engineer)
Questo pacchetto contiene tutto ciò che definisce il "corpo" del robot:
* File **URDF/SDF** (geometrie, masse, inerzie, collisioni).
* Mesh 3D (visual e collision) del braccio robotico e del gripper.

#### 2. simulation_env (Environment & Perception Engineer)
Questo pacchetto gestisce il "mondo" in cui il robot opera:
* File `.sdf` di **Gazebo Fortress** (tavoli, oggetti).
* File `.obj` o `.dae` contenenti i modelli 3D (tavoli, oggetti).

#### 3. robot_control (System & Control Engineer)
Il "cervello" del sistema. Essendo basato sulla logica, questo pacchetto è sviluppato in **Python**:
* La **Macchina a Stati** (Event-Driven) che orchestra il task collaborativo.
* Nodi per inviare i comandi di movimento al robot in base agli input dell'ambiente.

#### 4. human_control (Human animation manager)
Questo pacchetto è sviluppato in **Python**:
* Contiene il file che permette di generare l'sdf dell'umano in modo randomico.

### Gli Script di Sistema

La cartella `scripts/` contiene dei file batch fondamentali per semplificare l'avvio dei vari moduli del progetto:
* `launch.sh`: Avvia il simulatore Gazebo Fortress e carica il mondo virtuale (`worldCobotta.sdf`) con il robot e l'ambiente.
* `bridge.sh`: Lancia il pacchetto `ros_gz_bridge` per instaurare la comunicazione bidirezionale tra i topic di Gazebo e quelli nativi di ROS 2.
* `runrviz.sh`: Avvia l'interfaccia RViz per la visualizzazione cinematica e dei sensori in tempo reale.

---

## Prerequisiti e Installazione

Per garantire il corretto funzionamento della pipeline di Computer Vision e della simulazione, è fondamentale installare le dipendenze corrette, prestando attenzione ad alcuni conflitti di versione.

### Dipendenze ROS 2
Assicurati di aver installato i pacchetti di sistema necessari (incluso il launch per URDF):
    `sudo apt install ros-humble-urdf-launch`

### Dipendenze Python (Requirements Rigidi)
Durante lo sviluppo sono emersi conflitti critici tra NumPy 2.x e la libreria pre-compilata `cv_bridge` di ROS 2, oltre a deprecazioni nelle API di MediaPipe. **È obbligatorio rispettare queste versioni:**

1. Disinstalla eventuali versioni conflittuali di OpenCV:
    `pip uninstall opencv-contrib-python opencv-python -y`
2. Installa le librerie con le versioni limitate:
    `pip install "numpy<2.0.0"`
    `pip install "opencv-contrib-python<4.10.0" "opencv-python<4.10.0"`
    `pip install mediapipe==0.10.14`

---

## Come Iniziare

### 1. Clona il repository
Apri il terminale e scarica il codice (assicurati di non avere già una cartella `charm_ws`):
    `git clone https://github.com/marco-lizza/Collaborative-Human-Aware-Robotic-Manipulation.git charm_ws`
    `cd charm_ws`

### 2. Generazione dell'Attore Umano
Prima di avviare la simulazione, è necessario generare il file `male_visitor_random.sdf` che contiene la sequenza di movimenti dell'attore umano.

**Come generare la sequenza:**
Apri un terminale, spostati nella cartella dello script ed eseguilo con Python:
    `cd src/human_controll`
    `python3 generate_random_human.py [numero_azioni]`

**Esempi di utilizzo:**
* **Default:** Genera una sequenza standard di 6 azioni.
  `python3 generate_random_human.py`
* **Personalizzato:** Genera una sequenza con un numero specifico di azioni (es. 10).
  `python3 generate_random_human.py 10`

**Logica di funzionamento:**
Lo script crea un'animazione continua alternando pose statiche a due tipi di gesti (gesture1 e gesture2). Per evitare che la pura casualità generi sequenze monotone o ripetitive, lo script applica una logica di bilanciamento:
* **Garanzia Varietà:** È impostata una soglia minima del 30% per ogni tipo di gesto (es. su 30 azioni, avrai sempre almeno 9 "Gesto 1" e 9 "Gesto 2").
* **Casualità:** Il restante 40% delle azioni viene scelto in modo totalmente randomico.
* **Shuffle:** L'intera lista finale viene mescolata prima della scrittura del file.

Questo assicura che ogni avvio di Gazebo offra un'interazione sempre diversa, ma costantemente variegata e realistica.

### 3. Avvio della Simulazione
Dopo aver preparato il file dell'attore umano, sei pronto per avviare il sistema. Esegui i seguenti comandi posizionandoti sempre nella cartella principale del progetto (`charm_ws`):

1. **Avvia Gazebo:**
   Lancia il mondo simulato eseguendo:

       `./scripts/launch.sh`
   
   *Si aprirà la finestra di Gazebo con l'ambiente 3D.*

2. **Collega ROS a Gazebo:**
   In un nuovo terminale, avvia il bridge di comunicazione:

       `./scripts/bridge.sh`

3. **Esegui la Macchina a Stati:**
   In un terzo terminale, lancia la logica di controllo (il "cervello") per far partire la simulazione collaborativa:

       `python3 src/robot_control/cobottaSM.py`

4. **Avvia RViz (Opzionale):**
   In un ulteriore terminale (dopo aver avviato il bridge), puoi visualizzare lo stato interno del robot eseguendo:

       `./scripts/runrviz.sh`

---

## Troubleshooting e Note Architetturali

Durante l'integrazione tra la pipeline visiva e ROS 2, sono stati risolti i seguenti colli di bottiglia architetturali:

* **Conflitto NumPy / cv_bridge (`_ARRAY_API not found`)**: L'installazione standard di MediaPipe forza l'aggiornamento a NumPy 2.x, rompendo la compatibilità con le librerie ROS 2. Risolto eseguendo un downgrade esplicito a NumPy 1.x.
* **Compatibilità API MediaPipe (`AttributeError`)**: Nelle versioni di MediaPipe > 0.10.15, l'architettura legacy `mp.solutions` è stata deprecata. Il codice è stato stabilizzato bloccando la libreria alla release `0.10.14`.