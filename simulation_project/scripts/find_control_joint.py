"""
Find the ACTUAL control joint for ROBOTIQ 85
The finger joints are dependent/passive - need to find the motor joint
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

try:
    sim.closeScene()
except:
    pass

if sim.getSimulationState() != sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        time.sleep(0.1)

COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")

print("=" * 60)
print("Finding ACTUAL Control Joints")
print("=" * 60)

# Get ALL joints and check their modes
all_joints = [
    ('Ljoint1', '/ROBOTIQ85/Ljoint1'),
    ('Rjoint1', '/ROBOTIQ85/Rjoint1'),
    ('Ljoint2', '/ROBOTIQ85/Ljoint2'),
    ('Rjoint2', '/ROBOTIQ85/Rjoint2'),
    ('RactiveJoint', '/ROBOTIQ85/RactiveJoint'),
    ('LactiveJoint', '/ROBOTIQ85/LactiveJoint'),
    ('prismatic', '/ROBOTIQ85/prismatic'),
    ('prismatic2', '/ROBOTIQ85/prismatic2'),
]

print("\nJoint Analysis:")
print("-" * 60)

for name, path in all_joints:
    try:
        joint = sim.getObject(path)
        mode = sim.getJointMode(joint)
        pos = sim.getJointPosition(joint)
        cyclic, interval = sim.getJointInterval(joint)
        joint_type = sim.getJointType(joint)
        
        # Mode explanation:
        # 0 = force/torque mode (kinematic, motor on)
        # 1 = inverse kinematic mode
        # 2 = dependent mode  
        # 3 = motion mode
        # 5 = passive mode
        
        mode_str = {
            0: "FORCE/TORQUE (controllable)",
            1: "IK",
            2: "DEPENDENT",
            3: "MOTION",
            5: "PASSIVE"
        }.get(mode[0], f"UNKNOWN({mode[0]})")
        
        type_str = {
            10: "REVOLUTE",
            11: "PRISMATIC",
            12: "SPHERICAL"
        }.get(joint_type, f"TYPE_{joint_type}")
        
        print(f"\n{name}:")
        print(f"  Mode: {mode_str}")
        print(f"  Type: {type_str}")
        print(f"  Position: {pos:.6f}")
        print(f"  Limits: [{interval[0]:.6f}, {interval[1]:.6f}]")
        
        if mode[0] == 0 or mode[0] == 3:
            print(f"  ✓ THIS JOINT CAN BE CONTROLLED!")
            
    except Exception as e:
        print(f"{name}: Not found or error - {e}")

print("\n" + "=" * 60)
print("Testing which joint actually controls the gripper")
print("=" * 60)

sim.startSimulation()
time.sleep(1)

# Test each potential control joint
for name, path in all_joints:
    try:
        joint = sim.getObject(path)
        mode = sim.getJointMode(joint)
        
        if mode[0] == 5:  # Skip passive joints
            continue
            
        print(f"\nTesting {name}...")
        
        # Get finger positions before
        try:
            L1 = sim.getJointPosition(sim.getObject('/ROBOTIQ85/Ljoint1'))
            R1 = sim.getJointPosition(sim.getObject('/ROBOTIQ85/Rjoint1'))
            print(f"  Fingers before: L={L1:.4f}, R={R1:.4f}")
        except:
            pass
        
        # Try setting this joint
        initial = sim.getJointPosition(joint)
        sim.setJointTargetPosition(joint, initial + 0.1)
        time.sleep(2)
        
        # Check finger positions after
        try:
            L2 = sim.getJointPosition(sim.getObject('/ROBOTIQ85/Ljoint1'))
            R2 = sim.getJointPosition(sim.getObject('/ROBOTIQ85/Rjoint1'))
            print(f"  Fingers after:  L={L2:.4f}, R={R2:.4f}")
            
            if abs(L2 - L1) > 0.01 or abs(R2 - R1) > 0.01:
                print(f"  ✓✓✓ {name} CONTROLS THE GRIPPER! ✓✓✓")
        except:
            pass
            
    except:
        pass

sim.stopSimulation()
print("\n" + "=" * 60)
