import rclpy
from rclpy.node import Node
import cv2

# Importiamo le nostre classi dai file separati
from CobottaArm import CobottaArm
from CobottaCamera import CobottaCamera
from GestureAnalyzer import GestureAnalyzer
from ObjectDetector import ObjectDetector

class CobottaStateMachine(Node):
    """Nodo principale che gestisce la logica di alto livello e gli stati."""
    def __init__(self):
        super().__init__('cobotta_state_machine')
        
        joints = ["1", "2", "3", "4", "5", "6", "_left", "_right"]
        
        # Istanziamo le classi importate
        self.robot = CobottaArm(self, joints)
        self.camera = CobottaCamera(self, '/camera')
        self.analyzer = GestureAnalyzer()
        self.object_detector = ObjectDetector() #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        
        self.current_state = "INIT"
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        
        self.get_logger().info("Macchina a stati Cobotta avviata.")

    def state_machine_loop(self):
        # 1. Acquisizione dati
        frame = self.camera.get_frame()
        gesture_id = self.analyzer.analyze(frame)
        detected_object = self.object_detector.identify_object(frame)[0] # NUOVO: Rilevamento oggetto AAAAAAAAAAAAAA
        
        # 2. Visualizzazione (Opzionale)
        if frame is not None:
            # Mostra gesto e stato
            cv2.putText(frame, f"Gesto: {gesture_id} | Stato: {self.current_state}", 
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # NUOVO: Mostra cosa sta leggendo l'ArUco
            cv2.putText(frame, f"Goal pos: {detected_object}", #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                        (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            
            cv2.imshow("Cobotta Vision", frame)
            cv2.waitKey(1)
        
        # 3. Logica degli Stati
        if self.current_state == "INIT":
            self.current_state = "WAITING_FOR_IDLE"
            
        elif self.current_state == "WAITING_FOR_IDLE":
            self.robot.go_idle()

            if self.robot.is_target_reached(self.robot.IDLE_POSITION):
                self.get_logger().info("Posizione IDLE raggiunta! Vado in MONITORING.")
                self.current_state = "WAITING_FOR_MONITORING"

        elif self.current_state == "WAITING_FOR_MONITORING":
            self.robot.go_monitoring()
            if self.robot.is_target_reached(self.robot.MONITORING_POSITION):
                self.get_logger().info("Posizione MONITORING raggiunta! In attesa di comandi.")
                self.current_state = "WAITING_FOR_COMMAND"
            
        elif self.current_state == "WAITING_FOR_COMMAND":
            if gesture_id == 1:
                self.get_logger().info("Richiesta Azione 1 (Tazza). Controllo lo slot...")
                self.current_state = "CHECK_SLOT_1"
            elif gesture_id == 2:
                self.get_logger().info("Richiesta Azione 2 (Piatto). Controllo lo slot...")
                self.current_state = "CHECK_SLOT_2"
            elif gesture_id == 3:
                self.get_logger().info("Azione 3 avviata")
                self.current_state = "ACTION_3"

        # --- NUOVI STATI DI CONTROLLO SLOT ---
        elif self.current_state == "CHECK_SLOT_1":
            if detected_object == "EMPTY": #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                self.get_logger().info("Slot libero! Procedo a prendere la Tazza.")
                self.current_state = "ACTION_1"
            elif detected_object == "CUP": #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                self.get_logger().info("C'è già una tazza nello slot. Ritorno in attesa.")
                self.current_state = "INIT"
            elif detected_object == "PLATE": #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                self.get_logger().info("ATTENZIONE: C'è un piatto! Devo sgomberarlo (Logica da implementare).")
                self.current_state = "INIT" # Sostituisci "INIT" con lo stato di sgombero quando lo avrai

        elif self.current_state == "CHECK_SLOT_2":
            if detected_object == "EMPTY":
                self.get_logger().info("Slot libero! Procedo a prendere il Piatto.")
                self.current_state = "ACTION_2"
            elif detected_object == "PLATE":
                self.get_logger().info("C'è già un piatto nello slot. Ritorno in attesa.")
                self.current_state = "INIT"
            elif detected_object == "CUP":
                self.get_logger().info("ATTENZIONE: C'è una tazza! Devo sgomberarla (Logica da implementare).")
                self.current_state = "INIT" # Sostituisci "INIT" con lo stato di sgombero quando lo avrai

        # --- AZIONI ESISTENTI INALTERATE ---
        
        #action per le 1 dito rilevato, prende tazza
        elif self.current_state.startswith("ACTION_1"):
            #allineamento con la tazza
            pos0 = {
                "1": 0.0, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00,
                "_left": 0.0, "_right": 0.0
            }
            #discesa
            pos1 = {
                "1": 0.0, "2": 1.65, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00,
                "_left": 0.0, "_right": 0.0
            }
            #chiusura
            pos2 = {
                "1": 0.0, "2": 1.65, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00,
                "_left": -0.02, "_right": -0.02
            }
            #alzata
            pos3 = {
                "1": 0.0, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00,
                "_left": -0.02, "_right": -0.02
            }

            if(self.current_state=="ACTION_1"):
                self.robot.move_all_joints(pos0)   
                if self.robot.is_target_reached(pos0):
                    self.get_logger().info("Azione 1 _ posizione 0 raggiunta")
                    self.current_state="ACTION_1_POS0"

            if(self.current_state=="ACTION_1_POS0"):
                self.robot.move_all_joints(pos1)   
                if self.robot.is_target_reached(pos1):
                    self.get_logger().info("Azione 1 _ posizione 1 raggiunta")
                    self.current_state="ACTION_1_POS1"

            if(self.current_state=="ACTION_1_POS1"):
                self.robot.move_all_joints(pos2)   
                if self.robot.is_target_reached(pos2):
                    self.get_logger().info("Azione 1 _ posizione 2 raggiunta")
                    self.current_state="ACTION_1_POS2"

            if(self.current_state=="ACTION_1_POS2"):
                self.robot.move_all_joints(pos3)   
                if self.robot.is_target_reached(pos3):
                    self.get_logger().info("Azione 1 _ posizione 3 raggiunta")
                    if gesture_id == 4: 
                        self.current_state = "INIT"
            
        #action per le 2 dita rilevate, prende piatto
        elif self.current_state.startswith("ACTION_2"):
            #rotazione
            pos0 = {
                "1": -0.96, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.00, "6": 0.00,
                "_left": 0.0, "_right": 0.0
            }
            #rotazione pinza e inclinamento pinza
            pos1 = {
                "1": -0.96, "2": 1.30, "3": 0.31, "4": 0.00, "5": 1.40, "6": 1.70,
                "_left": 0.0, "_right": 0.0
            }
            #discesa
            pos2 = {
                "1": -0.96, "2": 1.55, "3": 0.31, "4": 0.00, "5": 1.40, "6": 1.70,
                "_left": 0.0, "_right": 0.0
            }
            #chiusura
            pos3 = {
                "1": -0.96, "2": 1.55, "3": 0.31, "4": 0.00, "5": 1.50, "6": 1.70,
                "_left": -0.02, "_right": -0.02
            }
            #alzata
            pos4 = {
                "1": -0.96, "2": 1, "3": 0.31, "4": 0.00, "5": 1.50, "6": 1.70,
                "_left": -0.02, "_right": -0.02
            }

            if(self.current_state=="ACTION_2"):
                self.robot.move_all_joints(pos0)   
                if self.robot.is_target_reached(pos0):
                    self.get_logger().info("Azione 2 _ posizione 0 raggiunta")
                    self.current_state="ACTION_2_POS0"

            if(self.current_state=="ACTION_2_POS0"):
                self.robot.move_all_joints(pos1)
                if self.robot.is_target_reached(pos1):
                    self.get_logger().info("Azione 2 _ posizione 1 raggiunta")
                    self.current_state="ACTION_2_POS1"

            if(self.current_state=="ACTION_2_POS1"):
                self.robot.move_all_joints(pos2)   
                if self.robot.is_target_reached(pos2):
                    self.get_logger().info("Azione 2 _ posizione 2 raggiunta")
                    self.current_state="ACTION_2_POS2"

            if(self.current_state=="ACTION_2_POS2"):
                self.robot.move_all_joints(pos3)   
                if self.robot.is_target_reached(pos3):
                    self.get_logger().info("Azione 2 _ posizione 3 raggiunta")
                    self.current_state="ACTION_2_POS3"

            if(self.current_state=="ACTION_2_POS3"):
                self.robot.move_all_joints(pos4)   
                if self.robot.is_target_reached(pos4):
                    self.get_logger().info("Azione 2 _ posizione 4 raggiunta")
                    if gesture_id == 4: 
                        self.current_state = "INIT"

        #action non ancora impostata
        elif self.current_state.startswith("ACTION_3"):
            pos_saluto = {
                "1": 1, "2": 0.74, "3": 0.32, "4": 0.02, "5": -0.52, "6": -2.01,
                "_left": -0.01, "_right": -0.01
            }
            self.robot.move_all_joints(pos_saluto)
            
            if self.robot.is_target_reached(pos_saluto):
                if gesture_id == 4:
                    self.current_state = "INIT"

def main(args=None):
    rclpy.init(args=args)
    nodo = CobottaStateMachine()
    
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()