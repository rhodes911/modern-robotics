"""
Test ROBOTIQ 85 control with UI buttons to see what actually works
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Close all scenes without saving
print("Closing all open scenes...")
try:
    sim.closeScene()
except:
    pass

# Stop sim if running
if sim.getSimulationState() != sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        time.sleep(0.1)

# Load ROBOTIQ 85
COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")

print("\n" + "=" * 60)
print("Testing ROBOTIQ 85 Control Methods")
print("=" * 60)

# Get all objects to find the script
print("\nSearching for all objects...")
def print_all_objects(handle, indent=0):
    try:
        name = sim.getObjectAlias(handle)
        obj_type = sim.getObjectType(handle)
        print("  " * indent + f"├─ {name} (type: {obj_type}, handle: {handle})")
        
        idx = 0
        while True:
            try:
                child = sim.getObjectChild(handle, idx)
                if child == -1:
                    break
                print_all_objects(child, indent + 1)
                idx += 1
            except:
                break
    except:
        pass

print_all_objects(gripper)

# Try to find custom UI element or script signal
print("\n" + "=" * 60)
print("Looking for UI elements and signals...")

# Start simulation to enable the UI
print("\nStarting simulation...")
sim.startSimulation()
time.sleep(1)

# Try getting all current signals
print("\nChecking what signals exist...")
try:
    # The UI creates signals - let's see what's available
    test_names = [
        'ROBOTIQ85_open',
        'ROBOTIQ85_close',
        'RG2_open', 
        'RG2_close',
        'gripper_open',
        'gripper_close',
    ]
    
    for name in test_names:
        try:
            val = sim.getInt32Signal(name)
            if val is not None:
                print(f"  Signal exists: {name} = {val}")
        except:
            pass
except Exception as e:
    print(f"Error checking signals: {e}")

# Get RactiveJoint
joint = sim.getObject('/ROBOTIQ85/RactiveJoint')
print(f"\nRactiveJoint initial position: {sim.getJointPosition(joint):.4f}")

# Try method 1: Direct position control
print("\n" + "=" * 60)
print("Method 1: Direct setJointTargetPosition")
print("Attempting to close...")
sim.setJointTargetPosition(joint, 0.8)  # Try closing
time.sleep(3)
pos1 = sim.getJointPosition(joint)
print(f"Position after target=0.8: {pos1:.4f}")

print("Attempting to open...")
sim.setJointTargetPosition(joint, 0.0)
time.sleep(3)
pos2 = sim.getJointPosition(joint)
print(f"Position after target=0.0: {pos2:.4f}")

# Try method 2: Check if there's a custom data block
print("\n" + "=" * 60)
print("Method 2: Checking custom data...")
try:
    # The UI script might use custom string signals
    sim.setStringSignal('ROBOTIQ85', 'c')  # 'c' for close
    time.sleep(2)
    pos3 = sim.getJointPosition(joint)
    print(f"Position after string signal 'c': {pos3:.4f}")
    
    sim.setStringSignal('ROBOTIQ85', 'o')  # 'o' for open
    time.sleep(2)
    pos4 = sim.getJointPosition(joint)
    print(f"Position after string signal 'o': {pos4:.4f}")
except Exception as e:
    print(f"String signal method failed: {e}")

print("\n" + "=" * 60)
print("Stopping simulation...")
sim.stopSimulation()
print("Test complete!")
