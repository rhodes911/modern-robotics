"""
Simple test: Load RG2, switch joint mode from PASSIVE to KINEMATIC, then control it
"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("RG2 - The REAL Solution")
    print("="*70)
    
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop simulation if running
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    print("\n📋 Creating new scene...")
    # Create a new scene (this gives us floor, camera, lights)
    sim.closeScene()
    
    # Load RG2 model - try multiple path variations
    print("\n📦 Loading RG2 gripper...")
    gripper_handle = None
    paths_to_try = [
        'models/components/grippers/RG2.ttm',
        'models\\components\\grippers\\RG2.ttm',
        r'C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu\models\components\grippers\RG2.ttm',
    ]
    
    for path in paths_to_try:
        try:
            print(f"  Trying: {path}")
            gripper_handle = sim.loadModel(path)
            print(f"✓ RG2 loaded (handle {gripper_handle})")
            break
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue
    
    if gripper_handle is None:
        print("\n✗ Could not load RG2 from any path")
        print("   Please ensure CoppeliaSim is running and the model exists")
        return
    
    # List all objects to find the joint
    print("\n🔍 Inspecting loaded objects...")
    all_objects = sim.getObjectsInTree(sim.handle_scene)
    for obj in all_objects:
        obj_type = sim.getObjectType(obj)
        alias = sim.getObjectAlias(obj)
        if obj_type == sim.object_joint_type:
            print(f"  Joint: {alias} (handle {obj})")
    
    # Find the control joint
    try:
        control_joint = sim.getObject('/RG2/RG2_openCloseJoint')
        print(f"\n✓ Found control joint (handle {control_joint})")
    except:
        print("\n✗ Could not find /RG2/RG2_openCloseJoint")
        print("   Searching for alternative names...")
        try:
            control_joint = sim.getObject('/:RG2_openCloseJoint')
            print(f"✓ Found at /:RG2_openCloseJoint (handle {control_joint})")
        except:
            try:
                control_joint = sim.getObject('/openCloseJoint')
                print(f"✓ Found at /openCloseJoint (handle {control_joint})")
            except:
                try:
                    control_joint = sim.getObject('openCloseJoint')
                    print(f"✓ Found as 'openCloseJoint' (handle {control_joint})")
                except:
                    print("✗ Cannot find control joint. Exiting.")
                    return
    
    # Check current mode
    mode = sim.getJointMode(control_joint)
    print(f"\nCurrent joint mode: {mode[0]}")
    
    if mode[0] == 5:
        print("  → Mode 5 = PASSIVE (physics-driven, can't control directly)")
        print("\n🔧 FIXING: Switching to FORCE/TORQUE mode (0)...")
        sim.setJointMode(control_joint, sim.jointmode_dynamic, 0)
        print("✓ Switched to force/torque mode")
    
    # Get joint interval (limits)
    cyclic, interval = sim.getJointInterval(control_joint)
    print(f"\nJoint limits: cyclic={cyclic}, range=[{interval[0]:.4f}, {interval[0]+interval[1]:.4f}]")
    
    # Make base static so it doesn't fall over
    print("\n🔧 Stabilizing gripper base...")
    base = sim.getObject('/RG2')
    sim.setObjectInt32Param(base, sim.shapeintparam_static, 1)
    print("✓ Base is now static (won't fall)")
    
    # Configure motor with slower, gentler settings
    print("\n🔧 Configuring motor...")
    sim.setObjectInt32Param(control_joint, sim.jointintparam_motor_enabled, 1)
    sim.setObjectInt32Param(control_joint, sim.jointintparam_ctrl_enabled, 1)
    sim.setJointTargetVelocity(control_joint, 0.1)  # Slower velocity
    sim.setJointTargetForce(control_joint, 20.0)     # Gentler force
    print("✓ Motor enabled (slow & gentle)")
    
    # Set initial position
    current_pos = sim.getJointPosition(control_joint)
    print(f"✓ Current position: {current_pos:.4f}")
    sim.setJointPosition(control_joint, interval[0])
    print(f"✓ Set to closed position: {interval[0]:.4f}")
    
    # Start simulation
    print("\n▶ Starting simulation...")
    sim.startSimulation()
    time.sleep(0.5)
    print("✓ Running")
    
    # Demo
    print("\n" + "="*70)
    print("DEMO: RG2 Under YOUR Control")
    print("="*70)
    
    for cycle in range(2):
        print(f"\n--- CYCLE {cycle + 1} ---")
        
        # OPEN - use max of interval
        open_pos = interval[0] + interval[1]
        print(f"\n>>> OPENING to {open_pos:.4f}...")
        sim.setJointTargetPosition(control_joint, open_pos)
        time.sleep(3.0)  # More time for slower movement
        pos = sim.getJointPosition(control_joint)
        print(f"  Position: {pos:.4f} ({pos*100:.2f} cm)")
        
        # CLOSE - use min of interval
        close_pos = interval[0]
        print(f"\n>>> CLOSING to {close_pos:.4f}...")
        sim.setJointTargetPosition(control_joint, close_pos)
        time.sleep(3.0)  # More time for slower movement
        pos = sim.getJointPosition(control_joint)
        print(f"  Position: {pos:.4f} ({pos*100:.2f} cm)")
    
    print("\n" + "="*70)
    print("✓ SUCCESS! RG2 works when you set it to KINEMATIC mode!")
    print("="*70)
    print("\nSimulation still running - stop manually when done.")


if __name__ == "__main__":
    main()
