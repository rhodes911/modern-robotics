"""
CoppeliaSim Scene Builder
Generates a complete robotic arm workspace scene programmatically
"""

import sys
import yaml
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

from coppelia_api import CoppeliaSimConnection


class SceneBuilder:
    """Build and configure CoppeliaSim scene for robotic arm simulation"""
    
    def __init__(self, config_path: str):
        """
        Initialize scene builder with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.conn = CoppeliaSimConnection(
            host=self.config['coppeliasim']['host'],
            port=self.config['coppeliasim']['port']
        )
        self.object_handles = {}
    
    def build_scene(self):
        """Build complete simulation scene"""
        print("\n=== Building CoppeliaSim Scene ===\n")
        
        # Connect to CoppeliaSim
        if not self.conn.connect():
            print("Failed to connect. Make sure CoppeliaSim is running!")
            return False
        
        try:
            # Clear existing scene
            self._clear_scene()
            
            # Build scene components
            self._create_desk()
            self._setup_robot()
            self._create_sorting_zones()
            self._spawn_objects()
            self._setup_vision_sensor()
            
            print("\n✓ Scene built successfully!")
            print(f"  - Desk: {self.config['desk']['length']}m × {self.config['desk']['depth']}m")
            print(f"  - Robot: {self.config['robot']['model']}")
            print(f"  - Objects: {len(self.object_handles)} spawned")
            print(f"  - Sorting zones: {len(self.config['sorting_zones'])}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Error building scene: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _clear_scene(self):
        """Remove all dynamic objects from scene"""
        print("Clearing existing scene...")
        # Note: In practice, you might want to be more selective
        # This is a simplified version
    
    def _create_desk(self):
        """Create the desk/table surface"""
        print("Creating desk...")
        
        desk_cfg = self.config['desk']
        
        # Create cuboid for desk
        desk_handle = self.conn.sim.createPrimitiveShape(
            self.conn.sim.primitiveshape_cuboid,
            [desk_cfg['length'], desk_cfg['depth'], desk_cfg['height']]
        )
        
        # Set position
        self.conn.set_object_position(desk_handle, desk_cfg['position'])
        
        # Set color
        self.conn.sim.setShapeColor(
            desk_handle, None, 
            self.conn.sim.colorcomponent_ambient_diffuse,
            desk_cfg['color']
        )
        
        # Set as static
        self.conn.sim.setObjectInt32Param(
            desk_handle,
            self.conn.sim.shapeintparam_static,
            1
        )
        
        # Make desk respondable (can collide with objects)
        self.conn.sim.setObjectInt32Param(
            desk_handle,
            self.conn.sim.shapeintparam_respondable,
            1
        )
        
        # Name it
        self.conn.sim.setObjectAlias(desk_handle, "desk")
        
        self.object_handles['desk'] = desk_handle
        print(f"  ✓ Desk created at {desk_cfg['position']}")
    
    def _setup_robot(self):
        """Setup robot arm in the scene"""
        print(f"Setting up {self.config['robot']['model']} robot arm...")
        
        robot_cfg = self.config['robot']
        
        # Note: This assumes you have the robot model available in CoppeliaSim
        # You would typically load a model file (.ttm) here
        print(f"  → Robot model: {robot_cfg['model']}")
        print(f"  → Base position: {robot_cfg['base_position']}")
        print(f"  → Gripper type: {robot_cfg['gripper_type']}")
        print("  ⚠ Manual step: Load robot model in CoppeliaSim UI")
        print(f"     File > Load Model... > Select {robot_cfg['model']} model")
        
        # After loading, you can position it programmatically
        # Uncomment when robot is loaded:
        # robot_handle = self.conn.get_object_handle(robot_cfg['model'])
        # if robot_handle != -1:
        #     self.conn.set_object_position(robot_handle, robot_cfg['base_position'])
        #     self.object_handles['robot'] = robot_handle
    
    def _create_sorting_zones(self):
        """Create visual markers for sorting bins"""
        print("Creating sorting zones...")
        
        for zone in self.config['sorting_zones']:
            # Create a flat cuboid as bin marker
            bin_handle = self.conn.sim.createPrimitiveShape(
                self.conn.sim.primitiveshape_cuboid,
                zone['size']
            )
            
            # Position it
            self.conn.set_object_position(bin_handle, zone['position'])
            
            # Color it
            self.conn.sim.setShapeColor(
                bin_handle, None,
                self.conn.sim.colorcomponent_ambient_diffuse,
                zone['color']
            )
            
            # Make it transparent
            self.conn.sim.setObjectInt32Param(
                bin_handle,
                self.conn.sim.shapeintparam_static,
                1
            )
            
            # Make bins respondable
            self.conn.sim.setObjectInt32Param(
                bin_handle,
                self.conn.sim.shapeintparam_respondable,
                1
            )
            
            # Name it
            self.conn.sim.setObjectAlias(bin_handle, zone['name'])
            
            self.object_handles[zone['name']] = bin_handle
            print(f"  ✓ {zone['name']} at {zone['position']}")
    
    def _spawn_objects(self):
        """Spawn random objects on the desk"""
        print(f"Spawning {self.config['objects']['count']} objects...")
        
        obj_cfg = self.config['objects']
        spawn_area = obj_cfg['spawn_area']
        
        objects_created = 0
        
        for i in range(obj_cfg['count']):
            # Choose random object type
            obj_type = np.random.choice(
                obj_cfg['types'],
                p=[t['weight'] for t in obj_cfg['types']]
            )
            
            # Choose random color
            color = obj_type['colors'][np.random.randint(len(obj_type['colors']))]
            
            # Create object based on type
            if obj_type['type'] == 'cube':
                handle = self.conn.sim.createPrimitiveShape(
                    self.conn.sim.primitiveshape_cuboid,
                    [obj_type['size']] * 3
                )
            elif obj_type['type'] == 'cylinder':
                handle = self.conn.sim.createPrimitiveShape(
                    self.conn.sim.primitiveshape_cylinder,
                    [obj_type['radius'], obj_type['radius'], obj_type['height']]
                )
            elif obj_type['type'] == 'sphere':
                handle = self.conn.sim.createPrimitiveShape(
                    self.conn.sim.primitiveshape_spheroid,
                    [obj_type['radius']] * 3
                )
            else:
                continue
            
            # Random position in spawn area
            x = np.random.uniform(spawn_area['x_min'], spawn_area['x_max'])
            y = np.random.uniform(spawn_area['y_min'], spawn_area['y_max'])
            z = spawn_area['z']
            
            self.conn.set_object_position(handle, [x, y, z])
            
            # Set color
            self.conn.sim.setShapeColor(
                handle, None,
                self.conn.sim.colorcomponent_ambient_diffuse,
                color
            )
            
            # Make it dynamic (affected by physics)
            self.conn.sim.setObjectInt32Param(
                handle,
                self.conn.sim.shapeintparam_static,
                0
            )
            
            # Enable respondable (can collide)
            self.conn.sim.setObjectInt32Param(
                handle,
                self.conn.sim.shapeintparam_respondable,
                1
            )
            
            # Set mass
            self.conn.sim.setShapeMass(handle, 0.05)  # 50 grams
            
            # Name it
            obj_name = f"object_{obj_type['type']}_{i}"
            self.conn.sim.setObjectAlias(handle, obj_name)
            
            self.object_handles[obj_name] = handle
            objects_created += 1
        
        print(f"  ✓ Spawned {objects_created} objects")
    
    def _setup_vision_sensor(self):
        """Setup vision sensor camera"""
        print("Setting up vision sensor...")
        print("  ⚠ Manual step: Add vision sensor in CoppeliaSim")
        print("     Add > Vision sensor > Vision sensor (perspective)")
        print("     Position: [-0.5, 0.0, 0.6]")
        print("     Point at: [0.0, 0.0, 0.05]")
        
        # Skip automatic creation for now - can add manually in UI
        # The main controller will look for it by name "vision_sensor"
    
    def save_scene(self, filename: str):
        """Save the current scene to a file"""
        print(f"\nSaving scene to {filename}...")
        scene_path = Path(__file__).parent.parent / "scenes" / filename
        scene_path.parent.mkdir(exist_ok=True)
        
        # Save scene
        self.conn.sim.saveScene(str(scene_path))
        print(f"✓ Scene saved to {scene_path}")
    
    def cleanup(self):
        """Disconnect from CoppeliaSim"""
        self.conn.disconnect()


def main():
    """Main entry point"""
    config_path = Path(__file__).parent.parent / "config" / "sim_config.yaml"
    
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        return
    
    builder = SceneBuilder(str(config_path))
    
    try:
        if builder.build_scene():
            print("\n✓ Scene ready for simulation!")
            
            # Auto-save scene
            print("\nSaving scene...")
            builder.save_scene("yahboom_arm_workspace.ttt")
            
            print("\nNext steps:")
            print("  1. Manually load robot model (UR5) from CoppeliaSim UI:")
            print("     Model browser > robots > non-mobile > UR5.ttm")
            print("  2. Manually add vision sensor:")
            print("     Add > Vision sensor > Vision sensor (perspective)")
            print("     Name: vision_sensor, Position: [-0.5, 0.0, 0.6]")
            print("  3. Save scene again: File > Save Scene")
            print("  4. Run pick-and-place demo: python scripts/basic_pick_place.py")
        
    finally:
        builder.cleanup()


if __name__ == "__main__":
    main()
