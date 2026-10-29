# Object Seeker

A small robot with a camera that you drive around in Gazebo.
Later stages add YOLO so it can find and follow objects on its own.

## Stages (git branches)

Each stage has its own branch. `main` always holds the latest finished stage.

| Branch | What it adds | Status |
|---|---|---|
| `stage-1-robot-sim` | Robot + camera in Gazebo, keyboard driving | done |
| `stage-2-yolo` | YOLO finds objects in the camera image | next |
| `stage-3-follow` | Robot drives to the object it found | planned |

Open a stage, then rebuild from clean:

```bash
git switch stage-1-robot-sim
rm -rf build install log && colcon build --symlink-install
```

## 1. Build

```bash
cd ~/Robotics/Projects/object_seeker_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

Rebuild only when you add a new file. Edits to existing files apply on the next launch.

## 2. Run

Terminal 1 — start Gazebo, the robot and RViz:

```bash
source ~/Robotics/Projects/object_seeker_ws/install/setup.bash
ros2 launch seeker_sim sim.launch.py
```

The first launch downloads the person and fire hydrant models, so it takes a little longer.

Terminal 2 — drive with the keyboard (`i` forward, `j`/`l` turn, `,` back, `k` stop):

```bash
source /opt/ros/jazzy/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Tip: add `source /opt/ros/jazzy/setup.bash` to `~/.bashrc` so every new terminal has ROS.

## 3. Check it works

```bash
ros2 topic list                       # should include /camera/image_raw, /cmd_vel, /odom
ros2 topic hz /camera/image_raw       # about 15 images per second
ros2 run rqt_image_view rqt_image_view
```

## Files

All in `src/seeker_sim/`:

| File | What it does |
|---|---|
| `urdf/seeker.urdf.xacro` | The robot: body, 2 wheels, caster, camera, plus the Gazebo drive and camera plugins |
| `worlds/seeker_world.sdf` | The world: ground, sun, a person and a fire hydrant |
| `config/bridge.yaml` | Which topics are copied between Gazebo and ROS 2 |
| `launch/sim.launch.py` | Starts everything with one command |
| `rviz/seeker.rviz` | RViz layout: robot model, frames and camera view |

## How it fits together

```
keyboard ──/cmd_vel──► bridge ──► Gazebo: DiffDrive turns the wheels
Gazebo camera ──► bridge ──/camera/image_raw──► RViz   (Stage 2: YOLO)
Gazebo ──/odom /tf /joint_states──► bridge ──► robot_state_publisher, RViz
```

## If something goes wrong

- **Gazebo window is black or crashes:** run `export LIBGL_ALWAYS_SOFTWARE=1`, then launch again.
- **Robot doesn't move:** click on the teleop terminal first; it only reads keys when focused.

## Next

Stage 2: a Python node that reads `/camera/image_raw`, runs YOLO and draws boxes around the person and the hydrant.
