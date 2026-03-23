import time
import rclpy
from rclpy.node import Node
import cv2
import math

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
        self.window_open = False
        
        # Variabili per la gestione dinamica delle traiettorie
        self.current_trajectory = []
        self.current_step = 0
        
        # --- DEFINIZIONE TRAIETTORIE (Liste di dizionari) ---
        
        # Traiettoria 1: Tazza
        self.action_1_trajectory = [
            {"1": -1.90, "2": 0.0, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00, "_left": 0.0, "_right": 0.0},
            {"1": -1.90, "2": 0.90, "3": 1.62, "4": 0.00, "5": 0.10, "6": 0.00, "_left": 0.0, "_right": 0.0},
            {"1": -1.90, "2": 1.25, "3": 1.58, "4": 0.00, "5": -1.02, "6": 0.00, "_left": 0.0, "_right": 0.0},
            {"1": -1.90, "2": 1.25, "3": 1.58, "4": 0.00, "5": -1.02, "6": 0.00, "_left": -0.02, "_right": -0.02},
            {"1": -1.90, "2": 1.00, "3": 1.50, "4": 0.00, "5": -0.80, "6": 0.00, "_left": -0.02, "_right": -0.02},
            {"1": -1.90, "2": 0.40, "3": 1.50, "4": 0.00, "5": -0.80, "6": 0.00, "_left": -0.02, "_right": -0.02},
            {"1": 1.65, "2": 0.40, "3": 1.50, "4": 0.00, "5": -0.80, "6": 0.00, "_left": -0.02, "_right": -0.02}, # presa tazza -> gira
            {"1": 1.35, "2": 0.99, "3": 1.50, "4": 0.00, "5": -0.80, "6": 0.00, "_left": -0.02, "_right": -0.02}, # si abbassa
            {"1": 1.35, "2": 0.99, "3": 1.50, "4": 0.00, "5": -0.80, "6": 0.00, "_left": 0.0, "_right": 0.0}      # molla tazza
        ]

        # Traiettoria 2: Piatto
        self.action_2_trajectory = [
            {"1": -1.289, "2": 0.625, "3": 1.480, "4": 2.214, "5": 0.030, "6": 2.425, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 0.925, "3": 1.380, "4": 2.214, "5": 0.030, "6": 2.425, "_left": 0.0, "_right": 0.0},

            {"1": -1.289, "2": 1.030, "3": 1.358, "4": 2.233, "5": 0.019, "6": 2.452, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 1.104, "3": 1.264, "4": 2.241, "5": 0.030, "6": 2.452, "_left": 0.0, "_right": 0.0},

            {"1": -1.289, "2": 1.030, "3": 1.358, "4": 2.233, "5": 0.030, "6": 2.452,  "_left": -0.02, "_right": -0.02},
            {"1": -1.289, "2": 0.600, "3": 1.358, "4": 2.233, "5": 0.019, "6": 2.452,  "_left": -0.02, "_right": -0.02},
            {"1": 1.445, "2": 0.600, "3": 1.190, "4": 2.214, "5": 0.030, "6": 2.485, "_left": -0.02, "_right": -0.02},
            {"1": 1.445, "2": 0.600, "3": 1.190, "4": 2.214, "5": 0.030, "6": 2.485, "_left": 0.0, "_right": 0.0},
        ]

        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.get_logger().info("Macchina a stati Cobotta avviata.")

    def state_machine_loop(self):
        gesture_id = 0

        camera_active = (self.current_state == "WAITING_FOR_COMMAND")

        # Gestione Telecamera
        if camera_active:
            frame = self.camera.get_frame()
            if frame is not None:
                gesture_id = self.analyzer.analyze(frame)
                
                cv2.putText(frame, f"Gesto: {gesture_id} | Stato: {self.current_state}", 
                            (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Cobotta Vision", frame)
                cv2.waitKey(1)
                self.window_open = True
        else:
            if self.window_open:
                cv2.destroyWindow("Cobotta Vision")
                cv2.waitKey(1)
                self.window_open = False
                self.get_logger().info("Telecamera disattivata durante il movimento.")

        # Logica degli Stati
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
                self.get_logger().info("Azione 1 avviata (Tazza)")
                self.current_trajectory = self.action_1_trajectory
                self.current_step = 0
                self.current_state = "EXECUTING_ACTION"
                
            elif gesture_id == 2:
                self.get_logger().info("Azione 2 avviata (Piatto)")
                self.current_trajectory = self.action_2_trajectory
                self.current_step = 0
                self.current_state = "EXECUTING_ACTION"

        elif self.current_state == "EXECUTING_ACTION":
            if self.current_step < len(self.current_trajectory):
                
                target_pos = self.current_trajectory[self.current_step]
                
                self.robot.move_all_joints(target_pos)
                
                if self.robot.is_target_reached(target_pos):
                    print(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1 # Passo alla posizione successiva
            else:
                self.get_logger().info("Azione completata. Ritorno in INIT.")
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