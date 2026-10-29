"""Follow node: drives the robot to an object that YOLO found.

Subscribes:  /detections  (vision_msgs/Detection2DArray) from yolo_node
Publishes:   /cmd_vel     (geometry_msgs/Twist)

Ten times a second it decides:
  - target not seen        -> turn on the spot to search for it
  - target seen            -> steer to keep it centred and drive towards it
  - target box wide enough -> it's close, so stop
  - no detections for 1 s  -> yolo_node isn't running, so stop

    ros2 run seeker_follow follow_node
    ros2 run seeker_follow follow_node --ros-args -p target:="fire hydrant"
"""

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from vision_msgs.msg import Detection2DArray

IMAGE_WIDTH = 640  # same as the camera in seeker.urdf.xacro


class FollowNode(Node):

    def __init__(self):
        super().__init__('follow_node')

        # Settings you can change with --ros-args -p name:=value
        self.target = self.declare_parameter('target', 'person').value       # any YOLO class name
        self.stop_width = self.declare_parameter('stop_width', 0.3).value    # stop when box is 30 % of image width
        self.forward_speed = self.declare_parameter('forward_speed', 0.2).value  # m/s
        self.turn_gain = self.declare_parameter('turn_gain', 0.6).value      # how hard to steer
        self.search_speed = self.declare_parameter('search_speed', 0.3).value    # rad/s while searching

        self.detections = None
        self.last_detection_time = 0.0

        self.create_subscription(Detection2DArray, '/detections', self.on_detections, 1)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_timer(0.1, self.control_loop)

    def on_detections(self, msg):
        self.detections = msg
        self.last_detection_time = time.time()

    def find_target(self):
        """Return the widest (closest) box of the target class, or None."""
        boxes = [d for d in self.detections.detections
                 if d.results and d.results[0].hypothesis.class_id == self.target]
        return max(boxes, key=lambda d: d.bbox.size_x, default=None)

    def control_loop(self):
        cmd = Twist()  # all zeros = stand still

        if time.time() - self.last_detection_time > 1.0:
            status = 'Waiting for /detections (is yolo_node running?)'
        else:
            box = self.find_target()

            if box is None:
                cmd.angular.z = self.search_speed
                status = f'Searching for {self.target}...'
            else:
                # Where is the box? -1 = left edge, 0 = centre, +1 = right edge
                offset = (box.bbox.center.position.x - IMAGE_WIDTH / 2) / (IMAGE_WIDTH / 2)
                # The closer the object, the wider its box
                width = box.bbox.size_x / IMAGE_WIDTH

                if width < self.stop_width:
                    cmd.linear.x = self.forward_speed
                    cmd.angular.z = -self.turn_gain * offset  # target on the right -> turn right
                    status = f'Driving to {self.target} (offset {offset:+.2f}, width {width:.2f})'
                else:
                    status = f'Reached {self.target}!'

        self.cmd_pub.publish(cmd)
        self.get_logger().info(status, throttle_duration_sec=1.0)


def main():
    # Handle Ctrl-C ourselves so we can still send a stop command before exiting
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = FollowNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cmd_pub.publish(Twist())  # Gazebo keeps the last command, so stop the robot
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
