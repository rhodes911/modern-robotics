"""
Simple RG2 Gripper Demo - Python Control
=========================================

The RG2 gripper is designed for direct programmatic control.
Unlike ROBOTIQ 85, it has a single control joint: openCloseJoint

Target positions:
- CLOSED: 0.0 (fully closed)
- OPEN: 0.085 (8.5cm opening)
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("RG2 Gripper - Python Control Demo")
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
    
    # Load RG2 gripper
    print("\nLoading RG2 gripper...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print("✓ Loaded")
    
    # Get the control joint
    print("\nGetting control joint...")
    control_joint = sim.getObject('/RG2/openCloseJoint')
    print("✓ openCloseJoint found")
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    
    # Configure joint for control
    print("\nConfiguring joint...")
    sim.setJointMode(control_joint, sim.jointmode_kinematic, 0)
    sim.setObjectInt32Param(control_joint, sim.jointintparam_motor_enabled, 1)
    sim.setJointTargetVelocity(control_joint, 0.1)
    sim.setJointTargetForce(control_joint, 20.0)
    print("✓ Configured")
    
    # Target positions
    OPEN_POS = 0.085   # 8.5 cm opening
    CLOSED_POS = 0.0   # Fully closed
    
    # Demo
    print("\n" + "="*70)
    print("DEMO: OPEN → CLOSE → OPEN → CLOSE")
    print("="*70)
    
    for cycle in range(2):
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle + 1}")
        print('='*70)
        
        # OPEN
        print("\n>>> OPENING gripper...")
        sim.setJointTargetPosition(control_joint, OPEN_POS)
        
        # Monitor progress
        for i in range(15):
            time.sleep(0.2)
            pos = sim.getJointPosition(control_joint)
            width_cm = pos * 100
            print(f"  [{(i+1)*0.2:.1f}s] Position: {pos:+.4f} rad  ({width_cm:5.2f} cm)")
            
            if abs(pos - OPEN_POS) < 0.001:
                print("  ✓ OPEN!")
                break
        
        time.sleep(1.0)
        
        # CLOSE
        print("\n>>> CLOSING gripper...")
        sim.setJointTargetPosition(control_joint, CLOSED_POS)
        
        # Monitor progress
        for i in range(15):
            time.sleep(0.2)
            pos = sim.getJointPosition(control_joint)
            width_cm = pos * 100
            print(f"  [{(i+1)*0.2:.1f}s] Position: {pos:+.4f} rad  ({width_cm:5.2f} cm)")
            
            if abs(pos - CLOSED_POS) < 0.001:
                print("  ✓ CLOSED!")
                break
        
        time.sleep(1.0)
    
    # Final state
    print("\n" + "="*70)
    print("✓ Demo Complete!")
    print("="*70)
    
    final_pos = sim.getJointPosition(control_joint)
    final_width = final_pos * 100
    print(f"\nFinal position: {final_pos:+.4f} rad ({final_width:.2f} cm)")
    print("\n✓ Full Python control achieved!")
    print("  Simulation still running. Stop manually when done.")


if __name__ == "__main__":
    main()
