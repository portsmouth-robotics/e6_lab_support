import rclpy
from rclpy.node import Node

from dobot_msgs_v4.srv import (
    RequestControl,
    EnableRobot,
    SetTool,
    Tool,
    SetPayload,
    User
)


# This example contains more comments than you would normally write in a ROS 2 program.
# They are included to help you understand the structure of the code and get started.
#
# In your own programs, comments should usually explain things that are not obvious
# from reading the code itself, rather than describing every individual line.


class E6RobotSetup(Node):

    def __init__(self):
        # Initialise this ROS 2 node.
        super().__init__('e6_robot_setup')

        # Create service clients for the Dobot commands used during setup.
        #
        # A service client allows this node to send a request to a ROS 2 service
        # and wait for the robot driver to return a response.
        self.request_control = self.create_client(
            RequestControl,
            '/dobot_bringup_ros2/srv/RequestControl'
        )

        self.enable_robot = self.create_client(
            EnableRobot,
            '/dobot_bringup_ros2/srv/EnableRobot'
        )

        self.set_user = self.create_client(
            User,
            '/dobot_bringup_ros2/srv/User'
        )

        self.set_tool = self.create_client(
            SetTool,
            '/dobot_bringup_ros2/srv/SetTool'
        )

        self.select_tool = self.create_client(
            Tool,
            '/dobot_bringup_ros2/srv/Tool'
        )

        self.set_payload = self.create_client(
            SetPayload,
            '/dobot_bringup_ros2/srv/SetPayload'
        )

    def call_service(self, client, request):
        # Wait until the requested service is available.
        client.wait_for_service()

        # Send the request asynchronously.
        future = client.call_async(request)

        # Keep this node running until the service call has finished.
        rclpy.spin_until_future_complete(self, future)

        return future.result()

    def run_setup(self):
        print('Requesting robot control...')

        # Request control of the robot.
        # The robot will reject motion commands if control has not been granted.
        response = self.call_service(
            self.request_control,
            RequestControl.Request()
        )
        print(f'  result: {response.res}')

        print('Enabling robot...')

        # Enable the robot so that it can accept movement commands.
        response = self.call_service(
            self.enable_robot,
            EnableRobot.Request()
        )
        print(f'  result: {response.res}')

        print('Selecting User 0 (robot base frame)...')

        # User 0 is the robot base coordinate system.
        # Selecting it explicitly makes the Cartesian reference frame predictable
        # for pose readings and motion commands.
        request = User.Request()
        request.index = 0

        response = self.call_service(
            self.set_user,
            request
        )
        print(f'  result: {response.res}')

        print('Configuring vacuum tool TCP...')

        # Tool 1 is the vacuum gripper.
        #
        # The TCP (Tool Centre Point) is at the end of the vacuum sucker,
        # 91 mm along the positive Z axis from the robot flange.
        request = SetTool.Request()
        request.index = 1
        request.value = '{0,0,91,0,0,0}'

        response = self.call_service(
            self.set_tool,
            request
        )
        print(f'  result: {response.res}')

        print('Selecting Tool 1...')

        # Select Tool 1 so that Cartesian positions use the vacuum sucker
        # as the active tool centre point.
        request = Tool.Request()
        request.index = 1

        response = self.call_service(
            self.select_tool,
            request
        )
        print(f'  result: {response.res}')

        print('Setting payload...')

        # The vacuum tool has a mass of approximately 0.25 kg.
        #
        # Centre-of-mass offsets are left at zero for this teaching setup.
        request = SetPayload.Request()
        request.load = 0.25
        request.x = 0.0
        request.y = 0.0
        request.z = 0.0

        response = self.call_service(
            self.set_payload,
            request
        )
        print(f'  result: {response.res}')

        print('Robot setup complete.')


def main(args=None):
    # Start ROS 2.
    rclpy.init(args=args)

    node = E6RobotSetup()

    try:
        node.run_setup()
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()