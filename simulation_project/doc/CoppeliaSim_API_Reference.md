# CoppeliaSim Remote API Engineering Reference (Focused Subset)

This document distills the core portions of the CoppeliaSim manual relevant to programmatic scene construction and precise mechanism control via the ZeroMQ Remote API (Python `coppeliasim_zmqremoteapi_client`). It is intentionally scoped to functions we are using or will need. For full details consult the official offline manual included with the CoppeliaSim installation.

**Manual Location (Local Installation):**
- Path: `C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\manual\`
- Entry: `index.html` (open in browser)
- English docs: `manual\en\`
- Key files found:
  - `manual\en\joints.htm` - Joint fundamentals
  - `manual\en\jointModes.htm` - Joint control modes explained
  - `manual\en\scripts.htm` - Scripting overview
  - `manual\en\zmqRemoteApiOverview.htm` - ZeroMQ Remote API
  - `manual\en\regularApi\simSetJointTargetPosition.htm` - Function reference
  - `manual\en\regularApi\simGetJointMode.htm` - Mode query
  - `manual\en\regularApi\simSetInt32Signal.htm` - Signal control
  - `manual\en\regularApi\simCallScriptFunction.htm` - Script invocation

Base install (EDU): `C:/Program Files/CoppeliaRobotics/CoppeliaSimEdu/`
Models root (relative paths when calling `sim.loadModel`): `models/...`

---
## 1. Simulation Lifecycle

| Purpose | API | Notes |
|---------|-----|-------|
| Start physics & scripts | `sim.startSimulation()` | Non-blocking. Child/customization scripts begin executing. |
| Stop simulation | `sim.stopSimulation()` | Asynchronous; poll `sim.getSimulationState()` until `sim.simulation_stopped`. |
| State query | `sim.getSimulationState()` | Returns enumerated state (stopped, paused, running). Only build/attach objects while stopped for repeatability. |

Best practice: Always ensure the simulation is stopped before loading models, parenting, or setting initial joint positions. Race conditions appear if joint targets are changed during the first physics step.

---
## 2. Object & Model Handling

| Task | API | Key Points |
|------|-----|------------|
| Load a model | `sim.loadModel(relPath)` | Path must be **relative** to installation root. Returns handle of model base. |
| Retrieve object by path | `sim.getObject('/Alias/child')` | Uses object aliases; forward slashes only. |
| Get object's type | `sim.getObjectType(handle)` | Distinguish shape vs joint vs dummy. |
| Iterate tree | `sim.getObjectChild(parent, index)` | Returns `-1` when out of bounds. |
| Set parent | `sim.setObjectParent(child, parent, keepInPlace=True)` | Use world-align first if necessary. Parenting during simulation can introduce physics impulses—prefer stopped state. |
| Set/get pose | `sim.setObjectPosition(handle,-1,[x,y,z])` / `sim.getObjectPosition(handle,-1)` | Frame `-1` = world. Similarly for `Orientation`. |
| Alias assignment | `sim.setObjectAlias(handle,'name')` | Shortens future lookups. |

Attachment recipe (RG2 to UR5): 1) Get connection dummy `/UR5/connection`. 2) Get gripper attach dummy `/RG2/attachPoint`. 3) Read world pose of connection; apply to gripper; 4) Parent gripper base to connection.

---
## 3. Joint Fundamentals

### Joint Types
- Revolute (type 10) – angular position
- Prismatic (type 11) – linear position
- Passive joints: no motor influence unless switched mode.

### Joint Modes (first element of tuple from `sim.getJointMode(joint)`)
| Mode Code | Meaning | Typical Control APIs |
|-----------|---------|----------------------|
| 0 | Force/torque (motor/kinematic) | `sim.setJointTargetPosition`, `sim.setJointTargetVelocity`, `sim.setJointTargetForce` |
| 1 | Inverse kinematics | Controlled by IK groups (not used here) |
| 2 | Dependent | Follows another joint via dependency relation (script/internal) |
| 3 | Motion mode | Time-based trajectories inside CoppeliaSim (rare in remote-only control) |
| 5 | Passive | Read-only unless reconfigured |

For remote deterministic control, convert passive joints to kinematic: `sim.setJointMode(joint, sim.jointmode_kinematic, 0)` then enable motor: `sim.setObjectInt32Param(joint, sim.jointintparam_motor_enabled, 1)`.

### Core Joint APIs
| API | Purpose | Notes |
|-----|---------|-------|
| `sim.getJointPosition(j)` | Current (actual) position | Use for verification; may lag target under dynamics. |
| `sim.setJointTargetPosition(j, pos)` | Set desired position (kinematic or PID motor) | Requires appropriate mode. |
| `sim.setJointTargetVelocity(j, vel)` | Set desired velocity | Use for opening/closing with dynamic grippers. |
| `sim.setJointTargetForce(j, force)` | Limit applied force/torque | Avoid chatter by capping force on delicate mechanisms. |
| `sim.getJointInterval(j)` | Returns `(cyclic,[min,max])` | Use to compute normalized range and prevent overshoot. |
| `sim.getJointMode(j)` / `sim.setJointMode(j, mode, dependencyHandle)` | Read/change mode | Changing while running can produce discontinuities—apply when stopped. |

### Engineering Guidance
1. Always log joint mode before attempting control. If it is 5 (passive) or 2 (dependent), commands will appear ignored.
2. For multi-finger grippers (e.g., ROBOTIQ 85), visible finger joints may be passive, driven internally by hidden active joints or script—reconfiguring them directly can yield unrealistic motion. Prefer documented control interface (signals or exposed active joint) rather than force-changing modes of passive joints.
3. Use conservative velocity & force limits when first asserting control to avoid instability.

---
## 4. Signals & Script Interaction

Signals provide a lightweight global communication channel:
| API | Use |
|-----|-----|
| `sim.setInt32Signal(name, value)` | Set integer flag (e.g., command trigger) |
| `sim.getInt32Signal(name)` | Read flag; returns value or `None` if absent |
| `sim.clearInt32Signal(name)` | Remove signal from table |
| `sim.setStringSignal(name, str)` | Send string command (e.g., 'open','close') |
| `sim.getStringSignal(name)` | Read string |

`sim.callScriptFunction(functionName, scriptHandle, args...)` invokes a function defined in a customization or child script attached to an object. This requires that function to be explicitly declared in that script.

If a model offers a UI (e.g., ROBOTIQ 85) the open/close buttons often set internal signals or directly drive hidden joints via its script.

### Discovery Procedure
1. Enumerate all joints -> capture modes.
2. Attempt gentle target adjustments only on mode 0/3 joints.
3. If fingers remain static: record signals before and after manual UI button press (poll `getInt32Signal` names). If unchanged, the script may bypass public signals; you may need to expose new script functions manually (editing the model inside CoppeliaSim). Remote API alone cannot change internal script logic.

---
## 5. Scene Integrity & Determinism

Checklist before simulation start:
- Simulation state is `sim.simulation_stopped`.
- All models loaded & attached (final transforms confirmed).
- All controllable joints have correct mode (kinematic for deterministic path execution).
- Initial joint targets set (avoid immediate jump on first physics frame).
- Signals cleared to avoid stale commands.

Stop sequence: send final open gripper command (if gripping) -> small delay -> `sim.stopSimulation()` -> poll until stopped.

---
## 6. Gripper Control Patterns

### RG2 (Parallel Jaw)
- Control Joint: `openCloseJoint` (found via alias search containing `openclose`).
- Range (from observed intervals): approx `[-0.048, 0.1018]` (depends on model version). Practical mapping may differ from nominal 0.0–0.085 spec. Always query interval and clamp.
- Recommended: OPEN = near upper bound; CLOSED = near lower bound; avoid driving exactly to extremes—use 95% of range to reduce chatter.

Example:
```python
low, high = sim.getJointInterval(rg2_joint)[1]
open_pos = high - 0.005
closed_pos = low + 0.002
sim.setJointTargetPosition(rg2_joint, open_pos)
```

### ROBOTIQ 85
- Visible finger joints (`Ljoint1`, `Rjoint1`) passive (mode 5) by default; direct control yields inconsistent state.
- Two active revolute joints (`LactiveJoint`, `RactiveJoint`) may not propagate finger motion meaningfully (internal linkages & script constraints).
- Provided UI indicates internal script logic. Without documented remote interface (signals or script functions), precise remote-only control is limited.
- Engineering options:
  1. Open model in CoppeliaSim, inspect attached script, expose `open()` / `close()` functions, then call via `sim.callScriptFunction`.
  2. Replace with RG2 or Panda gripper for straightforward jaw position control if remote determinism is priority.

---
## 7. Robust Joint Discovery Utility (Pattern)
```python
def enumerate_joints(sim, root):
    results = []
    def walk(h):
        t = sim.getObjectType(h)
        if t == sim.object_joint_type:
            mode = sim.getJointMode(h)[0]
            results.append({
                'handle': h,
                'alias': sim.getObjectAlias(h),
                'mode': mode,
                'interval': sim.getJointInterval(h)[1],
            })
        idx = 0
        while True:
            child = sim.getObjectChild(h, idx)
            if child == -1: break
            walk(child)
            idx += 1
    walk(root)
    return results
```

---
## 8. Error & Instability Mitigation
| Symptom | Likely Cause | Mitigation |
|---------|--------------|-----------|
| Joint target ignored | Passive/dependent mode | Set kinematic mode & enable motor (if appropriate). |
| Gripper vibrates near limit | Overshoot & high force | Lower target force via `sim.setJointTargetForce`, avoid extreme bound. |
| Object falls through gripper | Collision masks or respondable flags absent | Ensure `sim.shapeintparam_respondable = 1` and proper dynamic shape. |
| Gripper snaps closed at sim start | Initial target not set before `startSimulation()` | Set position while stopped. |
| No response from UI-driven gripper | Internal script private | Expose script API or use different model. |

---
## 9. Recommended Control Abstractions
Wrap gripper operations:
```python
class RG2Controller:
    def __init__(self, sim, rg2_handle):
        self.sim = sim
        self.joint = find_rg2_joint(sim, rg2_handle)
        low, high = sim.getJointInterval(self.joint)[1]
        self.open_pos = high - 0.005
        self.closed_pos = low + 0.002
        sim.setJointMode(self.joint, sim.jointmode_kinematic, 0)
        sim.setObjectInt32Param(self.joint, sim.jointintparam_motor_enabled, 1)
        sim.setJointTargetPosition(self.joint, self.open_pos)
    def open(self):
        self.sim.setJointTargetPosition(self.joint, self.open_pos)
    def close(self):
        self.sim.setJointTargetPosition(self.joint, self.closed_pos)
```

---
## 10. Next Expansion Areas
- Script inspection & modification pipeline (expose functions of ROBOTIQ 85 script).
- Collision mask tuning for reliable grasp (enable respondable on fingertips; set correct friction).
- Trajectory planning integration: compute approach pose using forward kinematics then apply gripper close with delay.

---
## 11. Reference Function Mapping (Quick Lookup)
| Intent | Function(s) |
|--------|-------------|
| Load UR5 | `sim.loadModel('models/robots/non-mobile/UR5.ttm')` |
| Load RG2 | `sim.loadModel('models/components/grippers/RG2.ttm')` |
| Attach | `sim.setObjectParent(gripper, connection, True)` |
| Find connection | `sim.getObject('/UR5/connection')` |
| Find RG2 control joint | Walk children & match alias containing `openclose` |
| Start/Stop | `sim.startSimulation()` / `sim.stopSimulation()` |
| Set joint target | `sim.setJointTargetPosition(joint, value)` |
| Force limit | `sim.setJointTargetForce(joint, force)` |
| Read actual | `sim.getJointPosition(joint)` |
| Signals | `sim.setInt32Signal`, `sim.getInt32Signal`, `sim.clearInt32Signal` |

---
## 12. Verification Script Sketch
```python
# Run after scene build, before simulation start
for j in enumerate_joints(sim, ur5_handle):
    print(f"Joint {j['alias']}: mode={j['mode']} interval={j['interval']}")
# Assert expected control modes
assert all(j['mode'] in (0,5) for j in enumerate_joints(sim, ur5_handle)), "Unexpected joint mode"
```

---
**Disclaimer:** This reference summarizes essential operational semantics and best practices; it does not reproduce proprietary manual content verbatim. Always defer to the official manual for exhaustive descriptions and edge cases.
