"""
Simple ROBOTIQ 85 Gripper Open/Close Demo
==========================================

Loads gripper in scene and controls it directly using Python.
Based on monitoring results - we know exact target positions.
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("ROBOTIQ 85 Gripper Demo - Open/Close")
    print("="*70)
    
    # Connect
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop any running simulation
    if sim.getSimulationState() != sim.simulation_stopped:
        print("\nStopping existing simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    # Close any existing scene and create new one
    print("Creating new scene...")
    sim.closeScene()
    
    # Load gripper into scene (use absolute path)
    print("Loading ROBOTIQ 85 gripper...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")
    print("✓ Gripper loaded")
    
    # Get all 6 joint handles (note: base object is /ROBOTIQ85, not /ROBOTIQ 85)
    print("\nGetting joint handles...")
    joints = {}
    joint_names = ['Ljoint1', 'Rjoint1', 'Ljoint2', 'Rjoint2', 'LactiveJoint', 'RactiveJoint']
    
    for name in joint_names:
        joints[name] = sim.getObject(f'/ROBOTIQ85/{name}')
        print(f"  ✓ {name}")
    
    # Start simulation first
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    
    # Configure all joints for direct control
    print("\nConfiguring joints for control...")
    for name, handle in joints.items():
        # Set to kinematic mode
        sim.setJointMode(handle, sim.jointmode_kinematic, 0)
        # Enable motor
        sim.setObjectInt32Param(handle, sim.jointintparam_motor_enabled, 1)
        # Set max velocity (use setJointTargetVelocity instead of setObjectFloatParam)
        sim.setJointTargetVelocity(handle, 0.5)
        # Set force limit
        sim.setJointTargetForce(handle, 20.0)
    
    print("✓ All joints configured")
    
    # Define target positions (from monitoring data)
    OPEN_POSITIONS = {
        'Ljoint1': +0.787,
        'Rjoint1': +0.803,
        'Ljoint2': -0.779,
        'Rjoint2': -0.801,
        'LactiveJoint': +0.794,
        'RactiveJoint': +0.803
    }
    
    CLOSED_POSITIONS = {name: 0.0 for name in joint_names}
    
    # Demo sequence
    print("\n" + "="*70)
    print("DEMO SEQUENCE: OPEN → CLOSE → OPEN → CLOSE")
    print("="*70)
    
    for cycle in range(2):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # OPEN
        print("\n>>> OPENING gripper...")
        for name, target in OPEN_POSITIONS.items():
            sim.setJointTargetPosition(joints[name], target)
        
        # Wait and show progress
        for i in range(6):
            time.sleep(0.5)
            pos = sim.getJointPosition(joints['LactiveJoint'])
            print(f"  [{(i+1)*0.5:.1f}s] LactiveJoint: {pos:+7.4f} rad")
        
        print("✓ OPEN")
        
        # CLOSE
        print("\n>>> CLOSING gripper...")
        for name, target in CLOSED_POSITIONS.items():
            sim.setJointTargetPosition(joints[name], target)
        
        # Wait and show progress
        for i in range(6):
            time.sleep(0.5)
            pos = sim.getJointPosition(joints['LactiveJoint'])
            print(f"  [{(i+1)*0.5:.1f}s] LactiveJoint: {pos:+7.4f} rad")
        
        print("✓ CLOSED")
    
    # Final state
    print("\n" + "="*70)
    print("FINAL POSITIONS:")
    print("="*70)
    for name, handle in joints.items():
        pos = sim.getJointPosition(handle)
        print(f"  {name:15s}: {pos:+7.4f} rad")
    
    print("\n✓ Demo complete - gripper will remain in scene")
    print("  (Simulation still running - stop manually or close scene)")


if __name__ == "__main__":
    main()
