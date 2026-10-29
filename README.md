# Object Seeker

A small robot with a camera in Gazebo. YOLO looks at the camera images and finds objects
(a person and a fire hydrant), and the robot drives to the one you choose.

## Stages (git branches)

Each stage has its own branch. `main` always holds the latest finished stage.

| Branch | What it adds | Status |
|---|---|---|
| `stage-1-robot-sim` | Robot + camera in Gazebo, keyboard driving | done |
| `stage-2-yolo` | YOLO finds objects in the camera image | done |
| `stage-3-follow` | Robot searches for an object and drives to it | done |

Open a stage, then rebuild from clean:

```bash
git switch stage-1-robot-sim
rm -rf build install log && colcon build
```

## 1. One-time setup: YOLO

YOLO runs in its own Python environment so it doesn't clash with ROS:

```bash
sudo apt install python3.12-venv
python3 -m venv --system-site-packages ~/yolo_venv
~/yolo_venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
~/yolo_venv/bin/pip install "numpy<2" ultralytics
```

- `--system-site-packages` lets the venv see ROS packages such as `rclpy` and `cv_bridge`.
- The `cpu` PyTorch is much smaller; this laptop has no NVIDIA GPU.
- `numpy<2` because ROS Jazzy's `cv_bridge` is built for NumPy 1.

## 2. Build

```bash
cd ~/Robotics/Projects/object_seeker_ws
source /opt/ros/jazzy/setup.bash
colcon build
```

Run `colcon build` again after every change.

## 3. Run

Terminal 1 — Gazebo, the robot and RViz:

```bash
source ~/Robotics/Projects/object_seeker_ws/install/setup.bash
ros2 launch seeker_sim sim.launch.py
```

Terminal 2 — YOLO (the first run downloads the small `yolo11n.pt` model into this folder):

```bash
source ~/yolo_venv/bin/activate
source ~/Robotics/Projects/object_seeker_ws/install/setup.bash
cd ~/Robotics/Projects/object_seeker_ws
ros2 run seeker_yolo yolo_node
```

It prints `Found: person 0.91` and so on, and RViz shows the boxes in the **YOLO** panel.

Terminal 3 — follow the person:

```bash
source ~/Robotics/Projects/object_seeker_ws/install/setup.bash
ros2 run seeker_follow follow_node
```

The robot turns until it sees the person, drives up to them and stops about 1.5 m away.
Then try:

- **Another target:** `ros2 run seeker_follow follow_node --ros-args -p target:="fire hydrant"`
- **Moving target:** in Gazebo, pick the Translate tool (`T`), drag the person, and the robot follows.
- **Drive by hand:** stop `follow_node` first (both send `/cmd_vel`), then
  `ros2 run teleop_twist_keyboard teleop_twist_keyboard` (`i` forward, `j`/`l` turn, `k` stop).

Tip: add `source /opt/ros/jazzy/setup.bash` to `~/.bashrc` so every new terminal has ROS.

## 4. Check it works

```bash
ros2 topic hz /camera/image_raw       # camera, about 15 per second
ros2 topic echo /detections           # boxes found by YOLO
ros2 topic echo /cmd_vel              # speed commands from follow_node
```

## Files

| File | What it does |
|---|---|
| `src/seeker_sim/urdf/seeker.urdf.xacro` | The robot: body, 2 wheels, caster, camera, plus the Gazebo drive and camera plugins |
| `src/seeker_sim/worlds/seeker_world.sdf` | The world: ground, sun, a person and a fire hydrant |
| `src/seeker_sim/config/bridge.yaml` | Which topics are copied between Gazebo and ROS 2 |
| `src/seeker_sim/launch/sim.launch.py` | Starts Gazebo, the robot, the bridge and RViz |
| `src/seeker_sim/rviz/seeker.rviz` | RViz layout: robot, frames, camera and YOLO views |
| `src/seeker_yolo/seeker_yolo/yolo_node.py` | Runs YOLO on each camera image and publishes the boxes |
| `src/seeker_follow/seeker_follow/follow_node.py` | Turns the boxes into speed commands: search, steer, drive, stop |

## How it fits together

```
Gazebo camera ──► bridge ──/camera/image_raw──► yolo_node ──/detections──► follow_node
                                                          └─/detections/image──► RViz
follow_node (or keyboard) ──/cmd_vel──► bridge ──► Gazebo: DiffDrive turns the wheels
Gazebo ──/odom /tf /joint_states──► bridge ──► robot_state_publisher, RViz
```

## If something goes wrong

- **Gazebo window is black or crashes:** run `export LIBGL_ALWAYS_SOFTWARE=1`, then launch again.
- **Robot doesn't move with the keyboard:** click on the teleop terminal first; it only reads keys when focused.
- **`No module named 'ultralytics'`:** run `source ~/yolo_venv/bin/activate` in that terminal first.
- **follow_node says "Waiting for /detections":** start `yolo_node` (terminal 2).
- **Robot keeps spinning:** it can't see the target. Check the YOLO panel in RViz and the target name.
- **YOLO is slow:** normal on a CPU; it skips old frames and always uses the newest one.

## Ideas for more stages

- Map the world with `slam_toolbox`, then patrol it with Nav2 while YOLO reports what it sees.
- Train YOLO on your own object using images from the robot's camera.
