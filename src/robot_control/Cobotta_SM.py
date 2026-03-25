import asyncio
import time
import rclpy
from rclpy.node import Node
import cv2
import math

from CobottaArm import CobottaArm
from CobottaCamera import CobottaCamera
from ObjectDetector import ObjectDetector
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
        self.object_detector = ObjectDetector()
        
        self.current_state = "INIT"
        self.window_open = False
        
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

        # Traiettoria 1:  tazza goal pos -> tazza pos
        self.action_3_trajectory = [
            {"1": 1.652, "2": 1.454, "3": 0.996, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": 1.652, "2": 1.454, "3": 0.836, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": 1.652, "2": 1.604, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.000, "_right": -0.000},

            {"1": 1.652, "2": 1.604, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.03, "_right": -0.03}, #presa tazza
            {"1": 1.652, "2": 0.864, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.864, "3": 0.656, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.864, "3": 1.376, "4": 0.001, "5": -0.694, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.704, "3": 1.586, "4": 0.001, "5": -1.204, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.951, "2": 0.984, "3": 1.436, "4": 0.001, "5": -1.204, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.891, "2": 1.024, "3": 1.436, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.881, "2": 1.024, "3": 1.370, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},
            {"1": -1.881, "2": 1.314, "3": 1.370, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.031, "_right": -0.031},

            {"1": -1.890, "2": 1.314, "3": 1.370, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000}, #molla tazza
            
            {"1": -1.890, "2": 1.114, "3": 1.966, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000},
            {"1": -1.890, "2": 0.354, "3": 1.966, "4": 0.001, "5": -1.404, "6": -0.013, "_left": -0.000, "_right": -0.000}
        ]

        # Traiettoria 2: Piatto
        self.action_2_trajectory = [
            {"1": -1.289, "2": 0.625, "3": 1.480, "4": 2.214, "5": 0.030, "6": 2.425, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 0.925, "3": 1.380, "4": 2.214, "5": 0.030, "6": 2.425, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 1.030, "3": 1.358, "4": 2.233, "5": 0.019, "6": 2.452, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 1.104, "3": 1.264, "4": 2.241, "5": 0.030, "6": 2.452, "_left": 0.0, "_right": 0.0},
            {"1": -1.289, "2": 1.030, "3": 1.358, "4": 2.233, "5": 0.030, "6": 2.452,  "_left": -0.02, "_right": -0.02},
            {"1": -1.289, "2": 0.600, "3": 1.358, "4": 2.233, "5": 0.019, "6": 2.452,  "_left": -0.02, "_right": -0.02},

            {"1": 1.50, "2": 0.600, "3": 1.190, "4": 1.891, "5": 0.012, "6": 2.93, "_left": -0.02, "_right": -0.02},
            {"1": 1.50, "2": 1.21, "3": 0.84, "4": 1.90, "5": 0.0, "6": 2.93, "_left": -0.02, "_right": -0.02},
            {"1": 1.50, "2": 1.21, "3": 0.84, "4": 1.90, "5": 0.0, "6": 2.93, "_left": 0.0, "_right": 0.0},
            {"1": 1.50, "2": 0.32, "3": 1.81, "4": 1.90, "5": 0.0, "6": 2.93, "_left": 0.0, "_right": 0.0},
        ]

        self.monitoring_object_time_ticks=40
        self.last_gesture_id = 4
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
            cv2.putText(frame, f"Goal pos: {detected_object}",
                        (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            
            cv2.imshow("Cobotta Vision", frame)
            cv2.waitKey(1)
            
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
                self.last_gesture_id = gesture_id
                self.get_logger().info("Posizione MONITORING raggiunta! In attesa di comandi.")
                self.current_state = "CHECK_GOAL_POS"

        elif self.current_state == "RELOCATE_CUP":
            self.get_logger().info("Riposizionamento tazza")
            self.current_trajectory = self.action_2_trajectory
            self.current_step = 0
            self.current_state = "EXECUTING_ACTION"

        elif self.current_state == "RELOCATE_PLATE":
            self.get_logger().info("Riposizionamento piatto")
            self.current_trajectory = self.action_4_trajectory
            self.current_step = 0
            self.current_state = "EXECUTING_ACTION"

        elif self.current_state == "CHECK_GOAL_POS":
            self.robot.go_monitoring_goal_pos()
            detected_object = self.object_detector.identify_object(frame)[0]
            #detected_object = "CUP"
            self.monitoring_object_time_ticks-=1
            print(f"count: {self.monitoring_object_time_ticks}")
            if(self.monitoring_object_time_ticks==0):
            
                if detected_object == "EMPTY":
                        if self.last_gesture_id == 1:
                            self.get_logger().info("Azione 1 avviata (Tazza)")
                            self.current_trajectory = self.action_1_trajectory
                            self.current_step = 0
                            self.current_state = "EXECUTING_ACTION"
                            print(self.current_state)

                        elif self.last_gesture_id == 2:
                            self.get_logger().info("Azione 2 avviata (Piatto)")
                            self.current_trajectory = self.action_2_trajectory
                            self.current_step = 0
                            self.current_state = "EXECUTING_ACTION"

                        self.monitoring_object_time_ticks=40
                        
                elif detected_object == "CUP": #full
                    if self.last_gesture_id == 2: #ci va 2, 1 solo per test
                        self.get_logger().info("Azione 3 avviata (Tazza -> tazza pos)")
                        self.current_trajectory = self.action_3_trajectory
                        self.current_step = 0
                        self.monitoring_object_time_ticks-=1
                        self.current_state = "RELOCATE_ACTION_CUP"
                    else:
                        self.current_state = "INIT"
                    self.monitoring_object_time_ticks=40

                    

                elif detected_object == "PLATE":
                    if self.last_gesture_id == 1:
                        self.get_logger().info("Azione 4 avviata (piatto -> piatto pos)")
                        self.current_trajectory = self.action_4_trajectory
                        self.current_step = 0
                        self.monitoring_object_time_ticks-=1
                        self.current_state = "RELOCATE_ACTION_PLATE"
                    else:
                        self.current_state = "INIT"
                    self.monitoring_object_time_ticks=20
            

        # --- ESECUZIONE DINAMICA DELLE TRAIETTORIE ---
        elif self.current_state == "EXECUTING_ACTION":
            # Controllo se ci sono ancora posizioni da raggiungere nella lista
            if self.current_step < len(self.current_trajectory):
                
                # Prendo la posizione target attuale
                target_pos = self.current_trajectory[self.current_step]
                
                # Mando il comando al robot
                self.robot.move_all_joints(target_pos)
                
                # Verifico se l'ha raggiunta
                if self.robot.is_target_reached(target_pos):
                    print(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1 # Passo alla posizione successiva
            else:
                # Se l'indice ha superato la lunghezza della lista, l'azione è finita
                self.get_logger().info("Azione completata. Ritorno in INIT.")
                self.current_state = "INIT"

        elif self.current_state == "RELOCATE_ACTION_CUP":
            # Controllo se ci sono ancora posizioni da raggiungere nella lista
            if self.current_step < len(self.current_trajectory):
                
                # Prendo la posizione target attuale
                target_pos = self.current_trajectory[self.current_step]
                
                # Mando il comando al robot
                self.robot.move_all_joints(target_pos)
                
                # Verifico se l'ha raggiunta
                if self.robot.is_target_reached(target_pos):
                    print(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1 # Passo alla posizione successiva
            else:
                # Se l'indice ha superato la lunghezza della lista, l'azione è finita
                self.get_logger().info("Azione completata. Ritorno in INIT.")
                self.current_state = "RELOCATE_PLATE"

        elif self.current_state == "RELOCATE_ACTION_PLATE":
            # Controllo se ci sono ancora posizioni da raggiungere nella lista
            if self.current_step < len(self.current_trajectory):
                
                # Prendo la posizione target attuale
                target_pos = self.current_trajectory[self.current_step]
                
                # Mando il comando al robot
                self.robot.move_all_joints(target_pos)
                
                # Verifico se l'ha raggiunta
                if self.robot.is_target_reached(target_pos):
                    print(f"Raggiunta posizione {self.current_step} della traiettoria.")
                    self.current_step += 1 # Passo alla posizione successiva
            else:
                # Se l'indice ha superato la lunghezza della lista, l'azione è finita
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