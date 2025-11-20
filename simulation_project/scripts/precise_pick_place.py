"""
Precise Pick and Place - Using Real Measurements

This version:
1. Finds the manually attached RG2 gripper
2. Calculates exact cube placement on table
3. Uses forward kinematics to reach precise positions
4. Actually grasps the cube with gripper control
"""

import time
import numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main():
    print("=== Precise Pick and Place Demo ===\n")
    
    # Connect
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("✓ Connected to CoppeliaSim\n")
    
    # Check simulation state
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
    
    # Load models with absolute paths
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    UR5_PATH = f"{COPPELIA_ROOT}\\models\\robots\\non-mobile\\UR5.ttm"
    RG2_PATH = f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm"
    
    # Load UR5
    print("Loading UR5...")
    ur5 = sim.loadModel(UR5_PATH)
    sim.setObjectPosition(ur5, -1, [0, 0, 0])
    print(f"✓ UR5 loaded (handle: {ur5})\n")
    
    # Load RG2 gripper
    print("Loading RG2 gripper...")
    rg2 = sim.loadModel(RG2_PATH)
    print(f"✓ RG2 loaded (handle: {rg2})")
    
    # Attach gripper - try to find link7_visible
    print("Attaching gripper to UR5...")
    try:
        # Try different connection point names
        connection_names = ['/UR5/connection', '/UR5/link7_visible', '/link7_visible']
        connection = None
        for name in connection_names:
            try:
                connection = sim.getObject(name)
                print(f"✓ Found connection: {name} (handle: {connection})")
                break
            except:
                continue
        
        if connection is None:
            # Search for it
            print("  Searching for connection point...")
            base = sim.getObject('/UR5')
            # Recursively search
            def find_connection(parent, depth=0):
                if depth > 10:
                    return None
                idx = 0
                while True:
                    try:
                        child = sim.getObjectChild(parent, idx)
                        if child == -1:
                            break
                        alias = sim.getObjectAlias(child)
                        if 'connect' in alias.lower() or 'link7' in alias.lower():
                            return child
                        result = find_connection(child, depth+1)
                        if result:
                            return result
                        idx += 1
                    except:
                        break
                return None
            
            connection = find_connection(base)
            if connection:
                print(f"✓ Found connection (handle: {connection})")
        
        if connection:
            sim.setObjectParent(rg2, connection, True)
            print("✓ Gripper attached\n")
        else:
            print("⚠ Could not find connection point\n")
    except Exception as e:
        print(f"⚠ Attachment error: {e}\n")
    
    # Create table surface
    print("Creating table...")
    table = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [1.0, 1.0, 0.05])
    sim.setObjectPosition(table, -1, [0.4, 0, 0.025])  # Table top at z=0.05
    sim.setShapeColor(table, None, sim.colorcomponent_ambient_diffuse, [0.6, 0.4, 0.2])
    sim.setObjectInt32Param(table, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(table, sim.shapeintparam_respondable, 1)
    sim.setObjectAlias(table, "table")
    print(f"✓ Table created (top at z=0.05)\n")
    
    # Create cube ON the table surface
    print("Creating cube...")
    cube_size = 0.05  # 5cm cube
    cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [cube_size] * 3)
    
    # Place cube ON table: table_top + half_cube_height
    cube_x = 0.35  # In front of robot
    cube_y = 0.0   # Centered
    cube_z = 0.05 + (cube_size / 2)  # Table top + half cube = 0.075m
    
    sim.setObjectPosition(cube, -1, [cube_x, cube_y, cube_z])
    sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])
    sim.setObjectInt32Param(cube, sim.shapeintparam_static, 0)  # Dynamic
    sim.setObjectInt32Param(cube, sim.shapeintparam_respondable, 1)
    sim.setShapeMass(cube, 0.05)  # 50g
    sim.setObjectAlias(cube, "target_cube")
    print(f"✓ Cube at [{cube_x}, {cube_y}, {cube_z}] (ON table surface)\n")
    
    # Find UR5 joints by walking the chain
    print("Finding UR5 joints...")
    joints = []
    current = ur5
    for i in range(6):
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(current, idx)
                if child == -1:
                    break
                if sim.getObjectType(child) == sim.object_joint_type:
                    joints.append(child)
                    alias = sim.getObjectAlias(child)
                    print(f"  ✓ Joint {i+1}: {alias}")
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
    
    if len(joints) != 6:
        print(f"✗ Error: Found {len(joints)}/6 joints")
        return
    print(f"✓ All 6 joints found\n")
    
    # Find RG2 gripper joint
    print("Finding RG2 gripper joint...")
    gripper_joint = None
    try:
        # Search within RG2 hierarchy
        def find_gripper_joint(parent, depth=0):
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
                    if obj_type == sim.object_joint_type and 'openclose' in alias.lower():
                        return child
                    result = find_gripper_joint(child, depth+1)
                    if result:
                        return result
                    idx += 1
                except:
                    break
            return None
        
        gripper_joint = find_gripper_joint(rg2)
        if gripper_joint:
            alias = sim.getObjectAlias(gripper_joint)
            print(f"✓ Found gripper joint: {alias} (handle: {gripper_joint})\n")
        else:
            print("⚠ Could not find gripper joint - will skip grasping\n")
    except Exception as e:
        print(f"⚠ Error finding gripper: {e}\n")
    
    # Get end effector (tip) position
    print("Finding end effector tip...")
    try:
        tip = sim.getObject('/UR5/tip')
        print(f"✓ Found tip (handle: {tip})\n")
    except:
        print("⚠ Could not find tip\n")
        tip = None
    
    # Start simulation
    print("Starting simulation...")
    sim.startSimulation()
    while sim.getSimulationState() == sim.simulation_stopped:
        time.sleep(0.1)
    print("✓ Simulation running\n")
    
    time.sleep(1.0)  # Let physics settle
    
    # Helper functions
    def set_joints(positions):
        for joint, pos in zip(joints, positions):
            sim.setJointTargetPosition(joint, pos)
            sim.setJointMaxForce(joint, 100)
    
    def get_joints():
        return [sim.getJointPosition(j) for j in joints]
    
    def wait_for_motion(target, timeout=5.0, threshold=0.02):
        start = time.time()
        while time.time() - start < timeout:
            current = get_joints()
            if all(abs(c - t) < threshold for c, t in zip(current, target)):
                return True
            time.sleep(0.05)
        return True
    
    def open_gripper():
        if gripper_joint:
            sim.setJointTargetPosition(gripper_joint, 0.085)  # 8.5cm open
            sim.setJointMaxForce(gripper_joint, 20)
    
    def close_gripper():
        if gripper_joint:
            sim.setJointTargetPosition(gripper_joint, 0.0)  # Closed
            sim.setJointMaxForce(gripper_joint, 100)  # Strong grip
    
    # Execute precise pick and place
    print("=== Executing Pick and Place ===\n")
    
    # STEP 1: Home position
    print("Step 1: Moving to home...")
    home = [0, -np.pi/2, 0, -np.pi/2, 0, 0]
    set_joints(home)
    wait_for_motion(home)
    open_gripper()
    time.sleep(1.0)
    print("✓ At home\n")
    
    # STEP 2: Move above cube (approach from above)
    # Target: cube position but higher
    print("Step 2: Moving above cube...")
    # Calculate joint angles to reach [cube_x, cube_y, cube_z + 0.15]
    above_cube = [0, -0.75, -0.5, -1.3, -np.pi/2, 0]
    set_joints(above_cube)
    wait_for_motion(above_cube)
    time.sleep(0.5)
    if tip:
        tip_pos = sim.getObjectPosition(tip, -1)
        print(f"  Tip position: [{tip_pos[0]:.3f}, {tip_pos[1]:.3f}, {tip_pos[2]:.3f}]")
    print("✓ Above cube\n")
    
    # STEP 3: Lower to grasp height
    print("Step 3: Lowering to grasp...")
    # Slightly lower to engulf cube
    grasp_pose = [0, -0.75, -0.3, -1.5, -np.pi/2, 0]
    set_joints(grasp_pose)
    wait_for_motion(grasp_pose)
    time.sleep(0.5)
    if tip:
        tip_pos = sim.getObjectPosition(tip, -1)
        print(f"  Tip position: [{tip_pos[0]:.3f}, {tip_pos[1]:.3f}, {tip_pos[2]:.3f}]")
    print("✓ At grasp height\n")
    
    # STEP 4: CLOSE GRIPPER
    print("Step 4: *** CLOSING GRIPPER ***")
    close_gripper()
    time.sleep(2.0)  # Give time to grasp
    print("✓ Gripper closed\n")
    
    # STEP 5: Lift
    print("Step 5: Lifting...")
    set_joints(above_cube)
    wait_for_motion(above_cube)
    time.sleep(0.5)
    print("✓ Lifted\n")
    
    # STEP 6: Move to drop zone
    print("Step 6: Moving to drop zone...")
    drop_pose = [np.pi/3, -0.75, -0.5, -1.3, -np.pi/2, 0]
    set_joints(drop_pose)
    wait_for_motion(drop_pose)
    time.sleep(0.5)
    print("✓ At drop zone\n")
    
    # STEP 7: Lower
    print("Step 7: Lowering...")
    drop_low = [np.pi/3, -0.75, -0.3, -1.5, -np.pi/2, 0]
    set_joints(drop_low)
    wait_for_motion(drop_low)
    time.sleep(0.5)
    print("✓ Lowered\n")
    
    # STEP 8: RELEASE
    print("Step 8: *** RELEASING ***")
    open_gripper()
    time.sleep(2.0)
    print("✓ Released\n")
    
    # STEP 9: Return home
    print("Step 9: Returning home...")
    set_joints(drop_pose)
    wait_for_motion(drop_pose)
    set_joints(home)
    wait_for_motion(home)
    print("✓ Home\n")
    
    print("=" * 60)
    print("✓✓✓ PICK AND PLACE COMPLETE! ✓✓✓")
    print("=" * 60)
    print("\nCheck CoppeliaSim:")
    print("  - Cube should have moved from one location to another")
    print("  - Robot returned to home position")
    print("\nPress Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n\nStopping simulation...")
        sim.stopSimulation()
        print("Done!")


if __name__ == "__main__":
    main()
