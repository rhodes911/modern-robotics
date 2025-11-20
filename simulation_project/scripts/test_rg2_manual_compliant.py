"""
RG2 Gripper Control Test - Following CoppeliaSim Manual Specifications

References from C:/Program Files/CoppeliaRobotics/CoppeliaSimEdu/manual/:
- en/joints.htm - Joint fundamentals
- en/jointModes.htm - Control mode semantics
- en/regularApi/simGetJointMode.htm - Query mode
- en/regularApi/simSetJointMode.htm - Set to kinematic
- en/regularApi/simGetJointInterval.htm - Get safe limits
- en/regularApi/simSetJointTargetPosition.htm - Position control
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def main():
    print("=" * 70)
    print("RG2 Gripper Control - Manual-Compliant Implementation")
    print("=" * 70 + "\n")
    
    # Connect
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("✓ Connected to CoppeliaSim\n")
    
    # Close all open scenes
    print("Closing all open scenes...")
    try:
        sim.closeScene()
    except:
        pass
    print("✓ Scenes closed\n")
    
    # Ensure stopped
    if sim.getSimulationState() != sim.simulation_stopped:
        print("Stopping simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Load RG2 gripper
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    print("Loading RG2 gripper...")
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print(f"✓ RG2 loaded (handle: {gripper})\n")
    
    # Find control joint - search for 'openclose' in alias
    print("Finding control joint...")
    def find_openclose_joint(parent):
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(parent, idx)
                if child == -1:
                    break
                obj_type = sim.getObjectType(child)
                if obj_type == sim.object_joint_type:
                    alias = sim.getObjectAlias(child)
                    if 'openclose' in alias.lower():
                        return child
                result = find_openclose_joint(child)
                if result:
                    return result
                idx += 1
            except:
                break
        return None
    
    control_joint = find_openclose_joint(gripper)
    if not control_joint:
        print("✗ Could not find openCloseJoint")
        return
    
    joint_alias = sim.getObjectAlias(control_joint)
    print(f"✓ Found control joint: {joint_alias} (handle: {control_joint})\n")
    
    # Step 1: Query current mode (per manual: simGetJointMode.htm)
    print("Step 1: Querying joint mode...")
    mode_tuple = sim.getJointMode(control_joint)
    mode_code = mode_tuple[0]
    mode_names = {
        0: "Force/Torque (kinematic)",
        1: "Inverse Kinematics",
        2: "Dependent",
        3: "Motion Mode",
        5: "Passive"
    }
    print(f"  Current mode: {mode_code} = {mode_names.get(mode_code, 'Unknown')}")
    
    # Step 2: Get joint limits (per manual: simGetJointInterval.htm)
    print("\nStep 2: Querying joint limits...")
    cyclic, interval = sim.getJointInterval(control_joint)
    min_limit, max_limit = interval
    print(f"  Cyclic: {cyclic}")
    print(f"  Limits: [{min_limit:.6f}, {max_limit:.6f}]")
    
    # Calculate safe operating range (95% of limits per engineering best practice)
    range_span = max_limit - min_limit
    safety_margin = range_span * 0.05
    safe_open = max_limit - safety_margin
    safe_closed = min_limit + safety_margin
    print(f"  Safe OPEN position: {safe_open:.6f} ({safe_open*1000:.2f}mm)")
    print(f"  Safe CLOSED position: {safe_closed:.6f} ({safe_closed*1000:.2f}mm)")
    
    # Step 3: Set to kinematic mode if not already (per manual: simSetJointMode.htm)
    if mode_code != 0:
        print("\nStep 3: Setting joint to kinematic mode...")
        sim.setJointMode(control_joint, sim.jointmode_kinematic, 0)
        print("  ✓ Mode set to kinematic")
    else:
        print("\nStep 3: Joint already in kinematic mode ✓")
    
    # Step 4: Enable motor (per manual: joint control requires motor enabled)
    print("\nStep 4: Enabling motor...")
    sim.setObjectInt32Param(control_joint, sim.jointintparam_motor_enabled, 1)
    print("  ✓ Motor enabled")
    
    # Step 5: Set initial position BEFORE starting simulation
    print("\nStep 5: Setting initial OPEN position (while stopped)...")
    sim.setJointTargetPosition(control_joint, safe_open)
    current_pos = sim.getJointPosition(control_joint)
    print(f"  Target: {safe_open:.6f}")
    print(f"  Current: {current_pos:.6f}")
    print("  ✓ Initial position set\n")
    
    # Step 6: Start simulation
    print("Step 6: Starting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    print("  ✓ Simulation running\n")
    
    print("=" * 70)
    print("GRIPPER CONTROL TEST SEQUENCE")
    print("=" * 70 + "\n")
    
    # Test 1: Verify OPEN state
    print("Test 1: Gripper should be OPEN")
    time.sleep(1.0)
    pos = sim.getJointPosition(control_joint)
    print(f"  Position: {pos:.6f} (target: {safe_open:.6f})")
    print(f"  Gap: {pos*1000:.2f}mm")
    error = abs(pos - safe_open)
    if error < 0.005:
        print("  ✓ PASS - Gripper is open\n")
    else:
        print(f"  ⚠ WARNING - Error: {error:.6f}\n")
    
    # Test 2: Close gripper
    print("Test 2: CLOSING gripper...")
    sim.setJointTargetPosition(control_joint, safe_closed)
    print(f"  Target: {safe_closed:.6f}")
    time.sleep(2.0)
    pos = sim.getJointPosition(control_joint)
    print(f"  Position: {pos:.6f}")
    print(f"  Gap: {pos*1000:.2f}mm")
    error = abs(pos - safe_closed)
    if error < 0.005:
        print("  ✓ PASS - Gripper closed\n")
    else:
        print(f"  ⚠ WARNING - Error: {error:.6f}\n")
    
    # Test 3: Open gripper again
    print("Test 3: OPENING gripper...")
    sim.setJointTargetPosition(control_joint, safe_open)
    print(f"  Target: {safe_open:.6f}")
    time.sleep(2.0)
    pos = sim.getJointPosition(control_joint)
    print(f"  Position: {pos:.6f}")
    print(f"  Gap: {pos*1000:.2f}mm")
    error = abs(pos - safe_open)
    if error < 0.005:
        print("  ✓ PASS - Gripper opened\n")
    else:
        print(f"  ⚠ WARNING - Error: {error:.6f}\n")
    
    # Test 4: Partial close (50% grip)
    mid_position = (safe_open + safe_closed) / 2
    print("Test 4: PARTIAL grip (50%)...")
    sim.setJointTargetPosition(control_joint, mid_position)
    print(f"  Target: {mid_position:.6f}")
    time.sleep(2.0)
    pos = sim.getJointPosition(control_joint)
    print(f"  Position: {pos:.6f}")
    print(f"  Gap: {pos*1000:.2f}mm")
    error = abs(pos - mid_position)
    if error < 0.005:
        print("  ✓ PASS - Partial grip achieved\n")
    else:
        print(f"  ⚠ WARNING - Error: {error:.6f}\n")
    
    print("=" * 70)
    print("✓✓✓ GRIPPER CONTROL TEST COMPLETE ✓✓✓")
    print("=" * 70)
    print("\nObserve CoppeliaSim window - gripper should have moved smoothly")
    print("through all positions without vibration or instability.\n")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n\nStopping simulation...")
        sim.stopSimulation()
        print("Done!")

if __name__ == "__main__":
    main()
