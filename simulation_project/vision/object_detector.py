"""
Vision Processing Pipeline
Object detection, classification, and pose estimation using OpenCV
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class DetectedObject:
    """Container for detected object information"""
    label: str
    color: Tuple[int, int, int]  # RGB
    position_2d: Tuple[int, int]  # Pixel coordinates (x, y)
    position_3d: Optional[Tuple[float, float, float]] = None  # World coordinates
    bounding_box: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
    contour: Optional[np.ndarray] = None
    area: float = 0.0
    confidence: float = 1.0


class VisionProcessor:
    """Computer vision pipeline for object detection and classification"""
    
    def __init__(self, config: Dict):
        """
        Initialize vision processor
        
        Args:
            config: Vision configuration dictionary
        """
        self.config = config
        self.ml_config = config.get('ml', {})
        self.detection_method = self.ml_config.get('object_detection', {}).get('model', 'color_based')
        
        # Color definitions for classification (HSV ranges)
        self.color_ranges = {
            'red': [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),
                (np.array([170, 100, 100]), np.array([180, 255, 255]))  # Red wraps around
            ],
            'green': [
                (np.array([40, 50, 50]), np.array([80, 255, 255]))
            ],
            'blue': [
                (np.array([100, 100, 100]), np.array([130, 255, 255]))
            ],
            'yellow': [
                (np.array([20, 100, 100]), np.array([40, 255, 255]))
            ]
        }
        
        # Shape classification parameters
        self.shape_params = {
            'cube': {'sides': 4, 'tolerance': 0.15},
            'cylinder': {'circularity': 0.7},
            'sphere': {'circularity': 0.85}
        }
    
    def process_frame(self, image: np.ndarray, depth: Optional[np.ndarray] = None) -> List[DetectedObject]:
        """
        Process a single frame and detect objects
        
        Args:
            image: RGB image from vision sensor
            depth: Optional depth map
            
        Returns:
            List of detected objects
        """
        if self.detection_method == 'color_based':
            return self._color_based_detection(image, depth)
        elif self.detection_method == 'yolo':
            return self._yolo_detection(image, depth)
        else:
            raise ValueError(f"Unknown detection method: {self.detection_method}")
    
    def _color_based_detection(self, image: np.ndarray, 
                               depth: Optional[np.ndarray] = None) -> List[DetectedObject]:
        """
        Detect objects based on color segmentation
        
        Args:
            image: RGB image
            depth: Optional depth map
            
        Returns:
            List of detected objects
        """
        detected_objects = []
        
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Preprocessing
        blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
        
        # Detect objects for each color
        for color_name, ranges in self.color_ranges.items():
            # Create mask for this color
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in ranges:
                mask |= cv2.inRange(blurred, lower, upper)
            
            # Morphological operations to clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by minimum area
                if area < 100:  # Minimum 100 pixels
                    continue
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate center
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    cx, cy = x + w // 2, y + h // 2
                
                # Estimate 3D position from depth if available
                position_3d = None
                if depth is not None:
                    position_3d = self._estimate_3d_position(cx, cy, depth)
                
                # Classify shape
                shape = self._classify_shape(contour)
                
                # Get average color for verification
                mask_roi = mask[y:y+h, x:x+w]
                avg_color = cv2.mean(image[y:y+h, x:x+w], mask=mask_roi)[:3]
                
                # Create detected object
                obj = DetectedObject(
                    label=f"{color_name}_{shape}",
                    color=tuple(int(c) for c in avg_color),
                    position_2d=(cx, cy),
                    position_3d=position_3d,
                    bounding_box=(x, y, w, h),
                    contour=contour,
                    area=area,
                    confidence=0.9  # High confidence for color-based
                )
                
                detected_objects.append(obj)
        
        return detected_objects
    
    def _classify_shape(self, contour: np.ndarray) -> str:
        """
        Classify shape based on contour geometry
        
        Args:
            contour: OpenCV contour
            
        Returns:
            Shape name (cube, cylinder, sphere)
        """
        # Calculate perimeter and area
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        
        if perimeter == 0:
            return "unknown"
        
        # Circularity: 4π * area / perimeter²
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Approximate polygon
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_sides = len(approx)
        
        # Classify based on circularity and sides
        if circularity > self.shape_params['sphere']['circularity']:
            return "sphere"
        elif circularity > self.shape_params['cylinder']['circularity']:
            return "cylinder"
        elif 3 <= num_sides <= 6:
            return "cube"
        else:
            return "unknown"
    
    def _estimate_3d_position(self, px: int, py: int, 
                             depth: np.ndarray) -> Tuple[float, float, float]:
        """
        Estimate 3D world position from pixel coordinates and depth
        
        Args:
            px, py: Pixel coordinates
            depth: Depth map
            
        Returns:
            (x, y, z) in world coordinates
        """
        # Get depth at pixel
        if 0 <= py < depth.shape[0] and 0 <= px < depth.shape[1]:
            z = depth[py, px]
        else:
            z = 1.0  # Default depth
        
        # Simple pinhole camera model
        # TODO: Use actual camera intrinsics
        focal_length = 500  # Approximate
        cx = depth.shape[1] / 2
        cy = depth.shape[0] / 2
        
        x = (px - cx) * z / focal_length
        y = (py - cy) * z / focal_length
        
        return (x, y, z)
    
    def _yolo_detection(self, image: np.ndarray,
                       depth: Optional[np.ndarray] = None) -> List[DetectedObject]:
        """
        Detect objects using YOLO model
        
        Args:
            image: RGB image
            depth: Optional depth map
            
        Returns:
            List of detected objects
        """
        # Placeholder for YOLO implementation
        print("YOLO detection not yet implemented")
        return []
    
    def draw_detections(self, image: np.ndarray, 
                       detections: List[DetectedObject]) -> np.ndarray:
        """
        Draw detection overlays on image
        
        Args:
            image: Original image
            detections: List of detected objects
            
        Returns:
            Image with overlays
        """
        output = image.copy()
        
        for obj in detections:
            if obj.bounding_box is None:
                continue
            
            x, y, w, h = obj.bounding_box
            cx, cy = obj.position_2d
            
            # Draw bounding box
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(output, (cx, cy), 5, (255, 0, 0), -1)
            
            # Draw label
            label = f"{obj.label} ({obj.confidence:.2f})"
            cv2.putText(output, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw 3D position if available
            if obj.position_3d is not None:
                pos_str = f"({obj.position_3d[0]:.2f}, {obj.position_3d[1]:.2f}, {obj.position_3d[2]:.2f})"
                cv2.putText(output, pos_str, (x, y + h + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return output
    
    def filter_by_workspace(self, detections: List[DetectedObject],
                           workspace_bounds: Dict) -> List[DetectedObject]:
        """
        Filter detections to only those within workspace
        
        Args:
            detections: List of detected objects
            workspace_bounds: Dict with x_min, x_max, y_min, y_max, z_min, z_max
            
        Returns:
            Filtered list of detections
        """
        filtered = []
        
        for obj in detections:
            if obj.position_3d is None:
                continue
            
            x, y, z = obj.position_3d
            
            if (workspace_bounds['x_min'] <= x <= workspace_bounds['x_max'] and
                workspace_bounds['y_min'] <= y <= workspace_bounds['y_max'] and
                workspace_bounds['z_min'] <= z <= workspace_bounds['z_max']):
                filtered.append(obj)
        
        return filtered


def test_vision_processor():
    """Test the vision processor with a dummy image"""
    # Create test configuration
    config = {
        'ml': {
            'object_detection': {
                'model': 'color_based'
            }
        }
    }
    
    processor = VisionProcessor(config)
    
    # Create test image with colored circles
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Red circle
    cv2.circle(test_img, (100, 100), 30, (255, 0, 0), -1)
    # Green circle
    cv2.circle(test_img, (300, 200), 40, (0, 255, 0), -1)
    # Blue circle
    cv2.circle(test_img, (500, 300), 35, (0, 0, 255), -1)
    
    # Process
    detections = processor.process_frame(test_img)
    
    print(f"\nDetected {len(detections)} objects:")
    for obj in detections:
        print(f"  - {obj.label} at {obj.position_2d}, area: {obj.area:.0f}")
    
    # Visualize
    output = processor.draw_detections(test_img, detections)
    
    # Save result
    cv2.imwrite("test_detection.png", cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
    print("\n✓ Test output saved to test_detection.png")


if __name__ == "__main__":
    test_vision_processor()
