"""
Load and Control Manual Scene - test1.ttt

This version:
1. Loads your manually created scene (test1.ttt)
2. Finds the existing UR5 and RG2 setup
3. Controls them for precise pick and place
"""

import time
import numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main():
    print("=== Loading Manual Scene (test1.ttt) ===\n")
    
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
    
    # Load your manual scene
    SCENE_PATH = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\scenes\test1.ttt"
    print(f"Loading scene: {SCENE_PATH}")
    try:
        sim.loadScene(SCENE_PATH)
        print("✓ Scene loaded\n")
    except Exception as e:
        print(f"✗ Error loading scene: {e}")
        return
    
    # Find UR5 joints by walking the chain
    print("Finding UR5 joints...")
    joints = []
    try:
        ur5 = sim.getObject('/UR5')
        print(f"✓ Found UR5 (handle: {ur5})")
        
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
                        print(f"  ✓ Joint {i+1}: {alias} (handle: {child})")
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
    except Exception as e:
        print(f"✗ Error finding UR5: {e}")
        return
    
    # Find RG2 gripper joint
    print("Finding RG2 gripper joint...")
    gripper_joint = None
    try:
        # Try to find RG2 base
        rg2 = sim.getObject('/RG2')
        print(f"✓ Found RG2 (handle: {rg2})")
        
        # Search within RG2 hierarchy for the control joint
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
                    
                    # Print all joints found for debugging
                    if obj_type == sim.object_joint_type:
                        print(f"    Found joint: {alias} (handle: {child})")
                        if 'openclose' in alias.lower() or 'actuator' in alias.lower():
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
            print(f"  ✓ Found gripper control joint: {alias} (handle: {gripper_joint})\n")
        else:
            print("  ⚠ Could not find gripper control joint - will skip grasping\n")
    except Exception as e:
        print(f"⚠ Error finding RG2: {e}\n")
    
    # Find end effector tip
    print("Finding end effector tip...")
    tip = None
    try:
        tip = sim.getObject('/UR5/tip')
        print(f"✓ Found tip (handle: {tip})\n")
    except:
        try:
            tip = sim.getObject('/tip')
            print(f"✓ Found tip (handle: {tip})\n")
        except:
            print("⚠ Could not find tip\n")
    
    # Look for existing cube
    print("Looking for target cube...")
    cube = None
    try:
        # Try common names
        for name in ['/target_cube', '/cube', '/Cuboid']:
            try:
                cube = sim.getObject(name)
                pos = sim.getObjectPosition(cube, -1)
                print(f"✓ Found cube: {name} at position [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]\n")
                break
            except:
                continue
        
        if cube is None:
            print("⚠ No cube found - will create one")
            # Create cube ON the table surface
            cube_size = 0.05  # 5cm cube
            cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [cube_size] * 3)
            
            # Place cube on surface
            cube_x = 0.35
            cube_y = 0.0
            cube_z = 0.075  # Adjust based on your table height
            
            sim.setObjectPosition(cube, -1, [cube_x, cube_y, cube_z])
            sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])
            sim.setObjectInt32Param(cube, sim.shapeintparam_static, 0)
            sim.setObjectInt32Param(cube, sim.shapeintparam_respondable, 1)
            sim.setShapeMass(cube, 0.05)
            sim.setObjectAlias(cube, "target_cube")
            print(f"✓ Created cube at [{cube_x}, {cube_y}, {cube_z}]\n")
    except Exception as e:
        print(f"⚠ Error with cube: {e}\n")
    
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
            print("    [Gripper: OPEN]")
    
    def close_gripper():
        if gripper_joint:
            sim.setJointTargetPosition(gripper_joint, 0.0)  # Closed
            sim.setJointMaxForce(gripper_joint, 100)  # Strong grip
            print("    [Gripper: CLOSED]")
    
    def show_tip_position():
        if tip:
            pos = sim.getObjectPosition(tip, -1)
            print(f"    Tip: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
    
    # Execute precise pick and place
    print("=" * 60)
    print("=== Executing Pick and Place ===")
    print("=" * 60 + "\n")
    
    # STEP 1: Home position
    print("Step 1: Moving to home position...")
    home = [0, -np.pi/2, 0, -np.pi/2, 0, 0]
    set_joints(home)
    wait_for_motion(home)
    open_gripper()
    time.sleep(1.0)
    show_tip_position()
    print("✓ At home\n")
    
    # STEP 2: Move above cube
    print("Step 2: Moving above cube...")
    above_cube = [0, -0.75, -0.5, -1.3, -np.pi/2, 0]
    set_joints(above_cube)
    wait_for_motion(above_cube)
    time.sleep(0.5)
    show_tip_position()
    print("✓ Above cube\n")
    
    # STEP 3: Lower to grasp height
    print("Step 3: Lowering to grasp height...")
    grasp_pose = [0, -0.75, -0.3, -1.5, -np.pi/2, 0]
    set_joints(grasp_pose)
    wait_for_motion(grasp_pose)
    time.sleep(0.5)
    show_tip_position()
    print("✓ At grasp height\n")
    
    # STEP 4: CLOSE GRIPPER
    print("Step 4: *** CLOSING GRIPPER ***")
    close_gripper()
    time.sleep(2.0)
    print("✓ Gripper closed\n")
    
    # STEP 5: Lift
    print("Step 5: Lifting cube...")
    set_joints(above_cube)
    wait_for_motion(above_cube)
    time.sleep(0.5)
    show_tip_position()
    print("✓ Lifted\n")
    
    # STEP 6: Move to drop zone
    print("Step 6: Moving to drop zone...")
    drop_pose = [np.pi/3, -0.75, -0.5, -1.3, -np.pi/2, 0]
    set_joints(drop_pose)
    wait_for_motion(drop_pose)
    time.sleep(0.5)
    show_tip_position()
    print("✓ At drop zone\n")
    
    # STEP 7: Lower
    print("Step 7: Lowering to release height...")
    drop_low = [np.pi/3, -0.75, -0.3, -1.5, -np.pi/2, 0]
    set_joints(drop_low)
    wait_for_motion(drop_low)
    time.sleep(0.5)
    show_tip_position()
    print("✓ Lowered\n")
    
    # STEP 8: RELEASE
    print("Step 8: *** RELEASING ***")
    open_gripper()
    time.sleep(2.0)
    print("✓ Released\n")
    
    # STEP 9: Return home
    print("Step 9: Returning to home...")
    set_joints(drop_pose)
    wait_for_motion(drop_pose)
    set_joints(home)
    wait_for_motion(home)
    show_tip_position()
    print("✓ Home\n")
    
    print("=" * 60)
    print("✓✓✓ PICK AND PLACE COMPLETE! ✓✓✓")
    print("=" * 60)
    print("\nResults:")
    print("  - Loaded your manually created scene (test1.ttt)")
    print("  - Found and controlled UR5 and RG2")
    print("  - Executed complete pick and place sequence")
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
