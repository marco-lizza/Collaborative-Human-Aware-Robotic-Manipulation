from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CobottaCamera:
    """Gestisce la ricezione e la conversione delle immagini dalla telecamera."""
    def __init__(self, node: Node, camera_topic='/camera'):
        self.node = node
        self.br = CvBridge()
        self.latest_frame = None
        self.is_monitoring = True
        
        self.subscription = self.node.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        """Salva l'ultimo frame se il monitoraggio è attivo."""
        if not self.is_monitoring:
            return
            
        try:
            self.latest_frame = self.br.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.node.get_logger().error(f"Errore conversione immagine: {e}")

    def get_frame(self):
        """Restituisce l'ultimo frame ricevuto."""
        return self.latest_frame

    def start_monitoring(self):
        self.is_monitoring = True

    def stop_monitoring(self):
        self.is_monitoring = False