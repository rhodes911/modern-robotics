"""
Look for the actual script functions that control the gripper
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Close all scenes
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

# Find the script
script = sim.getObject('/ROBOTIQ85/Script')
print(f"Script handle: {script}")

# Start sim
sim.startSimulation()
time.sleep(1)

# Get joint
joint = sim.getObject('/ROBOTIQ85/RactiveJoint')
print(f"Initial position: {sim.getJointPosition(joint):.4f}")

# Try calling script functions directly
print("\n" + "=" * 60)
print("Trying to call script functions...")

try:
    # The customization script might have functions we can call
    # Common patterns: open(), close(), setGripperPosition()
    
    # Try calling via script
    result = sim.callScriptFunction('close', script)
    print(f"Called 'close' function: {result}")
    time.sleep(3)
    print(f"Position after close(): {sim.getJointPosition(joint):.4f}")
except Exception as e:
    print(f"close() failed: {e}")

try:
    result = sim.callScriptFunction('open', script)
    print(f"Called 'open' function: {result}")
    time.sleep(3)
    print(f"Position after open(): {sim.getJointPosition(joint):.4f}")
except Exception as e:
    print(f"open() failed: {e}")

# Try simRMLMoveToPosition (this is what many grippers use)
print("\n" + "=" * 60)
print("Trying RML movement...")

try:
    # Control via Ljoint1 and Rjoint1 (the main finger joints)
    Ljoint1 = sim.getObject('/ROBOTIQ85/Ljoint1')
    Rjoint1 = sim.getObject('/ROBOTIQ85/Rjoint1')
    
    print(f"Ljoint1: {sim.getJointPosition(Ljoint1):.4f}")
    print(f"Rjoint1: {sim.getJointPosition(Rjoint1):.4f}")
    
    # Check joint modes and enable motors
    print(f"\nLjoint1 mode: {sim.getJointMode(Ljoint1)}")
    print(f"Rjoint1 mode: {sim.getJointMode(Rjoint1)}")
    
    # Set to force/torque mode and enable motor
    print("\nEnabling motors and setting to kinematic mode...")
    sim.setJointMode(Ljoint1, sim.jointmode_kinematic, 0)
    sim.setJointMode(Rjoint1, sim.jointmode_kinematic, 0)
    sim.setObjectInt32Param(Ljoint1, sim.jointintparam_motor_enabled, 1)
    sim.setObjectInt32Param(Rjoint1, sim.jointintparam_motor_enabled, 1)
    
    # Try closing by setting target positions
    print("\nSetting finger joints to close (0.8)...")
    sim.setJointTargetPosition(Ljoint1, 0.8)
    sim.setJointTargetPosition(Rjoint1, 0.8)
    time.sleep(3)
    
    print(f"Ljoint1 after: {sim.getJointPosition(Ljoint1):.4f}")
    print(f"Rjoint1 after: {sim.getJointPosition(Rjoint1):.4f}")
    
    print("\nSetting finger joints to open (0.0)...")
    sim.setJointTargetPosition(Ljoint1, 0.0)
    sim.setJointTargetPosition(Rjoint1, 0.0)
    time.sleep(3)
    
    print(f"Ljoint1 final: {sim.getJointPosition(Ljoint1):.4f}")
    print(f"Rjoint1 final: {sim.getJointPosition(Rjoint1):.4f}")
    
except Exception as e:
    print(f"Finger joint control failed: {e}")

print("\nStopping...")
sim.stopSimulation()
