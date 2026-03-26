import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState, Image
from cv_bridge import CvBridge
import cv2

# --- IMPORTAZIONE OBBLIGATORIA ---
# Assicurati che il file ObjectDetector.py sia nella stessa cartella.
try:
    from ObjectDetector import ObjectDetector
except ImportError:
    print("ERRORE: Impossibile importare 'ObjectDetector'.")
    print("Verifica che il file 'ObjectDetector.py' sia nella stessa cartella di questo script.")
    import sys
    sys.exit(1)


class CobottaSyncCalibratorVision(Node):
    def __init__(self):
        super().__init__('cobotta_sync_calibrator_vision')
        
        self.joint_names = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint_left", "joint_right"]
        self.current_positions = {name: 0.0 for name in self.joint_names}
        self.synced = False 

        # --- Inizializzazione Visione ---
        self.bridge = CvBridge()
        self.current_frame = None
        self.object_detector = ObjectDetector() # Istanziamo il rilevatore ArUco
        self.detected_marker = "Nessun Marker"

        # Publisher per ogni joint
        self.publishers_dict = {name: self.create_publisher(Float64, f"/{name}_cmd", 10) for name in self.joint_names}
        
        # Sottoscrizioni: Joint states e Camera
        self.create_subscription(JointState, '/joint_states', self.sync_callback, 10)
        
        # NOTA: Cambia '/camera/image_raw' con il vero topic della tua camera su Gazebo se diverso
        self.create_subscription(Image, '/camera', self.image_callback, 10)
        
        self.selected_index = 0
        self.step = 0.01 
        self.gripper_joints = ["joint_left", "joint_right"]

        # Loop principale gestito da un timer ROS 2 (50ms / 20Hz)
        # Sostituisce il 'while True' bloccante e permette di gestire video e tastiera simultaneamente
        self.timer = self.create_timer(0.05, self.keyboard_and_video_loop)

        print("Attesa sincronizzazione con Gazebo...")

    def image_callback(self, msg):
        """Converte il messaggio ROS in un'immagine OpenCV."""
        try:
            self.current_frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Errore conversione immagine: {e}")

    def sync_callback(self, msg):
        if not self.synced:
            for i, name in enumerate(msg.name):
                if name in self.current_positions:
                    self.current_positions[name] = msg.position[i]
            
            self.synced = True
            print("\n" + "!"*40)
            print("SINCRONIZZAZIONE COMPLETATA!")
            print("Le pinze (left/right) sono ora collegate.")
            print("Ora la finestra video gestirà gli input da tastiera.")
            print("!"*40)
            self.print_menu()

    def print_menu(self):
        if not self.synced: return
        name = self.joint_names[self.selected_index]
        is_gripper = name in self.gripper_joints
        
        print("\n" + "="*45)
        label = "GRIPPER (SYNCED)" if is_gripper else f"JOINT: {name}"
        print(f" SELEZIONATO: {label}")
        print(f" VALORE ATTUALE: {self.current_positions[name]:.3f}")
        print(f" STATO ARUCO: {self.detected_marker}") # Mostriamo ArUco anche qui
        print("-" * 45)
        print(" Assicurati di avere la finestra video selezionata!")
        print(" [w/s] : Cambia Joint | [a/d] : Muovi (-/+)")
        print(" [p]   : STAMPA DIZIONARIO PER LO SCRIPT")
        print(" [q]   : Esci")
        print("="*45)

    def move_robot(self, name):
        """Invia il comando al robot. Se è una pinza, invia a entrambi."""
        if name in self.gripper_joints:
            val = self.current_positions[name]
            for g_joint in self.gripper_joints:
                self.current_positions[g_joint] = val
                msg = Float64()
                msg.data = float(val)
                self.publishers_dict[g_joint].publish(msg)
        else:
            msg = Float64()
            msg.data = float(self.current_positions[name])
            self.publishers_dict[name].publish(msg)

    def print_current_config(self):
        mapping = {"joint1":"1","joint2":"2","joint3":"3","joint4":"4","joint5":"5","joint6":"6","joint_left":"_left","joint_right":"_right"}
        output = "self.target_pos = {" + ", ".join([f'"{mapping[k]}": {v:.3f}' for k, v in self.current_positions.items()]) + "}"
        print("\n--- COPIA QUESTO ---")
        print(output)
        print("--------------------\n")

    def keyboard_and_video_loop(self):
        """Gestisce il rendering video, ArUco e l'input da tastiera simultaneamente."""
        if not self.synced:
            return

        # Visualizza la telecamera e ArUco se abbiamo ricevuto frame
        if self.current_frame is not None:
            # Creiamo una copia per non sporcare il frame originale
            display_frame = self.current_frame.copy()
            
            # --- ANALISI ARUCO ---
            # ObjectDetector.identify_object restituisce una tupla (id, ...)
            detection_result = self.object_detector.identify_object(display_frame)
            if detection_result and detection_result[0] != "EMPTY":
                self.detected_marker = f"Marker ID: {detection_result[0]}"
                # Testo ArUco in sovraimpressione (Arancione)
                cv2.putText(display_frame, self.detected_marker, (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            else:
                self.detected_marker = "Nessun Marker"
            
            # --- OVERLAY INFORMAZIONI ROBOT ---
            name = self.joint_names[self.selected_index]
            
            # Mostriamo le informazioni del joint direttamente a schermo (Opzionale ma molto comodo)
            # Testo Joint in sovraimpressione (Verde)
            cv2.putText(display_frame, f"Selezionato: {name}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Valore: {self.current_positions[name]:.3f}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Cobotta Camera & ArUco Calibrator", display_frame)

        # waitKey(1) permette di catturare la tastiera e aggiornare l'immagine senza bloccare il nodo.
        # RITORNA IL CODICE ASCII DEL TASTO PREMUTO SULLA FINESTRA VIDEO.
        key = cv2.waitKey(1) & 0xFF

        if key == 255:  # Nessun tasto premuto sulla finestra video
            return

        name = self.joint_names[self.selected_index]
        
        if key == ord('w'):
            self.selected_index = (self.selected_index - 1) % len(self.joint_names)
            self.print_menu()
        elif key == ord('s'):
            self.selected_index = (self.selected_index + 1) % len(self.joint_names)
            self.print_menu()
        elif key == ord('d'):
            self.current_positions[name] += self.step
            self.move_robot(name)
            # Log in terminale e nel logger di ROS 2
            self.get_logger().info(f"[+] {name} -> {self.current_positions[name]:.3f} | {self.detected_marker}")
        elif key == ord('a'):
            self.current_positions[name] -= self.step
            self.move_robot(name)
            self.get_logger().info(f"[-] {name} -> {self.current_positions[name]:.3f} | {self.detected_marker}")
        elif key == ord('p'):
            self.print_current_config()
        elif key == ord('q'):
            self.get_logger().info("Uscita in corso...")
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = CobottaSyncCalibratorVision()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Pulizia corretta di OpenCV e ROS 2
        cv2.destroyAllWindows()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()