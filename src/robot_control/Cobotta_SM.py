import rclpy
from rclpy.node import Node
import cv2
import math

# Importiamo le nostre classi dai file separati
from CobottaArm import CobottaArm
from CobottaCamera import CobottaCamera
from GestureAnalyzer import GestureAnalyzer

class CobottaStateMachine(Node):
    """Nodo principale che gestisce la logica di alto livello e gli stati."""
    def __init__(self):
        super().__init__('cobotta_state_machine')
        
        joints = ["1", "2", "3", "4", "5", "6", "_left", "_right"]
        
        # Istanziamo le classi importate
        self.robot = CobottaArm(self, joints)
        self.camera = CobottaCamera(self, '/camera')
        self.analyzer = GestureAnalyzer()
        
        self.current_state = "INIT"
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        
        self.get_logger().info("Macchina a stati Cobotta avviata.")

    def state_machine_loop(self):
        # 1. Acquisizione dati
        frame = self.camera.get_frame()
        gesture_id = self.analyzer.analyze(frame)
        
        #Visualizzazione (Opzionale)
        
        if frame is not None:
            cv2.putText(frame, f"Gesto: {gesture_id} | Stato: {self.current_state}", 
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
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
                self.get_logger().info("Azione 1 avviata")
                self.current_state = "ACTION_1"
            elif gesture_id == 2:
                self.get_logger().info("Azione 2 avviata")
                self.current_state = "ACTION_2"
            elif gesture_id == 3:
                self.get_logger().info("Azione 3 avviata")
                self.current_state = "ACTION_3"

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
            

        elif self.current_state == "ACTION_2":
            pos_esultanza = {
                "1": 1.45, "2": 0.81, "3": 1.69, "4": -2.97, "5": -0.46, "6": -2.02,
                "_left": 0.0, "_right": 0.00
            }
            self.robot.move_all_joints(pos_esultanza)
            
            if self.robot.is_target_reached(pos_esultanza):
                if gesture_id == 4:
                    self.current_state = "INIT"

        elif self.current_state == "ACTION_3":
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