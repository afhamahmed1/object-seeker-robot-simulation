# Setup from scratch: Windows → WSL → ROS 2 Jazzy → Object Seeker

This is everything installed on this laptop, in order. It only lists the steps that worked.
The mistakes from the first try are at the bottom, under "Problems hit last time".

Result: Ubuntu 24.04 inside WSL 2, ROS 2 Jazzy, Gazebo Harmonic, and the YOLO project.


## Part A: Windows

### 1. Install WSL and Ubuntu 24.04

Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart the PC when it asks. Then open **Ubuntu 24.04** from the Start menu. It asks for a
new Linux username and password (this is the password `sudo` asks for later).

Check that it is WSL **2** (run this in PowerShell):

```powershell
wsl --update
wsl -l -v
```

Windows 11 can show Linux windows (Gazebo, RViz) by itself, so nothing else is needed for graphics.

### 2. Install VS Code (optional)

1. Install VS Code on **Windows** from https://code.visualstudio.com
2. In VS Code, install the **WSL** extension (by Microsoft).
3. From the Ubuntu terminal, `code .` opens the current folder in VS Code.


## Part B: Ubuntu (run everything below in the Ubuntu terminal)

### 3. Update Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Set the language to UTF-8 (ROS needs this)

```bash
sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### 5. Add the ROS 2 package source

```bash
sudo apt install software-properties-common curl -y
sudo add-apt-repository universe

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

This creates `/etc/apt/sources.list.d/ros2.sources`. Use **only** this method. Do not also add a
`ros2.list` file by hand (see "Problems hit last time").

### 6. Install ROS 2 Jazzy

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-jazzy-desktop ros-dev-tools
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Test it with two terminals:

```bash
ros2 run demo_nodes_cpp talker      # terminal 1: prints "Publishing: Hello World"
ros2 run demo_nodes_py listener     # terminal 2: prints "I heard: Hello World"
```

`Ctrl+C` stops each one.

### 7. Install Gazebo and the robot packages

```bash
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  ros-jazzy-tf2-tools \
  ros-jazzy-tf-transformations \
  ros-jazzy-urdf \
  ros-jazzy-urdf-tutorial \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-moveit \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-bringup \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  git
```

Object Seeker only needs the first few (`ros-gz`, `robot-state-publisher`, `xacro`). The others
(MoveIt, Nav2, SLAM, ros2_control) are there for later projects.

Test Gazebo:

```bash
gz sim --versions     # should print 8.x (Gazebo Harmonic)
gz sim shapes.sdf     # a window with a box, sphere and cylinder
```

### 8. tmux: several terminals in one window (optional)

```bash
sudo apt install tmux -y
nano ~/.tmux.conf
```

Paste this, then save (`Ctrl+O`, `Enter`, `Ctrl+X`):

```
set -g mouse on
set -g default-terminal "screen-256color"
bind -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel "clip.exe"
```

Start it with `tmux`. `Ctrl+B` then `%` splits left/right, `Ctrl+B` then `"` splits top/bottom.

### 9. Git and GitHub

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Make an SSH key so you can push to GitHub without a password:

```bash
ssh-keygen -t ed25519 -C "you@example.com"    # press Enter for each question
cat ~/.ssh/id_ed25519.pub
```

Copy the printed line into GitHub → Settings → SSH and GPG keys → **New SSH key**.
Test it with `ssh -T git@github.com`.


## Part C: The Object Seeker project

### 10. Get the code

```bash
mkdir -p ~/Robotics/Projects
cd ~/Robotics/Projects
git clone git@github.com:afhamahmed1/object-seeker-robot-simulation.git object_seeker_ws
```

### 11. YOLO's Python environment

```bash
sudo apt install python3.12-venv -y
python3 -m venv --system-site-packages ~/yolo_venv
~/yolo_venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
~/yolo_venv/bin/pip install "numpy<2" ultralytics
```

The reasons for each choice are in `README.md`, section 1.

### 12. Build

```bash
cd ~/Robotics/Projects/object_seeker_ws
colcon build
```

### 13. Run

Follow `README.md` section 3 (three terminals: Gazebo, YOLO, follow).


## Problems hit last time

| Error | Cause | Fix |
|---|---|---|
| `Unable to locate package ros-lyrical-desktop` | ROS 2 Lyrical is not for Ubuntu 24.04 | Use **Jazzy** (the ROS 2 release for 24.04). Remove any `lyrical` line from `~/.bashrc` |
| `Conflicting values set for option Signed-By` | The ROS source was added twice (`ros2.sources` from step 5 and a hand-made `ros2.list`) | `sudo rm /etc/apt/sources.list.d/ros2.list` then `sudo apt update` |
| `apt update` fails with hash or download errors | Old, broken package lists | `sudo apt clean && sudo rm -rf /var/lib/apt/lists/* && sudo apt update` |
| `gz: command not found` | Gazebo is installed inside ROS, so ROS is not loaded in this terminal | `source /opt/ros/jazzy/setup.bash` (or open a new terminal after step 6) |
| Gazebo window is black or crashes | WSL graphics | `export LIBGL_ALWAYS_SOFTWARE=1`, then launch again |
