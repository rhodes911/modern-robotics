"""Basic pick-and-place demo for UR5 robot.

Simplified version that moves the robot through predefined joint positions
to pick up an object and place it in a sorting bin. Does not use vision -
assumes objects are at known locations.

Usage:
    1. Build scene with scene_builder.py (sim must be stopped)
    2. Manually load UR5 robot model in CoppeliaSim
    3. Start simulation
    4. Run: python scripts/basic_pick_place.py
"""

import time
import numpy as np
from pathlib import Path
import yaml

from coppelia_api import CoppeliaAPI


def connect_from_config():
    """Load config and connect to CoppeliaSim"""
    cfg_path = Path(__file__).parent.parent / "config" / "sim_config.yaml"
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    
    host = cfg.get("coppeliasim", {}).get("host", "127.0.0.1")
    port = cfg.get("coppeliasim", {}).get("port", 23000)
    
    api = CoppeliaAPI(host, port)
    if not api.connect():
        print("Failed to connect to CoppeliaSim")
        return None, None
    
    return api, cfg


def find_ur5_joints(api):
    """Find all UR5 joint handles"""
    joint_names = [
        "UR5_joint1",
        "UR5_joint2", 
        "UR5_joint3",
        "UR5_joint4",
        "UR5_joint5",
        "UR5_joint6"
    ]
    
    joints = []
    for name in joint_names:
        try:
            handle = api.sim.getObject(f"/{name}")
            joints.append(handle)
        except Exception as e:
            print(f"Warning: Could not find {name}: {e}")
            return None
    
    return joints


def set_joint_positions(api, joints, positions, speed=0.5):
    """Set joint target positions with velocity control"""
    if len(joints) != len(positions):
        print(f"Error: Expected {len(joints)} positions, got {len(positions)}")
        return False
    
    for joint, pos in zip(joints, positions):
        try:
            # Set position
            api.sim.setJointTargetPosition(joint, pos)
            # Set velocity for smooth motion
            api.sim.setJointTargetVelocity(joint, speed)
        except Exception as e:
            print(f"Error setting joint position: {e}")
            return False
    
    return True


def get_joint_positions(api, joints):
    """Read current joint positions"""
    positions = []
    for joint in joints:
        try:
            pos = api.sim.getJointPosition(joint)
            positions.append(pos)
        except Exception as e:
            print(f"Error reading joint: {e}")
            return None
    return positions


def wait_for_motion(api, joints, target, timeout=5.0, threshold=0.01):
    """Wait until joints reach target positions"""
    start = time.time()
    while time.time() - start < timeout:
        current = get_joint_positions(api, joints)
        if current is None:
            return False
        
        diffs = [abs(c - t) for c, t in zip(current, target)]
        if all(d < threshold for d in diffs):
            return True
        
        time.sleep(0.1)
    
    print("Warning: Motion timeout")
    return False


def control_gripper(api, close=True):
    """Control UR5 gripper (if available)"""
    try:
        # Try to find gripper joint
        gripper = api.sim.getObject("/RG2_openCloseJoint")
        if close:
            api.sim.setJointTargetPosition(gripper, 0.0)  # closed
            print("  → Gripper closed")
        else:
            api.sim.setJointTargetPosition(gripper, 0.085)  # open
            print("  → Gripper opened")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"  ⚠ Gripper control failed (may not be loaded): {e}")
        return False


def run_pick_and_place_demo(api, config):
    """Execute a simple pick-and-place sequence"""
    
    # Ensure simulation is running
    state = api.sim.getSimulationState()
    if state == api.sim.simulation_stopped:
        print("Starting simulation...")
        api.sim.startSimulation()
        time.sleep(1.0)
    
    # Find UR5 joints
    print("\nFinding UR5 robot joints...")
    joints = find_ur5_joints(api)
    if joints is None:
        print("✗ Could not find UR5 robot. Make sure it's loaded in the scene.")
        return False
    
    print(f"✓ Found {len(joints)} joints")
    
    # Read current position
    current = get_joint_positions(api, joints)
    print(f"\nCurrent joint positions: {[f'{p:.3f}' for p in current]}")
    
    # Define motion sequence (joint angles in radians)
    # These are example positions - adjust based on your scene
    
    # Home position (upright)
    home_pos = [0.0, -np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, 0.0]
    
    # Pre-pick position (above object)
    pre_pick_pos = [0.0, -np.pi/3, np.pi/3, -np.pi/2, -np.pi/2, 0.0]
    
    # Pick position (at object)
    pick_pos = [0.0, -np.pi/3, np.pi/2.5, -np.pi/2, -np.pi/2, 0.0]
    
    # Lift position
    lift_pos = [0.0, -np.pi/3, np.pi/3, -np.pi/2, -np.pi/2, 0.0]
    
    # Pre-place position (above bin)
    pre_place_pos = [np.pi/4, -np.pi/3, np.pi/3, -np.pi/2, -np.pi/2, 0.0]
    
    # Place position (at bin)
    place_pos = [np.pi/4, -np.pi/3, np.pi/2.5, -np.pi/2, -np.pi/2, 0.0]
    
    print("\n=== Starting Pick-and-Place Sequence ===\n")
    
    # Step 1: Move to home
    print("1. Moving to home position...")
    set_joint_positions(api, joints, home_pos)
    wait_for_motion(api, joints, home_pos)
    control_gripper(api, close=False)
    time.sleep(0.5)
    
    # Step 2: Move to pre-pick
    print("\n2. Moving to pre-pick position...")
    set_joint_positions(api, joints, pre_pick_pos)
    wait_for_motion(api, joints, pre_pick_pos)
    time.sleep(0.5)
    
    # Step 3: Move down to pick
    print("\n3. Moving down to pick...")
    set_joint_positions(api, joints, pick_pos)
    wait_for_motion(api, joints, pick_pos)
    time.sleep(0.5)
    
    # Step 4: Close gripper
    print("\n4. Closing gripper...")
    control_gripper(api, close=True)
    time.sleep(1.0)
    
    # Step 5: Lift object
    print("\n5. Lifting object...")
    set_joint_positions(api, joints, lift_pos)
    wait_for_motion(api, joints, lift_pos)
    time.sleep(0.5)
    
    # Step 6: Move to pre-place
    print("\n6. Moving to sorting bin...")
    set_joint_positions(api, joints, pre_place_pos)
    wait_for_motion(api, joints, pre_place_pos)
    time.sleep(0.5)
    
    # Step 7: Move down to place
    print("\n7. Moving down to place...")
    set_joint_positions(api, joints, place_pos)
    wait_for_motion(api, joints, place_pos)
    time.sleep(0.5)
    
    # Step 8: Open gripper
    print("\n8. Releasing object...")
    control_gripper(api, close=False)
    time.sleep(1.0)
    
    # Step 9: Return to home
    print("\n9. Returning to home...")
    set_joint_positions(api, joints, pre_place_pos)
    wait_for_motion(api, joints, pre_place_pos)
    set_joint_positions(api, joints, home_pos)
    wait_for_motion(api, joints, home_pos)
    
    print("\n✓ Pick-and-place sequence complete!")
    return True


def main():
    api, config = connect_from_config()
    if api is None:
        return
    
    try:
        success = run_pick_and_place_demo(api, config)
        if not success:
            print("\n✗ Demo failed. Check:")
            print("  - UR5 robot is loaded in scene")
            print("  - Objects are present on desk")
            print("  - Simulation is running")
    
    finally:
        print("\nDisconnecting...")
        api.disconnect()


if __name__ == "__main__":
    main()
