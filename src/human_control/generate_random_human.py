import random
import os
import sys

# Path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
percorso_calcolato = os.path.join(SCRIPT_DIR, "..", "simulation_env", "male_visitor")
CARTELLA_DESTINAZIONE = os.path.abspath(percorso_calcolato)
OUTPUT_FILE = os.path.join(CARTELLA_DESTINAZIONE, "male_visitor_random.sdf")

FILE_STATIC = "male_visitor_static.dae"
FILE_GESTURE_1 = "male_visitor_gesture1.dae"
FILE_GESTURE_2 = "male_visitor_gesture2.dae" 

# --- IMPOSTAZIONI ANIMAZIONI E TEMPI ---
DURATA_STATICO = 90.0  # Modificato a 90 secondi (1.5 minuti)
DURATA_GESTO_1 = 6.1
DURATA_GESTO_2 = 6.1 
NUM_RIPETIZIONI = 6  
MIN_PERCENTUALE = 0.3  

if len(sys.argv) > 1:
    try:
        NUM_RIPETIZIONI = int(sys.argv[1])
        print(f"Hai scelto un numero personalizzato: {NUM_RIPETIZIONI} azioni.")
    except ValueError:
        print("Attenzione: non hai inserito un numero valido. Uso il default.")
else:
    print(f"Nessun numero inserito. Uso il default: {NUM_RIPETIZIONI} azioni.")

# --- IMPOSTAZIONI SPAZIALI ---
POS_X = -7.5
POS_Y = -1.2
Z_HEIGHT = 0.9  
ROLL = -1.57  
PITCH = 0.0
YAW = -1.57 

def genera_sdf():
    current_time = 0.0

    # PREPARAZIONE DELLA LISTA GESTI 
    min_richiesti = int(NUM_RIPETIZIONI * MIN_PERCENTUALE)
    scelte_gesti = ["gesto_1"] * min_richiesti + ["gesto_2"] * min_richiesti
    
    rimanenti = NUM_RIPETIZIONI - len(scelte_gesti)
    if rimanenti > 0:
        for _ in range(rimanenti):
            scelte_gesti.append(random.choice(["gesto_1", "gesto_2"]))
            
    random.shuffle(scelte_gesti)

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

    # --- CICLO TRAIETTORIA ---
    # Invertito l'ordine: prima il gesto, poi lo statico
    for i in range(NUM_RIPETIZIONI):
        # 1. GESTO (Viene eseguito per primo)
        scelta = scelte_gesti[i]
        durata_g = DURATA_GESTO_1 if scelta == "gesto_1" else DURATA_GESTO_2
        
        sdf += f"""      <trajectory id="{i*2}" type="{scelta}">\n        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n"""
        current_time += durata_g
        sdf += f"""        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n      </trajectory>\n"""

        # 2. POSA STATICA (Dura 90 secondi)
        sdf += f"""      <trajectory id="{i*2 + 1}" type="posa_statica">\n        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n"""
        current_time += DURATA_STATICO
        sdf += f"""        <waypoint><time>{current_time:.2f}</time><pose>{POS_X} {POS_Y} {Z_HEIGHT} {ROLL} {PITCH} {YAW}</pose></waypoint>\n      </trajectory>\n"""

    sdf += """    </script>\n  </actor>\n</sdf>\n"""

    with open(OUTPUT_FILE, "w") as f:
        f.write(sdf)

if __name__ == "__main__":
    print("Avvio la generazione della traiettoria (Gesto -> 90s Statico)...")
    genera_sdf()
    print(f"Generazione completata! L'attore farà {NUM_RIPETIZIONI} cicli.")