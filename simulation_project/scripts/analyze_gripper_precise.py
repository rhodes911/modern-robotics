"""
Precise analysis of ROBOTIQ 85 joint properties and safe operating range
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Close and clean
try:
    sim.closeScene()
except:
    pass

if sim.getSimulationState() != sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        time.sleep(0.1)

# Load gripper
COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")

print("=" * 60)
print("ROBOTIQ 85 Precise Joint Analysis")
print("=" * 60)

# Get the finger joints
Ljoint1 = sim.getObject('/ROBOTIQ85/Ljoint1')
Rjoint1 = sim.getObject('/ROBOTIQ85/Rjoint1')

print("\nBefore simulation - Joint Properties:")
print("-" * 60)

for name, joint in [("Ljoint1", Ljoint1), ("Rjoint1", Rjoint1)]:
    print(f"\n{name}:")
    
    # Get current state
    pos = sim.getJointPosition(joint)
    print(f"  Current position: {pos:.6f}")
    
    # Get joint mode
    mode = sim.getJointMode(joint)
    print(f"  Mode: {mode}")
    
    # Get joint interval (limits)
    cyclic, interval = sim.getJointInterval(joint)
    print(f"  Cyclic: {cyclic}")
    print(f"  Interval (limits): [{interval[0]:.6f}, {interval[1]:.6f}]")
    
    # Get joint type
    joint_type = sim.getJointType(joint)
    print(f"  Type: {joint_type}")

# Start simulation and test incremental positions
print("\n" + "=" * 60)
print("Testing incremental positions during simulation")
print("=" * 60)

sim.startSimulation()
time.sleep(1)

# Enable motors with kinematic mode
sim.setJointMode(Ljoint1, sim.jointmode_kinematic, 0)
sim.setJointMode(Rjoint1, sim.jointmode_kinematic, 0)
sim.setObjectInt32Param(Ljoint1, sim.jointintparam_motor_enabled, 1)
sim.setObjectInt32Param(Rjoint1, sim.jointintparam_motor_enabled, 1)

# Test different positions
test_positions = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

print("\nTesting positions (watch for vibration/instability):")
print("-" * 60)

for target in test_positions:
    sim.setJointTargetPosition(Ljoint1, target)
    sim.setJointTargetPosition(Rjoint1, target)
    time.sleep(2.0)
    
    actual_L = sim.getJointPosition(Ljoint1)
    actual_R = sim.getJointPosition(Rjoint1)
    
    error_L = abs(actual_L - target)
    error_R = abs(actual_R - target)
    
    print(f"  Target: {target:.2f} -> L: {actual_L:.6f} (err: {error_L:.6f}), R: {actual_R:.6f} (err: {error_R:.6f})")
    
    # Check if stable (error should be near zero)
    if error_L > 0.01 or error_R > 0.01:
        print(f"    ⚠ WARNING: High error at position {target}")

print("\n" + "=" * 60)
print("RECOMMENDED SAFE OPERATING RANGE:")
print("  Fully OPEN: 0.0")
print("  Fully CLOSED: Find the maximum stable position from above")
print("=" * 60)

sim.stopSimulation()
