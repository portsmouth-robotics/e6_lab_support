import time

import rclpy
from rclpy.node import Node

from dobot_msgs_v4.srv import MovJ, MovL


# This example contains more comments than you would normally write in a ROS 2 program.
# They are included to help you understand the structure of the code and get started.
#
# In your own programs, comments should usually explain things that are not obvious
# from reading the code itself, rather than describing every individual line.
#
# IMPORTANT:
# Run robot_setup before running this example.
#
# robot_setup:
#   - requests control of the robot
#   - enables the robot
#   - selects User 0 (the robot base coordinate system)
#   - selects Tool 1 (the vacuum tool TCP)
#   - sets the vacuum-tool payload
#
# The Cartesian coordinates below therefore describe the Tool 1 TCP
# relative to User 0 / the robot base coordinate system.


# These two poses were physically taught and checked on the lab E6.
#
# Each pose is:
#   X, Y, Z, Rx, Ry, Rz
#
# Position values are in millimetres.
# Orientation values are in degrees.

POSE_A = (
    -127.75,
    314.51,
    214.49,
    -176.30,
    -30.01,
    151.93,
)

POSE_B = (
    -33.94,
    225.85,
    213.57,
    178.98,
    1.28,
    151.06,
)


class E6MovementDemo(Node):

    def __init__(self):
        # Initialise this ROS 2 node.
        super().__init__('e6_movement_demo')

        # Create service clients for the two motion commands used by this demo.
        #
        # MovJ moves to a target using joint-interpolated motion.
        # The tool does not necessarily travel in a straight Cartesian line.
        self.mov_j = self.create_client(
            MovJ,
            '/dobot_bringup_ros2/srv/MovJ'
        )

        # MovL moves the tool centre point along a linear Cartesian path.
        self.mov_l = self.create_client(
            MovL,
            '/dobot_bringup_ros2/srv/MovL'
        )

    def call_service(self, client, request):
        # Wait until the Dobot driver is offering this service.
        client.wait_for_service()

        # Send the request asynchronously...
        future = client.call_async(request)

        # ...then keep this node running until the driver responds.
        rclpy.spin_until_future_complete(self, future)

        return future.result()

    def make_cartesian_request(self, service_type, pose):
        # MovJ and MovL use the same request layout.
        request = service_type.Request()

        # mode=False tells the Dobot driver that a-f represent a Cartesian pose:
        #
        #   a = X
        #   b = Y
        #   c = Z
        #   d = Rx
        #   e = Ry
        #   f = Rz
        #
        # mode=True would instead interpret a-f as six joint angles.
        request.mode = False

        request.a = float(pose[0])
        request.b = float(pose[1])
        request.c = float(pose[2])
        request.d = float(pose[3])
        request.e = float(pose[4])
        request.f = float(pose[5])

        # These optional parameters are passed directly to the Dobot motion command.
        #
        # user=0 means the coordinates use the robot base coordinate system.
        # tool=1 means the target refers to the vacuum tool TCP.
        #
        # a and v limit acceleration and velocity for this teaching example.
        # cp=0 disables continuous-path blending so each target is treated distinctly.
        request.param_value = [
            'user=0',
            'tool=1',
            'a=20',
            'v=20',
            'cp=0',
        ]

        return request

    def move_j(self, pose):
        print('\nMovJ: moving to Pose A using joint-interpolated motion...')

        request = self.make_cartesian_request(
            MovJ,
            pose
        )

        response = self.call_service(
            self.mov_j,
            request
        )

        print(f'  robot_return: {response.robot_return}')
        print(f'  result: {response.res}')

    def move_l(self, pose):
        print('\nMovL: moving to Pose B using linear Cartesian motion...')

        request = self.make_cartesian_request(
            MovL,
            pose
        )

        response = self.call_service(
            self.mov_l,
            request
        )

        print(f'  robot_return: {response.robot_return}')
        print(f'  result: {response.res}')

    def run_demo(self):
        print('E6 Movement Demo')
        print()
        print('This example demonstrates the difference between MovJ and MovL.')
        print()
        print('MovJ: joint-interpolated movement.')
        print('MovL: straight-line Cartesian movement of the tool TCP.')
        print()
        print('Make sure the robot workspace is clear before continuing.')

        input('\nPress Enter to start...')

        while True:
            # First move to the known starting position.
            self.move_j(POSE_A)

            # Dobot motion commands are queued. This short delay makes the
            # demonstration easier to watch and avoids immediately filling
            # the command queue with repeated cycles.
            time.sleep(3.0)

            # Move from A to B using a Cartesian straight-line move.
            self.move_l(POSE_B)

            time.sleep(3.0)

            # Return to A using joint-interpolated motion.
            self.move_j(POSE_A)

            time.sleep(3.0)

            print()
            repeat = input(
                'Cycle complete. Press Enter to repeat, or type q and Enter to quit: '
            )

            if repeat.strip().lower() == 'q':
                break

        print('Movement demo complete.')


def main(args=None):
    # Start ROS 2.
    rclpy.init(args=args)

    node = E6MovementDemo()

    try:
        node.run_demo()

    except KeyboardInterrupt:
        print('\nMovement demo interrupted.')

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()