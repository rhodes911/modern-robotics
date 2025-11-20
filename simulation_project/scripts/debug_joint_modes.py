"""
Debug script to check joint modes and understand why left joint won't close
"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    # Connect
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Wait for scene to load
    time.sleep(1)
    
    # Get joints (assuming custom gripper is loaded)
    try:
        left_joint = sim.getObject('/LeftJoint')
        right_joint = sim.getObject('/RightJoint')
        
        print("="*70)
        print("JOINT MODE ANALYSIS")
        print("="*70)
        
        # Check modes
        left_mode = sim.getJointMode(left_joint)
        right_mode = sim.getJointMode(right_joint)
        
        print(f"\nLeft Joint Mode: {left_mode[0]}")
        print(f"Right Joint Mode: {right_mode[0]}")
        print("\nMode Reference:")
        print("  0 = Force/torque (kinematic)")
        print("  1 = IK mode")
        print("  2 = Dependent")
        print("  3 = Motion mode")
        print("  5 = Passive (hybrid dynamics)")
        
        # Check intervals
        left_cyclic, left_interval = sim.getJointInterval(left_joint)
        right_cyclic, right_interval = sim.getJointInterval(right_joint)
        
        print(f"\nLeft Joint Interval: {left_interval} (cyclic: {left_cyclic})")
        print(f"Right Joint Interval: {right_interval} (cyclic: {right_cyclic})")
        
        # Check current positions
        left_pos = sim.getJointPosition(left_joint)
        right_pos = sim.getJointPosition(right_joint)
        
        print(f"\nCurrent Positions:")
        print(f"  Left: {left_pos:.6f} m ({left_pos*100:.2f} cm)")
        print(f"  Right: {right_pos:.6f} m ({right_pos*100:.2f} cm)")
        
        # Check motor enabled
        left_motor = sim.getObjectInt32Param(left_joint, sim.jointintparam_motor_enabled)
        right_motor = sim.getObjectInt32Param(right_joint, sim.jointintparam_motor_enabled)
        
        print(f"\nMotor Enabled:")
        print(f"  Left: {left_motor}")
        print(f"  Right: {right_motor}")
        
        # Try setting target positions
        print("\n" + "="*70)
        print("TESTING JOINT CONTROL")
        print("="*70)
        
        print("\nSetting left joint to 0.0 (closed)...")
        sim.setJointTargetPosition(left_joint, 0.0)
        time.sleep(1.0)
        left_pos = sim.getJointPosition(left_joint)
        print(f"  Result: {left_pos:.6f} m ({left_pos*100:.2f} cm)")
        
        print("\nSetting left joint to -0.04 (open)...")
        sim.setJointTargetPosition(left_joint, -0.04)
        time.sleep(1.0)
        left_pos = sim.getJointPosition(left_joint)
        print(f"  Result: {left_pos:.6f} m ({left_pos*100:.2f} cm)")
        
        print("\nSetting left joint back to 0.0 (closed)...")
        sim.setJointTargetPosition(left_joint, 0.0)
        time.sleep(1.0)
        left_pos = sim.getJointPosition(left_joint)
        print(f"  Result: {left_pos:.6f} m ({left_pos*100:.2f} cm)")
        
        print("\n" + "="*70)
        print("Analysis complete!")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the custom gripper scene is loaded and simulation is running!")

if __name__ == "__main__":
    main()
