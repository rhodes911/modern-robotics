"""
Simple Custom Gripper - Full Python Control
============================================

Creates a basic 2-finger gripper from scratch using primitive shapes.
No Lua scripts - complete Python control!
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def create_simple_gripper(sim):
    """
    Create a simple gripper from basic shapes.
    Returns the base handle and control joint handle.
    """
    print("\nBuilding custom gripper from primitives...")
    
    # Create base (palm) - wider base
    base = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.08, 0.04, 0.02])
    sim.setObjectPosition(base, -1, [0, 0, 0.1])
    sim.setObjectAlias(base, "GripperBase")
    print("  ✓ Base created")
    
    # Create fingers - HORIZONTAL bars for gripping (8cm long, 1.5cm wide, 2cm tall)
    left_finger = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.08, 0.015, 0.02])
    sim.setObjectAlias(left_finger, "LeftFinger")
    sim.setShapeColor(left_finger, None, sim.colorcomponent_ambient_diffuse, [0.9, 0.3, 0.3])
    
    right_finger = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.08, 0.015, 0.02])
    sim.setObjectAlias(right_finger, "RightFinger")
    sim.setShapeColor(right_finger, None, sim.colorcomponent_ambient_diffuse, [0.3, 0.3, 0.9])
    print("  ✓ Fingers created")
    
    # Create prismatic joints on OPPOSITE sides of base
    # Left joint starts on LEFT side, moves inward (positive = toward center)
    left_joint = sim.createJoint(sim.joint_prismatic, sim.jointmode_kinematic, 0)
    sim.setObjectPosition(left_joint, base, [0.03, -0.02, 0.01])  # LEFT side
    sim.setObjectOrientation(left_joint, base, [0, 0, -1.5708])  # Point toward center
    sim.setObjectAlias(left_joint, "LeftJoint")
    
    # Right joint starts on RIGHT side, moves inward (positive = toward center)
    right_joint = sim.createJoint(sim.joint_prismatic, sim.jointmode_kinematic, 0)
    sim.setObjectPosition(right_joint, base, [0.03, +0.02, 0.01])  # RIGHT side
    sim.setObjectOrientation(right_joint, base, [0, 0, 1.5708])  # Point toward center
    sim.setObjectAlias(right_joint, "RightJoint")
    print("  ✓ Joints created")
    
    # Configure joints - BOTH move in POSITIVE direction (0 = open, 0.04 = closed)
    # Since joints point toward center, positive motion closes the gripper
    sim.setJointPosition(left_joint, 0.0)  # Start open
    sim.setJointPosition(right_joint, 0.0)  # Start open
    
    # Left joint: 0 (open/out) to 0.04 (closed/in)
    sim.setObjectInt32Param(left_joint, sim.jointintparam_motor_enabled, 1)
    sim.setObjectInt32Param(left_joint, sim.jointintparam_ctrl_enabled, 1)
    sim.setJointTargetVelocity(left_joint, 999.0)
    sim.setJointTargetForce(left_joint, 100.0)
    sim.setJointInterval(left_joint, False, [0.0, 0.04])
    
    # Right joint: 0 (open/out) to 0.04 (closed/in)
    sim.setObjectInt32Param(right_joint, sim.jointintparam_motor_enabled, 1)
    sim.setObjectInt32Param(right_joint, sim.jointintparam_ctrl_enabled, 1)
    sim.setJointTargetVelocity(right_joint, 999.0)
    sim.setJointTargetForce(right_joint, 100.0)
    sim.setJointInterval(right_joint, False, [0.0, 0.04])
    
    print("  ✓ Joint properties set")
    
    # Assemble hierarchy
    sim.setObjectParent(left_joint, base, True)
    sim.setObjectParent(right_joint, base, True)
    sim.setObjectParent(left_finger, left_joint, True)
    sim.setObjectParent(right_finger, right_joint, True)
    
    # Position fingers extending forward from joints
    sim.setObjectPosition(left_finger, left_joint, [0, 0, 0])
    sim.setObjectPosition(right_finger, right_joint, [0, 0, 0])
    print("  ✓ Hierarchy assembled")
    
    # Make fingers collidable/respondable
    for finger in [left_finger, right_finger]:
        sim.setObjectInt32Param(finger, sim.shapeintparam_respondable, 1)
    
    print("✓ Custom gripper created!")
    
    return base, left_joint, right_joint


def main():
    print("="*70)
    print("Custom Gripper - Full Python Control")
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
    
    # Create gripper
    base, left_joint, right_joint = create_simple_gripper(sim)
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    print("✓ Simulation running")
    
    # Target positions (in meters for prismatic joints)
    # Both joints move in same direction: 0 = open (out), 0.04 = closed (in toward center)
    OPEN_POS = 0.0    # Both fingers out
    CLOSED_POS = 0.04  # Both fingers in (toward center)
    
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
        sim.setJointTargetPosition(left_joint, OPEN_POS)
        sim.setJointTargetPosition(right_joint, OPEN_POS)
        
        # Monitor progress
        for i in range(10):
            time.sleep(0.3)
            left_pos = sim.getJointPosition(left_joint)
            right_pos = sim.getJointPosition(right_joint)
            total_width = abs(left_pos) + abs(right_pos)  # Total opening width
            total_width_cm = total_width * 100  # Convert to cm
            
            print(f"  [{(i+1)*0.3:.1f}s] L:{left_pos*100:+5.2f}cm  R:{right_pos*100:+5.2f}cm  |  Width:{total_width_cm:5.2f}cm")
            
            if abs(left_pos - OPEN_POS) < 0.001 and abs(right_pos - OPEN_POS) < 0.001:
                print("  ✓ OPEN!")
                break
        
        time.sleep(1.0)
        
        # CLOSE
        print("\n>>> CLOSING gripper...")
        sim.setJointTargetPosition(left_joint, CLOSED_POS)
        sim.setJointTargetPosition(right_joint, CLOSED_POS)
        
        # Monitor progress
        for i in range(10):
            time.sleep(0.3)
            left_pos = sim.getJointPosition(left_joint)
            right_pos = sim.getJointPosition(right_joint)
            total_width = abs(left_pos) + abs(right_pos)  # Total opening width
            total_width_cm = total_width * 100  # Convert to cm
            
            print(f"  [{(i+1)*0.3:.1f}s] L:{left_pos*100:+5.2f}cm  R:{right_pos*100:+5.2f}cm  |  Width:{total_width_cm:5.2f}cm")
            
            if abs(left_pos - CLOSED_POS) < 0.001 and abs(right_pos - CLOSED_POS) < 0.001:
                print("  ✓ CLOSED!")
                break
        
        time.sleep(1.0)
    
    # Final state
    print("\n" + "="*70)
    print("✓ Demo Complete - Full Python Control!")
    print("="*70)
    
    left_pos = sim.getJointPosition(left_joint)
    right_pos = sim.getJointPosition(right_joint)
    print(f"\nFinal: Left={left_pos*100:.2f}cm  Right={right_pos*100:.2f}cm")
    print("\n✓ This gripper is under YOUR complete control!")
    print("  No Lua scripts interfering.")
    print("  Simulation still running - stop manually when done.")


if __name__ == "__main__":
    main()
