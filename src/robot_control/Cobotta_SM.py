import asyncio
import time

import numpy as np
import rclpy
from rclpy.node import Node
import cv2
import math

from CobottaArm import CobottaArm
from CobottaCamera import CobottaCamera
from ObjectDetector import ObjectDetector
from GestureAnalyzer import GestureAnalyzer

MONITORING_OBJECT_TIME_TICKS = 20

class CobottaStateMachine(Node):
    """Nodo principale che gestisce la logica di alto livello e gli stati."""
    def __init__(self):
        super().__init__('cobotta_state_machine')
        
        joints = ["1", "2", "3", "4", "5", "6", "_left", "_right"]
        
        # Istanziamo le classi importate
        self.robot = CobottaArm(self, joints)
        self.camera = CobottaCamera(self, '/camera')
        self.analyzer = GestureAnalyzer()
        self.object_detector = ObjectDetector()
        
        self.current_state = "INIT_POS"
        self.window_open = False

        self.standby_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(self.standby_image, "CAMERA STANDBY", (180, 220), 
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        
        # Variabili per la gestione dinamica delle traiettorie
        self.current_trajectory = []
        self.current_step = 0
        
        # --- DEFINIZIONE TRAIETTORIE (Liste di dizionari) ---
        
        # Traiettoria 1: Tazza -> goal pos
        self.action_1_trajectory = [
            {"1": -1.90, "2": 0.560, "3": 1.950, "4": 0.005, "5": 0.000, "6": -0.000, "_left": -0.000, "_right": -0.000},
            {"1": -1.90, "2": 0.910, "3": 1.950, "4": 0.005, "5": -1.010, "6": -0.000, "_left": -0.000, "_right": -0.000},
            {"1": -1.90, "2": 1.140, "3": 1.550, "4": 0.005, "5": -1.010, "6": -0.000, "_left": -0.000, "_right": -0.000},
            {"1": -1.90, "2": 1.140, "3": 1.550, "4": 0.005, "5": -1.010, "6": -0.000, "_left": -0.020, "_right": -0.020}, #presa tazza
            
            {"1": -1.90, "2": 0.320, "3": 1.550, "4": 0.005, "5": -1.010, "6": -0.000, "_left": -0.030, "_right": -0.030},
            {"1": 1.660, "2": 0.320, "3": 1.550, "4": 0.005, "5": -1.010, "6": -0.000, "_left": -0.030, "_right": -0.030},
            {"1": 1.660, "2": 0.840, "3": 0.960, "4": 0.005, "5": -0.810, "6": -0.000, "_left": -0.030, "_right": -0.030},
            {"1": 1.658, "2": 1.312, "3": 0.761, "4": -0.001, "5": -0.694, "6": -0.024, "_left": -0.028, "_right": -0.028},
            {"1": 1.658, "2": 1.602, "3": 0.471, "4": -0.001, "5": -0.694, "6": -0.024, "_left": -0.028, "_right": -0.028},


            {"1": 1.660, "2": 1.540, "3": 0.750, "4": 0.005, "5": -0.700, "6": -0.000, "_left": -0.000, "_right": -0.000}, #molla tazza
            {"1": 1.660, "2": 0.200, "3": 0.750, "4": 0.005, "5": -0.700, "6": -0.000, "_left": -0.000, "_right": -0.000}
        ]

        # Traiettoria 2: Piatto
        self.action_2_trajectory = [
            #inizio della 2 
            {"1": -0.000, "2": 0.463, "3": 1.481, "4": 0.003, "5": 0.000, "6": 0.000, "_left": 0.000, "_right": 0.000},
            {"1": -0.000, "2": 0.463, "3": 1.481, "4": -0.007, "5": 0.000, "6": -1.522, "_left": 0.000, "_right": 0.000},
            {"1": -0.000, "2": 0.940, "3": 1.021, "4": 0.033, "5": 0.486, "6": -1.522, "_left": 0.00, "_right": 0.00},
            {"1": -0.000, "2": 0.940, "3": 1.021, "4": 0.033, "5": 0.486, "6": -1.522, "_left": -0.02, "_right": -0.02},
            {"1": -0.002, "2": 0.574, "3": 1.248, "4": 0.027, "5": 0.368, "6": -1.522, "_left": -0.02, "_right": -0.02},
            {"1": -0.003, "2": 0.120, "3": 1.249, "4": 0.026, "5": 0.369, "6": -1.522, "_left": -0.02, "_right": -0.02},
            {"1": 1.678, "2": 0.120, "3": 1.249, "4": 0.026, "5": 0.369, "6": -1.522, "_left": -0.02, "_right": -0.02},
            {"1": 1.678, "2": 0.927, "3": 0.567, "4": 0.026, "5": 0.287, "6": -1.522, "_left": -0.02, "_right": -0.02},
            {"1": 1.643, "2": 1.210, "3": 0.314, "4": 0.018, "5": 0.410, "6": -1.541, "_left": -0.02, "_right": -0.02},
            {"1": 1.643, "2": 1.210, "3": 0.314, "4": 0.018, "5": 0.410, "6": -1.541, "_left": 0.0, "_right": 0.0},

        ]

        # Traiettoria 3:  tazza goal pos -> tazza pos
        self.action_3_trajectory = [
            {"1": 1.657, "2": 1.454, "3": 0.996, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": 1.657, "2": 1.454, "3": 0.836, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": 1.657, "2": 1.604, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},

            {"1": 1.657, "2": 1.604, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.03, "_right": -0.03}, #presa tazza
            {"1": 1.657, "2": 0.864, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.864, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.864, "3": 1.376, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.704, "3": 1.586, "4": 0.001, "5": -1.204, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.984, "3": 1.436, "4": 0.001, "5": -1.204, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.893, "2": 1.024, "3": 1.436, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.893, "2": 1.024, "3": 1.363, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.893, "2": 1.314, "3": 1.363, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.895, "2": 1.316, "3": 1.366, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.895, "2": 1.316, "3": 1.366, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.895, "2": 1.316, "3": 1.370, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.897, "2": 1.316, "3": 1.375, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.899, "2": 1.318, "3": 1.378, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.905, "2": 1.318, "3": 1.385, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.907, "2": 1.318, "3": 1.388, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},

            {"1": -1.893, "2": 1.314, "3": 1.363, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000}, #molla tazza
            
            {"1": -1.893, "2": 1.114, "3": 1.976, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": -1.893, "2": 0.354, "3": 1.976, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000}
        ]

        # Traiettoria 4:  piatto goal pos -> piatto pos
        self.action_4_trajectory = [
            {"1": 1.692, "2": 0.558, "3": 1.731, "4": 0.007, "5": 0.031, "6": 1.554, "_left": -0.000, "_right": 0.000},
            {"1": 1.696, "2": 1.174, "3": 1.268, "4": 0.007, "5": 0.002, "6": 1.554, "_left": 0.000, "_right": 0.000},
            {"1": 1.695, "2": 1.309, "3": 1.054, "4": 0.007, "5": 0.002, "6": 1.554, "_left": 0.000, "_right": 0.000},
            {"1": 1.695, "2": 1.309, "3": 1.054, "4": 0.007, "5": 0.002, "6": 1.554, "_left": 0.000, "_right": 0.000},
            {"1": 1.695, "2": 1.309, "3": 1.054, "4": 0.007, "5": 0.002, "6": 1.554, "_left": -0.025, "_right": -0.025},
            {"1": 1.691, "2": 0.809, "3": 1.053, "4": 0.007, "5": 0.002, "6": 1.554, "_left": -0.025, "_right": -0.025},
            {"1": 0.007, "2": 0.809, "3": 1.052, "4": 0.007, "5": 0.002, "6": 1.554, "_left": -0.025, "_right": -0.025},
            {"1": 0.015, "2": 0.477, "3": 1.940, "4": 0.007, "5": 0.002, "6": 1.554, "_left": -0.025, "_right": -0.025},


            {"1": 0.015, "2": 0.559, "3": 2.025, "4": 0.007, "5": 0.001, "6": 1.554, "_left": 0.000, "_right": 0.000},
            {"1": 0.005, "2": -0.559, "3": 2.325, "4": 0.007, "5": 0.001, "6": 1.554, "_left": 0.000, "_right": 0.000},
            {"1": 0.015, "2": 0.805, "3": 1.574, "4": 0.029, "5": 0.003, "6": 1.574, "_left": -0.000, "_right": 0.000},
            {"1": 0.015, "2": 0.805, "3": 1.374, "4": 0.029, "5": 0.003, "6": 1.574, "_left": -0.000, "_right": 0.000},
            {"1": 0.015, "2": 0.782, "3": 1.822, "4": 0.029, "5": 0.003, "6": 1.574, "_left": -0.000, "_right": 0.000},
            {"1": 0.015, "2": -0.241, "3": 1.838, "4": 0.029, "5": 0.003, "6": 1.574, "_left": -0.001, "_right": 0.000},
            
        ]

        self.monitoring_object_time_ticks = MONITORING_OBJECT_TIME_TICKS
        self.last_gesture_id = 0
        self.last_detected_object="EMPTY"
        self.timer = self.create_timer(0.1, self.state_machine_loop)
        self.get_logger().info("Macchina a stati Cobotta avviata.")

    def state_machine_loop(self):
        # 1. Setup variabili di default
        frame = None
        gesture_id = 0
        detected_object = "EMPTY"
        
        vision_active_states = ["CHECK_GESTURE", "GOAL_POS", "CHECK_OBJECT"] #stati in cui la camera è attiva

        # 2. Acquisizione dati SOLO se necessario
        if self.current_state in vision_active_states:
            frame = self.camera.get_frame()
            if frame is not None:
                # Analizziamo i gesti solo se siamo in CHECK_GESTURE
                if self.current_state == "CHECK_GESTURE":
                    gesture_id = self.analyzer.analyze(frame)
                
                # Analizziamo l'oggetto solo se siamo in CHECK_OBJECT
                if self.current_state in ["CHECK_OBJECT"]:
                    detected_object = self.object_detector.identify_object(frame)[0]

                # Visualizzazione
                cv2.putText(frame, f"Gesto: {gesture_id} | Stato: {self.current_state}", 
                            (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Vision: {detected_object}",
                            (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                
                cv2.imshow("Cobotta Vision", frame)
                cv2.waitKey(1) # Essenziale per non bloccare la finestra CV2
        else:
            # Usiamo l'immagine già pronta, aggiungiamo solo lo stato dinamico
            temp_frame = self.standby_image.copy() # Copia veloce
            cv2.putText(temp_frame, f"Status: {self.current_state}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
            cv2.imshow("Cobotta Vision", temp_frame)
            cv2.waitKey(1)

        # Logica degli Stati
        if self.current_state == "INIT_POS":
            self.current_state = "WAITING_FOR_IDLE"
            
        elif self.current_state == "WAITING_FOR_IDLE":
            self.robot.go_idle()
            if self.robot.is_target_reached(self.robot.IDLE_POSITION):
                self.get_logger().info("Posizione IDLE raggiunta!")
                self.current_state = "CAM_POS"

        elif self.current_state == "CAM_POS":
            self.robot.go_monitoring()#Movimento verso posizione di monitoraggio del gesto(CAM_POS)
            if self.robot.is_target_reached(self.robot.MONITORING_POSITION):
                self.get_logger().info("Posizione di monitoraggio gesti raggiunta!")
                self.current_state = "CHECK_GESTURE"

        elif self.current_state == "CHECK_GESTURE":
            if gesture_id > 0: 
                self.last_gesture_id = gesture_id
                self.get_logger().info(f"Gesto {self.last_gesture_id} rilevato!")
                self.current_state = "GOAL_POS"
            # Se non c'è gesto (gesture_id == 0), rimango qui in attesa    

        elif self.current_state == "GOAL_POS":
            self.robot.go_monitoring_goal_pos()  #Movimento verso posizione di monitoraggio del goal (GOAL_POS)
            if self.robot.is_target_reached(self.robot.MONITORING_GOAL_POSITION):
                self.get_logger().info("Posizione di monitoraggio goal raggiunta!")
                self.monitoring_object_time_ticks = MONITORING_OBJECT_TIME_TICKS # Reset del timer per la visione
                self.current_state = "CHECK_OBJECT"

        elif self.current_state == "CHECK_OBJECT":
            # Usiamo detected_object aggiornato condizionalmente sopra
            self.monitoring_object_time_ticks -= 1
            
            if detected_object != "EMPTY":
                self.last_detected_object = detected_object
            
            if self.monitoring_object_time_ticks <= 0:
                # Logica decisionale (Tazza, Piatto, Empty...)
                if self.last_detected_object == "EMPTY":
                    if self.last_gesture_id == 1:
                        self.get_logger().info("Gesto 1 e nessun oggetto: eseguo azione 1 (tazza -> goal pos)")
                        self.current_trajectory = self.action_1_trajectory
                        self.current_state = "EXECUTING_ACTION"
                    elif self.last_gesture_id == 2:
                        self.get_logger().info("Gesto 2 e nessun oggetto: eseguo azione 2 (piatto -> goal pos)")
                        self.current_trajectory = self.action_2_trajectory
                        self.current_state = "EXECUTING_ACTION"
                    self.current_step = 0
                
                elif self.last_detected_object == "CUP":
                    if self.last_gesture_id == 2:
                        self.get_logger().info("Gesto 2 e tazza: eseguo azione 3 (tazza goal pos -> tazza pos)")
                        self.current_trajectory = self.action_3_trajectory
                        self.current_state = "RELOCATE_ACTION_CUP"
                        self.current_step = 0
                    else:
                        self.current_state = "INIT_POS"
                        self.get_logger().info("Rilevato gesto ma oggetto già in posizione, ritorno in INIT_POS")

                elif self.last_detected_object == "PLATE":
                    if self.last_gesture_id == 1:
                        self.current_trajectory = self.action_4_trajectory
                        self.current_state = "RELOCATE_ACTION_PLATE"
                        self.current_step = 0
                    else:
                        self.current_state = "INIT_POS"
                        self.get_logger().info("Rilevato gesto ma oggetto già in posizione, ritorno in INIT_POS")

                else:
                    # Se l'oggetto non è coerente, torna in INIT
                    self.get_logger().error(f"Non riesco a gestire l'oggetto rilevato")
                    self.current_state = "INIT_POS"  

        elif self.current_state == "RELOCATE_CUP":
            self.get_logger().info("Riposizionamento tazza")
            self.current_trajectory = self.action_1_trajectory
            self.current_step = 0
            self.current_state = "EXECUTING_ACTION"

        elif self.current_state == "RELOCATE_PLATE":
            self.get_logger().info("Riposizionamento piatto")
            self.current_trajectory = self.action_2_trajectory
            self.current_step = 0
            self.current_state = "EXECUTING_ACTION"             

        # --- ESECUZIONE TRAIETTORIE (Qui la camera è spenta = simulazione fluida) ---
        elif self.current_state == "EXECUTING_ACTION":
            # Controllo se ci sono ancora posizioni da raggiungere nella lista
            if self.current_step < len(self.current_trajectory):
                target_pos = self.current_trajectory[self.current_step]
                self.robot.move_all_joints(target_pos)
                if self.robot.is_target_reached(target_pos):
                    self.get_logger().info(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1 # Passo alla posizione successiva
            else:
                # Se l'indice ha superato la lunghezza della lista, l'azione è finita
                self.get_logger().info("Azione completata. Ritorno in INIT_POS.")
                self.current_state = "INIT_POS"
            self.last_detected_object="EMPTY" # Reset dell'oggetto rilevato dopo l'esecuzione dell'azione
            self.last_gesture_id=0 # Reset del gesto rilevato dopo l'esecuzione dell'azione    


        elif self.current_state == "RELOCATE_ACTION_CUP":
            if self.current_step < len(self.current_trajectory):
                target_pos = self.current_trajectory[self.current_step]
                self.robot.move_all_joints(target_pos)
                if self.robot.is_target_reached(target_pos):
                    self.get_logger().info(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1
            else:
                self.get_logger().info("Azione completata. Ritorno in INIT_POS.")
                self.current_state = "RELOCATE_PLATE"

        elif self.current_state == "RELOCATE_ACTION_PLATE":
            if self.current_step < len(self.current_trajectory):
                target_pos = self.current_trajectory[self.current_step]
                self.robot.move_all_joints(target_pos)
                if self.robot.is_target_reached(target_pos):
                    self.get_logger().info(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1
            else:
                self.get_logger().info("Azione completata. Ritorno in INIT.")
                self.current_state = "RELOCATE_CUP"

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