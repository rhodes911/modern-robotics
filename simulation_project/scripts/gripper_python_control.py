"""
ROBOTIQ 85 Gripper - Direct Control (Script Disabled)
======================================================

This version disables the internal Lua script and takes full control.
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("ROBOTIQ 85 Direct Control Demo")
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
    
    # Create new scene
    print("Creating new scene...")
    sim.closeScene()
    
    # Load gripper
    print("Loading ROBOTIQ 85 gripper...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")
    print("✓ Gripper loaded")
    
    # CRITICAL: Find and disable the internal script that's fighting us
    print("\nDisabling internal Lua script...")
    try:
        # The script is typically attached to the base object
        script_handle = sim.getScript(sim.scripttype_customization, gripper)
        if script_handle != -1:
            # Disable the script
            sim.setScriptAttribute(script_handle, sim.scriptattribute_enabled, False)
            print("✓ Internal script disabled")
        else:
            print("  (No customization script found - good!)")
    except Exception as e:
        print(f"  Warning: Could not disable script: {e}")
    
    # Get joint handles
    print("\nGetting joint handles...")
    joints = {}
    joint_names = ['Ljoint1', 'Rjoint1', 'Ljoint2', 'Rjoint2', 'LactiveJoint', 'RactiveJoint']
    
    for name in joint_names:
        joints[name] = sim.getObject(f'/ROBOTIQ85/{name}')
        print(f"  ✓ {name}")
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    
    # Configure joints
    print("\nConfiguring joints for direct control...")
    for name, handle in joints.items():
        # Set to kinematic mode
        sim.setJointMode(handle, sim.jointmode_kinematic, 0)
        # Enable motor
        sim.setObjectInt32Param(handle, sim.jointintparam_motor_enabled, 1)
        # Set velocity and force
        sim.setJointTargetVelocity(handle, 1.0)  # Faster velocity
        sim.setJointTargetForce(handle, 50.0)     # More force
    
    print("✓ All joints configured")
    
    # Target positions
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
    print("DEMO: OPEN → CLOSE → OPEN")
    print("="*70)
    
    for cycle in range(2):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # OPEN
        print("\n>>> OPENING gripper...")
        for name, target in OPEN_POSITIONS.items():
            sim.setJointTargetPosition(joints[name], target)
        
        # Monitor progress
        for i in range(8):
            time.sleep(0.5)
            pos = sim.getJointPosition(joints['LactiveJoint'])
            print(f"  [{(i+1)*0.5:.1f}s] LactiveJoint: {pos:+7.4f} rad")
            if abs(pos - 0.794) < 0.01:
                print("  ✓ Target reached!")
                break
        
        time.sleep(1.0)  # Hold open
        
        # CLOSE
        print("\n>>> CLOSING gripper...")
        for name in joint_names:
            sim.setJointTargetPosition(joints[name], 0.0)
        
        # Monitor progress
        for i in range(8):
            time.sleep(0.5)
            pos = sim.getJointPosition(joints['LactiveJoint'])
            print(f"  [{(i+1)*0.5:.1f}s] LactiveJoint: {pos:+7.4f} rad")
            if abs(pos) < 0.01:
                print("  ✓ Target reached!")
                break
        
        time.sleep(1.0)  # Hold closed
    
    # Final state
    print("\n" + "="*70)
    print("FINAL JOINT POSITIONS:")
    print("="*70)
    for name, handle in joints.items():
        pos = sim.getJointPosition(handle)
        print(f"  {name:15s}: {pos:+7.4f} rad")
    
    print("\n✓ Demo complete!")
    print("  The gripper is under YOUR control now.")
    print("  Simulation still running - you can manually send more commands.")


if __name__ == "__main__":
    main()
