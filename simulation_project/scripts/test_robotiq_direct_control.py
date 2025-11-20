"""
ROBOTIQ 85 Direct Control from Python
======================================

Based on monitoring results, we know the target positions:
- CLOSED: All 6 joints at 0.000 radians
- OPEN: 
  * Ljoint1: +0.787
  * Rjoint1: +0.803
  * Ljoint2: -0.779
  * Rjoint2: -0.801
  * LactiveJoint: +0.794
  * RactiveJoint: +0.803

Strategy: Set all 6 joints to kinematic mode (force/torque mode 0) and 
drive them directly to target positions using setJointTargetPosition.
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def setup_joint_for_control(sim, joint_handle, joint_name):
    """
    Configure a joint for direct position control.
    
    Sets joint to kinematic mode (mode 0) with motor enabled.
    """
    try:
        # Set to kinematic mode (force/torque mode)
        sim.setJointMode(joint_handle, sim.jointmode_kinematic, 0)
        
        # Enable motor
        sim.setObjectInt32Param(joint_handle, sim.jointintparam_motor_enabled, 1)
        
        # Set velocity (not too fast to avoid instability)
        sim.setObjectFloatParam(joint_handle, sim.jointfloatparam_velocity, 0.5)
        
        # Set force/torque limit
        sim.setJointTargetForce(joint_handle, 20.0)
        
        print(f"✓ {joint_name} configured for control")
        return True
        
    except Exception as e:
        print(f"✗ Error configuring {joint_name}: {e}")
        return False


def get_robotiq_joints(sim):
    """
    Get handles for all 6 ROBOTIQ 85 control joints.
    
    Returns:
        dict: Joint names mapped to handles
    """
    joint_names = [
        'Ljoint1',
        'Rjoint1', 
        'Ljoint2',
        'Rjoint2',
        'LactiveJoint',
        'RactiveJoint'
    ]
    
    joints = {}
    for name in joint_names:
        try:
            handle = sim.getObject(f'/ROBOTIQ85/{name}')
            joints[name] = handle
            print(f"✓ Found {name}")
        except Exception as e:
            print(f"✗ Error finding {name}: {e}")
            return None
    
    return joints


def open_gripper(sim, joints):
    """
    Open the ROBOTIQ 85 gripper by setting all joints to OPEN positions.
    """
    print("\n>>> OPENING GRIPPER <<<")
    
    # Target positions discovered from monitoring
    targets = {
        'Ljoint1': +0.787,
        'Rjoint1': +0.803,
        'Ljoint2': -0.779,
        'Rjoint2': -0.801,
        'LactiveJoint': +0.794,
        'RactiveJoint': +0.803
    }
    
    for name, target in targets.items():
        try:
            sim.setJointTargetPosition(joints[name], target)
            print(f"  {name}: → {target:+7.3f}")
        except Exception as e:
            print(f"  ✗ Error setting {name}: {e}")


def close_gripper(sim, joints):
    """
    Close the ROBOTIQ 85 gripper by setting all joints to CLOSED (0.0).
    """
    print("\n>>> CLOSING GRIPPER <<<")
    
    for name in joints.keys():
        try:
            sim.setJointTargetPosition(joints[name], 0.0)
            print(f"  {name}: → 0.000")
        except Exception as e:
            print(f"  ✗ Error setting {name}: {e}")


def get_gripper_positions(sim, joints):
    """
    Read current positions of all gripper joints.
    
    Returns:
        dict: Joint names mapped to current positions
    """
    positions = {}
    for name, handle in joints.items():
        try:
            pos = sim.getJointPosition(handle)
            positions[name] = pos
        except Exception as e:
            print(f"✗ Error reading {name}: {e}")
            positions[name] = None
    
    return positions


def wait_for_gripper_motion(sim, joints, duration=3.0):
    """
    Wait for gripper to complete motion, printing progress.
    """
    start_time = time.time()
    
    print(f"\nWaiting {duration}s for motion to complete...")
    
    while time.time() - start_time < duration:
        time.sleep(0.5)
        elapsed = time.time() - start_time
        
        # Read LactiveJoint as state indicator
        pos = sim.getJointPosition(joints['LactiveJoint'])
        print(f"  [{elapsed:4.1f}s] LactiveJoint: {pos:+7.4f}")
    
    print("✓ Motion complete")


def main():
    print("="*70)
    print("ROBOTIQ 85 Direct Python Control Test")
    print("="*70)
    
    # Connect
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop any running simulation
    if sim.getSimulationState() != sim.simulation_stopped:
        print("\n⚠ Stopping existing simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Load gripper (use forward slashes - CoppeliaSim standard)
    print("\nLoading ROBOTIQ 85 gripper...")
    try:
        # Try different path formats
        paths = [
            'models/components/grippers/ROBOTIQ 85.ttm',
            'models\\components\\grippers\\ROBOTIQ 85.ttm',
            '../models/components/grippers/ROBOTIQ 85.ttm',
        ]
        
        gripper = None
        for path in paths:
            try:
                gripper = sim.loadModel(path)
                print(f"✓ Gripper loaded from: {path}")
                break
            except:
                continue
        
        if gripper is None:
            raise Exception("Could not load gripper with any path format")
            
    except Exception as e:
        print(f"✗ Error loading gripper: {e}")
        return
    
    # Get joint handles
    print("\nGetting joint handles...")
    joints = get_robotiq_joints(sim)
    if not joints:
        print("✗ Failed to get all joint handles")
        return
    
    # Start simulation BEFORE configuring joints
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    
    # Configure all joints for direct control
    print("\nConfiguring joints for control...")
    for name, handle in joints.items():
        setup_joint_for_control(sim, handle, name)
    
    # Read initial positions
    print("\nInitial positions:")
    positions = get_gripper_positions(sim, joints)
    for name, pos in positions.items():
        if pos is not None:
            print(f"  {name}: {pos:+7.4f}")
    
    # Test sequence
    print("\n" + "="*70)
    print("TEST SEQUENCE: OPEN → CLOSE → OPEN")
    print("="*70)
    
    # 1. OPEN
    open_gripper(sim, joints)
    wait_for_gripper_motion(sim, joints, duration=3.0)
    
    # 2. CLOSE
    close_gripper(sim, joints)
    wait_for_gripper_motion(sim, joints, duration=3.0)
    
    # 3. OPEN again
    open_gripper(sim, joints)
    wait_for_gripper_motion(sim, joints, duration=3.0)
    
    # Final positions
    print("\n" + "="*70)
    print("FINAL POSITIONS:")
    print("="*70)
    positions = get_gripper_positions(sim, joints)
    for name, pos in positions.items():
        if pos is not None:
            print(f"  {name}: {pos:+7.4f}")
    
    # Cleanup
    print("\nStopping simulation...")
    sim.stopSimulation()
    print("Done!")


if __name__ == "__main__":
    main()
