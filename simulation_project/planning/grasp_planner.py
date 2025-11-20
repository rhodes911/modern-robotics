"""
Grasp Planning Module
Computes grasp poses and generates motion trajectories
"""

import numpy as np
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "packages" / "Python"))
try:
    import modern_robotics as mr
except ImportError:
    print("Warning: modern_robotics library not found")
    mr = None


@dataclass
class GraspPose:
    """Container for grasp pose information"""
    position: Tuple[float, float, float]  # (x, y, z) in meters
    orientation: Tuple[float, float, float]  # (roll, pitch, yaw) in radians
    approach_vector: Tuple[float, float, float]  # Unit vector for approach
    confidence: float  # Grasp quality score 0-1
    gripper_width: float  # Required gripper opening in meters


class GraspPlanner:
    """Generate grasp poses for detected objects"""
    
    def __init__(self, config: Dict):
        """
        Initialize grasp planner
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.control_cfg = config.get('control', {})
        self.ml_cfg = config.get('ml', {})
        
        self.approach_distance = self.control_cfg.get('approach_distance', 0.1)
        self.method = self.ml_cfg.get('grasp_planning', {}).get('method', 'rule_based')
        
    def plan_grasp(self, object_info: Dict) -> Optional[GraspPose]:
        """
        Plan a grasp for a detected object
        
        Args:
            object_info: Dictionary with object properties
                         (label, position_3d, shape, size, etc.)
        
        Returns:
            GraspPose or None if grasp not feasible
        """
        if self.method == 'rule_based':
            return self._rule_based_grasp(object_info)
        elif self.method == 'dexnet':
            return self._dexnet_grasp(object_info)
        else:
            raise ValueError(f"Unknown grasp method: {self.method}")
    
    def _rule_based_grasp(self, obj: Dict) -> Optional[GraspPose]:
        """
        Generate grasp using rule-based heuristics
        
        Args:
            obj: Object information dictionary
            
        Returns:
            GraspPose or None
        """
        # Extract object properties
        pos = obj.get('position_3d')
        if pos is None:
            return None
        
        label = obj.get('label', 'unknown')
        shape = self._extract_shape(label)
        
        # Default top-down grasp
        x, y, z = pos
        
        # Determine gripper orientation based on shape
        if 'cube' in shape or 'box' in shape:
            # Top-down grasp for cubes
            roll = 0.0
            pitch = np.pi  # Point down
            yaw = 0.0
            gripper_width = 0.04  # 4cm opening
            approach = (0, 0, -1)  # From above
            confidence = 0.85
            
        elif 'cylinder' in shape:
            # Side grasp for cylinders
            roll = np.pi / 2  # Rotate gripper
            pitch = 0.0
            yaw = np.arctan2(y, x)  # Face object
            gripper_width = 0.05
            approach = (-np.cos(yaw), -np.sin(yaw), 0)
            confidence = 0.80
            
        elif 'sphere' in shape:
            # Top-down grasp for spheres
            roll = 0.0
            pitch = np.pi
            yaw = 0.0
            gripper_width = 0.06  # Wider opening
            approach = (0, 0, -1)
            confidence = 0.75
            
        else:
            # Default conservative grasp
            roll = 0.0
            pitch = np.pi
            yaw = 0.0
            gripper_width = 0.05
            approach = (0, 0, -1)
            confidence = 0.60
        
        # Adjust grasp position to approach from above
        grasp_x = x
        grasp_y = y
        grasp_z = z + 0.02  # Slightly above object center
        
        return GraspPose(
            position=(grasp_x, grasp_y, grasp_z),
            orientation=(roll, pitch, yaw),
            approach_vector=approach,
            confidence=confidence,
            gripper_width=gripper_width
        )
    
    def _dexnet_grasp(self, obj: Dict) -> Optional[GraspPose]:
        """
        Generate grasp using DexNet model
        
        Args:
            obj: Object information
            
        Returns:
            GraspPose or None
        """
        # Placeholder for DexNet implementation
        print("DexNet grasp planning not yet implemented")
        return self._rule_based_grasp(obj)
    
    def _extract_shape(self, label: str) -> str:
        """Extract shape name from label"""
        label_lower = label.lower()
        for shape in ['cube', 'cylinder', 'sphere', 'box']:
            if shape in label_lower:
                return shape
        return 'unknown'
    
    def compute_pre_grasp_pose(self, grasp: GraspPose) -> Tuple[float, float, float]:
        """
        Compute pre-grasp pose (approach position)
        
        Args:
            grasp: Grasp pose
            
        Returns:
            (x, y, z) of pre-grasp position
        """
        x, y, z = grasp.position
        ax, ay, az = grasp.approach_vector
        
        # Move back along approach vector
        pre_x = x - ax * self.approach_distance
        pre_y = y - ay * self.approach_distance
        pre_z = z - az * self.approach_distance
        
        return (pre_x, pre_y, pre_z)


class TrajectoryGenerator:
    """Generate smooth trajectories for robot motion"""
    
    def __init__(self, config: Dict):
        """
        Initialize trajectory generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.control_cfg = config.get('control', {})
        
        self.max_vel = self.control_cfg.get('max_velocity', 1.0)
        self.max_acc = self.control_cfg.get('max_acceleration', 2.0)
    
    def generate_joint_trajectory(self, start_config: List[float],
                                  end_config: List[float],
                                  duration: float,
                                  timestep: float = 0.01) -> np.ndarray:
        """
        Generate smooth joint trajectory using quintic time scaling
        
        Args:
            start_config: Starting joint angles (radians)
            end_config: Ending joint angles (radians)
            duration: Trajectory duration (seconds)
            timestep: Time step for trajectory points (seconds)
            
        Returns:
            Array of shape (N, num_joints) with trajectory points
        """
        if mr is None:
            # Fallback to linear interpolation
            return self._linear_trajectory(start_config, end_config, 
                                          duration, timestep)
        
        # Use Modern Robotics quintic time scaling
        N = int(duration / timestep)
        trajectory = []
        
        start = np.array(start_config)
        end = np.array(end_config)
        
        for i in range(N + 1):
            t = i * timestep
            s = mr.QuinticTimeScaling(duration, t)
            
            # Interpolate joint positions
            config = start + s * (end - start)
            trajectory.append(config)
        
        return np.array(trajectory)
    
    def _linear_trajectory(self, start: List[float], end: List[float],
                          duration: float, timestep: float) -> np.ndarray:
        """
        Generate linear interpolation trajectory
        
        Args:
            start: Start configuration
            end: End configuration
            duration: Duration in seconds
            timestep: Time step
            
        Returns:
            Trajectory array
        """
        N = int(duration / timestep)
        trajectory = []
        
        start = np.array(start)
        end = np.array(end)
        
        for i in range(N + 1):
            alpha = i / N
            config = start + alpha * (end - start)
            trajectory.append(config)
        
        return np.array(trajectory)
    
    def generate_cartesian_trajectory(self, start_pose: np.ndarray,
                                     end_pose: np.ndarray,
                                     duration: float,
                                     timestep: float = 0.01) -> List[np.ndarray]:
        """
        Generate Cartesian trajectory between two SE(3) poses
        
        Args:
            start_pose: Starting 4x4 transformation matrix
            end_pose: Ending 4x4 transformation matrix
            duration: Trajectory duration
            timestep: Time step
            
        Returns:
            List of 4x4 transformation matrices
        """
        if mr is None:
            # Simple linear position, SLERP orientation
            return self._simple_cartesian_trajectory(start_pose, end_pose,
                                                     duration, timestep)
        
        # Use Modern Robotics CartesianTrajectory
        N = int(duration / timestep)
        Tf = duration
        
        trajectory = mr.CartesianTrajectory(
            Xstart=start_pose,
            Xend=end_pose,
            Tf=Tf,
            N=N,
            method=5  # Quintic
        )
        
        return trajectory
    
    def _simple_cartesian_trajectory(self, start: np.ndarray, end: np.ndarray,
                                    duration: float, timestep: float) -> List[np.ndarray]:
        """
        Simple Cartesian trajectory interpolation
        
        Args:
            start: Start pose (4x4)
            end: End pose (4x4)
            duration: Duration
            timestep: Time step
            
        Returns:
            List of poses
        """
        N = int(duration / timestep)
        trajectory = []
        
        for i in range(N + 1):
            alpha = i / N
            
            # Linear position interpolation
            pos_start = start[:3, 3]
            pos_end = end[:3, 3]
            pos = pos_start + alpha * (pos_end - pos_start)
            
            # Simple rotation interpolation (not ideal but works)
            rot = start[:3, :3] if alpha < 0.5 else end[:3, :3]
            
            # Build pose matrix
            pose = np.eye(4)
            pose[:3, :3] = rot
            pose[:3, 3] = pos
            
            trajectory.append(pose)
        
        return trajectory


def test_grasp_planner():
    """Test the grasp planner"""
    config = {
        'control': {
            'approach_distance': 0.1,
            'max_velocity': 1.0,
            'max_acceleration': 2.0
        },
        'ml': {
            'grasp_planning': {
                'method': 'rule_based'
            }
        }
    }
    
    planner = GraspPlanner(config)
    
    # Test object
    test_obj = {
        'label': 'red_cube',
        'position_3d': (0.2, 0.1, 0.05),
        'shape': 'cube'
    }
    
    grasp = planner.plan_grasp(test_obj)
    
    if grasp:
        print("\n✓ Grasp planned successfully:")
        print(f"  Position: {grasp.position}")
        print(f"  Orientation (RPY): {grasp.orientation}")
        print(f"  Approach: {grasp.approach_vector}")
        print(f"  Confidence: {grasp.confidence:.2f}")
        print(f"  Gripper width: {grasp.gripper_width * 1000:.1f}mm")
        
        pre_grasp = planner.compute_pre_grasp_pose(grasp)
        print(f"  Pre-grasp: {pre_grasp}")
    else:
        print("\n✗ Failed to plan grasp")


if __name__ == "__main__":
    test_grasp_planner()
