import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import math

class CobottaTest(Node):
    def __init__(self):
        super().__init__('cobotta_test_node')
        # questo parlerà tramite il bridge a gazibo
        self.publisher_ = self.create_publisher(Float64, '/joint1_cmd', 10)

        timer_period = 0.1  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.contatore = 0.0

    def timer_callback(self):
        msg = Float64()
        msg.data = math.sin(self.contatore) * 1.0 

        self.publisher_.publish(msg)
        self.get_logger().info(f'Comando inviato al Joint 1: {msg.data:.2f} rad')
        self.contatore += 0.1

def main(args=None):
    rclpy.init(args=args)
    nodo = CobottaTest()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()