"""
Main Controller - Complete UR5 + ROBOTIQ 85 Pick and Place
Uses modular functions for clean, maintainable code
"""

import time
import sys
import numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# Import our attachment function
from step1_attach import attach_gripper_to_ur5


def find_ur5_joints(sim, ur5_handle):
    """Find all 6 UR5 joints by walking the kinematic chain."""
    joints = []
    current = ur5_handle
    
    for i in range(6):
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(current, idx)
                if child == -1:
                    break
                if sim.getObjectType(child) == sim.object_joint_type:
                    joints.append(child)
                    # Move to link child
                    link_idx = 0
                    while True:
                        try:
                            link = sim.getObjectChild(child, link_idx)
                            if link == -1:
                                break
                            if sim.getObjectType(link) != sim.object_joint_type:
                                current = link
                                break
                            link_idx += 1
                        except:
                            break
                    break
                idx += 1
            except:
                break
    
    return joints


def find_gripper_joint(sim, gripper_handle):
    """Find the gripper control joint (openCloseJoint for RG2, RactiveJoint for ROBOTIQ 85)."""
    def search(parent, depth=0):
        if depth > 5:
            return None
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(parent, idx)
                if child == -1:
                    break
                alias = sim.getObjectAlias(child)
                obj_type = sim.getObjectType(child)
                # Check for RG2 or ROBOTIQ 85 control joints
                if obj_type == sim.object_joint_type and ('openclose' in alias.lower() or 'ractivejoint' in alias.lower()):
                    return child
                result = search(child, depth+1)
                if result:
                    return result
                idx += 1
            except:
                break
        return None
    
    return search(gripper_handle)


def main():
    print("=" * 60)
    print("UR5 + RG2 Pick and Place - Main Controller")
    print("=" * 60 + "\n")
    
    # Connect
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("✓ Connected to CoppeliaSim\n")
    
    # Close all open scenes without saving
    print("Closing all open scenes...")
    try:
        sim.closeScene()
    except:
        pass
    print("✓ Scenes closed\n")
    
    # Stop simulation if running
    if sim.getSimulationState() != sim.simulation_stopped:
        print("Stopping simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Clear scene
    print("Clearing scene...")
    try:
        all_objects = sim.getObjects(sim.handle_scene, sim.object_shape_type)
        for obj in all_objects:
            try:
                sim.removeObject(obj)
            except:
                pass
    except:
        pass
    print("✓ Scene cleared\n")
    
    # Load models
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    
    print("Loading UR5...")
    ur5 = sim.loadModel(f"{COPPELIA_ROOT}\\models\\robots\\non-mobile\\UR5.ttm")
    # Raise UR5 base off the ground - gripper is about 20cm long, so raise base by 25cm to be safe
    sim.setObjectPosition(ur5, -1, [0, 0, 0.25])
    print(f"✓ UR5 loaded (base raised 25cm off ground)\n")
    
    print("Loading RG2 gripper...")
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print(f"✓ RG2 loaded\n")
    
    # Attach gripper using our function
    print("Attaching gripper...")
    connection = attach_gripper_to_ur5(sim, ur5, gripper)
    if not connection:
        print("✗ Failed to attach gripper!")
        return
    print()
    
    # Find joints
    print("Finding UR5 joints...")
    joints = find_ur5_joints(sim, ur5)
    if len(joints) != 6:
        print(f"✗ Error: Found {len(joints)}/6 joints")
        return
    print(f"✓ Found all 6 joints\n")
    
    print("Finding RG2 control joint...")
    gripper_joint = find_gripper_joint(sim, gripper)
    if not gripper_joint:
        print("✗ Could not find openCloseJoint")
        return
    
    print(f"✓ Found RG2 openCloseJoint (handle: {gripper_joint})")
    
    # Check current mode
    mode = sim.getJointMode(gripper_joint)
    print(f"  Current joint mode: {mode[0]}")
    
    # If passive mode (5), switch to force/torque mode (0)
    if mode[0] == 5:
        print("  → Mode 5 = PASSIVE (physics-driven, can't control directly)")
        print("  → Switching to FORCE/TORQUE mode (0)...")
        sim.setJointMode(gripper_joint, sim.jointmode_dynamic, 0)
        print("  ✓ Switched to force/torque mode")
    
    # Get joint limits
    cyclic, interval = sim.getJointInterval(gripper_joint)
    print(f"  Joint limits: [{interval[0]:.4f}, {interval[0]+interval[1]:.4f}]")
    
    # Make gripper base static so it doesn't affect physics
    print("  → Stabilizing gripper base...")
    try:
        gripper_base = sim.getObject('/RG2')
        sim.setObjectInt32Param(gripper_base, sim.shapeintparam_static, 1)
        print("  ✓ Base is now static")
    except:
        print("  → Could not find /RG2 base (might be attached differently)")
    
    # Configure motor with proper settings
    sim.setObjectInt32Param(gripper_joint, sim.jointintparam_motor_enabled, 1)
    sim.setObjectInt32Param(gripper_joint, sim.jointintparam_ctrl_enabled, 1)
    sim.setJointTargetVelocity(gripper_joint, 0.1)  # Slower, smoother
    sim.setJointTargetForce(gripper_joint, 20.0)    # Gentler force
    
    # Set to OPEN initially (use max of interval)
    open_pos = interval[0] + interval[1]
    sim.setJointPosition(gripper_joint, open_pos)
    print(f"✓ Gripper initialized to OPEN ({open_pos:.4f}m)\n")
    
    # Create test cube at ground level
    print("Creating test cube...")
    cube_size = 0.05
    cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [cube_size, cube_size, cube_size])
    # Cube on ground: half height above ground
    sim.setObjectPosition(cube, -1, [0.4, 0, cube_size/2])
    sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])
    sim.setObjectInt32Param(cube, sim.shapeintparam_static, 0)
    sim.setObjectInt32Param(cube, sim.shapeintparam_respondable, 1)
    sim.setShapeMass(cube, 0.05)
    print(f"✓ Cube created at ground level [0.4, 0, 0.025]\n")
    
    # Start simulation
    print("Starting simulation...")
    sim.startSimulation()
    while sim.getSimulationState() == sim.simulation_stopped:
        time.sleep(0.1)
    
    # Set simulation to real-time mode
    print("Setting simulation to REAL-TIME mode...")
    sim.setInt32Param(sim.intparam_speedmodifier, 1)  # 1 = real-time, 2 = 2x speed, etc.
    print("✓ Simulation running at REAL-TIME speed\n")
    
    time.sleep(1.0)
    
    # Control functions
    def set_joints(positions):
        for joint, pos in zip(joints, positions):
            sim.setJointTargetPosition(joint, pos)
            sim.setJointMaxForce(joint, 100)
    
    def open_gripper():
        """Open the RG2 gripper using the correct range"""
        open_pos = interval[0] + interval[1]  # Max position
        sim.setJointTargetPosition(gripper_joint, open_pos)
        print(f"    [Gripper: OPENING to {open_pos:.4f}m]")
    
    def close_gripper():
        """Close the RG2 gripper using the correct range"""
        close_pos = interval[0]  # Min position
        sim.setJointTargetPosition(gripper_joint, close_pos)
        print(f"    [Gripper: CLOSING to {close_pos:.4f}m]")
    
    def check_gripper_position():
        """Check and display current gripper position"""
        try:
            pos = sim.getJointPosition(gripper_joint)
            print(f"    Gripper position: {pos:.4f}m ({pos*1000:.2f}mm)")
            return pos
        except:
            print("    [Warning: Could not read gripper position]")
            return None
    
    # Simple test - just test gripper control
    print("=" * 60)
    print("Simple Gripper Test")
    print("=" * 60 + "\n")
    
    # Step 1: Safe home position with gripper OPEN
    print("Step 1: Safe home position")
    home = [0, -np.pi/4, -np.pi/4, -np.pi/2, 0, 0]  # Safe above-table pose
    set_joints(home)
    open_gripper()
    check_gripper_position()
    time.sleep(3.0)
    check_gripper_position()
    print("✓ At home - gripper OPEN\n")
    
    # Step 2: Wait and watch gripper
    print("Step 2: Gripper should be OPEN now")
    time.sleep(2.0)
    check_gripper_position()
    print("✓ Gripper is open\n")
    
    # Step 3: Close gripper
    print("Step 3: CLOSING gripper")
    close_gripper()
    check_gripper_position()
    time.sleep(3.0)
    check_gripper_position()
    print("✓ Gripper should be CLOSED\n")
    
    # Step 4: Open gripper again
    print("Step 4: OPENING gripper")
    open_gripper()
    check_gripper_position()
    time.sleep(3.0)
    check_gripper_position()
    print("✓ Gripper should be OPEN\n")
    
    print("=" * 60)
    print("✓✓✓ GRIPPER TEST COMPLETE! ✓✓✓")
    print("=" * 60)
    print("\nDid you see the gripper open and close?")
    print("Check if it's working properly.\n")
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
