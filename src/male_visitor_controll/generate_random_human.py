import random
import os

# --- IMPOSTAZIONI ANIMAZIONI E TEMPI ---
PERCORSO_BASE = "/home/simona99/charm_ws/src/simulation_env/male_visitor/"
FILE_STATIC = PERCORSO_BASE + "male_visitor_static.dae"
FILE_GESTURE_1 = PERCORSO_BASE + "male_visitor_gesture1.dae"
FILE_GESTURE_2 = PERCORSO_BASE + "male_visitor_gesture2.dae" 
OUTPUT_FILE = PERCORSO_BASE + "male_visitor_random.sdf"

DURATA_STATICO = 4.0
DURATA_GESTO_1 = 6.1
DURATA_GESTO_2 = 6.1 

# --- IMPOSTAZIONI SPAZIALI ---
POS_X = -7.5
POS_Y = -1.2
Z_HEIGHT = 0.9  

# RIMETTIAMO IL RADDRIZZAMENTO NEI WAYPOINT!
# Se è a testa in giù o sul fianco, il colpevole è questo numero. Prova 1.57 o -1.57
ROLL = -1.57  
PITCH = 0.0
YAW = -1.57 

def genera_sdf():
    current_time = 0.0

    sdf = f"""<?xml version="1.0" ?>
<sdf version="1.7">
  <actor name="male_visitor">
    <pose>0 0 0 0 0 0</pose> 

    <skin>
      <filename>{FILE_STATIC}</filename>
      <scale>1.0</scale>
    </skin>

    <animation name="posa_statica">
      <filename>{FILE_STATIC}</filename>
      <scale>1.0</scale>
      <interpolate_x>false</interpolate_x>
    </animation>
    <animation name="gesto_1">
      <filename>{FILE_GESTURE_1}</filename>
      <scale>1.0</scale>
      <interpolate_x>false</interpolate_x>
    </animation>
    <animation name="gesto_2">
      <filename>{FILE_GESTURE_2}</filename>
      <scale>1.0</scale>
      <interpolate_x>false</interpolate_x>
    </animation>

    <script>
      <loop>true</loop>
      <auto_start>true</auto_start>
"""

    for i in range(30):
        # I VALORI ROLL, PITCH E YAW SONO ORA DENTRO I WAYPOINT
        sdf += f"""      <trajectory id="{i*2}" type="posa_statica">\n        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n"""
        current_time += DURATA_STATICO
        sdf += f"""        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n      </trajectory>\n"""

        scelta = random.choice(["gesto_1", "gesto_2"])
        durata = DURATA_GESTO_1 if scelta == "gesto_1" else DURATA_GESTO_2
        
        sdf += f"""      <trajectory id="{i*2 + 1}" type="{scelta}">\n        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n"""
        current_time += durata
        sdf += f"""        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n      </trajectory>\n"""

    sdf += """    </script>\n  </actor>\n</sdf>\n"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(sdf)

if __name__ == "__main__":
    genera_sdf()