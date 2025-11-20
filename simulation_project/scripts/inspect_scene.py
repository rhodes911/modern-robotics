"""
Inspect Current CoppeliaSim Scene
Reads everything in your manually created scene and exports the structure
"""

import json
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def inspect_object(sim, handle, depth=0):
    """Recursively inspect an object and its children"""
    indent = "  " * depth
    
    try:
        alias = sim.getObjectAlias(handle)
        obj_type = sim.getObjectType(handle)
        position = sim.getObjectPosition(handle, -1)
        orientation = sim.getObjectOrientation(handle, -1)
        
        type_names = {
            sim.object_shape_type: "SHAPE",
            sim.object_joint_type: "JOINT",
            sim.object_dummy_type: "DUMMY",
            sim.object_camera_type: "CAMERA",
            sim.object_light_type: "LIGHT",
            sim.object_mirror_type: "MIRROR",
            sim.object_octree_type: "OCTREE",
            sim.object_pointcloud_type: "POINTCLOUD",
            sim.object_graph_type: "GRAPH",
            sim.object_forcesensor_type: "FORCESENSOR",
            sim.object_visionsensor_type: "VISIONSENSOR",
            sim.object_proximitysensor_type: "PROXIMITYSENSOR"
        }
        
        type_name = type_names.get(obj_type, f"TYPE_{obj_type}")
        
        info = {
            "handle": handle,
            "alias": alias,
            "type": type_name,
            "position": [round(p, 4) for p in position],
            "orientation": [round(o, 4) for o in orientation]
        }
        
        # Get joint info if it's a joint
        if obj_type == sim.object_joint_type:
            try:
                joint_pos = sim.getJointPosition(handle)
                joint_mode = sim.getJointMode(handle)
                info["joint_position"] = round(joint_pos, 4)
                info["joint_mode"] = joint_mode
            except:
                pass
        
        # Get parent
        try:
            parent = sim.getObjectParent(handle)
            if parent != -1:
                parent_alias = sim.getObjectAlias(parent)
                info["parent"] = f"{parent_alias} ({parent})"
        except:
            pass
        
        print(f"{indent}{alias} [{type_name}] (handle: {handle})")
        print(f"{indent}  Position: {info['position']}")
        print(f"{indent}  Orientation: {info['orientation']}")
        if "parent" in info:
            print(f"{indent}  Parent: {info['parent']}")
        if obj_type == sim.object_joint_type:
            print(f"{indent}  Joint Pos: {info.get('joint_position', 'N/A')}")
        
        # Get children
        children = []
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(handle, idx)
                if child == -1:
                    break
                children.append(child)
                idx += 1
            except:
                break
        
        if children:
            print(f"{indent}  Children: {len(children)}")
            for child in children:
                inspect_object(sim, child, depth + 1)
        
        return info
        
    except Exception as e:
        print(f"{indent}Error inspecting handle {handle}: {e}")
        return None


def main():
    print("=== Inspecting CoppeliaSim Scene ===\n")
    
    # Connect
    client = RemoteAPIClient('127.0.0.1', 23002)
    sim = client.getObject('sim')
    print("✓ Connected\n")
    
    # Get all top-level objects (objects without parents)
    print("Scene Structure:\n")
    print("=" * 60)
    
    all_objects = sim.getObjects(sim.handle_scene, sim.object_all_type)
    print(f"Total objects in scene: {len(all_objects)}\n")
    
    # Find root objects (no parent)
    root_objects = []
    for obj in all_objects:
        try:
            parent = sim.getObjectParent(obj)
            if parent == -1:
                root_objects.append(obj)
        except:
            pass
    
    print(f"Root objects: {len(root_objects)}\n")
    
    # Inspect each root object tree
    scene_data = []
    for root in root_objects:
        info = inspect_object(sim, root, depth=0)
        if info:
            scene_data.append(info)
        print()
    
    # Look specifically for UR5 and RG2
    print("=" * 60)
    print("\nSearching for specific objects:\n")
    
    ur5_objects = [obj for obj in all_objects if 'UR5' in sim.getObjectAlias(obj).upper()]
    rg2_objects = [obj for obj in all_objects if 'RG2' in sim.getObjectAlias(obj).upper()]
    
    if ur5_objects:
        print(f"Found {len(ur5_objects)} UR5-related objects:")
        for obj in ur5_objects[:10]:  # Show first 10
            alias = sim.getObjectAlias(obj)
            obj_type = sim.getObjectType(obj)
            print(f"  - {alias} (handle: {obj}, type: {obj_type})")
    
    if rg2_objects:
        print(f"\nFound {len(rg2_objects)} RG2-related objects:")
        for obj in rg2_objects[:10]:
            alias = sim.getObjectAlias(obj)
            obj_type = sim.getObjectType(obj)
            parent = sim.getObjectParent(obj)
            parent_name = sim.getObjectAlias(parent) if parent != -1 else "None"
            print(f"  - {alias} (handle: {obj}, parent: {parent_name})")
    
    # Find RG2 gripper joint specifically
    print("\n" + "=" * 60)
    print("\nSearching for RG2 gripper control joint:\n")
    for obj in rg2_objects:
        if sim.getObjectType(obj) == sim.object_joint_type:
            alias = sim.getObjectAlias(obj)
            try:
                pos = sim.getJointPosition(obj)
                print(f"  ✓ JOINT: {alias} (handle: {obj})")
                print(f"    Current position: {pos}")
                print(f"    This is likely the gripper control!")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("\n✓ Inspection complete!")
    print("\nNow I can create a script that matches your exact setup.")


if __name__ == "__main__":
    main()
