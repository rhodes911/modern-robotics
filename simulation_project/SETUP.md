# CoppeliaSim Robotic Arm Simulation - Setup Guide

## Installation Steps

### 1. Install CoppeliaSim

**Windows:**
```powershell
# Download installer
Invoke-WebRequest -Uri "https://downloads.coppeliarobotics.com/V4_10_0_rev0/CoppeliaSim_Edu_V4_10_0_rev0_Setup.exe" -OutFile "CoppeliaSim_Setup.exe"

# Run installer
.\CoppeliaSim_Setup.exe

# Default install location: C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\
```

**Linux:**
```bash
# Download and extract
wget https://downloads.coppeliarobotics.com/V4_10_0_rev0/CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz
tar xvf CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04.tar.xz

# Run
cd CoppeliaSim_Edu_V4_10_0_rev0_Ubuntu22_04
./coppeliaSim.sh
```

**macOS:**
```bash
# Download and extract
# Then run: open coppeliaSim.app

# If app crashes on startup:
sudo xattr -r -d com.apple.quarantine coppeliaSim.app
```

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd simulation_project

# Install requirements
pip install -r requirements.txt

# Install Modern Robotics library
cd ../packages/Python
pip install -e .
cd ../../simulation_project
```

### 3. Verify Installation

Test CoppeliaSim connection:
```bash
# Make sure CoppeliaSim is running first!
python scripts/coppelia_api.py
```

Expected output:
```
Connecting to CoppeliaSim at 127.0.0.1:23000...
✓ Connected to CoppeliaSim

Connection test successful!
Simulation time: 0.00s
✓ Disconnected
```

### 4. Load Robot Model in CoppeliaSim

1. Launch CoppeliaSim
2. File → Load Model...
3. Navigate to: `CoppeliaSim/models/robots/`
4. Select one of:
   - `universal_robots/UR5.ttm` (recommended)
   - `franka_emika/panda.ttm`
5. Position robot at: `(-0.45, 0.0, 0.08)` using object properties panel

### 5. Build the Scene

```bash
python scripts/scene_builder.py
```

This creates:
- Desk surface (1.04m × 0.43m)
- Random objects (cubes, cylinders, spheres)
- Color-coded sorting bins
- Vision sensor (overhead camera)

### 6. Run Your First Simulation

```bash
python scripts/main_controller.py
```

Watch the robot:
1. Scan workspace with vision
2. Detect colored objects
3. Plan grasp poses
4. Pick and place into correct bins

## Configuration

Edit `config/sim_config.yaml` to customize:

```yaml
desk:
  length: 1.04  # Match your real desk
  depth: 0.43

robot:
  model: "UR5"  # or "Panda"
  base_position: [-0.45, 0.0, 0.08]

objects:
  count: 15  # Number of objects to spawn
```

## Troubleshooting

### "Failed to connect to CoppeliaSim"
**Solution:** 
- Ensure CoppeliaSim is running
- Check that ZMQ Remote API is enabled (it is by default in EDU version)
- Try restarting CoppeliaSim

### "Vision sensor not found"
**Solution:**
- Run `scene_builder.py` first to create the sensor
- Or manually add a vision sensor in CoppeliaSim UI

### "No objects detected"
**Solution:**
- Check camera position/orientation in `sim_config.yaml`
- Verify objects are spawned on desk
- Adjust HSV color ranges in `vision/object_detector.py`

### Import errors for cv2, yaml, etc.
**Solution:**
```bash
pip install opencv-python pyyaml numpy
```

### Modern Robotics import error
**Solution:**
```bash
cd packages/Python
pip install -e .
```

## Next Steps

Once basic simulation is working:

1. **Tune vision parameters** - Adjust color detection thresholds
2. **Experiment with grasp planning** - Try different approaches for different shapes
3. **Test arm extensions** - Run `arm_extension_experiment.py`
4. **Add ML models** - Integrate YOLO for detection or DexNet for grasping
5. **Connect real robot** - Replace `coppelia_api.py` with ROS2 interface

## Getting Help

- CoppeliaSim Forum: https://forum.coppeliarobotics.com/
- Modern Robotics: http://modernrobotics.org
- Project documentation: See `README.md`

Happy simulating! 🤖
