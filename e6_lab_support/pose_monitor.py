import select
import sys

import rclpy
from rclpy.node import Node

from dobot_msgs_v4.msg import ToolVectorActual
from dobot_msgs_v4.srv import StartDrag, StopDrag


# This example contains more comments than you would normally write in a ROS 2 program.
# They are included to help you understand the structure of the code and get started.
#
# In your own programs, comments should usually explain things that are not obvious
# from reading the code itself, rather than describing every individual line.


class E6PoseMonitor(Node):

    def __init__(self):
        # Initialise this ROS 2 node.
        super().__init__('e6_pose_monitor')

        # Keep track of whether drag mode is currently enabled.
        # The program starts with drag mode disabled.
        self.drag_enabled = False

        # Store the most recently received pose.
        self.current_pose = None

        # Subscribe to the robot's live Cartesian tool position.
        #
        # The message contains:
        #   x, y, z    - position in millimetres
        #   rx, ry, rz - orientation in degrees
        self.subscription = self.create_subscription(
            ToolVectorActual,
            '/dobot_msgs_v4/msg/ToolVectorActual',
            self.pose_callback,
            10
        )

        # These service clients allow us to enter and leave drag mode.
        self.start_drag = self.create_client(
            StartDrag,
            '/dobot_bringup_ros2/srv/StartDrag'
        )

        self.stop_drag = self.create_client(
            StopDrag,
            '/dobot_bringup_ros2/srv/StopDrag'
        )

        # A timer checks the keyboard periodically.
        #
        # This lets ROS continue processing pose messages while also allowing
        # the user to press Enter to toggle drag mode.
        self.timer = self.create_timer(
            0.1,
            self.check_keyboard
        )

        print('E6 Pose Monitor')
        print()
        print('Press Enter to toggle drag mode.')
        print('Press Ctrl+C to stop.')
        print()
        print('Waiting for pose data...')

    def pose_callback(self, msg):
        # Save the newest pose. The display is redrawn by this callback every
        # time the Dobot driver publishes a new position.
        self.current_pose = msg

        self.update_display()

    def call_service(self, client, request):
        # Wait for the requested Dobot service to become available.
        client.wait_for_service()

        # Send the request asynchronously.
        future = client.call_async(request)

        # Do not call spin_until_future_complete() here because this node is
        # already being spun by rclpy.spin().
        #
        # Instead, return the future and let ROS complete it normally.
        return future

    def check_keyboard(self):
        # select() checks whether there is keyboard input waiting without
        # pausing the ROS node.
        ready, _, _ = select.select([sys.stdin], [], [], 0)

        if not ready:
            return

        # Remove the Enter key from the input buffer.
        sys.stdin.readline()

        if self.drag_enabled:
            # The robot is currently free to move by hand, so pressing Enter
            # again tells it to leave drag mode and lock the joints.
            future = self.call_service(
                self.stop_drag,
                StopDrag.Request()
            )

            future.add_done_callback(self.drag_stopped)

        else:
            # Enter drag mode. The robot joints can now be repositioned
            # manually by moving the arm.
            future = self.call_service(
                self.start_drag,
                StartDrag.Request()
            )

            future.add_done_callback(self.drag_started)

    def drag_started(self, future):
        response = future.result()

        if response.res == 0:
            self.drag_enabled = True
        else:
            print(f'\nStartDrag failed with result {response.res}')

        self.update_display()

    def drag_stopped(self, future):
        response = future.result()

        if response.res == 0:
            self.drag_enabled = False
        else:
            print(f'\nStopDrag failed with result {response.res}')

        self.update_display()

    def update_display(self):
        # Move the terminal cursor back to the start of the display block.
        #
        # The escape sequence clears each line before redrawing it so the
        # monitor stays as one fixed block instead of producing a stream of
        # output.
        print('\033[4F', end='')

        if self.current_pose is None:
            return

        msg = self.current_pose

        drag_text = 'ON - move the robot by hand' if self.drag_enabled else 'OFF - joints locked'

        print('\033[2K' + f'Drag mode:   {drag_text}')
        print(
            '\033[2K'
            f'Position:    '
            f'X {msg.x:8.2f} mm   '
            f'Y {msg.y:8.2f} mm   '
            f'Z {msg.z:8.2f} mm'
        )
        print(
            '\033[2K'
            f'Orientation: '
            f'Rx {msg.rx:8.2f} deg   '
            f'Ry {msg.ry:8.2f} deg   '
            f'Rz {msg.rz:8.2f} deg'
        )
        print('\033[2KPress Enter to toggle drag mode. Ctrl+C to stop.')


def main(args=None):
    rclpy.init(args=args)

    node = E6PoseMonitor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        print('\nStopping pose monitor.')

    finally:
        # If the program is closed while drag mode is active, try to stop drag
        # mode before shutting ROS down.
        #
        # This leaves the robot locked rather than free-moving.
        if node.drag_enabled and rclpy.ok():
            future = node.stop_drag.call_async(StopDrag.Request())
            rclpy.spin_until_future_complete(node, future)

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()