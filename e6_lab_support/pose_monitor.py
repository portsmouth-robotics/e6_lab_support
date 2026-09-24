import rclpy
from rclpy.node import Node

from dobot_msgs_v4.msg import ToolVectorActual


# This example contains more comments than you would normally write in a ROS 2 program.
# They are included to help you understand the structure of the code and get started.
#
# In your own programs, comments should usually explain things that are not obvious
# from reading the code itself, rather than describing every individual line.


class E6PoseMonitor(Node):

    def __init__(self):
        # Initialise this ROS 2 node.
        super().__init__('e6_pose_monitor')

        # Subscribe to the topic published by the Dobot driver that contains
        # the robot's current Cartesian tool position.
        #
        # The values are:
        #   x, y, z   - position in millimetres
        #   rx, ry, rz - tool orientation in degrees
        self.subscription = self.create_subscription(
            ToolVectorActual,
            '/dobot_msgs_v4/msg/ToolVectorActual',
            self.pose_callback,
            10
        )
        self.display_started = False


        print('Monitoring current tool pose.')
        print('Move the robot using drag mode to teach a position.')
        print('Press Ctrl+C to stop.')
        print()

    def pose_callback(self, msg):
        # This function is called automatically whenever a new pose message
        # is received from the robot.
        #  
        # Move the cursor back to the start of the 3-line display block
        # after the first update.
        if hasattr(self, 'display_started'):
            print('\033[3F', end='')

        print(
            f'Position:    '
            f'X {msg.x:8.2f} mm   '
            f'Y {msg.y:8.2f} mm   '
            f'Z {msg.z:8.2f} mm   '
        )

        print(
            f'Orientation: '
            f'Rx {msg.rx:8.2f} deg   '
            f'Ry {msg.ry:8.2f} deg   '
            f'Rz {msg.rz:8.2f} deg   '
        )

        print('Press Ctrl+C to stop.                    ')

        self.display_started = True



def main(args=None):
    # Start ROS 2.
    rclpy.init(args=args)

    node = E6PoseMonitor()

    try:
        # Keep the node alive so it can continue receiving pose messages.
        rclpy.spin(node)

    except KeyboardInterrupt:
        print('\nStopping pose monitor.')

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()