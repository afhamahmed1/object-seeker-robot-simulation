# Object Seeker

A small robot with a camera in Gazebo. YOLO looks at the camera images and finds objects
(a person and a fire hydrant). The next stage makes the robot drive to them.

## Stages (git branches)

Each stage has its own branch. `main` always holds the latest finished stage.

| Branch | What it adds | Status |
|---|---|---|
| `stage-1-robot-sim` | Robot + camera in Gazebo, keyboard driving | done |
| `stage-2-yolo` | YOLO finds objects in the camera image | done |
| `stage-3-follow` | Robot drives to the object it found | next |

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

Terminal 3 — drive with the keyboard (`i` forward, `j`/`l` turn, `,` back, `k` stop).
Turn right to find the fire hydrant:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Tip: add `source /opt/ros/jazzy/setup.bash` to `~/.bashrc` so every new terminal has ROS.

## 4. Check it works

```bash
ros2 topic hz /camera/image_raw       # camera, about 15 per second
ros2 topic echo /detections           # boxes found by YOLO
ros2 run rqt_image_view rqt_image_view   # pick /detections/image
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

## How it fits together

```
keyboard ──/cmd_vel──► bridge ──► Gazebo: DiffDrive turns the wheels
Gazebo camera ──► bridge ──/camera/image_raw──► yolo_node ──/detections────────► (Stage 3: follow)
                                                          └─/detections/image──► RViz
Gazebo ──/odom /tf /joint_states──► bridge ──► robot_state_publisher, RViz
```

## If something goes wrong

- **Gazebo window is black or crashes:** run `export LIBGL_ALWAYS_SOFTWARE=1`, then launch again.
- **Robot doesn't move:** click on the teleop terminal first; it only reads keys when focused.
- **`No module named 'ultralytics'`:** run `source ~/yolo_venv/bin/activate` in that terminal first.
- **YOLO is slow:** normal on a CPU; it skips old frames and always uses the newest one.

## Next

Stage 3: a node that reads `/detections` and drives the robot towards the person.
