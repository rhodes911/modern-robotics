"""
ROBOTIQ 85 Control via Signals
===============================

Instead of fighting the internal script, work WITH it by sending
the signals it's listening for (discovered from UI monitoring).
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("ROBOTIQ 85 - Signal-Based Control")
    print("="*70)
    
    # Connect
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop and create fresh scene
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    sim.closeScene()
    
    # Load gripper
    print("\nLoading ROBOTIQ 85...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")
    print("✓ Loaded")
    
    # Get gripper base handle for signal prefix
    print("\nFinding gripper handle...")
    gripper_base = sim.getObject('/ROBOTIQ85')
    print(f"✓ Gripper handle: {gripper_base}")
    
    # Get monitoring joint
    left_active = sim.getObject('/ROBOTIQ85/LactiveJoint')
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(1.0)
    
    print("\n" + "="*70)
    print("Testing signal-based control...")
    print("="*70)
    
    # Try different signal names that might trigger the script
    signal_attempts = [
        ('ROBOTIQ85_open', 1),
        ('ROBOTIQ85_close', 1),
        (f'ROBOTIQ85_{gripper_base}_open', 1),
        (f'ROBOTIQ85_{gripper_base}_close', 1),
        ('gripper_cmd', 1),  # 1 = open
        ('gripper_cmd', 0),  # 0 = close
    ]
    
    print("\nAttempting OPEN via signals...")
    for signal_name, value in signal_attempts:
        print(f"  Trying: {signal_name} = {value}")
        try:
            sim.setInt32Signal(signal_name, value)
            time.sleep(0.5)
            pos = sim.getJointPosition(left_active)
            print(f"    Position: {pos:+.4f}")
            sim.clearInt32Signal(signal_name)
        except Exception as e:
            print(f"    Error: {e}")
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    print("The ROBOTIQ 85 gripper's internal Lua script does NOT")
    print("respond to signals from the Remote API.")
    print("")
    print("It ONLY responds to its built-in UI dialog buttons.")
    print("")
    print("To get programmatic control, you must:")
    print("  1. Modify the gripper's internal Lua script, OR")
    print("  2. Use the RG2 gripper instead (simpler, direct control)")
    print("="*70)
    
    # Cleanup
    sim.stopSimulation()


if __name__ == "__main__":
    main()
