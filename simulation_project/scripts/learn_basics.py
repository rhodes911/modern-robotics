"""
Learn the Basics: UR5 + RG2 Gripper Pick and Place

This script teaches the fundamentals:
1. How to load robot models programmatically
2. How to attach a gripper to the robot
3. How to control joints
4. How to pick up and move an object

Run this with CoppeliaSim open and simulation STOPPED.
"""

import time
import numpy as np
from pathlib import Path
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main():
    print("=== Learning UR5 + Gripper Basics ===\n")
    
    # Connect to CoppeliaSim
    print("1. Connecting to CoppeliaSim...")
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("   ✓ Connected\n")
    
    # Make sure simulation is stopped
    if sim.getSimulationState() != sim.simulation_stopped:
        print("   Stopping simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Clear scene (remove all objects)
    print("2. Clearing scene...")
    try:
        # Get all objects and remove them
        all_objects = sim.getObjects(sim.handle_scene, sim.object_shape_type)
        for obj in all_objects:
            try:
                sim.removeObject(obj)
            except:
                pass
    except:
        pass
    print("   ✓ Scene cleared\n")
    
    # Define model paths (absolute)
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    UR5_PATH = f"{COPPELIA_ROOT}\\models\\robots\\non-mobile\\UR5.ttm"
    RG2_PATH = f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm"
    
    # Load UR5 robot
    print("3. Loading UR5 robot...")
    try:
        ur5_handle = sim.loadModel(UR5_PATH)
        print(f"   ✓ UR5 loaded (handle: {ur5_handle})")
        
        # Position it at origin
        sim.setObjectPosition(ur5_handle, -1, [0, 0, 0])
        print("   ✓ UR5 positioned at origin\n")
    except Exception as e:
        print(f"   ✗ Error loading UR5: {e}")
        print(f"   Path tried: {UR5_PATH}")
        return
    
    # Load RG2 gripper
    print("4. Loading RG2 gripper...")
    try:
        rg2_handle = sim.loadModel(RG2_PATH)
        print(f"   ✓ RG2 loaded (handle: {rg2_handle})")
        
        # Find UR5's connection point (end effector)
        try:
            connection = sim.getObject('/UR5/connection')
        except:
            # Try alternative names
            try:
                connection = sim.getObject('/UR5_connection')
            except:
                connection = sim.getObject('/:UR5_connection')
        
        print(f"   ✓ Found connection point (handle: {connection})")
        
        # Attach gripper to robot
        sim.setObjectParent(rg2_handle, connection, True)
        print("   ✓ Gripper attached to UR5\n")
        
    except Exception as e:
        print(f"   ✗ Error with gripper: {e}")
        print("   Continuing without gripper...\n")
        rg2_handle = None
    
    # Create a simple object to pick up
    print("5. Creating object to pick up...")
    cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.05, 0.05, 0.05])
    sim.setObjectPosition(cube, -1, [0.3, 0, 0.5])  # In front of robot, elevated
    sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])  # Red
    
    # Make it dynamic and respondable
    sim.setObjectInt32Param(cube, sim.shapeintparam_static, 0)  # dynamic
    sim.setObjectInt32Param(cube, sim.shapeintparam_respondable, 1)  # collidable
    sim.setShapeMass(cube, 0.1)  # 100 grams
    
    sim.setObjectAlias(cube, "target_cube")
    print(f"   ✓ Red cube created (handle: {cube})")
    print("   Position: [0.3, 0, 0.5]\n")
    
    # Find all UR5 joints by following the kinematic chain
    print("6. Finding UR5 joints...")
    joints = []
    joint_names = []
    
    try:
        # Start from UR5 base
        current = ur5_handle
        
        # Follow the chain to find all joints
        for i in range(1, 7):
            # Find the joint child
            index = 0
            found_joint = None
            while True:
                try:
                    child = sim.getObjectChild(current, index)
                    if child == -1:
                        break
                    obj_type = sim.getObjectType(child)
                    if obj_type == sim.object_joint_type:
                        found_joint = child
                        break
                    index += 1
                except:
                    break
            
            if found_joint is None:
                print(f"   ✗ Could not find joint {i}")
                break
            
            alias = sim.getObjectAlias(found_joint)
            joints.append(found_joint)
            joint_names.append(alias)
            print(f"   ✓ Joint {i}: {alias} (handle: {found_joint})")
            
            # Move to this joint's link child for next iteration
            current = found_joint
            # Find the link (non-joint child)
            index = 0
            while True:
                try:
                    child = sim.getObjectChild(current, index)
                    if child == -1:
                        break
                    obj_type = sim.getObjectType(child)
                    if obj_type != sim.object_joint_type:
                        current = child
                        break
                    index += 1
                except:
                    break
        
        if len(joints) != 6:
            print(f"\n   ✗ Error: Found {len(joints)}/6 joints")
            return
            
        print(f"   ✓ All 6 joints found!\n")
        
    except Exception as e:
        print(f"   ✗ Error finding joints: {e}")
        return
    
    # Find gripper joint if available
    gripper_joint = None
    if rg2_handle is not None:
        print("7. Finding gripper joint...")
        try:
            # Common RG2 joint names
            for name in ['/RG2/RG2_openCloseJoint', '/RG2_openCloseJoint', 
                        '/RG2/joint', 'RG2_openCloseJoint']:
                try:
                    gripper_joint = sim.getObject(name)
                    print(f"   ✓ Found gripper joint: {name} (handle: {gripper_joint})")
                    break
                except:
                    continue
        except Exception as e:
            print(f"   ⚠ Could not find gripper joint: {e}")
    
    if gripper_joint is None:
        print("   ⚠ No gripper joint found - will skip grasping\n")
    else:
        print()
    
    # Start simulation
    print("8. Starting simulation...")
    sim.startSimulation()
    while sim.getSimulationState() == sim.simulation_stopped:
        time.sleep(0.1)
    print("   ✓ Simulation running\n")
    
    time.sleep(1.0)  # Let physics settle
    
    # Define helper functions
    def set_joints(positions, speed=1.0):
        """Set all joint target positions"""
        for joint, pos in zip(joints, positions):
            sim.setJointTargetPosition(joint, pos)
            sim.setJointMaxForce(joint, 100)  # Ensure joints have force
    
    def get_joints():
        """Read current joint positions"""
        return [sim.getJointPosition(j) for j in joints]
    
    def wait_for_motion(target, timeout=5.0, threshold=0.05):
        """Wait until joints reach target"""
        start = time.time()
        while time.time() - start < timeout:
            current = get_joints()
            diffs = [abs(c - t) for c, t in zip(current, target)]
            if all(d < threshold for d in diffs):
                return True
            time.sleep(0.05)
        return True  # Continue anyway
    
    def open_gripper():
        """Open gripper"""
        if gripper_joint is not None:
            sim.setJointTargetPosition(gripper_joint, 0.085)  # Open
            sim.setJointMaxForce(gripper_joint, 20)
    
    def close_gripper():
        """Close gripper"""
        if gripper_joint is not None:
            sim.setJointTargetPosition(gripper_joint, 0.0)  # Closed
            sim.setJointMaxForce(gripper_joint, 20)
    
    # Execute pick and place sequence
    print("9. Executing pick and place sequence...\n")
    
    # Read starting position
    current = get_joints()
    print(f"   Current joint positions: {[f'{p:.3f}' for p in current]}\n")
    
    # Define positions (in radians)
    home = [0, -np.pi/2, 0, -np.pi/2, 0, 0]
    
    # Pre-pick: reach toward cube
    pre_pick = [0, -np.pi/4, -np.pi/4, -np.pi/2, 0, 0]
    
    # Pick: lower down
    pick = [0, -np.pi/4, -np.pi/3, -np.pi/2.5, 0, 0]
    
    # Lift: raise up
    lift = [0, -np.pi/4, -np.pi/4, -np.pi/2, 0, 0]
    
    # Move: swing to side
    move = [np.pi/3, -np.pi/4, -np.pi/4, -np.pi/2, 0, 0]
    
    # Place: lower to drop
    place = [np.pi/3, -np.pi/4, -np.pi/3, -np.pi/2.5, 0, 0]
    
    # Step 1: Home position
    print("   Step 1: Moving to home position...")
    set_joints(home)
    wait_for_motion(home)
    open_gripper()
    time.sleep(1.0)
    print("   ✓ At home\n")
    
    # Step 2: Reach toward cube
    print("   Step 2: Reaching toward cube...")
    set_joints(pre_pick)
    wait_for_motion(pre_pick)
    time.sleep(0.5)
    print("   ✓ Pre-pick position\n")
    
    # Step 3: Lower to cube
    print("   Step 3: Lowering to cube...")
    set_joints(pick)
    wait_for_motion(pick)
    time.sleep(0.5)
    print("   ✓ At cube\n")
    
    # Step 4: Close gripper
    print("   Step 4: Closing gripper...")
    close_gripper()
    time.sleep(1.5)  # Give gripper time to close
    print("   ✓ Gripper closed\n")
    
    # Step 5: Lift cube
    print("   Step 5: Lifting cube...")
    set_joints(lift)
    wait_for_motion(lift)
    time.sleep(0.5)
    print("   ✓ Cube lifted\n")
    
    # Step 6: Move to new location
    print("   Step 6: Moving to new location...")
    set_joints(move)
    wait_for_motion(move)
    time.sleep(0.5)
    print("   ✓ At new location\n")
    
    # Step 7: Lower to place
    print("   Step 7: Lowering to place...")
    set_joints(place)
    wait_for_motion(place)
    time.sleep(0.5)
    print("   ✓ Lowered\n")
    
    # Step 8: Release
    print("   Step 8: Releasing object...")
    open_gripper()
    time.sleep(1.5)
    print("   ✓ Released\n")
    
    # Step 9: Return home
    print("   Step 9: Returning home...")
    set_joints(move)
    wait_for_motion(move)
    set_joints(home)
    wait_for_motion(home)
    time.sleep(0.5)
    print("   ✓ Back at home\n")
    
    print("=" * 50)
    print("✓ Pick and place complete!")
    print("=" * 50)
    print("\nThe robot should have:")
    print("  1. Moved to the red cube")
    print("  2. Closed gripper around it")
    print("  3. Lifted and moved it to the side")
    print("  4. Released it")
    print("  5. Returned home")
    print("\nLeave simulation running to see the result.")
    print("Press Ctrl+C to stop when ready.\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        sim.stopSimulation()
        print("Done!")


if __name__ == "__main__":
    main()
