"""
Quick script to inspect ROBOTIQ 85 structure
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Stop sim if running
if sim.getSimulationState() != sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        time.sleep(0.1)

# Clear scene
try:
    all_objects = sim.getObjects(sim.handle_scene, sim.object_shape_type)
    if isinstance(all_objects, list):
        for obj in all_objects:
            try:
                sim.removeObject(obj)
            except:
                pass
except:
    pass

# Load ROBOTIQ 85
COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")

print("ROBOTIQ 85 structure:")
print("=" * 60)

def print_tree(handle, indent=0):
    """Recursively print object tree."""
    try:
        name = sim.getObjectAlias(handle)
        obj_type = sim.getObjectType(handle)
        
        type_names = {
            sim.object_shape_type: "SHAPE",
            sim.object_joint_type: "JOINT",
            sim.object_dummy_type: "DUMMY",
            sim.sceneobject_dummy: "DUMMY",
        }
        type_str = type_names.get(obj_type, f"TYPE_{obj_type}")
        
        print("  " * indent + f"├─ {name} ({type_str}, handle: {handle})")
        
        # If it's a joint, print its properties
        if obj_type == sim.object_joint_type:
            try:
                pos = sim.getJointPosition(handle)
                mode = sim.getJointMode(handle)
                print("  " * indent + f"   └─ Position: {pos:.4f}, Mode: {mode}")
            except:
                pass
        
        # Get children
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(handle, idx)
                if child == -1:
                    break
                print_tree(child, indent + 1)
                idx += 1
            except:
                break
    except Exception as e:
        print(f"Error: {e}")

print_tree(gripper)

print("\n" + "=" * 60)
print("Looking for joints with 'finger' or 'motor' in name...")

def search_joints(handle):
    """Find all joints."""
    joints = []
    
    def search(h):
        try:
            name = sim.getObjectAlias(h)
            obj_type = sim.getObjectType(h)
            
            if obj_type == sim.object_joint_type:
                joints.append((h, name))
            
            idx = 0
            while True:
                try:
                    child = sim.getObjectChild(h, idx)
                    if child == -1:
                        break
                    search(child)
                    idx += 1
                except:
                    break
        except:
            pass
    
    search(handle)
    return joints

all_joints = search_joints(gripper)
print(f"\nFound {len(all_joints)} joints:")
for handle, name in all_joints:
    try:
        pos = sim.getJointPosition(handle)
        print(f"  - {name} (handle: {handle}, pos: {pos:.4f})")
    except:
        print(f"  - {name} (handle: {handle})")
