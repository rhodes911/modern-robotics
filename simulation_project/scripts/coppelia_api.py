"""
CoppeliaSim API Connection Module
Provides connection and communication with CoppeliaSim via ZeroMQ Remote API
"""

import sys
import time
import numpy as np
from typing import Optional, List, Tuple, Any

try:
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
except ImportError:
    print("Warning: coppeliasim_zmqremoteapi_client not installed")
    print("Install with: pip install coppeliasim-zmqremoteapi-client")


class CoppeliaSimConnection:
    """Manages connection to CoppeliaSim and provides high-level API methods"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 23000):
        """
        Initialize connection to CoppeliaSim
        
        Args:
            host: CoppeliaSim server host
            port: CoppeliaSim server port
        """
        self.host = host
        self.port = port
        self.client = None
        self.sim = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to CoppeliaSim
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"Connecting to CoppeliaSim at {self.host}:{self.port}...")
            self.client = RemoteAPIClient(self.host, self.port)
            self.sim = self.client.require('sim')
            self.connected = True
            print("✓ Connected to CoppeliaSim")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to CoppeliaSim: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from CoppeliaSim"""
        if self.connected:
            print("Disconnecting from CoppeliaSim...")
            self.client = None
            self.sim = None
            self.connected = False
            print("✓ Disconnected")
    
    def start_simulation(self):
        """Start the simulation"""
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.startSimulation()
        print("✓ Simulation started")
    
    def stop_simulation(self):
        """Stop the simulation"""
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.stopSimulation()
        print("✓ Simulation stopped")
    
    def pause_simulation(self):
        """Pause the simulation"""
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.pauseSimulation()
    
    def get_object_handle(self, object_name: str) -> int:
        """
        Get handle for a scene object by name
        
        Args:
            object_name: Name of the object in CoppeliaSim
            
        Returns:
            Object handle (integer)
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        try:
            handle = self.sim.getObject(f"/{object_name}")
            return handle
        except Exception as e:
            print(f"Warning: Could not get handle for '{object_name}': {e}")
            return -1
    
    def get_object_position(self, object_handle: int, 
                           relative_to: int = -1) -> List[float]:
        """
        Get position of an object
        
        Args:
            object_handle: Handle of the object
            relative_to: Reference frame (-1 for world frame)
            
        Returns:
            Position as [x, y, z]
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        return self.sim.getObjectPosition(object_handle, relative_to)
    
    def set_object_position(self, object_handle: int, position: List[float],
                           relative_to: int = -1):
        """
        Set position of an object
        
        Args:
            object_handle: Handle of the object
            position: Position as [x, y, z]
            relative_to: Reference frame (-1 for world frame)
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.setObjectPosition(object_handle, relative_to, position)
    
    def get_object_orientation(self, object_handle: int,
                              relative_to: int = -1) -> List[float]:
        """
        Get orientation of an object (Euler angles)
        
        Args:
            object_handle: Handle of the object
            relative_to: Reference frame (-1 for world frame)
            
        Returns:
            Orientation as [alpha, beta, gamma] in radians
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        return self.sim.getObjectOrientation(object_handle, relative_to)
    
    def set_object_orientation(self, object_handle: int, 
                              orientation: List[float],
                              relative_to: int = -1):
        """
        Set orientation of an object (Euler angles)
        
        Args:
            object_handle: Handle of the object
            orientation: Orientation as [alpha, beta, gamma] in radians
            relative_to: Reference frame (-1 for world frame)
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.setObjectOrientation(object_handle, relative_to, orientation)
    
    def get_joint_position(self, joint_handle: int) -> float:
        """
        Get position/angle of a joint
        
        Args:
            joint_handle: Handle of the joint
            
        Returns:
            Joint position in radians (for revolute) or meters (for prismatic)
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        return self.sim.getJointPosition(joint_handle)
    
    def set_joint_position(self, joint_handle: int, position: float):
        """
        Set target position of a joint
        
        Args:
            joint_handle: Handle of the joint
            position: Target position in radians or meters
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.setJointPosition(joint_handle, position)
    
    def set_joint_target_position(self, joint_handle: int, position: float):
        """
        Set target position for a joint in position control mode
        
        Args:
            joint_handle: Handle of the joint
            position: Target position in radians or meters
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.setJointTargetPosition(joint_handle, position)
    
    def get_vision_sensor_image(self, sensor_handle: int) -> np.ndarray:
        """
        Get image from vision sensor
        
        Args:
            sensor_handle: Handle of the vision sensor
            
        Returns:
            Image as numpy array (RGB)
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        
        img, resolution = self.sim.getVisionSensorImg(sensor_handle)
        img = np.frombuffer(img, dtype=np.uint8)
        img = img.reshape((resolution[1], resolution[0], 3))
        img = np.flipud(img)  # Flip vertically
        return img
    
    def get_vision_sensor_depth(self, sensor_handle: int) -> np.ndarray:
        """
        Get depth buffer from vision sensor
        
        Args:
            sensor_handle: Handle of the vision sensor
            
        Returns:
            Depth image as numpy array
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        
        depth, resolution = self.sim.getVisionSensorDepth(sensor_handle)
        depth = np.array(depth).reshape((resolution[1], resolution[0]))
        depth = np.flipud(depth)
        return depth
    
    def create_dummy(self, name: str, size: float = 0.01) -> int:
        """
        Create a dummy object (invisible reference point)
        
        Args:
            name: Name for the dummy
            size: Size of the dummy visualization
            
        Returns:
            Handle of created dummy
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        handle = self.sim.createDummy(size)
        self.sim.setObjectAlias(handle, name)
        return handle
    
    def remove_object(self, object_handle: int):
        """
        Remove an object from the scene
        
        Args:
            object_handle: Handle of object to remove
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        self.sim.removeObject(object_handle)
    
    def get_simulation_time(self) -> float:
        """
        Get current simulation time
        
        Returns:
            Simulation time in seconds
        """
        if not self.connected:
            raise RuntimeError("Not connected to CoppeliaSim")
        return self.sim.getSimulationTime()
    
    def wait(self, duration: float):
        """
        Wait for specified duration in simulation time
        
        Args:
            duration: Time to wait in seconds
        """
        start_time = self.get_simulation_time()
        while self.get_simulation_time() - start_time < duration:
            time.sleep(0.01)


def test_connection():
    """Test the CoppeliaSim connection"""
    conn = CoppeliaSimConnection()
    
    if conn.connect():
        print("\nConnection test successful!")
        print(f"Simulation time: {conn.get_simulation_time():.2f}s")
        conn.disconnect()
        return True
    else:
        print("\nConnection test failed!")
        print("Make sure CoppeliaSim is running and the ZMQ Remote API is enabled")
        return False


if __name__ == "__main__":
    test_connection()
