# CoppeliaSim Robotic Arm Simulation Project

A comprehensive simulation environment for developing and testing autonomous pick-and-place behaviors for a 6-DOF robotic arm (Yahboom-style) in CoppeliaSim.

## Project Overview

This project implements a complete AI/ML pipeline for robotic manipulation:

- **Workspace**: Desk (1.04m × 0.43m) with 6-DOF arm mounted at edge
- **Objects**: Colored cubes, cylinders, and spheres scattered on desk
- **Task**: Autonomous object detection, classification, grasping, and sorting into color-coded bins
- **Vision**: OpenCV-based object detection with depth sensing
- **Planning**: Rule-based and learning-based grasp planning
- **Control**: Trajectory generation using Modern Robotics library

## Directory Structure

```
simulation_project/
├── config/
│   └── sim_config.yaml          # Main configuration file
├── scripts/
│   ├── coppelia_api.py          # CoppeliaSim ZeroMQ API wrapper
│   ├── scene_builder.py         # Programmatic scene generation
│   └── main_controller.py       # Main task controller
├── vision/
│   └── object_detector.py       # Computer vision pipeline
├── planning/
│   └── grasp_planner.py         # Grasp planning & trajectories
├── ml_models/                   # ML model storage (optional)
├── logs/                        # Task logs and images
└── README.md                    # This file
```

## Prerequisites

### Software Requirements

1. **CoppeliaSim EDU** (v4.10.0 or later)
   - Download from: https://www.coppeliarobotics.com/
   - Enable ZeroMQ Remote API plugin

2. **Python 3.11+**

3. **Python Packages**:
   ```bash
   pip install coppeliasim-zmqremoteapi-client
   pip install numpy opencv-python pyyaml
   ```

4. **Modern Robotics Library** (already in repo)
   ```bash
   cd packages/Python
   pip install -e .
   ```

### Hardware Specifications

This simulation mirrors a real physical setup:
- Desk: 43cm depth × 104cm length
- Robot: 6-DOF Yahboom Pi robotic arm (or UR5/Panda equivalent)
- Objects: 15-20 small items (3-5cm size)
- Vision: Overhead camera/sensor

## Quick Start

### 1. Launch CoppeliaSim

```bash
# Windows
"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\coppeliaSim.exe"

# Linux
./coppeliaSim.sh

# macOS
open coppeliaSim.app
```

### 2. Build the Scene

Run the scene builder to create the workspace:

```bash
cd simulation_project
python scripts/scene_builder.py
```

This will:
- Create a desk matching real-world dimensions
- Spawn random colored objects
- Create color-coded sorting bins
- Setup vision sensor

**Manual step**: Load robot model (UR5 or Panda) from CoppeliaSim:
- File → Load Model → Select UR5 or Panda
- Position at configured base location: `(-0.45, 0.0, 0.08)`

### 3. Run the Simulation

Execute the main controller:

```bash
python scripts/main_controller.py
```

This will:
1. Connect to CoppeliaSim
2. Start the simulation
3. Run pick-and-place task loop:
   - Scan workspace with vision sensor
   - Detect and classify objects
   - Plan grasp poses
   - Execute pick-and-place motions
   - Sort objects into correct bins
4. Log results to `logs/`

## Configuration

Edit `config/sim_config.yaml` to customize:

- **Desk dimensions**: Match your physical setup
- **Robot model**: UR5, Panda, or custom
- **Object types**: Count, shapes, colors, sizes
- **Sorting zones**: Positions and target colors
- **Vision settings**: Resolution, FOV, camera position
- **Control parameters**: Velocities, approach distances
- **ML settings**: Detection method, grasp planning algorithm

## Module Documentation

### CoppeliaSim API (`scripts/coppelia_api.py`)

Wrapper for ZeroMQ Remote API providing:
- Connection management
- Object manipulation (position, orientation)
- Joint control
- Vision sensor access
- Simulation control

Example:
```python
from scripts.coppelia_api import CoppeliaSimConnection

conn = CoppeliaSimConnection()
conn.connect()
conn.start_simulation()

# Get vision sensor image
image = conn.get_vision_sensor_image(sensor_handle)

conn.stop_simulation()
```

### Vision Processing (`vision/object_detector.py`)

Computer vision pipeline with:
- Color-based segmentation (HSV)
- Shape classification (contour analysis)
- 3D pose estimation (from depth)
- Object filtering by workspace bounds
- Visualization overlays

Methods:
- `color_based`: HSV segmentation + contour detection
- `yolo`: Deep learning object detection (placeholder)

### Grasp Planning (`planning/grasp_planner.py`)

Grasp pose generation with:
- Rule-based heuristics (shape-specific grasps)
- Pre-grasp pose computation
- Smooth trajectory generation
- Modern Robotics integration

Strategies:
- **Cubes**: Top-down parallel jaw grasp
- **Cylinders**: Side approach with rotation
- **Spheres**: Wide top-down grasp

### Main Controller (`scripts/main_controller.py`)

High-level task orchestrator:
1. Initialize CoppeliaSim connection
2. Get robot and sensor handles
3. Run perception-planning-action loop
4. Log performance metrics

## Advanced Features

### Extending the Arm

To test arm extensions (longer links):

1. Modify link length in CoppeliaSim scene
2. Update kinematics parameters in config
3. Re-run simulations to evaluate workspace coverage
4. Compare success rates before/after extension

### Custom Grippers

To swap end-effectors:

1. Load new gripper model in CoppeliaSim
2. Update `robot.gripper_type` in config
3. Modify grasp width calculations in `grasp_planner.py`
4. Test grasp success with different objects

### Mobile Base Integration

To transition to mobile manipulation:

1. Replace fixed base with mobile chassis (differential drive)
2. Add navigation layer (path planning)
3. Coordinate base motion with arm control
4. Maintain same grasp planning pipeline

### ML Model Integration

To add learned models:

1. Train YOLOv8/YOLONAS for object detection
2. Save model to `ml_models/`
3. Update `ml.object_detection.model` in config
4. Implement `_yolo_detection()` in `object_detector.py`

For learned grasping:

1. Train DexNet or GR-ConvNet model
2. Update `ml.grasp_planning.method` to `dexnet`
3. Implement `_dexnet_grasp()` in `grasp_planner.py`

## Logging and Analysis

All runs generate logs in `logs/`:

- **Images**: `scan_YYYYMMDD_HHMMSS.png` - Vision sensor frames with detections
- **Task logs**: `task_log_YYYYMMDD_HHMMSS.json` - Complete task execution data

Example log entry:
```json
{
  "iteration": 1,
  "object": {
    "label": "red_cube",
    "position": [0.2, 0.1, 0.05],
    "confidence": 0.9
  },
  "grasp": {
    "position": [0.2, 0.1, 0.07],
    "confidence": 0.85
  },
  "target_zone": "red_bin",
  "success": true
}
```

## Testing Individual Components

Test API connection:
```bash
python scripts/coppelia_api.py
```

Test vision pipeline:
```bash
python vision/object_detector.py
```

Test grasp planner:
```bash
python planning/grasp_planner.py
```

## Troubleshooting

### Connection Failed
- Ensure CoppeliaSim is running
- Check that ZMQ Remote API plugin is enabled
- Verify port 23000 is not blocked

### Objects Not Detected
- Check vision sensor position and orientation
- Verify objects are in camera FOV
- Adjust HSV color ranges in `object_detector.py`

### Robot Not Moving
- Confirm robot model is loaded
- Check joint handles are correct
- Verify IK targets are reachable

### Gripper Not Grasping
- Increase gripper closing time
- Check grasp pose is aligned with object
- Verify gripper force parameters

## Future Enhancements

- [ ] Implement YOLO-based object detection
- [ ] Add DexNet grasp planning model
- [ ] Integrate MoveIt2 for advanced planning
- [ ] Add collision avoidance
- [ ] Implement reinforcement learning for grasping
- [ ] Multi-robot coordination
- [ ] Real robot deployment pipeline (ROS2)

## Hardware Deployment

When transitioning to physical robot:

1. **ROS2 Bridge**: Replace `coppelia_api.py` with ROS2 publishers/subscribers
2. **Camera Driver**: Swap vision sensor with real camera (RealSense, Kinect)
3. **Joint Controller**: Use servo/motor controllers instead of sim commands
4. **Calibration**: Perform hand-eye calibration for camera-robot transform
5. **Safety**: Add collision detection and emergency stop

The same high-level logic in `main_controller.py`, `object_detector.py`, and `grasp_planner.py` can be reused with minimal modification.

## References

- Modern Robotics textbook: http://modernrobotics.org
- CoppeliaSim documentation: https://www.coppeliarobotics.com/helpFiles/
- Northwestern ME 449 course: https://hades.mech.northwestern.edu/

## License

This project follows the same license as the Modern Robotics code library.

## Contributors

Built as a foundation for autonomous robotics development with the Yahboom Pi 6-DOF arm and Raspberry Pi 5.
