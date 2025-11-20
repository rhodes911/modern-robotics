"""
Inspect RG2 Gripper Structure
==============================

Load RG2 and analyze its internal structure to understand
how it achieves proper gripper motion.
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def main():
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Stop and create fresh scene
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    sim.closeScene()
    
    # Load RG2
    print("Loading RG2 gripper...")
    COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
    gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\RG2.ttm")
    print(f"RG2 base handle: {gripper}\n")
    
    # Get all objects in the RG2 hierarchy
    print("="*70)
    print("RG2 GRIPPER STRUCTURE")
    print("="*70)
    
    def print_tree(handle, indent=0):
        """Recursively print object tree"""
        try:
            alias = sim.getObjectAlias(handle)
            obj_type = sim.getObjectType(handle)
            
            type_names = {
                sim.object_shape_type: "SHAPE",
                sim.object_joint_type: "JOINT",
                sim.object_dummy_type: "DUMMY",
                sim.object_forcesensor_type: "FORCE_SENSOR",
            }
            type_str = type_names.get(obj_type, f"TYPE_{obj_type}")
            
            # For joints, get mode and limits
            extra_info = ""
            if obj_type == sim.object_joint_type:
                mode = sim.getJointMode(handle)
                mode_names = {0: "kinematic", 1: "ik", 2: "dependent", 3: "motion", 5: "passive"}
                mode_str = mode_names.get(mode[0], f"mode_{mode[0]}")
                
                joint_type = sim.getJointType(handle)
                jtype_names = {
                    sim.joint_revolute: "revolute",
                    sim.joint_prismatic: "prismatic",
                    sim.joint_spherical: "spherical"
                }
                jtype_str = jtype_names.get(joint_type, f"type_{joint_type}")
                
                cyclic, interval = sim.getJointInterval(handle)
                extra_info = f" [{jtype_str}, {mode_str}, limits: {interval}]"
            
            print(f"{'  '*indent}├─ {alias} ({type_str}){extra_info}")
            
            # Get children
            child_index = 0
            while True:
                child = sim.getObjectChild(handle, child_index)
                if child == -1:
                    break
                print_tree(child, indent + 1)
                child_index += 1
                
        except Exception as e:
            print(f"{'  '*indent}└─ Error: {e}")
    
    print_tree(gripper)
    
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)
    
    # Get the control joint
    try:
        control_joint = sim.getObject('/RG2/openCloseJoint')
        print(f"\n✓ Control Joint: openCloseJoint")
        print(f"  Handle: {control_joint}")
        
        # Get its properties
        mode = sim.getJointMode(control_joint)
        jtype = sim.getJointType(control_joint)
        cyclic, interval = sim.getJointInterval(control_joint)
        
        print(f"  Type: {'prismatic' if jtype == sim.joint_prismatic else 'revolute' if jtype == sim.joint_revolute else 'other'}")
        print(f"  Mode: {mode[0]}")
        print(f"  Limits: {interval}")
        
        # Get position
        pos = sim.getJointPosition(control_joint)
        print(f"  Current position: {pos:.6f}")
        
    except Exception as e:
        print(f"\n✗ Could not analyze control joint: {e}")


if __name__ == "__main__":
    main()
