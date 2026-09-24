import rclpy
import select
import sys
from rclpy.node import Node

from dobot_msgs_v4.srv import (
    RequestControl,
    EnableRobot,
    ToolDOInstant,
    ToolDI,
)


class E6HardwareTest(Node):

    def __init__(self):
        super().__init__('e6_hardware_test')

        self.request_control = self.create_client(
            RequestControl,
            '/dobot_bringup_ros2/srv/RequestControl'
        )

        self.enable_robot = self.create_client(
            EnableRobot,
            '/dobot_bringup_ros2/srv/EnableRobot'
        )

        self.tool_do = self.create_client(
            ToolDOInstant,
            '/dobot_bringup_ros2/srv/ToolDOInstant'
        )

        self.tool_di = self.create_client(
            ToolDI,
            '/dobot_bringup_ros2/srv/ToolDI'
        )

    def call_service(self, client, request):
        client.wait_for_service()
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def run_test(self):
        print('Requesting robot control...')
        response = self.call_service(
            self.request_control,
            RequestControl.Request()
        )
        print(f'  result: {response.res}')

        print('Enabling robot...')
        response = self.call_service(
            self.enable_robot,
            EnableRobot.Request()
        )
        print(f'  result: {response.res}')

        print('Vacuum ON...')
        request = ToolDOInstant.Request()
        request.index = 1
        request.status = 1
        response = self.call_service(self.tool_do, request)
        print(f'  result: {response.res}')

        print('Monitoring vacuum-loss input DI2.')
        print('Press Enter to stop monitoring and switch the vacuum off.')

        while True:
            request = ToolDI.Request()
            request.index = 2
            response = self.call_service(self.tool_di, request)

            state = response.robot_return.strip('{}')

            if state == '0':
                message = 'Vacuum seal OK'
            elif state == '1':
                message = 'Vacuum lost'
            else:
                message = f'Unknown state: {response.robot_return}'

            print(
                f'\rDI2: {state} - {message}      ',
                end='',
                flush=True
            )

            # Wait up to 0.2 seconds for Enter.
            ready, _, _ = select.select([sys.stdin], [], [], 0.2)

            if ready:
                sys.stdin.readline()
                break

        print('\nStopping monitor.')

        request = ToolDOInstant.Request()
        request.index = 1
        request.status = 0
        response = self.call_service(self.tool_do, request)
        print(f'  result: {response.res}')

        print('Hardware test complete.')


def main(args=None):
    rclpy.init(args=args)

    node = E6HardwareTest()

    try:
        node.run_test()
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
