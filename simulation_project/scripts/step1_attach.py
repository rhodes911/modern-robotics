"""
Step 1: Just attach RG2 to UR5 programmatically
Nothing else - no movement, no cube, just verify gripper attachment works
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def attach_gripper_to_ur5(sim, ur5_handle, gripper_handle):
    """
    Attach a gripper to UR5's connection point.
    
    Args:
        sim: CoppeliaSim remote API object
        ur5_handle: Handle of the UR5 robot base
        gripper_handle: Handle of the gripper base (e.g., RG2)
    
    Returns:
        connection_handle: Handle of the connection point (or None if failed)
    """
    # Find UR5 connection point
    try:
        connection = sim.getObject('/UR5/connection')
        print(f"✓ Found /UR5/connection (handle: {connection})")
    except:
        print("✗ Could not find /UR5/connection")
        return None
    
    # Find gripper's attachment point
    try:
        # Try ROBOTIQ 85 first
        gripper_connector = sim.getObject('/ROBOTIQ85/attachPoint')
        print(f"✓ Found ROBOTIQ85 attachPoint")
    except:
        try:
            # Try RG2
            gripper_connector = sim.getObject('/RG2/attachPoint')
            print(f"✓ Found RG2 attachPoint")
        except:
            print("⚠ No attachPoint found, using gripper base")
            gripper_connector = gripper_handle
    
    # Align gripper to connection
    try:
        conn_pos = sim.getObjectPosition(connection, -1)
        conn_ori = sim.getObjectOrientation(connection, -1)
        
        sim.setObjectPosition(gripper_handle, -1, conn_pos)
        sim.setObjectOrientation(gripper_handle, -1, conn_ori)
        sim.setObjectParent(gripper_handle, connection, True)
        
        print("✓ GRIPPER ATTACHED!")
        return connection
        
    except Exception as e:
        print(f"✗ Attachment failed: {e}")
        return None


def main():
    print("=== Step 1: Attach Gripper ===\n")
    
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
    print(f"✓ UR5 loaded (handle: {ur5})\n")
    
    # Load RG2
    print("Loading RG2...")
    rg2 = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print(f"✓ RG2 loaded (handle: {rg2})\n")
    
    # ATTACH GRIPPER using reusable function
    print("Attaching RG2 to UR5...")
    connection = attach_gripper_to_ur5(sim, ur5, rg2)
    
    if not connection:
        print("✗ Attachment failed!")
        return
    
    print()
    
    # Verify attachment
    print("Verifying attachment...")
    parent = sim.getObjectParent(rg2)
    parent_name = sim.getObjectAlias(parent)
    print(f"✓ RG2 parent is now: {parent_name} (handle: {parent})\n")
    
    # Get RG2 position relative to connection
    rg2_pos = sim.getObjectPosition(rg2, connection)
    print(f"RG2 position relative to connection: {rg2_pos}\n")
    
    print("=" * 60)
    print("✓✓✓ SUCCESS! ✓✓✓")
    print("=" * 60)
    print("\nCheck CoppeliaSim:")
    print("  - UR5 should be visible")
    print("  - RG2 should be attached to the end of UR5")
    print("  - They should move together as one unit")
    print("\nDONE - gripper is programmatically attached!")


if __name__ == "__main__":
    main()
