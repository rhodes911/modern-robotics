"""
ROBOTIQ 85 Gripper Control - Based on UI Monitoring Results
============================================================

Key Findings from monitor_gripper_ui.py:
- ROBOTIQ 85 uses internal Lua script that controls 6 joints
- No signals - purely joint-position based control
- Gripper state is reflected in LactiveJoint position:
  * CLOSED: 0.000 radians
  * OPEN: ~0.794 radians (left), ~0.803 radians (right)
- Cannot control directly via Remote API - joints are driven by script

This script demonstrates READING gripper state, not controlling it.
For programmatic control, you must:
1. Click UI buttons to open/close, OR
2. Modify the internal Lua script to expose control functions
"""

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

def get_gripper_state(sim):
    """
    Read the current gripper state by checking LactiveJoint position.
    
    Returns:
        tuple: (state_str, left_position, right_position)
            state_str: "OPEN", "CLOSED", or "MOVING"
            left_position: LactiveJoint position in radians
            right_position: RactiveJoint position in radians
    """
    try:
        # Get joint handles
        left_active = sim.getObject('/ROBOTIQ85/LactiveJoint')
        right_active = sim.getObject('/ROBOTIQ85/RactiveJoint')
        
        # Read positions
        left_pos = sim.getJointPosition(left_active)
        right_pos = sim.getJointPosition(right_active)
        
        # Determine state based on position
        # Tolerance for "close enough" to target
        TOLERANCE = 0.01
        
        if abs(left_pos) < TOLERANCE and abs(right_pos) < TOLERANCE:
            state = "CLOSED"
        elif abs(left_pos - 0.794) < TOLERANCE and abs(right_pos - 0.803) < TOLERANCE:
            state = "OPEN"
        else:
            state = "MOVING"
        
        return state, left_pos, right_pos
    
    except Exception as e:
        print(f"Error reading gripper state: {e}")
        return "ERROR", 0.0, 0.0


def wait_for_gripper_state(sim, target_state, timeout=5.0):
    """
    Wait until gripper reaches the target state.
    
    Args:
        sim: CoppeliaSim remote API object
        target_state: "OPEN" or "CLOSED"
        timeout: Maximum time to wait in seconds
    
    Returns:
        bool: True if target state reached, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        state, left, right = get_gripper_state(sim)
        
        if state == target_state:
            print(f"✓ Gripper reached {target_state} state (L:{left:.3f}, R:{right:.3f})")
            return True
        
        time.sleep(0.05)  # Poll every 50ms
    
    print(f"✗ Timeout waiting for gripper to reach {target_state}")
    return False


def monitor_gripper_continuously(sim, duration=10.0):
    """
    Continuously monitor and display gripper state.
    
    Args:
        sim: CoppeliaSim remote API object
        duration: How long to monitor in seconds
    """
    print(f"\nMonitoring gripper state for {duration} seconds...")
    print("Click the UI 'open' or 'close' buttons to see state changes.\n")
    
    start_time = time.time()
    last_state = None
    
    while time.time() - start_time < duration:
        state, left, right = get_gripper_state(sim)
        
        # Only print when state changes
        if state != last_state:
            timestamp = time.time() - start_time
            print(f"[{timestamp:6.2f}s] State: {state:8s} | L:{left:+7.4f} | R:{right:+7.4f}")
            last_state = state
        
        time.sleep(0.05)  # Poll every 50ms


def main():
    print("="*70)
    print("ROBOTIQ 85 Gripper State Monitor")
    print("="*70)
    
    # Connect to CoppeliaSim
    client = RemoteAPIClient('localhost', 23002)
    sim = client.getObject('sim')
    
    # Check if simulation is running
    if sim.getSimulationState() != sim.simulation_stopped:
        print("⚠ Stopping existing simulation...")
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            time.sleep(0.1)
    
    print("\nLoading ROBOTIQ 85 gripper...")
    try:
        gripper = sim.loadModel('models/components/grippers/ROBOTIQ 85.ttm')
        print("✓ Gripper loaded")
    except Exception as e:
        print(f"✗ Error loading gripper: {e}")
        return
    
    # Start simulation
    print("\nStarting simulation...")
    sim.startSimulation()
    time.sleep(0.5)  # Wait for simulation to stabilize
    
    # Get initial state
    state, left, right = get_gripper_state(sim)
    print(f"\nInitial state: {state} (L:{left:.4f}, R:{right:.4f})")
    
    # Monitor for changes
    print("\n" + "="*70)
    print("INSTRUCTIONS:")
    print("="*70)
    print("1. In CoppeliaSim, double-click the ROBOTIQ 85 gripper")
    print("2. Click 'open' or 'close' buttons in the dialog")
    print("3. Watch the state changes below")
    print("="*70)
    
    try:
        monitor_gripper_continuously(sim, duration=30.0)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    
    # Final state
    state, left, right = get_gripper_state(sim)
    print(f"\nFinal state: {state} (L:{left:.4f}, R:{right:.4f})")
    
    # Cleanup
    print("\nStopping simulation...")
    sim.stopSimulation()
    print("Done!")


if __name__ == "__main__":
    main()
