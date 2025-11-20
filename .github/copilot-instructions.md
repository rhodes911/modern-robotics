# CoppeliaSim Development Instructions for GitHub Copilot

## Local Documentation References

**CRITICAL:** Always consult the local CoppeliaSim manual before implementing any joint, signal, or script control logic.

### Manual Location
- **Base Path:** `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\`
- **Entry Point:** `index.html`
- **English Docs:** `manual\en\`

### Required Reading Before Implementation

When working with **joints**, reference:
- `manual\en\joints.htm` - Joint fundamentals and types
- `manual\en\jointModes.htm` - **CRITICAL**: Explains modes 0-5, passive vs kinematic vs dependent
- `manual\en\jointDynamicsProperties.htm` - Force, velocity, position control
- `manual\en\regularApi\simGetJointMode.htm` - How to query current mode
- `manual\en\regularApi\simSetJointMode.htm` - How to change mode
- `manual\en\regularApi\simSetJointTargetPosition.htm` - Position control
- `manual\en\regularApi\simGetJointInterval.htm` - Get joint limits

When working with **signals** (for scripted models):
- `manual\en\regularApi\simSetInt32Signal.htm` - Integer command flags
- `manual\en\regularApi\simGetInt32Signal.htm` - Read signals
- `manual\en\regularApi\simClearInt32Signal.htm` - Clear signals
- `manual\en\regularApi\simSetStringSignal.htm` - String commands

When working with **scripts and customization**:
- `manual\en\scripts.htm` - Script types overview
- `manual\en\customizationScripts.htm` - Model-attached scripts
- `manual\en\regularApi\simCallScriptFunction.htm` - Invoke script functions

When working with **object hierarchy and parenting**:
- `manual\en\accessingSceneObjects.htm` - Object paths and handles
- `manual\en\regularApi\simGetObject.htm` - Get by path
- `manual\en\regularApi\simSetObjectParent.htm` - Attach objects
- `manual\en\regularApi\simGetObjectChild.htm` - Tree traversal

### Engineering Protocol for Gripper Control

1. **Discovery Phase:**
   ```python
   # Query joint mode FIRST - never assume controllability
   mode = sim.getJointMode(joint_handle)
   # mode[0]: 0=force/torque, 1=IK, 2=dependent, 3=motion, 5=passive
   ```

2. **RG2 Gripper (Direct Joint Control):**
   - Control joint: `/RG2/openCloseJoint` (search for 'openclose' in alias)
   - Mode: Must be 0 (kinematic) with motor enabled
   - Range: Query via `simGetJointInterval` - typically `[-0.048, 0.1018]`
   - Safe operation: Use 95% of range (avoid hard limits)
   - Reference: `manual\en\regularApi\simSetJointTargetPosition.htm`

3. **ROBOTIQ 85 / Script-Driven Grippers:**
   - Finger joints (`Ljoint1`, `Rjoint1`) are **passive (mode 5)** - DO NOT force control
   - Check for internal script: Look for `/ROBOTIQ85/Script` object
   - Two options:
     a) Use integer signals if documented (test `ROBOTIQ85_open`, `ROBOTIQ85_close`)
     b) Call script functions via `simCallScriptFunction` if exposed
   - Reference: `manual\en\customizationScripts.htm`

4. **Always Verify Before Sim Start:**
   ```python
   # Set initial state while simulation STOPPED
   sim.setJointTargetPosition(joint, initial_pos)
   # Then start simulation
   sim.startSimulation()
   ```

### Model Paths Reference

**Base Directory:** `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\`

---

## Robot Arms (Non-Mobile)

### Universal Robots Series
```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\UR3.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\UR5.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\UR10.ttm
```

### Other Popular Arms
```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\FrankaEmikaPanda.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\ABB IRB 140.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\KUKA LBR iiwa 7 R800.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\KUKA LBR iiwa 14 R820.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\Baxter.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\Sawyer.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\ABB YuMi.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\Jaco arm.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\non-mobile\7 DoF manipulator.ttm
```

---

## Grippers & End Effectors

### Parallel Jaw Grippers
```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\RG2.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\ROBOTIQ 85.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Baxter gripper.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Franka gripper.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\ABB YuMi gripper.ttm
```

### Multi-Finger Hands
```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Barrett Hand.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Barrett Hand (simplified).ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Jaco hand.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Mico hand.ttm
```

### Vacuum & Specialized
```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\suction pad.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\Baxter vacuum cup.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\P-Grip-straight.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\P-Grip-right-angle.ttm
```

---

## Vision Sensors

```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\kinect.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\Mesa SR4000.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\Blob detection camera.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\spherical vision sensor RGB.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\spherical vision sensor depth.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\anaglyph stereo sensor.ttm
```

---

## Laser Scanners & LiDAR

```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\2D laser scanner.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\3D laser scanner.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\3D laser scanner Fast.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\Hokuyo URG 04LX UG01.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\Hokuyo URG 04LX UG01_Fast.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\SICK TiM310 Fast.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\velodyne VPL-16.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\sensors\velodyne HDL-64E S2.ttm
```

---

## Mobile Robots

```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\KUKA YouBot.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\pioneer p3dx.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\NAO.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\Quadcopter.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\e-puck.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\Kilobot.ttm
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\robots\mobile\hexapod.ttm
```

---

## Usage in Python Code

### Loading Models Programmatically

**Note:** `sim.loadModel()` requires paths relative to the CoppeliaSim installation directory.

```python
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Load UR5 robot
ur5 = sim.loadModel('models/robots/non-mobile/UR5.ttm')

# Load RG2 gripper
gripper = sim.loadModel('models/components/grippers/RG2.ttm')

# Attach gripper to robot end effector
connection = sim.getObject('/UR5/connection')
sim.setObjectParent(gripper, connection, True)
```

### Common Object Names After Loading

**UR5 Robot:**
- Base: `/UR5`
- Joints: `/UR5_joint1` through `/UR5_joint6` (note the underscore, not slash)
- Alternative: `/:UR5_joint1` through `/:UR5_joint6`
- End effector connection: `/UR5_connection` or `/UR5/connection`
- Tip: `/UR5_tip` or `/UR5/tip`

**RG2 Gripper:**
- Base: `/RG2`
- Control joint: `/RG2/RG2_openCloseJoint`
- Open value: `0.085` (8.5 cm)
- Closed value: `0.0`

**Franka Panda:**
- Base: `/Panda`
- Joints: `/Panda/joint1` through `/Panda/joint7`
- Gripper fingers: `/Panda/finger_joint1`, `/Panda/finger_joint2`

---

## Key Reminders for Copilot

1. **Always use forward slashes** in model paths, even on Windows
2. **Relative paths** are relative to CoppeliaSim installation directory
3. **Gripper attachment:** Use `sim.setObjectParent(gripper_handle, connection_handle, True)`
4. **Simulation state check:** Always verify `sim.getSimulationState() == sim.simulation_stopped` before building scenes
5. **Object naming:** Use `sim.setObjectAlias(handle, "name")` for easy reference
6. **Physics properties:**
   - Static: `sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)`
   - Respondable: `sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1)`
   - Mass: `sim.setShapeMass(handle, mass_in_kg)`

---

## Directory Structure Summary

```
C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\
├── robots\
│   ├── mobile\          (wheeled robots, drones, legged)
│   └── non-mobile\      (robot arms, manipulators)
├── components\
│   ├── grippers\        (end effectors)
│   ├── sensors\         (cameras, lidars, IMUs)
│   └── locomotion and propulsion\  (wheels, casters)
└── equipment\           (generic objects, furniture)
```

---

## Troubleshooting

**"File does not exist" error:**
- Verify CoppeliaSim is installed at: `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\`
- Check path uses forward slashes: `/` not `\`
- Ensure path is relative to CoppeliaSim root, not absolute
- Example: `models/robots/non-mobile/UR5.ttm` (no leading slash)

**Cannot find object after loading:**
- Use `sim.getObjectsInTree(sim.handle_scene)` to list all objects
- Check object was renamed during import
- Try searching by partial name or type

**Gripper won't attach:**
- Verify parent object exists (e.g., `/UR5/connection`)
- Use `sim.setObjectParent(child, parent, True)` with `True` for keeping position
- Check gripper and robot are both loaded before attachment

---

*Generated: November 19, 2025*
*CoppeliaSim EDU v4.10.0*
