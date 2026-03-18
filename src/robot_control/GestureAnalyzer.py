import cv2
import mediapipe as mp

class GestureAnalyzer:
    """Analizza un'immagine OpenCV e restituisce un valore da 1 a 4."""
    def __init__(self):
        self.mp_mani = mp.solutions.hands
        self.mani = self.mp_mani.Hands(
            static_image_mode=False, 
            max_num_hands=1, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def analyze(self, frame):
        """
        Analizza il frame e restituisce:
        1 -> un dito alzato
        2 -> due dita alzate
        3 -> tre dita alzate
        4 -> nessun dito, o condizione non valida
        """
        if frame is None:
            return 4

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        risultati = self.mani.process(frame_rgb)

        if not risultati.multi_hand_landmarks:
            return 4

        hand_landmarks = risultati.multi_hand_landmarks[0]
        
        dita_alzate = 0
        # Indici per punta e nocca di: Indice, Medio, Anulare, Mignolo
        punte = [8, 12, 16, 20] 
        nocche = [6, 10, 14, 18]

        for i in range(4):
            # Se la Y della punta è minore della nocca
            if hand_landmarks.landmark[punte[i]].y < hand_landmarks.landmark[nocche[i]].y:
                dita_alzate += 1

        # Controllo del pollice rimosso intenzionalmente(creava casini)

        if dita_alzate in [1, 2, 3]:
            return dita_alzate
        else:
            return 4