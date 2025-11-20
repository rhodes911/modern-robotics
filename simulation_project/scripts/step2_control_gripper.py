"""
Step 2: Control the gripper - open, close, move
Test gripper control with simple motion
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main():
    print("=== Step 2: Control Gripper ===\n")
    
    # Connect
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("✓ Connected\n")
    
    # Stop simulation
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Clear everything
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
    
    # Load UR5
    print("Loading UR5...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    ur5 = sim.loadModel(f"{COPPELIA_ROOT}\\models\\robots\\non-mobile\\UR5.ttm")
    sim.setObjectPosition(ur5, -1, [0, 0, 0])
    print(f"✓ UR5 loaded\n")
    
    # Load RG2
    print("Loading RG2...")
    rg2 = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print(f"✓ RG2 loaded\n")
    
    # Find connection point
    connection = sim.getObject('/UR5/connection')
    print(f"✓ Found connection\n")
    
    # Find RG2 attachment point
    try:
        rg2_connector = sim.getObject('/RG2/attachPoint')
    except:
        rg2_connector = rg2
    
    # Attach gripper
    print("Attaching RG2...")
    conn_pos = sim.getObjectPosition(connection, -1)
    conn_ori = sim.getObjectOrientation(connection, -1)
    sim.setObjectPosition(rg2, -1, conn_pos)
    sim.setObjectOrientation(rg2, -1, conn_ori)
    sim.setObjectParent(rg2, connection, True)
    print("✓ Gripper attached\n")
    
    # Find gripper control joint
    print("Finding gripper joint...")
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
    if not gripper_joint:
        print("✗ Could not find gripper joint!")
        return
    
    alias = sim.getObjectAlias(gripper_joint)
    print(f"✓ Found gripper joint: {alias}\n")
    
    # Find UR5 joints
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
    
    # Create a test cube at grasp position
    print("Creating test cube...")
    cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.05, 0.05, 0.05])
    sim.setObjectPosition(cube, -1, [0.3, 0, 0.3])  # In front of robot
    sim.setShapeColor(cube, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])
    sim.setObjectInt32Param(cube, sim.shapeintparam_static, 0)
    sim.setObjectInt32Param(cube, sim.shapeintparam_respondable, 1)
    sim.setShapeMass(cube, 0.05)
    sim.setObjectAlias(cube, "test_cube")
    print(f"✓ Cube at [0.3, 0, 0.3]\n")
    
    # Start simulation
    print("Starting simulation...")
    sim.startSimulation()
    while sim.getSimulationState() == sim.simulation_stopped:
        time.sleep(0.1)
    print("✓ Simulation running\n")
    
    time.sleep(1.0)
    
    # Helper functions
    def set_joints(positions):
        for joint, pos in zip(joints, positions):
            sim.setJointTargetPosition(joint, pos)
            sim.setJointMaxForce(joint, 100)
    
    def open_gripper():
        print("    [GRIPPER: OPENING]")
        sim.setJointTargetPosition(gripper_joint, 0.085)  # 8.5cm open
        sim.setJointMaxForce(gripper_joint, 20)
    
    def close_gripper():
        print("    [GRIPPER: CLOSING]")
        sim.setJointTargetPosition(gripper_joint, 0.0)  # Fully closed
        sim.setJointMaxForce(gripper_joint, 100)
    
    def get_gripper_pos():
        return sim.getJointPosition(gripper_joint)
    
    # Test sequence
    print("=" * 60)
    print("=== Test Sequence ===")
    print("=" * 60 + "\n")
    
    # Step 1: Home position with gripper open
    print("Step 1: Home position - gripper OPEN")
    import numpy as np
    home = [0, -np.pi/2, 0, -np.pi/2, 0, 0]
    set_joints(home)
    open_gripper()
    time.sleep(3.0)
    print(f"    Gripper position: {get_gripper_pos():.4f}")
    print("✓ Gripper open\n")
    
    # Step 2: Move to approach position
    print("Step 2: Moving to cube approach position")
    approach = [0, -0.8, -0.4, -1.3, -np.pi/2, 0]
    set_joints(approach)
    time.sleep(3.0)
    print("✓ At approach position\n")
    
    # Step 3: Move to grasp position (gripper still open)
    print("Step 3: Moving to grasp position - gripper still OPEN")
    grasp = [0, -0.8, -0.2, -1.5, -np.pi/2, 0]
    set_joints(grasp)
    time.sleep(3.0)
    print(f"    Gripper position: {get_gripper_pos():.4f}")
    print("✓ At grasp position\n")
    
    # Step 4: CLOSE GRIPPER
    print("Step 4: *** CLOSING GRIPPER ***")
    close_gripper()
    time.sleep(3.0)
    print(f"    Gripper position: {get_gripper_pos():.4f}")
    print("✓ Gripper closed (should grab cube)\n")
    
    # Step 5: Lift
    print("Step 5: Lifting with gripper CLOSED")
    set_joints(approach)
    time.sleep(3.0)
    print("✓ Lifted\n")
    
    # Step 6: Return to home
    print("Step 6: Returning to home")
    set_joints(home)
    time.sleep(3.0)
    print("✓ At home\n")
    
    # Step 7: OPEN GRIPPER (release)
    print("Step 7: *** OPENING GRIPPER (release) ***")
    open_gripper()
    time.sleep(3.0)
    print(f"    Gripper position: {get_gripper_pos():.4f}")
    print("✓ Gripper opened\n")
    
    print("=" * 60)
    print("✓✓✓ TEST COMPLETE! ✓✓✓")
    print("=" * 60)
    print("\nSequence:")
    print("  1. Started with gripper OPEN")
    print("  2. Moved to cube")
    print("  3. CLOSED gripper (should grab)")
    print("  4. Lifted")
    print("  5. Returned home")
    print("  6. OPENED gripper (release)")
    print("\nDid the cube get picked up and released?\n")
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
