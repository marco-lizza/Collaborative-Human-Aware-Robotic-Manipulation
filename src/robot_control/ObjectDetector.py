import cv2
import cv2.aruco as aruco

class ObjectDetector:
    def __init__(self):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.aruco_params = aruco.DetectorParameters()
        
        self.CUP_ID = 0
        self.PLATE_ID = 1
        
        # --- AGGIUNTA: Memoria per stabilizzare il rilevamento ---
        self.buffer = [] 
        self.buffer_size = 5 # Numero di frame da analizzare (es. 0.5 secondi se il loop è 0.1s)
        self.last_stable_object = "EMPTY"

    def identify_object(self, frame):
        """
        Analizza il frame, disegna i marker e restituisce l'oggetto trovato e il frame modificato.
        """
        if frame is None: 
            return "EMPTY", None
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Rilevamento dei marker (Sintassi OpenCV < 4.7, standard in ROS 2 Humble)
        corners, ids, rejected = aruco.detectMarkers(gray_frame, self.aruco_dict, parameters=self.aruco_params)
        
        current_detection = "EMPTY"

        if ids is not None:
            # Disegna i bordi verdi attorno ai marker trovati sul frame a colori
            aruco.drawDetectedMarkers(frame, corners, ids, borderColor=(0, 255, 0))
            
            detected_ids = [marker_id[0] for marker_id in ids]
            
            if self.CUP_ID in detected_ids:
                current_detection = "CUP"
            elif self.PLATE_ID in detected_ids:
                current_detection = "PLATE"

        # --- LOGICA DI STABILIZZAZIONE ---
        self.buffer.append(current_detection)
        
        # Mantieni il buffer della dimensione corretta
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)

        # Restituisci l'oggetto più frequente nel buffer (Moda)
        # Se nel buffer ho ["CUP", "CUP", "EMPTY", "CUP", "CUP"], vince "CUP"
        if len(self.buffer) > 0:
            self.last_stable_object = max(set(self.buffer), key=self.buffer.count)

        return self.last_stable_object, frame