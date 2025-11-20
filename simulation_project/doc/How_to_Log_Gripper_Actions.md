# How to Log ROBOTIQ 85 UI Button Actions

## Method 1: Modify the Gripper's Customization Script (Recommended)

1. **Open CoppeliaSim**
2. **Load the ROBOTIQ 85 gripper** (drag from Model Browser or load via script)
3. **Find the Script object**:
   - In the scene hierarchy, expand `/ROBOTIQ85`
   - Look for a child called `Script` (type: customization script)
4. **Double-click the Script** to open the editor
5. **Add logging at the top** of the script functions:

```lua
-- At the top of the script, after any existing variables:
function logAction(message)
    sim.addLog(sim.verbosity_scriptinfos, string.format("[ROBOTIQ85] %s", message))
    print(string.format("[ROBOTIQ85] %s", message))
end

-- In the UI button callback (look for functions like handleOpen() or similar):
function handleOpen()
    logAction("UI OPEN button pressed")
    logAction(string.format("Current joint positions: L=%f, R=%f", 
        sim.getJointPosition(Ljoint1Handle), 
        sim.getJointPosition(Rjoint1Handle)))
    
    -- ... existing open logic ...
    
    logAction("Open command completed")
end

function handleClose()
    logAction("UI CLOSE button pressed")
    logAction(string.format("Current joint positions: L=%f, R=%f", 
        sim.getJointPosition(Ljoint1Handle), 
        sim.getJointPosition(Rjoint1Handle)))
    
    -- ... existing close logic ...
    
    logAction("Close command completed")
end
```

6. **Check the console** (View → Show Status Bar, then click the console tab at bottom)
7. **Click open/close buttons** and watch the logs

---

## Method 2: Monitor from Python (Non-Invasive)

Create a monitoring script that polls joint positions and detects changes:

```python
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Get gripper joints
Ljoint1 = sim.getObject('/ROBOTIQ85/Ljoint1')
Rjoint1 = sim.getObject('/ROBOTIQ85/Rjoint1')
RactiveJoint = sim.getObject('/ROBOTIQ85/RactiveJoint')
LactiveJoint = sim.getObject('/ROBOTIQ85/LactiveJoint')

print("Monitoring ROBOTIQ 85 - Press UI buttons and watch for changes")
print("=" * 70)

# Start simulation
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    time.sleep(1)

last_positions = {
    'L1': None, 'R1': None, 
    'Lactive': None, 'Ractive': None
}

while True:
    try:
        # Read all joint positions
        current = {
            'L1': sim.getJointPosition(Ljoint1),
            'R1': sim.getJointPosition(Rjoint1),
            'Lactive': sim.getJointPosition(LactiveJoint),
            'Ractive': sim.getJointPosition(RactiveJoint),
        }
        
        # Detect changes
        for name, pos in current.items():
            if last_positions[name] is not None:
                delta = abs(pos - last_positions[name])
                if delta > 0.001:  # Threshold for significant change
                    print(f"[CHANGE] {name}: {last_positions[name]:.6f} → {pos:.6f} (Δ={delta:.6f})")
        
        last_positions = current
        time.sleep(0.1)  # Poll every 100ms
        
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        break

sim.stopSimulation()
```

---

## Method 3: Check Signal Usage (Discover Control Interface)

The UI buttons likely set signals. Monitor signal changes:

```python
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

# Common signal names to check
signal_names = [
    'ROBOTIQ85_open', 'ROBOTIQ85_close',
    'ROBOTIQ_open', 'ROBOTIQ_close',
    'gripper_open', 'gripper_close',
    'rg_command', 'gripper_cmd'
]

print("Monitoring signals - Press UI buttons now")
print("=" * 70)

sim.startSimulation()
time.sleep(1)

last_signals = {}
for name in signal_names:
    try:
        last_signals[name] = sim.getInt32Signal(name)
    except:
        last_signals[name] = None

while True:
    try:
        for name in signal_names:
            try:
                current = sim.getInt32Signal(name)
                if current != last_signals[name]:
                    print(f"[SIGNAL CHANGE] {name}: {last_signals[name]} → {current}")
                    last_signals[name] = current
            except:
                pass
        
        time.sleep(0.05)
        
    except KeyboardInterrupt:
        break

sim.stopSimulation()
```

---

## Method 4: Enable CoppeliaSim Console Logging

1. In CoppeliaSim, go to **Tools → User Settings**
2. Find **Console** or **Verbosity** settings
3. Set to **Debug** or **Trace** level
4. Console output will show all sim API calls

---

## Recommended Workflow

1. **Start with Method 2** (Python monitoring) - run it while clicking UI buttons
2. **If joints don't change**, use **Method 3** (signal monitoring)
3. **If you find active signals**, document them and use in your scripts
4. **If nothing changes externally**, the script is fully internal → use **Method 1** to add logging inside the Lua script

Would you like me to create a ready-to-run monitoring script for you?
