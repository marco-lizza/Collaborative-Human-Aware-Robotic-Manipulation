import random
import os

# --- IMPOSTAZIONI (Modifica questi tempi con i tuoi esatti) ---
DURATA_STATICO = 6.2   # Quanti secondi l'uomo aspetta fermo tra un gesto e l'altro
DURATA_GESTO_1 = 6.2 # Durata in secondi dell'animazione 1
DURATA_GESTO_2 = 6.2  # Durata in secondi dell'animazione 2 (sostituisci col tuo valore!)

NUM_GESTI_TOTALI = 5  # Genera n gesti a caso. Quando finiscono, il loop ricomincia.

# --- MODIFICA QUESTA VARIABILE, da sistemare per renderla relativa ---
# Percorso in cui salvare il file generato
OUTPUT_FILE = "/home/simona99/charm_ws/src/simulation_env/male_visitor/male_visitor_random.sdf"
# --------------------------------------------------------------

def genera_sdf():
    sdf_header = """<?xml version="1.0" ?>
                <sdf version="1.7">
                <actor name="male_visitor">
                    <pose>-7.5 -1.2 1 -1.57 0 -1.57</pose> 

                    <skin>
                    <filename>male_visitor_static.dae</filename>
                    <scale>1.0</scale>
                    </skin>

                    <animation name="posa_statica">
                    <filename>male_visitor_static.dae</filename>
                    <scale>1.0</scale>
                    <interpolate_x>false</interpolate_x>
                    </animation>

                    <animation name="gesto_1">
                    <filename>male_visitor_gesture1.dae</filename>
                    <scale>1.0</scale>
                    <interpolate_x>false</interpolate_x>
                    </animation>

                    <animation name="gesto_2">
                    <filename>male_visitor_gesture2.dae</filename>
                    <scale>1.0</scale>
                    <interpolate_x>false</interpolate_x>
                    </animation>

                    <script>
                    <loop>true</loop>
                    <auto_start>true</auto_start>
                """
    trajectories = ""
    current_time = 0.0

    print("Generazione sequenza casuale in corso...")
    
    for i in range(NUM_GESTI_TOTALI):
        # 1. Aggiungiamo un pezzo di animazione in cui sta fermo
        trajectories += f"""
      <trajectory id="{i*2}" type="posa_statica">
        <waypoint><time>{current_time:.2f}</time><pose>0 0 0 0 0 0</pose></waypoint>
        <waypoint><time>{(current_time + DURATA_STATICO):.2f}</time><pose>0 0 0 0 0 0</pose></waypoint>
      </trajectory>"""
        current_time += DURATA_STATICO

        # 2. Scegliamo a caso il gesto 1 o il gesto 2
        scelta = random.choice(["gesto_1", "gesto_2"])
        durata = DURATA_GESTO_1 if scelta == "gesto_1" else DURATA_GESTO_2
        
        print(f"Gesto {i+1}: {scelta}")

        # 3. Aggiungiamo la traiettoria del gesto scelto
        trajectories += f"""
      <trajectory id="{i*2 + 1}" type="{scelta}">
        <waypoint><time>{current_time:.2f}</time><pose>0 0 0 0 0 0</pose></waypoint>
        <waypoint><time>{(current_time + durata):.2f}</time><pose>0 0 0 0 0 0</pose></waypoint>
      </trajectory>"""
        current_time += durata

    sdf_footer = """
    </script>
  </actor>
</sdf>
"""
    # Salvataggio del file
    with open(OUTPUT_FILE, "w") as f:
        f.write(sdf_header + trajectories + sdf_footer)
    
    print(f"\nFatto! File generato: {OUTPUT_FILE}")
    print(f"Durata totale del loop prima di ricominciare: {current_time/60:.1f} minuti.")

if __name__ == "__main__":
    genera_sdf()