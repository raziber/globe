"""
LED Globe Debug Tool

This script provides a dedicated interface for debugging the LED globe visualization,
specifically to help identify which LEDs are lighting up for different coordinates.
"""
import argparse
from typing import List, Dict, Any
from globe_visualizer_3d import Globe3DVisualizer
from globe_visualization import GlobeVisualization

def debug_led_mapping(mode: str, **kwargs):
    """
    Debug the LED mapping with different visualizations.
    
    Args:
        mode: Visualization mode ('all', 'point', 'region', 'ids', 'coverage', 'compare')
        **kwargs: Additional arguments for specific modes
    """
    visualizer = Globe3DVisualizer()
    
    if mode == 'all':
        # Show all LEDs
        visualizer.visualize_all_leds()
    
    elif mode == 'point':
        # Debug a specific point
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        radius = kwargs.get('radius', 5)
        
        if lat is None or lon is None:
            print("Error: Latitude and longitude are required for point mode")
            return
            
        visualizer.visualize_point_highlight(lat, lon, radius)
        
    elif mode == 'region':
        # Debug a region
        polygon_str = kwargs.get('polygon')
        point_radius = kwargs.get('point_radius', 2)
        
        if not polygon_str:
            print("Error: Polygon is required for region mode")
            return
            
        # Parse the polygon string format: "lat1,lon1;lat2,lon2;..."
        try:
            points = polygon_str.split(';')
            polygon = []
            for point in points:
                lat, lon = map(float, point.split(','))
                polygon.append([lat, lon])
                
            visualizer.visualize_region_highlight(polygon, point_radius)
            
        except Exception as e:
            print(f"Error parsing polygon: {e}")
            return
    
    elif mode == 'ids':
        # Visualize LED IDs
        min_id = kwargs.get('min_id', 46)
        visualizer.visualize_led_ids(min_id)
        
    elif mode == 'coverage':
        # Visualize LED coverage (mapping between coords and IDs)
        min_id = kwargs.get('min_id', 46)
        visualizer.visualize_led_coverage(min_id)
    
    elif mode == 'compare':
        # Compare LED activation between different IDs
        globe = GlobeVisualization()
        
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        radius = kwargs.get('radius', 5)
        
        if lat is None or lon is None:
            print("Error: Latitude and longitude are required for compare mode")
            return
        
        # Use the globe's LED debug feature to show internal calculation
        debug_data = {
            "type": "point",
            "lat": lat,
            "lon": lon,
            "radius": radius
        }
        
        # This will print the internal LEDs calculation and show the 3D viz
        globe.debug_leds(debug_data)
        
    else:
        print(f"Unknown mode: {mode}")


def main():
    parser = argparse.ArgumentParser(description="Debug tool for the LED Globe visualization")
    parser.add_argument('--mode', type=str, default='all',
                        choices=['all', 'point', 'region', 'ids', 'coverage', 'compare'],
                        help='Visualization mode')
    
    # Arguments for point mode
    parser.add_argument('--lat', type=float, help='Latitude in degrees (-90 to 90)')
    parser.add_argument('--lon', type=float, help='Longitude in degrees (-180 to 180)')
    parser.add_argument('--radius', type=int, default=5, help='Radius for point highlighting')
    
    # Arguments for region mode
    parser.add_argument('--polygon', type=str, 
                        help='Polygon points as "lat1,lon1;lat2,lon2;..."')
    parser.add_argument('--point_radius', type=int, default=2, 
                        help='Radius for each point in region')
    
    # Arguments for IDs mode
    parser.add_argument('--min_id', type=int, default=46, help='Minimum LED ID to show')
    
    args = parser.parse_args()
    
    # Convert args to kwargs dict
    kwargs = vars(args)
    mode = kwargs.pop('mode')
    
    debug_led_mapping(mode, **kwargs)


if __name__ == "__main__":
    main()
