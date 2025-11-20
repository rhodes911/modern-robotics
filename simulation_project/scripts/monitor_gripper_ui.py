"""
Real-time monitor for ROBOTIQ 85 gripper actions
Watches joint positions and signals while you use the UI buttons

Usage:
1. Start CoppeliaSim and load ROBOTIQ 85 gripper
2. Run this script
3. Click the 'open' and 'close' UI buttons
4. Watch console output to see what changes
"""

import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

print("=" * 80)
print("ROBOTIQ 85 GRIPPER MONITOR")
print("=" * 80)
print("This script will monitor joint positions and signals in real-time.")
print("Action Required: Click the 'open' and 'close' UI buttons on the gripper")
print("=" * 80)

# Close any existing scenes
try:
    sim.closeScene()
except:
    pass

# Stop if running
if sim.getSimulationState() != sim.simulation_stopped:
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        time.sleep(0.1)

# Load gripper
print("\nLoading ROBOTIQ 85 gripper...")
COPPELIA_ROOT = r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu"
gripper = sim.loadModel(f"{COPPELIA_ROOT}\\models\\components\\grippers\\ROBOTIQ 85.ttm")
print("✓ Gripper loaded")

# Get all important joints
joints = {
    'Ljoint1': sim.getObject('/ROBOTIQ85/Ljoint1'),
    'Rjoint1': sim.getObject('/ROBOTIQ85/Rjoint1'),
    'Ljoint2': sim.getObject('/ROBOTIQ85/Ljoint2'),
    'Rjoint2': sim.getObject('/ROBOTIQ85/Rjoint2'),
    'LactiveJoint': sim.getObject('/ROBOTIQ85/LactiveJoint'),
    'RactiveJoint': sim.getObject('/ROBOTIQ85/RactiveJoint'),
}

# Signal names to monitor
signal_names = [
    'ROBOTIQ85_open', 'ROBOTIQ85_close',
    'ROBOTIQ_open', 'ROBOTIQ_close',
    'gripper_open', 'gripper_close',
    'gripper_cmd', 'rg_command',
]

print("\nMonitoring these joints:")
for name in joints.keys():
    print(f"  - {name}")

print("\nMonitoring these signals:")
for name in signal_names:
    print(f"  - {name}")

print("\n" + "=" * 80)
print("Starting simulation...")
sim.startSimulation()
time.sleep(1)
print("✓ Simulation running")
print("=" * 80)
print("\n>>> NOW CLICK THE 'open' AND 'close' BUTTONS IN THE GRIPPER UI <<<\n")
print("=" * 80)

# Initialize tracking
last_positions = {}
last_signals = {}
change_count = 0

for name, handle in joints.items():
    try:
        last_positions[name] = sim.getJointPosition(handle)
    except:
        last_positions[name] = None

for name in signal_names:
    try:
        last_signals[name] = sim.getInt32Signal(name)
    except:
        last_signals[name] = None

print("\n[READY] Monitoring started. Press Ctrl+C to stop.\n")

try:
    iteration = 0
    while True:
        changed = False
        
        # Check joint positions
        for name, handle in joints.items():
            try:
                current = sim.getJointPosition(handle)
                if last_positions[name] is not None:
                    delta = abs(current - last_positions[name])
                    if delta > 0.0001:  # Threshold for significant change
                        change_count += 1
                        print(f"[{change_count:04d}] JOINT {name:15s}: {last_positions[name]:+.6f} → {current:+.6f} (Δ={delta:+.6f})")
                        changed = True
                last_positions[name] = current
            except Exception as e:
                pass
        
        # Check signals
        for name in signal_names:
            try:
                current = sim.getInt32Signal(name)
                if current != last_signals[name]:
                    change_count += 1
                    print(f"[{change_count:04d}] SIGNAL {name:20s}: {last_signals[name]} → {current}")
                    changed = True
                    last_signals[name] = current
            except:
                pass
        
        # Progress indicator (every 50 iterations if no changes)
        if not changed:
            iteration += 1
            if iteration % 50 == 0:
                print(f"[....] Still monitoring... ({iteration} polls, {change_count} changes detected)")
        
        time.sleep(0.05)  # Poll every 50ms
        
except KeyboardInterrupt:
    print("\n" + "=" * 80)
    print("MONITORING STOPPED")
    print("=" * 80)
    print(f"\nTotal changes detected: {change_count}")
    
    if change_count == 0:
        print("\n⚠ WARNING: No changes detected!")
        print("Possible reasons:")
        print("  1. You didn't click the UI buttons")
        print("  2. The gripper uses internal script logic not visible to remote API")
        print("  3. The control interface is different than expected")
        print("\nNext steps:")
        print("  - Try editing the gripper's Lua script to add logging")
        print("  - Check CoppeliaSim console for internal messages")
        print("  - Refer to: doc/How_to_Log_Gripper_Actions.md")
    else:
        print("\n✓ Changes detected! Review the output above to understand the control mechanism.")

print("\nStopping simulation...")
sim.stopSimulation()
print("Done!")
