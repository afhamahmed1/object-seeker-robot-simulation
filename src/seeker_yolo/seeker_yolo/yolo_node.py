"""YOLO detector: finds objects in the robot's camera images.

Subscribes:  /camera/image_raw   (sensor_msgs/Image)
Publishes:   /detections         (vision_msgs/Detection2DArray) - one box per object found
             /detections/image   (sensor_msgs/Image)            - camera image with boxes drawn

    ros2 run seeker_yolo yolo_node
"""

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics import YOLO
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


class YoloNode(Node):

    def __init__(self):
        super().__init__('yolo_node')

        # Settings you can change with --ros-args -p name:=value
        self.declare_parameter('model', 'yolo11n.pt')   # n = nano, the fastest model
        self.declare_parameter('confidence', 0.5)       # ignore guesses below 50 %

        self.model = YOLO(self.get_parameter('model').value)
        self.bridge = CvBridge()

        # Queue size 1: if YOLO is busy, skip old frames and use the newest one
        self.create_subscription(Image, '/camera/image_raw', self.on_image, 1)
        self.detections_pub = self.create_publisher(Detection2DArray, '/detections', 10)
        self.image_pub = self.create_publisher(Image, '/detections/image', 1)

        self.get_logger().info('YOLO ready, waiting for camera images...')

    def on_image(self, msg):
        # 1. ROS image -> OpenCV image
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # 2. Run YOLO
        confidence = self.get_parameter('confidence').value
        result = self.model(frame, conf=confidence, verbose=False)[0]

        # 3. Turn each box into a ROS Detection2D message
        detections = Detection2DArray(header=msg.header)
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detection = Detection2D(header=msg.header)
            detection.bbox.center.position.x = (x1 + x2) / 2
            detection.bbox.center.position.y = (y1 + y2) / 2
            detection.bbox.size_x = x2 - x1
            detection.bbox.size_y = y2 - y1

            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = result.names[int(box.cls)]
            hypothesis.hypothesis.score = float(box.conf)
            detection.results.append(hypothesis)

            detections.detections.append(detection)

        self.detections_pub.publish(detections)

        # 4. Publish the image with boxes drawn on it (view in RViz or rqt_image_view)
        annotated = self.bridge.cv2_to_imgmsg(result.plot(), 'bgr8')
        annotated.header = msg.header
        self.image_pub.publish(annotated)

        # 5. Print what was found, at most once per second
        found = [f'{d.results[0].hypothesis.class_id} {d.results[0].hypothesis.score:.2f}'
                 for d in detections.detections]
        self.get_logger().info(f'Found: {", ".join(found) or "nothing"}',
                               throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = YoloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
