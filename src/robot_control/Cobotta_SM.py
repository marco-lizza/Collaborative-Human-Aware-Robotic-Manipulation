import rclpy
from rclpy.node import Node
import cv2

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
        
        # --- DEFINIZIONE POSIZIONI ---
        self.a1_pos0 = {"1": 0.0, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00, "_left": 0.0, "_right": 0.0}
        self.a1_pos1 = {"1": 0.0, "2": 1.65, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00, "_left": 0.0, "_right": 0.0}
        self.a1_pos2 = {"1": 0.0, "2": 1.65, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00, "_left": -0.02, "_right": -0.02}
        self.a1_pos3 = {"1": 0.0, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.10, "6": 0.00, "_left": -0.02, "_right": -0.02}

        self.a2_pos0 = {"1": -0.96, "2": 1.30, "3": 0.31, "4": 0.00, "5": 0.00, "6": 0.00, "_left": 0.0, "_right": 0.0}
        self.a2_pos1 = {"1": -0.96, "2": 1.30, "3": 0.31, "4": 0.00, "5": 1.40, "6": 1.70, "_left": 0.0, "_right": 0.0}
        self.a2_pos2 = {"1": -0.96, "2": 1.55, "3": 0.31, "4": 0.00, "5": 1.40, "6": 1.70, "_left": 0.0, "_right": 0.0}
        self.a2_pos3 = {"1": -0.96, "2": 1.55, "3": 0.31, "4": 0.00, "5": 1.50, "6": 1.70, "_left": -0.02, "_right": -0.02}
        self.a2_pos4 = {"1": -0.96, "2": 1.00, "3": 0.31, "4": 0.00, "5": 1.50, "6": 1.70, "_left": -0.02, "_right": -0.02}

        self.a3_saluto = {"1": 1.0, "2": 0.74, "3": 0.32, "4": 0.02, "5": -0.52, "6": -2.01, "_left": -0.01, "_right": -0.01}

        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.get_logger().info("Macchina a stati Cobotta avviata.")

    def state_machine_loop(self):
        gesture_id = 0

        camera_active=(self.current_state == "WAITING_FOR_COMMAND")

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
                self.current_state = "ACTION_1"
            elif gesture_id == 2:
                self.get_logger().info("Azione 2 avviata (Piatto)")
                self.current_state = "ACTION_2"

        # --- AZIONE 1 (Tazza) ---
        elif self.current_state.startswith("ACTION_1"):
            if self.current_state == "ACTION_1":
                self.robot.move_all_joints(self.a1_pos0)   
                if self.robot.is_target_reached(self.a1_pos0):
                    self.current_state = "ACTION_1_POS0"

            elif self.current_state == "ACTION_1_POS0":
                self.robot.move_all_joints(self.a1_pos1)   
                if self.robot.is_target_reached(self.a1_pos1):
                    self.current_state = "ACTION_1_POS1"

            elif self.current_state == "ACTION_1_POS1":
                self.robot.move_all_joints(self.a1_pos2)   
                if self.robot.is_target_reached(self.a1_pos2):
                    self.current_state = "ACTION_1_POS2"

            elif self.current_state == "ACTION_1_POS2":
                self.robot.move_all_joints(self.a1_pos3)   
                if self.robot.is_target_reached(self.a1_pos3):
                    self.get_logger().info("Azione 1 completata. Ritorno in INIT.")
                    self.current_state = "INIT"
            
        # --- AZIONE 2 (Piatto) ---
        elif self.current_state.startswith("ACTION_2"):
            if self.current_state == "ACTION_2":
                self.robot.move_all_joints(self.a2_pos0)   
                if self.robot.is_target_reached(self.a2_pos0):
                    self.current_state = "ACTION_2_POS0"

            elif self.current_state == "ACTION_2_POS0":
                self.robot.move_all_joints(self.a2_pos1)
                if self.robot.is_target_reached(self.a2_pos1):
                    self.current_state = "ACTION_2_POS1"

            elif self.current_state == "ACTION_2_POS1":
                self.robot.move_all_joints(self.a2_pos2)   
                if self.robot.is_target_reached(self.a2_pos2):
                    self.current_state = "ACTION_2_POS2"

            elif self.current_state == "ACTION_2_POS2":
                self.robot.move_all_joints(self.a2_pos3)   
                if self.robot.is_target_reached(self.a2_pos3):
                    self.current_state = "ACTION_2_POS3"

            elif self.current_state == "ACTION_2_POS3":
                self.robot.move_all_joints(self.a2_pos4)   
                if self.robot.is_target_reached(self.a2_pos4):
                    self.get_logger().info("Azione 2 completata. Ritorno in INIT.")
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