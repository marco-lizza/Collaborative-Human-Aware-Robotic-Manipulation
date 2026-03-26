from time import time
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState

class CobottaArm:
    """Gestisce la pubblicazione dei comandi ai joint del Cobotta."""
    def __init__(self, node: Node, joints: list):
        self.node = node
        self.joints = joints
        self.publishers = {}
        
        # Dizionario per salvare la posizione attuale dei giunti
        self.current_positions = {joint: 0.0 for joint in self.joints}
        
        # Crea i publisher per i 6 joint rotazionali e i 2 lineari
        for joint in self.joints:
            topic_name = f'/joint{joint}_cmd'
            self.publishers[joint] = self.node.create_publisher(Float64, topic_name, 10)
            
        # Subscriber per leggere la posizione reale del robot
        self.state_sub = self.node.create_subscription(
            JointState, 
            '/joint_states', 
            self.joint_state_callback, 
            10
        )
            
        # Posizioni fisse note
        self.IDLE_POSITION = {
            "1": 0.0, "2": 0.0, "3": 0.31, "4": 0.0, "5": 0.0, "6": 0.0, 
            "_left": 0.0, "_right": 0.0
        }

        self.MONITORING_POSITION = {
            "1": 1.5, "2": 0.00, "3": 1.40, "4": 0.0, "5": 0.0, "6": 0.0, 
            "_left": 0.0, "_right": 0.0
        }

        self.MONITORING_GOAL_POSITION = {
            "1": 1.71, "2": 0.57, "3": 1.70, "4": 0.0, "5": 0.0, "6": 0.0, 
            "_left": 0.0, "_right": 0.0
        }

    def joint_state_callback(self, msg: JointState):
        """Aggiorna le posizioni attuali leggendo dal robot."""
        for name, position in zip(msg.name, msg.position):
            clean_name = name.replace("joint", "") 
            if clean_name in self.current_positions:
                self.current_positions[clean_name] = position

    def is_target_reached(self, target_dict: dict, tolerance: float = 0.08) -> bool:
        """
        Verifica se tutti i giunti sono arrivati alla posizione desiderata 
        con un certo margine di tolleranza (default 0.05 radianti).
        """
        for joint_name, target_value in target_dict.items():
            current_value = self.current_positions.get(joint_name, 0.0)
            errore = abs(current_value - target_value)
            
            if errore > tolerance:
                return False # Basta che un solo giunto sia fuori tolleranza
                
        return True

    def move_joint(self, joint_name: str, value: float):
        if joint_name in self.publishers:
            msg = Float64()
            msg.data = float(value)
            self.publishers[joint_name].publish(msg)

    def move_all_joints(self, positions_dict: dict):
        for joint_name, value in positions_dict.items():
            self.move_joint(joint_name, value)

    def go_idle(self):
        #self.node.get_logger().info("Cobotta in movimento verso posizione IDLE...")
        self.move_all_joints(self.IDLE_POSITION)

    def go_monitoring(self):
        #self.node.get_logger().info("Cobotta in movimento verso posizione MONITORING...")
        self.move_all_joints(self.MONITORING_POSITION)

    def go_monitoring_goal_pos(self):
        #self.node.get_logger().info("Cobotta in movimento verso posizione MONITORING...")
        self.move_all_joints(self.MONITORING_GOAL_POSITION)