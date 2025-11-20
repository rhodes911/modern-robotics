"""
Find how ROBOTIQ 85 is controlled - look for signals, custom data, etc.
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

print("ROBOTIQ 85 Control Analysis")
print("=" * 60)

# Check for integer signals (common control method)
print("\nChecking for integer signals...")
try:
    # Common signal patterns
    signal_names = [
        'ROBOTIQ85_open',
        'ROBOTIQ85_close', 
        'ROBOTIQ_open',
        'ROBOTIQ_close',
        'gripper_open',
        'gripper_close',
    ]
    
    for name in signal_names:
        try:
            val = sim.getInt32Signal(name)
            print(f"  Found signal: {name} = {val}")
        except:
            pass
except:
    pass

# Check for string signals
print("\nChecking for string signals...")
try:
    for name in signal_names:
        try:
            val = sim.getStringSignal(name)
            print(f"  Found signal: {name} = {val}")
        except:
            pass
except:
    pass

# Get the script attached to the gripper
print("\nLooking for script...")
try:
    # Find script object
    script_handle = sim.getObject('/ROBOTIQ85/Script')
    print(f"✓ Found script (handle: {script_handle})")
    
    # Try to read script variables or associated data
    print("\nTrying to read script data...")
    
except Exception as e:
    print(f"Could not find script: {e}")

# Check RactiveJoint properties
print("\n" + "=" * 60)
print("RactiveJoint Analysis:")
try:
    joint = sim.getObject('/ROBOTIQ85/RactiveJoint')
    print(f"✓ Found RactiveJoint (handle: {joint})")
    
    # Get joint properties
    pos = sim.getJointPosition(joint)
    print(f"  Position: {pos:.4f}")
    
    mode = sim.getJointMode(joint)
    print(f"  Mode: {mode}")
    
    # Get joint limits
    cyclic, interval = sim.getJointInterval(joint)
    print(f"  Cyclic: {cyclic}, Interval: {interval}")
    
    # Get target position
    try:
        target = sim.getJointTargetPosition(joint)
        print(f"  Target Position: {target:.4f}")
    except:
        print("  No target position set")
    
    # Get motor properties
    try:
        motor_enabled = sim.getObjectInt32Param(joint, sim.jointintparam_motor_enabled)
        print(f"  Motor enabled: {motor_enabled}")
    except:
        pass
    
    try:
        ctrl_enabled = sim.getObjectInt32Param(joint, sim.jointintparam_ctrl_enabled)
        print(f"  Control enabled: {ctrl_enabled}")
    except:
        pass
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("\nNow testing signal-based control...")
print("Starting simulation...")

sim.startSimulation()
time.sleep(1)

print("\nTrying to CLOSE gripper via signal...")
try:
    # Clear open signal first
    sim.clearInt32Signal('ROBOTIQ85_open')
    sim.setInt32Signal('ROBOTIQ85_close', 1)
    print("  Set ROBOTIQ85_close = 1")
    time.sleep(3)
    pos = sim.getJointPosition(sim.getObject('/ROBOTIQ85/RactiveJoint'))
    print(f"  Position after close signal: {pos:.4f}")
    sim.clearInt32Signal('ROBOTIQ85_close')
except Exception as e:
    print(f"  Error: {e}")

print("\nWaiting...")
time.sleep(1)

print("\nTrying to OPEN gripper via signal...")
try:
    # Clear close signal first
    sim.clearInt32Signal('ROBOTIQ85_close')
    sim.setInt32Signal('ROBOTIQ85_open', 1)
    print("  Set ROBOTIQ85_open = 1")
    time.sleep(3)
    pos = sim.getJointPosition(sim.getObject('/ROBOTIQ85/RactiveJoint'))
    print(f"  Position after open signal: {pos:.4f}")
    sim.clearInt32Signal('ROBOTIQ85_open')
except Exception as e:
    print(f"  Error: {e}")

print("\nStopping simulation...")
sim.stopSimulation()

print("\n" + "=" * 60)
print("Analysis complete!")
