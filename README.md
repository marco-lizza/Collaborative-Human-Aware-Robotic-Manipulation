# Progetto di Robotica Collaborativa (ROS 2 Humble + Gazebo Fortress)

Questo repository contiene il workspace ROS 2 per la simulazione di un task collaborativo uomo-robot. Il progetto è sviluppato per essere eseguito su **Ubuntu 22.04** con **ROS 2 Humble**.

## Struttura del Workspace

Il workspace segue l'architettura standard di ROS 2 usando colcon. Tutto il codice sorgente si trova all'interno della cartella `src/`, divisa in tre pacchetti principali:

    charm_ws/
    ├── .gitignore               # Impedisce di caricare file pesanti/compilati su Git
    ├── README.md                # Questo file
    └── src/
        ├── robot_description/   # (C++/CMake) Modelli e cinematica
        ├── simulation_env/      # (C++/CMake) Ambienti e sensori
        └── robot_control/       # (Python) Logica e Macchina a Stati

### I Pacchetti nel Dettaglio

#### robot_description (Robot & Motion Engineer)
Questo pacchetto conterrà tutto ciò che definisce il "corpo" del robot:
* File **URDF/XACRO** (geometrie, masse, inerzie, collisioni).
* Mesh 3D (visual e collision) del braccio robotico e del gripper.
* Configurazioni di **MoveIt 2** per la cinematica inversa e la pianificazione delle traiettorie.
* File di *Launch* per caricare il robot su rViz2.

#### 2. simulation_env (Environment & Perception Engineer)
Questo pacchetto gestisce il "mondo" in cui il robot opera:
* File `.sdf` o `.world` di **Gazebo Fortress** (tavoli, oggetti, illuminazione).
* Il plugin dell'**Actor umano** per simulare l'interazione.
* Nodi ROS 2 (in C++ o Python) per elaborare i dati dei sensori simulati (es. LiDAR o telecamere) e rilevare l'avvicinamento dell'umano.

#### 3. robot_control (System & Control Engineer)
Il "cervello" del sistema. Essendo basato sulla logica, questo pacchetto è sviluppato in **Python**:
* La **Macchina a Stati** (Event-Driven) che orchestra il task collaborativo.
* Nodi per inviare i comandi di movimento al robot in base agli input dell'ambiente.

---

## Cartelle di Sistema (Ignorate da Git)
Quando si compilerà in locale, colcon genererà automaticamente tre cartelle nella radice del workspace: `build/`, `install/` e `log/`.
**NON forzate mai l'inserimento di queste cartelle su Git.** Il file `.gitignore` è già configurato per escluderle. 

---

## Come Iniziare

**1. Clona il repository:**
Apri il terminale e scarica il codice (assicurati di non avere già una cartella charm_ws):
`git clone https://github.com/marco-lizza/Collaborative-Human-Aware-Robotic-Manipulation.git charm_ws`
`cd charm_ws`

**2. Compila il workspace:**
`colcon build`

**3. Registra l'ambiente:**
`source install/setup.bash`
*(Consiglio: aggiungi questo comando al tuo ~/.bashrc per non doverlo ripetere ogni volta).Attento al percorso-deve puntare alla directory install e al file setup.bash della cartella del progetto*