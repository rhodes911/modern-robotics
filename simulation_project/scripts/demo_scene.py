"""
Simple Demo Script
Shows the scene and animates camera view
"""

import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from coppelia_api import CoppeliaSimConnection


def main():
    """Demo the scene"""
    print("\n=== CoppeliaSim Scene Demo ===\n")
    
    conn = CoppeliaSimConnection()
    
    if not conn.connect():
        print("Failed to connect to CoppeliaSim")
        return
    
    try:
        # Start simulation
        print("Starting simulation...")
        conn.start_simulation()
        
        print("\n✓ Simulation running!")
        print("\nIn CoppeliaSim you should see:")
        print("  🟤 Brown desk (1.04m × 0.43m)")
        print("  🔴🟢🔵🟡 Colored objects on the desk")
        print("  🟥🟩🟦 Three sorting bins on the right")
        print("\nObjects will fall and settle due to physics...")
        
        # Let objects settle
        print("\nLetting objects settle for 5 seconds...")
        for i in range(5, 0, -1):
            print(f"  {i}...", end='\r')
            time.sleep(1)
        
        print("\n\n✓ Scene is ready!")
        print("\nNext step: Load a robot arm (UR5 or Panda)")
        print("  File → Load Model → robots/non-mobile/universal_robots/UR5.ttm")
        
        # Keep simulation running
        print("\nSimulation will continue running...")
        print("Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping simulation...")
        
    finally:
        conn.stop_simulation()
        conn.disconnect()
        print("✓ Demo complete!")


if __name__ == "__main__":
    main()
