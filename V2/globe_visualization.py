"""
Globe visualization handler to control the globe LEDs based on location data.
This module translates geographic coordinates to LED positions and sends
commands via TCP socket to illuminate the appropriate LEDs.
"""
import time
import json
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from socket_client import SocketClient, TOTAL_LEDS

class GlobeVisualization:
    def __init__(self, ip: str = '100.85.4.50', port: int = 5000, min_delay: float = 0.2):
        """
        Initialize the globe visualization handler.
        
        Args:
            ip: IP address of the socket server
            port: Port number of the socket server
            min_delay: Minimum delay between sends in seconds
        """
        self.socket_client = SocketClient(ip=ip, port=port, min_delay=min_delay)
        self.socket_client.start()
        self.default_background = [5, 5, 5]  # Very dim white as default background
        self.current_led_data = self._create_led_data(self.default_background)
        print("Globe visualization handler initialized")
    
    def _create_led_data(self, base_color=None):
        """Create a new LED data array with all LEDs set to the same color."""
        if base_color is None:
            base_color = [0, 0, 0]  # Default to all off
        return [base_color.copy() for _ in range(402)]
    
    def _calculate_led_index(self, latitude: float, longitude: float) -> int:
        """
        Calculate the LED index based on latitude and longitude.
        This is a simplified version - a real implementation would need a proper mapping.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            
        Returns:
            The index of the LED closest to the given coordinates
        """
        # This is a very simplified mapping function
        # In a real implementation, you would have a more accurate mapping
        # based on the physical arrangement of LEDs on your globe
        
        # Normalize latitude and longitude to 0-1 range
        lat_norm = (latitude + 90) / 180
        lon_norm = (longitude + 180) / 360
        
        # Simple mapping to LED index (0-401)
        # This assumes LEDs are arranged in a grid-like pattern
        # wrapped around the globe
        rows = 20  # Assuming 20 rows of LEDs
        cols = int(402 / rows)  # Columns per row
        
        row = int(lat_norm * (rows - 1))
        col = int(lon_norm * (cols - 1))
        
        led_index = row * cols + col
        led_index = min(401, max(0, led_index))  # Clamp to valid range
        
        return led_index
    
    def _get_surrounding_leds(self, center_index: int, radius: int) -> List[int]:
        """
        Get the indices of LEDs surrounding a center LED.
        
        Args:
            center_index: Index of the center LED
            radius: How many surrounding LEDs to include
            
        Returns:
            List of LED indices
        """
        # For simplicity, we'll just return LEDs with nearby indices
        # In a real implementation, you would consider the 3D arrangement
        # of LEDs on the globe
        result = []
        for i in range(-radius, radius + 1):
            idx = (center_index + i) % 402
            result.append(idx)
        return result
    
    def highlight_point(self, latitude: float, longitude: float, 
                        color: List[int] = None, radius: int = 5,
                        background_color: List[int] = None) -> bool:
        """
        Highlight a point on the globe.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            color: RGB color to use [R, G, B]
            radius: How many LEDs around the point to highlight
            background_color: RGB color for background LEDs
            
        Returns:
            True if successful, False otherwise
        """
        if color is None:
            color = [255, 0, 0]  # Default to red
            
        # Set the background color
        if background_color is not None:
            self.current_led_data = self._create_led_data(background_color)
        else:
            self.current_led_data = self._create_led_data(self.default_background)
        
        # Calculate the center LED index
        center_index = self._calculate_led_index(latitude, longitude)
        
        # Get surrounding LEDs
        led_indices = self._get_surrounding_leds(center_index, radius)
        
        # Set the color for these LEDs
        for idx in led_indices:
            self.current_led_data[idx] = color
            
        # Send the data to the globe
        return self.socket_client.send_led_data(self.current_led_data)
    
    def highlight_region(self, polygon: List[List[float]], 
                         color: List[int] = None,
                         point_radius: int = 2,
                         background_color: List[int] = None) -> bool:
        """
        Highlight a region on the globe defined by a polygon.
        
        Args:
            polygon: List of [latitude, longitude] points defining the region
            color: RGB color to use [R, G, B]
            point_radius: Radius of each point in the polygon
            background_color: RGB color for background LEDs
            
        Returns:
            True if successful, False otherwise
        """
        if color is None:
            color = [0, 0, 255]  # Default to blue
            
        # Set the background color
        if background_color is not None:
            self.current_led_data = self._create_led_data(background_color)
        else:
            self.current_led_data = self._create_led_data(self.default_background)
        
        # Highlight each point in the polygon
        for point in polygon:
            latitude, longitude = point
            center_index = self._calculate_led_index(latitude, longitude)
            led_indices = self._get_surrounding_leds(center_index, point_radius)
            for idx in led_indices:
                self.current_led_data[idx] = color
        
        # Send the data to the globe
        return self.socket_client.send_led_data(self.current_led_data)
    
    def process_location_data(self, location_data: Dict[str, Any]) -> bool:
        """
        Process location data from GPT and update the globe visualization.
        
        Args:
            location_data: Dictionary with location data from GPT response
            
        Returns:
            True if successful, False otherwise
        """
        if location_data is None:
            return False
        
        try:
            location_type = location_data.get("type")
            color = location_data.get("color_rgb", [255, 0, 0])
            
            if location_type == "point":
                latitude = location_data.get("lat")
                longitude = location_data.get("lon")
                if latitude is None or longitude is None:
                    print("Error: Missing latitude or longitude in point data")
                    return False
                return self.highlight_point(latitude, longitude, color)
                
            elif location_type == "region":
                polygon = location_data.get("polygon")
                if not polygon:
                    print("Error: Missing polygon data in region")
                    return False
                return self.highlight_region(polygon, color)
                
            else:
                print(f"Error: Unknown location type: {location_type}")
                return False
                
        except Exception as e:
            print(f"Error processing location data: {e}")
            return False
    
    def set_all_leds(self, color: List[int]) -> bool:
        """
        Set all LEDs to a single color.
        
        Args:
            color: RGB color to set [R, G, B]
            
        Returns:
            True if successful, False otherwise
        """
        led_data = self._create_led_data(color)
        return self.socket_client.send_led_data(led_data)
    
    def turn_off(self) -> bool:
        """
        Turn off all LEDs.
        
        Returns:
            True if successful, False otherwise
        """
        return self.set_all_leds([0, 0, 0])
    
    def set_background(self, color: List[int]):
        """
        Set the default background color.
        
        Args:
            color: RGB color to set [R, G, B]
        """
        self.default_background = color
    
    def cleanup(self):
        """
        Clean up resources.
        """
        try:
            # Turn off all LEDs
            self.turn_off()
            time.sleep(0.5)  # Wait for the command to be sent
            
            # Stop the socket client
            self.socket_client.stop()
            print("Globe visualization cleanup complete")
        except Exception as e:
            print(f"Error during globe visualization cleanup: {e}")


# Test function to verify functionality
def test_globe_visualization():
    """Test the globe visualization with sample location data."""
    globe = GlobeVisualization()
    
    try:
        # Test 1: Set all LEDs to dim white
        print("\nTest 1: All LEDs dim white")
        globe.set_all_leds([30, 30, 30])
        time.sleep(2)
        
        # Test 2: Highlight Paris
        print("\nTest 2: Highlighting Paris")
        globe.highlight_point(48.8566, 2.3522, [255, 0, 0])
        time.sleep(3)
        
        # Test 3: Highlight a region (Australia)
        print("\nTest 3: Highlighting Australia")
        australia_polygon = [
            [-12.46, 130.84],  # Darwin
            [-33.87, 151.21],  # Sydney
            [-37.81, 144.96],  # Melbourne
            [-31.95, 115.86]   # Perth
        ]
        globe.highlight_region(australia_polygon, [0, 255, 0])
        time.sleep(3)
        
        # Test 4: Process location data from GPT
        print("\nTest 4: Processing GPT location data")
        sample_data = {
            "type": "point",
            "lat": 40.7128,
            "lon": -74.0060,
            "color_rgb": [255, 165, 0]  # Orange for NYC
        }
        globe.process_location_data(sample_data)
        time.sleep(3)
        
        # Test 5: Turn off all LEDs
        print("\nTest 5: All LEDs off")
        globe.turn_off()
        
    finally:
        # Clean up
        time.sleep(1)
        globe.cleanup()


if __name__ == "__main__":
    print("Testing Globe visualization...")
    test_globe_visualization()
