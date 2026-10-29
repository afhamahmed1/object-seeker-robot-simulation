"""Start Gazebo, add the Seeker robot, connect it to ROS 2 and open RViz.

    ros2 launch seeker_sim sim.launch.py
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('seeker_sim')
    world = PathJoinSubstitution([pkg, 'worlds', 'seeker_world.sdf'])
    xacro_file = PathJoinSubstitution([pkg, 'urdf', 'seeker.urdf.xacro'])
    bridge_config = PathJoinSubstitution([pkg, 'config', 'bridge.yaml'])
    rviz_config = PathJoinSubstitution([pkg, 'rviz', 'seeker.rviz'])

    # Run xacro to turn the .xacro file into plain URDF text
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        # 1. Gazebo with our world (-r = start running, not paused)
        IncludeLaunchDescription(
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py']),
            launch_arguments={'gz_args': ['-r ', world], 'on_exit_shutdown': 'true'}.items(),
        ),

        # 2. Publish the robot model and its frames (TF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        ),

        # 3. Put the robot into Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'seeker', '-z', '0.01'],
        ),

        # 4. Connect Gazebo topics to ROS 2 (list in config/bridge.yaml)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{'config_file': bridge_config, 'use_sim_time': True}],
        ),

        # 5. RViz to see the robot and its camera
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
        ),
    ])
