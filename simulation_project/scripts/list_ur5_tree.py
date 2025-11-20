"""List all objects in the UR5 hierarchy"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

print("Getting UR5 hierarchy...\n")

try:
    ur5 = sim.getObject('/UR5')
    print(f"Found UR5 base: {ur5}\n")
    
    # Get all children
    index = 0
    children = []
    while True:
        try:
            child = sim.getObjectChild(ur5, index)
            if child == -1:
                break
            alias = sim.getObjectAlias(child)
            obj_type = sim.getObjectType(child)
            children.append((alias, child, obj_type))
            index += 1
        except:
            break
    
    print(f"Direct children of UR5: {len(children)}\n")
    for alias, handle, otype in children:
        type_name = "joint" if otype == sim.object_joint_type else "shape" if otype == sim.object_shape_type else f"type{otype}"
        print(f"  - {alias} (handle: {handle}, {type_name})")
        
        # Get children of this child (recursive one level)
        subindex = 0
        while True:
            try:
                subchild = sim.getObjectChild(handle, subindex)
                if subchild == -1:
                    break
                subalias = sim.getObjectAlias(subchild)
                subtype = sim.getObjectType(subchild)
                type_name = "joint" if subtype == sim.object_joint_type else "shape" if subtype == sim.object_shape_type else f"type{subtype}"
                print(f"      └─ {subalias} (handle: {subchild}, {type_name})")
                subindex += 1
            except:
                break
    
except Exception as e:
    print(f"Error: {e}")
