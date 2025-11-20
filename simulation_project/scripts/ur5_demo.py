"""
UR5 Pick and Place Demo
Makes the UR5 robot actually move and interact with objects
"""

import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from coppelia_api import CoppeliaSimConnection


def main():
    """Demo UR5 pick and place motion"""
    print("\n=== UR5 Pick-and-Place Demo ===\n")
    
    conn = CoppeliaSimConnection()
    
    if not conn.connect():
        print("Failed to connect to CoppeliaSim")
        return
    
    try:
        # Start simulation
        print("Starting simulation...")
        conn.start_simulation()
        time.sleep(0.5)
        
        # Get UR5 joint handles
        joint_names = [f'/UR5/joint' for _ in range(6)]
        joint_handles = []
        
        print("\nFinding UR5 joints...")
        for i in range(6):
            # Try different naming conventions
            possible_names = [
                f'UR5_joint{i+1}',
                f'/UR5/joint{i+1}', 
                f'UR5/joint{i+1}',
                f'joint{i+1}'
            ]
            
            handle = -1
            for name in possible_names:
                handle = conn.get_object_handle(name)
                if handle != -1:
                    joint_handles.append(handle)
                    print(f"  ✓ Found {name} (handle: {handle})")
                    break
            
            if handle == -1:
                print(f"  ⚠ Could not find joint {i+1}")
        
        if len(joint_handles) < 6:
            print(f"\n⚠ Only found {len(joint_handles)} joints")
            print("The robot may not move correctly")
        
        print(f"\n✓ Found {len(joint_handles)} UR5 joints")
        
        # Demo motions
        print("\n🤖 Starting robot motion demo...")
        print("Watch the robot in CoppeliaSim!\n")
        
        # Home position
        print("1. Moving to home position...")
        home_position = [0, -90, 90, -90, -90, 0]  # Degrees
        home_rad = [pos * 3.14159 / 180 for pos in home_position]
        
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, home_rad[i])
        
        time.sleep(3)
        
        # Reach forward
        print("2. Reaching forward over desk...")
        reach_position = [0, -60, 60, -90, -90, 0]
        reach_rad = [pos * 3.14159 / 180 for pos in reach_position]
        
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, reach_rad[i])
        
        time.sleep(3)
        
        # Reach down (simulating picking)
        print("3. Moving down to pick object...")
        pick_position = [0, -45, 80, -125, -90, 0]
        pick_rad = [pos * 3.14159 / 180 for pos in pick_position]
        
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, pick_rad[i])
        
        time.sleep(3)
        
        # Lift up
        print("4. Lifting object...")
        lift_position = [0, -60, 60, -90, -90, 0]
        lift_rad = [pos * 3.14159 / 180 for pos in lift_position]
        
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, lift_rad[i])
        
        time.sleep(3)
        
        # Move to sorting zone
        print("5. Moving to sorting zone...")
        place_position = [45, -60, 60, -90, -90, 0]
        place_rad = [pos * 3.14159 / 180 for pos in place_position]
        
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, place_rad[i])
        
        time.sleep(3)
        
        # Return home
        print("6. Returning home...")
        for i, handle in enumerate(joint_handles):
            conn.set_joint_target_position(handle, home_rad[i])
        
        time.sleep(3)
        
        print("\n✓ Demo sequence complete!")
        print("\nThe UR5 should have:")
        print("  - Moved to home position")
        print("  - Reached over the desk")
        print("  - Moved down to pick")
        print("  - Lifted back up")
        print("  - Moved to sorting zone")
        print("  - Returned home")
        
        print("\nKeeping simulation running for 10 more seconds...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\nStopping simulation...")
        conn.stop_simulation()
        conn.disconnect()
        print("✓ Demo complete!")


if __name__ == "__main__":
    main()
