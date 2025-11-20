"""
Robot Arm Extension Experiment
Tests the effect of extending arm links on workspace coverage
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import yaml


class ArmExtensionAnalyzer:
    """Analyze workspace changes with arm extension"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def analyze_workspace_coverage(self, link_extensions: list):
        """
        Analyze how workspace changes with different link extensions
        
        Args:
            link_extensions: List of extension lengths to test (meters)
        """
        print("\n=== Arm Extension Analysis ===\n")
        
        # Base arm parameters (example for 6-DOF arm)
        base_link_lengths = [0.0, 0.15, 0.30, 0.25, 0.15, 0.10]  # meters
        
        results = []
        
        for extension in link_extensions:
            # Apply extension to upper arm link (index 2)
            extended_lengths = base_link_lengths.copy()
            extended_lengths[2] += extension
            
            # Calculate maximum reach
            max_reach = sum(extended_lengths)
            
            # Calculate workspace volume (approximate cylinder)
            workspace_volume = np.pi * max_reach**2 * max_reach
            
            # Calculate reachable desk area
            desk_length = self.config['desk']['length']
            desk_depth = self.config['desk']['depth']
            robot_base = self.config['robot']['base_position']
            
            # Approximate reachable area on desk
            reachable_area = self._calculate_reachable_area(
                max_reach, robot_base, desk_length, desk_depth
            )
            
            coverage_percent = (reachable_area / (desk_length * desk_depth)) * 100
            
            results.append({
                'extension': extension,
                'total_reach': max_reach,
                'workspace_volume': workspace_volume,
                'reachable_area': reachable_area,
                'coverage_percent': coverage_percent
            })
            
            print(f"Extension: +{extension*100:.1f}cm")
            print(f"  Max reach: {max_reach:.3f}m")
            print(f"  Workspace volume: {workspace_volume:.3f}m³")
            print(f"  Desk coverage: {coverage_percent:.1f}%")
            print()
        
        # Visualize results
        self._plot_results(results)
        
        return results
    
    def _calculate_reachable_area(self, reach, base_pos, desk_length, desk_depth):
        """
        Calculate approximate reachable area on desk surface
        
        Args:
            reach: Maximum arm reach (meters)
            base_pos: Robot base position [x, y, z]
            desk_length: Desk x-dimension
            desk_depth: Desk y-dimension
            
        Returns:
            Reachable area in m²
        """
        # Simplified: circle intersection with rectangle
        # More accurate would use actual kinematics
        
        base_x, base_y, base_z = base_pos
        
        # Circle centered at base projection
        circle_area = np.pi * reach**2
        
        # Approximate intersection with desk bounds
        desk_area = desk_length * desk_depth
        
        # Simple heuristic: min of circle and desk area
        return min(circle_area, desk_area)
    
    def _plot_results(self, results):
        """Plot analysis results"""
        extensions = [r['extension'] * 100 for r in results]  # Convert to cm
        reaches = [r['total_reach'] for r in results]
        coverages = [r['coverage_percent'] for r in results]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot reach vs extension
        ax1.plot(extensions, reaches, 'b-o', linewidth=2, markersize=8)
        ax1.set_xlabel('Link Extension (cm)', fontsize=12)
        ax1.set_ylabel('Maximum Reach (m)', fontsize=12)
        ax1.set_title('Arm Reach vs Link Extension', fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # Plot coverage vs extension
        ax2.plot(extensions, coverages, 'g-s', linewidth=2, markersize=8)
        ax2.set_xlabel('Link Extension (cm)', fontsize=12)
        ax2.set_ylabel('Desk Coverage (%)', fontsize=12)
        ax2.set_title('Workspace Coverage vs Link Extension', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=100, color='r', linestyle='--', alpha=0.5, label='Full coverage')
        ax2.legend()
        
        plt.tight_layout()
        
        # Save plot
        output_path = Path(__file__).parent.parent / "logs" / "arm_extension_analysis.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Analysis plot saved to {output_path}")
        
        plt.show()
    
    def recommend_extension(self, target_coverage: float = 95.0):
        """
        Recommend optimal extension for target coverage
        
        Args:
            target_coverage: Desired desk coverage percentage
            
        Returns:
            Recommended extension length in meters
        """
        print(f"\n=== Finding Extension for {target_coverage}% Coverage ===\n")
        
        # Test range of extensions
        test_extensions = np.linspace(0, 0.20, 20)  # 0 to 20cm
        
        results = []
        for ext in test_extensions:
            # Quick calculation
            base_reach = 0.95  # Approximate base arm reach
            extended_reach = base_reach + ext
            
            # Simplified coverage estimate
            coverage = min(100, (extended_reach / 0.75) * 100)
            
            results.append((ext, coverage))
            
            if coverage >= target_coverage and len(results) > 1:
                print(f"Recommended extension: +{ext*100:.1f}cm")
                print(f"  Achieves: {coverage:.1f}% coverage")
                print(f"  Total reach: {extended_reach:.3f}m")
                return ext
        
        print(f"⚠ Target coverage {target_coverage}% not achievable with tested extensions")
        return None


def main():
    """Main entry point"""
    config_path = Path(__file__).parent.parent / "config" / "sim_config.yaml"
    
    analyzer = ArmExtensionAnalyzer(str(config_path))
    
    # Test different extension lengths
    extensions = [0.00, 0.05, 0.10, 0.15, 0.20]  # 0, 5, 10, 15, 20 cm
    
    results = analyzer.analyze_workspace_coverage(extensions)
    
    # Recommend optimal extension
    analyzer.recommend_extension(target_coverage=95.0)
    
    print("\n✓ Analysis complete")


if __name__ == "__main__":
    main()
