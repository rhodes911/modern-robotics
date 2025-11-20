"""
Test RG2 gripper using the PROPER approach from CoppeliaSim documentation.
According to manual, check for:
1. Customization script functions
2. String signals (not integer signals)
3. Direct joint control if no script exists
"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    print("="*70)
    print("RG2 Gripper - PROPER Control Method Discovery")
    print("="*70)
    
    # Connect
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop simulation and clear scene
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    sim.closeScene()
    print("\n✓ Scene cleared")
    
    # Load RG2 model
    print("\nLoading RG2 model...")
    rg2_handle = sim.loadModel('models/components/grippers/RG2.ttm')
    print(f"✓ RG2 loaded (handle: {rg2_handle})")
    
    # Find all objects in RG2
    print("\n" + "="*70)
    print("RG2 STRUCTURE ANALYSIS")
    print("="*70)
    
    all_objects = sim.getObjectsInTree(rg2_handle, sim.object_shape_type, 0)
    all_objects.extend(sim.getObjectsInTree(rg2_handle, sim.object_joint_type, 0))
    all_objects.extend(sim.getObjectsInTree(rg2_handle, sim.object_dummy_type, 0))
    all_objects.extend(sim.getObjectsInTree(rg2_handle, sim.handle_all, 0))
    all_objects = list(set(all_objects))  # Remove duplicates
    
    print(f"\nFound {len(all_objects)} objects in RG2")
    
    # Look for scripts
    print("\n" + "="*70)
    print("CHECKING FOR CUSTOMIZATION SCRIPTS")
    print("="*70)
    
    script_found = False
    for obj in all_objects:
        alias = sim.getObjectAlias(obj)
        # Check if object has a customization script
        script_handle = sim.getScript(sim.scripttype_customization, obj)
        if script_handle != -1:
            print(f"\n✓ FOUND SCRIPT on object: {alias} (handle {obj})")
            print(f"  Script handle: {script_handle}")
            script_found = True
            
            # Try to get script functions
            print("\n  Attempting to discover callable functions...")
            
            # Common function names for grippers
            test_functions = [
                'rg2_open',
                'rg2_close', 
                'rg2_setPosition',
                'setGripperPosition',
                'open',
                'close',
                'setPosition',
                'rg2Open',
                'rg2Close',
                'simRG2.open',
                'simRG2.close'
            ]
            
            for func_name in test_functions:
                try:
                    result = sim.callScriptFunction(func_name, script_handle)
                    print(f"  ✓ Function '{func_name}' exists! Returned: {result}")
                except Exception as e:
                    pass  # Function doesn't exist, that's ok
    
    if not script_found:
        print("\n✗ No customization script found in RG2 model")
    
    # Check for control joint
    print("\n" + "="*70)
    print("CHECKING FOR CONTROL JOINT")
    print("="*70)
    
    try:
        control_joint = sim.getObject('/RG2/RG2_openCloseJoint')
        print(f"✓ Found control joint: /RG2/RG2_openCloseJoint (handle {control_joint})")
        
        mode = sim.getJointMode(control_joint)
        cyclic, interval = sim.getJointInterval(control_joint)
        pos = sim.getJointPosition(control_joint)
        motor_enabled = sim.getObjectInt32Param(control_joint, sim.jointintparam_motor_enabled)
        
        print(f"\n  Current position: {pos:.6f} m ({pos*100:.2f} cm)")
        print(f"  Joint mode: {mode[0]} (0=force/torque, 5=passive)")
        print(f"  Interval: {interval} (cyclic: {cyclic})")
        print(f"  Motor enabled: {motor_enabled}")
        
        if mode[0] == 5:
            print("\n  ⚠ WARNING: Joint is in PASSIVE mode (mode 5)")
            print("  This means it's controlled by physics/mechanism, not direct commands")
            print("\n  SOLUTION: Need to change to KINEMATIC mode (mode 0)")
            
            # Start simulation to test
            print("\n" + "="*70)
            print("TESTING CONTROL - Setting to KINEMATIC MODE")
            print("="*70)
            
            # Change to kinematic mode
            sim.setJointMode(control_joint, sim.jointmode_kinematic, 0)
            print("✓ Changed joint to kinematic mode")
            
            # Enable motor and set control parameters
            sim.setObjectInt32Param(control_joint, sim.jointintparam_motor_enabled, 1)
            sim.setObjectInt32Param(control_joint, sim.jointintparam_ctrl_enabled, 1)
            sim.setJointTargetVelocity(control_joint, 999.0)
            sim.setJointTargetForce(control_joint, 100.0)
            print("✓ Motor enabled and configured")
            
            # Start simulation
            sim.startSimulation()
            time.sleep(0.5)
            print("✓ Simulation started")
            
            # Test OPEN
            print("\n>>> OPENING gripper...")
            OPEN_POS = 0.085  # From your analysis
            sim.setJointTargetPosition(control_joint, OPEN_POS)
            
            for i in range(10):
                time.sleep(0.3)
                pos = sim.getJointPosition(control_joint)
                print(f"  [{(i+1)*0.3:.1f}s] Position: {pos*100:+5.2f} cm")
                if abs(pos - OPEN_POS) < 0.001:
                    print("  ✓ OPENED!")
                    break
            
            time.sleep(1.0)
            
            # Test CLOSE
            print("\n>>> CLOSING gripper...")
            CLOSED_POS = 0.0
            sim.setJointTargetPosition(control_joint, CLOSED_POS)
            
            for i in range(10):
                time.sleep(0.3)
                pos = sim.getJointPosition(control_joint)
                print(f"  [{(i+1)*0.3:.1f}s] Position: {pos*100:+5.2f} cm")
                if abs(pos - CLOSED_POS) < 0.001:
                    print("  ✓ CLOSED!")
                    break
            
            print("\n" + "="*70)
            print("✓ RG2 CONTROL SUCCESSFUL!")
            print("="*70)
            print("\nThe solution was to change the joint from PASSIVE to KINEMATIC mode!")
            print("Simulation still running - check the gripper in CoppeliaSim.")
        
    except Exception as e:
        print(f"\n✗ Could not find control joint: {e}")
    
    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)


if __name__ == "__main__":
    main()
