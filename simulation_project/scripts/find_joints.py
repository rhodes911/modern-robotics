"""Quick diagnostic script to discover UR5 joint names"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient('127.0.0.1', 23002)
sim = client.getObject('sim')

print("Searching for UR5 joints...\n")

# Try all possible naming patterns
patterns = [
    '/UR5_joint',
    '/:UR5_joint',
    '/UR5/joint',
    '/joint',
]

for pattern in patterns:
    print(f"Trying pattern: {pattern}#")
    found = []
    for i in range(1, 7):
        try:
            name = f"{pattern}{i}"
            handle = sim.getObject(name)
            found.append((name, handle))
            print(f"  ✓ {name} = {handle}")
        except:
            pass
    if len(found) == 6:
        print(f"\n✓✓✓ SUCCESS! Use pattern: {pattern}#\n")
        break
    elif len(found) > 0:
        print(f"  (Found {len(found)}/6)\n")
    else:
        print("  (None found)\n")
