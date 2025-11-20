# CoppeliaSim Robotic Arm Simulation - Complete Setup Guide

## Step-by-Step Instructions

Follow these steps **in order** to set up your complete robotic arm simulation.

---

## Step 1: Make Sure CoppeliaSim is Running

1. Close CoppeliaSim completely if it's open
2. Launch fresh: `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\coppeliaSim.exe`
3. Wait for it to fully load (you'll see an empty scene)

---

## Step 2: Build the Base Scene (Desk, Objects, Bins)

Open PowerShell and run:

```powershell
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/scene_builder.py
```

**What this creates:**
- ✅ Brown desk (1.04m × 0.43m)
- ✅ 6 colored cubes (2 red, 2 green, 2 blue)
- ✅ 3 sorting bins (red, green, blue on the right)

**You should see output ending with:**
```
✓ Scene built successfully!
  - Desk: 1.04m × 0.43m
  - Robot: UR5
  - Objects: 10 spawned
  - Sorting zones: 3
```

---

## Step 3: Load the UR5 Robot Arm

**In CoppeliaSim window:**

1. Click **File → Load Model...** (or press Ctrl+O)
2. Navigate to the CoppeliaSim installation folder, then:
   - `models/robots/non-mobile/universal_robots/`
3. Double-click **UR5.ttm**
4. The robot should appear in the scene

**Verify:** You should see the UR5 robot arm standing upright.

---

## Step 4: Add the Gripper (RG2)

**The UR5 needs a gripper to pick things up!**

**In CoppeliaSim:**

1. Click **File → Load Model...**
2. Navigate to: `models/components/grippers/`
3. Look for **RG2.ttm** or similar gripper model
4. Double-click to load it

**Attach gripper to UR5:**

1. In the scene hierarchy (left panel), find **RG2** (the gripper you just loaded)
2. **Drag and drop** the RG2 onto **UR5_connection** (the end of the robot arm)
   - This makes RG2 a child of the UR5's end effector
3. The gripper should now move with the robot arm

**Verify:** Select the UR5 and move it - the gripper should move with it.

**Note:** If you can't find RG2.ttm, browse other grippers in:
- `models/components/grippers/` (various gripper types)
- Or create a simple proximity sensor + dummy setup

---

## Step 5: Position the Robot on the Desk

**In CoppeliaSim:**

1. Click on the **UR5** object in the scene hierarchy (left panel)
2. Look for the object properties (usually shows position/orientation)
3. Set the position to:
   - **X: -0.45**
   - **Y: 0.0**
   - **Z: 0.08**

## Step 5: Position the Robot on the Desk

**In CoppeliaSim:**

1. Click on the **UR5** object in the scene hierarchy (left panel)
2. Look for the object properties (usually shows position/orientation)
3. Set the position to:
   - **X: -0.45**
   - **Y: 0.0**
   - **Z: 0.08**

**OR** you can just leave it where it loads - the important thing is it's near the desk.

---

## Step 6: Test the Scene (Let Objects Settle)

**In CoppeliaSim:**

1. Click the **Play button** ▶ (top toolbar)
2. Watch the 6 cubes **fall and land on the desk**
3. They should settle and stay on the desk (not disappear!)
4. Click **Stop button** ⏹ after a few seconds

## Step 6: Test the Scene (Let Objects Settle)

**In CoppeliaSim:**

1. Click the **Play button** ▶ (top toolbar)
2. Watch the 6 cubes **fall and land on the desk**
3. They should settle and stay on the desk (not disappear!)
4. Click **Stop button** ⏹ after a few seconds

**Expected result:** 6 colored cubes sitting nicely on the brown desk, 3 colored bins on the right.

---

## Step 7: Add Vision Sensor (Optional - for future vision-based control)

**In CoppeliaSim:**

1. Click **Add → Vision sensor → Vision sensor (perspective)**
2. A new vision sensor appears in the scene
3. **Rename it** in the scene hierarchy (left panel):
   - Right-click the vision sensor → **Rename**
   - Set name to: **vision_sensor**
4. **Position the sensor** (looking down at the desk):
   - Select the vision sensor
   - Set position:
     - **X: -0.5**
     - **Y: 0.0**
     - **Z: 0.6** (60cm above desk)
5. **Orient the sensor** (point it at the desk):
   - Set orientation angles to aim downward at approximately [0, 0, 0.05]
   - You can use the rotation tool or manually adjust until camera view shows the desk area

## Step 7: Add Vision Sensor (Optional - for future vision-based control)

**In CoppeliaSim:**

1. Click **Add → Vision sensor → Vision sensor (perspective)**
2. A new vision sensor appears in the scene
3. **Rename it** in the scene hierarchy (left panel):
   - Right-click the vision sensor → **Rename**
   - Set name to: **vision_sensor**
4. **Position the sensor** (looking down at the desk):
   - Select the vision sensor
   - Set position:
     - **X: -0.5**
     - **Y: 0.0**
     - **Z: 0.6** (60cm above desk)
5. **Orient the sensor** (point it at the desk):
   - Set orientation angles to aim downward at approximately [0, 0, 0.05]
   - You can use the rotation tool or manually adjust until camera view shows the desk area

**Verify:** Double-click the vision sensor to see its camera view - you should see the desk and objects from above.

---

## Step 8: Save Your Scene (Important!)

**In CoppeliaSim:**

1. Click **File → Save Scene** (or Ctrl+S)
2. Save as: `yahboom_workspace.ttt`
3. Choose location: `C:\Users\rhode\Repos\modern-robotics\simulation_project\scenes\`

## Step 8: Save Your Scene (Important!)

**In CoppeliaSim:**

1. Click **File → Save Scene** (or Ctrl+S)
2. Save as: `yahboom_workspace.ttt`
3. Choose location: `C:\Users\rhode\Repos\modern-robotics\simulation_project\scenes\`

Now you can reload this scene anytime!

---

## Step 9: Run the Basic Pick-and-Place Demo

**In PowerShell:**

```powershell
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/basic_pick_place.py
```

**What happens:**
- Simulation starts (if not already running)
- UR5 arm executes a complete pick-and-place sequence:
  1. Home position (upright)
  2. Move to pre-pick position
  3. Move down to pick an object
  4. Close gripper
  5. Lift object
  6. Move to sorting bin
  7. Lower and release object
  8. Return home

## Step 9: Run the Basic Pick-and-Place Demo

**In PowerShell:**

```powershell
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/basic_pick_place.py
```

**What happens:**
- Simulation starts (if not already running)
- UR5 arm executes a complete pick-and-place sequence:
  1. Home position (upright)
  2. Move to pre-pick position
  3. Move down to pick an object
  4. Close gripper
  5. Lift object
  6. Move to sorting bin
  7. Lower and release object
  8. Return home

**Watch the robot perform autonomous pick-and-place!** 🤖

---

## Step 10: (Optional) Run the UR5 Motion Demo

**In PowerShell:**

```powershell
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/ur5_demo.py
```

**What happens:**
- Simple motion sequence showing the robot moving through predefined positions
- Good for testing robot connectivity and joint control

---

## Troubleshooting

### Objects disappear when I press Play
- Stop the simulation
- Run `python scripts/scene_builder.py` again
- Reload the UR5 robot
- Make sure you see the cubes **fall and land** on the desk

### Robot doesn't move
- Make sure the simulation is running (Play button pressed)
- Check that the script found the UR5 joints (look at terminal output)
- Try closing CoppeliaSim and starting from Step 1

### Can't find UR5.ttm file
- Look in: `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\universal_robots\`
- Alternative: Use **Panda.ttm** from `franka_emika` folder

### Connection failed
- Make sure CoppeliaSim is actually running
- Check the terminal doesn't show any error messages
- Try closing and reopening CoppeliaSim

---

## What You Have Now

✅ Complete robotic workspace simulation  
✅ UR5 arm positioned on desk  
✅ 6 objects to pick and place  
✅ 3 sorting bins for color-coded placement  
✅ Working demo that makes the arm move  

---

## Next Steps (Optional)

Once the basic demo works, you can:

1. **Run the full autonomous system** (when vision is set up):
   ```powershell
   python scripts/main_controller.py
   ```

2. **Test vision processing**:
   ```powershell
   python vision/object_detector.py
   ```

3. **Analyze arm extensions**:
   ```powershell
   python scripts/arm_extension_experiment.py
   ```

---

## Quick Reference Commands

```powershell
# Build scene
cd C:\Users\rhode\Repos\modern-robotics\simulation_project
python scripts/scene_builder.py

# Run UR5 demo
python scripts/ur5_demo.py

# Test vision
python vision/object_detector.py

# Full autonomous system
python scripts/main_controller.py
```

---

## Success Checklist

- [ ] CoppeliaSim is running
- [ ] Scene built (desk, cubes, bins visible)
- [ ] UR5 robot loaded and positioned
- [ ] Cubes fall and stay on desk when Play is pressed
- [ ] Scene saved as .ttt file
- [ ] UR5 demo makes the arm move

**Once all checked ✓ you're ready to develop autonomous pick-and-place!** 🎉
