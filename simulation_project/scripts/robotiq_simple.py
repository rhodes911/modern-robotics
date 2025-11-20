"""
ROBOTIQ 85 - Simple Control via Active Joints Only
===================================================

Key insight: The finger joints (Ljoint1/2, Rjoint1/2) are PASSIVE/DEPENDENT.
They follow the active joints automatically through mechanical linkages.

We only need to control: LactiveJoint and RactiveJoint
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("ROBOTIQ 85 - Active Joint Control")
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
    
    # Get ONLY the active joints (the ones we should control)
    print("\nGetting active joint handles...")
    left_active = sim.getObject('/ROBOTIQ85/LactiveJoint')
    right_active = sim.getObject('/ROBOTIQ85/RactiveJoint')
    print("✓ LactiveJoint")
    print("✓ RactiveJoint")
    
    # Also get passive joints for monitoring (don't control these!)
    left_finger1 = sim.getObject('/ROBOTIQ85/Ljoint1')
    right_finger1 = sim.getObject('/ROBOTIQ85/Rjoint1')
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    
    # Configure ONLY active joints
    print("\nConfiguring active joints...")
    for handle in [left_active, right_active]:
        sim.setJointMode(handle, sim.jointmode_kinematic, 0)
        sim.setObjectInt32Param(handle, sim.jointintparam_motor_enabled, 1)
        sim.setJointTargetVelocity(handle, 0.5)
        sim.setJointTargetForce(handle, 20.0)
    print("✓ Configured")
    
    # Target positions (from monitoring data)
    OPEN_POS = 0.794  # LactiveJoint target when open
    CLOSED_POS = 0.0
    
    # Demo
    print("\n" + "="*70)
    print("DEMO: OPEN → CLOSE → OPEN → CLOSE")
    print("="*70)
    
    for cycle in range(2):
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle + 1}")
        print('='*70)
        
        # OPEN
        print("\n>>> OPENING...")
        sim.setJointTargetPosition(left_active, OPEN_POS)
        sim.setJointTargetPosition(right_active, OPEN_POS)
        
        # Wait and monitor
        for i in range(10):
            time.sleep(0.3)
            try:
                l_active = sim.getJointPosition(left_active)
                r_active = sim.getJointPosition(right_active)
                l_finger = sim.getJointPosition(left_finger1)
                r_finger = sim.getJointPosition(right_finger1)
                
                print(f"  [{(i+1)*0.3:.1f}s] Active: L={l_active:+.3f} R={r_active:+.3f}  |  "
                      f"Finger: L={l_finger:+.3f} R={r_finger:+.3f}")
                
                # Check if reached target
                if abs(l_active - OPEN_POS) < 0.05 and abs(r_active - OPEN_POS) < 0.05:
                    print("  ✓ OPEN target reached!")
                    break
            except Exception as e:
                print(f"  Error reading position: {e}")
                break
        
        time.sleep(1.0)
        
        # CLOSE
        print("\n>>> CLOSING...")
        sim.setJointTargetPosition(left_active, CLOSED_POS)
        sim.setJointTargetPosition(right_active, CLOSED_POS)
        
        # Wait and monitor
        for i in range(10):
            time.sleep(0.3)
            try:
                l_active = sim.getJointPosition(left_active)
                r_active = sim.getJointPosition(right_active)
                l_finger = sim.getJointPosition(left_finger1)
                r_finger = sim.getJointPosition(right_finger1)
                
                print(f"  [{(i+1)*0.3:.1f}s] Active: L={l_active:+.3f} R={r_active:+.3f}  |  "
                      f"Finger: L={l_finger:+.3f} R={r_finger:+.3f}")
                
                # Check if reached target
                if abs(l_active) < 0.05 and abs(r_active) < 0.05:
                    print("  ✓ CLOSED target reached!")
                    break
            except Exception as e:
                print(f"  Error reading position: {e}")
                break
        
        time.sleep(1.0)
    
    print("\n" + "="*70)
    print("✓ Demo Complete!")
    print("="*70)
    print("\nFINAL STATE:")
    try:
        print(f"  LactiveJoint:  {sim.getJointPosition(left_active):+7.4f} rad")
        print(f"  RactiveJoint:  {sim.getJointPosition(right_active):+7.4f} rad")
        print(f"  Ljoint1:       {sim.getJointPosition(left_finger1):+7.4f} rad")
        print(f"  Rjoint1:       {sim.getJointPosition(right_finger1):+7.4f} rad")
    except:
        print("  (Could not read final state)")
    
    print("\nSimulation still running. Stop manually when done.")


if __name__ == "__main__":
    main()
