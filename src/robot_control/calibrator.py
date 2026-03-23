import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
import sys
import termios
import tty

class CobottaSyncCalibrator(Node):
    def __init__(self):
        super().__init__('cobotta_sync_calibrator')
        
        self.joint_names = ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint_left", "joint_right"]
        self.current_positions = {name: 0.0 for name in self.joint_names}
        self.synced = False 

        # Publisher per ogni joint
        self.publishers_dict = {name: self.create_publisher(Float64, f"/{name}_cmd", 10) for name in self.joint_names}
        
        self.create_subscription(JointState, '/joint_states', self.sync_callback, 10)

        self.selected_index = 0
        self.step = 0.01 
        self.gripper_joints = ["joint_left", "joint_right"]

        print("Attesa sincronizzazione con Gazebo...")

    def sync_callback(self, msg):
        if not self.synced:
            for i, name in enumerate(msg.name):
                if name in self.current_positions:
                    self.current_positions[name] = msg.position[i]
            
            self.synced = True
            print("\n" + "!"*30)
            print("SINCRONIZZAZIONE COMPLETATA!")
            print("Le pinze (left/right) sono ora collegate.")
            print("!"*30)
            self.print_menu()

    def print_menu(self):
        if not self.synced: return
        name = self.joint_names[self.selected_index]
        is_gripper = name in self.gripper_joints
        
        print("\n" + "="*40)
        label = "GRIPPER (SYNCED)" if is_gripper else f"JOINT: {name}"
        print(f" SELEZIONATO: {label}")
        print(f" VALORE ATTUALE: {self.current_positions[name]:.3f}")
        print("-" * 40)
        print(" [w/s] : Cambia Joint | [a/d] : Muovi (-/+)")
        print(" [p]   : STAMPA DIZIONARIO PER LO SCRIPT")
        print(" [q]   : Esci")
        print("="*40)

    def move_robot(self, name):
        """Invia il comando al robot. Se è una pinza, invia a entrambi."""
        if name in self.gripper_joints:
            # Sincronizza i valori nel dizionario
            val = self.current_positions[name]
            for g_joint in self.gripper_joints:
                self.current_positions[g_joint] = val
                msg = Float64()
                msg.data = float(val)
                self.publishers_dict[g_joint].publish(msg)
        else:
            # Movimento singolo joint standard
            msg = Float64()
            msg.data = float(self.current_positions[name])
            self.publishers_dict[name].publish(msg)

    def print_current_config(self):
        mapping = {"joint1":"1","joint2":"2","joint3":"3","joint4":"4","joint5":"5","joint6":"6","joint_left":"_left","joint_right":"_right"}
        output = "self.target_pos = {" + ", ".join([f'"{mapping[k]}": {v:.3f}' for k, v in self.current_positions.items()]) + "}"
        print("\n--- COPIA QUESTO ---")
        print(output)
        print("--------------------\n")

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    rclpy.init()
    node = CobottaSyncCalibrator()
    
    while rclpy.ok() and not node.synced:
        rclpy.spin_once(node, timeout_sec=0.1)

    try:
        while True:
            key = get_key()
            name = node.joint_names[node.selected_index]
            
            if key == 'w':
                node.selected_index = (node.selected_index - 1) % len(node.joint_names)
                node.print_menu()
            elif key == 's':
                node.selected_index = (node.selected_index + 1) % len(node.joint_names)
                node.print_menu()
            elif key == 'd':
                node.current_positions[name] += node.step
                node.move_robot(name)
                print(f" [+] {name} (Sync): {node.current_positions[name]:.3f}")
            elif key == 'a':
                node.current_positions[name] -= node.step
                node.move_robot(name)
                print(f" [-] {name} (Sync): {node.current_positions[name]:.3f}")
            elif key == 'p':
                node.print_current_config()
            elif key == 'q':
                break
    except Exception as e: print(e)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()