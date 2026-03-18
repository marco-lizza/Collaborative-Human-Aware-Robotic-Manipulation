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

        elif self.current_state == "ACTION_1":
            pos_curioso = {
                "1": 1.0, "2": -0.84, "3": 0.32, "4": -1.13, "5": -0.49, "6": -2.04,
                "_left": 0.0, "_right": 0.0
            }
            self.robot.move_all_joints(pos_curioso)
            
            if self.robot.is_target_reached(pos_curioso):
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