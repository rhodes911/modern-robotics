# Quick Start Guide - CoppeliaSim Pick-and-Place Demo

## What You Have Now

✅ **Completed:**
- Scene builder with simulation-state guard (prevents object loss)
- Auto-save enabled (scene persists as `yahboom_arm_workspace.ttt`)
- Basic pick-and-place demo script
- Updated documentation

✅ **Working Features:**
- Desk with 6 colored cubes (2 red, 2 green, 2 blue)
- 3 sorting bins (color-coded)
- Physics simulation (objects stay on desk, no falling through)
- Programmatic scene generation

## Next Steps to Run Demo

### 1. Load UR5 Robot + Gripper (One-Time Setup)

In CoppeliaSim:

**Load Robot:**
1. Click **File → Load Model...**
2. Navigate to: `models/robots/non-mobile/universal_robots/`
3. Double-click **UR5.ttm**

**Load Gripper:**
1. Click **File → Load Model...**
2. Navigate to: `models/components/grippers/`
3. Double-click **RG2.ttm** or any gripper model

**Attach Gripper:**
1. In scene hierarchy, **drag RG2 onto UR5_connection**
2. Gripper becomes child of robot arm end effector
3. Test: move UR5, gripper should follow

**Why this matters:** Without a gripper, the robot can't grab objects!

### 2. (Optional) Add Vision Sensor

In CoppeliaSim:
1. Click **Add → Vision sensor → Vision sensor (perspective)**
2. Right-click in scene hierarchy → Rename to: **vision_sensor**
3. Set position: X=-0.5, Y=0.0, Z=0.6

### 3. Save Complete Scene

In CoppeliaSim:
- **File → Save Scene** (Ctrl+S)
- Overwrites `yahboom_arm_workspace.ttt`

### 4. Run Pick-and-Place Demo

```powershell
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/basic_pick_place.py
```

**Expected behavior:**
- Simulation starts automatically
- UR5 moves through 9-step sequence
- Picks up object → moves to bin → releases → returns home

## Available Scripts

```powershell
# Rebuild scene (must stop simulation first!)
python scripts/scene_builder.py

# Run basic pick-and-place demo
python scripts/basic_pick_place.py

# Run simple motion demo
python scripts/ur5_demo.py

# Monitor object positions during simulation (diagnostic)
python scripts/monitor_objects.py

# Analyze video frames (if you have keyframes extracted)
python scripts/analyze_frames.py <folder_path>
```

## Important Notes

⚠️ **Scene Building:**
- Always STOP simulation before running `scene_builder.py`
- Objects created during runtime won't persist after scene reset
- Script now checks and refuses to build if simulation is running

⚠️ **Gripper Control:**
- Demo attempts to control UR5 gripper (RG2)
- If gripper not loaded, motion continues without gripper control
- Check console for gripper warnings

⚠️ **Joint Positions:**
- Pre-defined positions in `basic_pick_place.py` may need tuning
- Adjust based on your desk/object layout
- See lines 60-75 in the script

## Troubleshooting

**Objects disappear when pressing Play:**
- You built scene while simulation was running
- Solution: Stop sim → rebuild → save scene

**"Could not find UR5 robot":**
- Load UR5 model manually (step 1 above)

**"Gripper control failed" or robot doesn't pick objects:**
- Load RG2 gripper and attach to UR5_connection
- Check scene hierarchy shows RG2 as child of UR5
- Without gripper, robot can move but not grasp
- Check scene hierarchy has joints named `UR5_joint1` through `UR5_joint6`

**Robot moves but doesn't pick objects:**
- Adjust pick/place positions in `basic_pick_place.py`
- Objects may be outside robot's reach
- Check gripper is loaded and functional

**Connection failed (port error):**
- Verify CoppeliaSim is running
- Check ZMQ Remote API port in console (should be 23002)
- Update `sim_config.yaml` if port differs

## File Locations

- **Scene file:** `simulation_project/scenes/yahboom_arm_workspace.ttt`
- **Config:** `simulation_project/config/sim_config.yaml`
- **Scripts:** `simulation_project/scripts/`
- **Logs:** `simulation_project/logs/`

## Next Development Steps

After demo works:
1. Integrate vision-based object detection
2. Connect grasp planner for automatic grasp pose generation
3. Implement color-based sorting logic
4. Add trajectory optimization using Modern Robotics library
5. Enable full autonomous pick-and-place loop

See `simulation_project/COMPLETE_SETUP.md` for detailed setup instructions.
