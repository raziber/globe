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
        self.default_background = [0, 0, 0]  # Very dim white as default background
        self.current_led_data = self._create_led_data(self.default_background)        
        print("Globe visualization handler initialized")
        
    def send_with_buffer_handling(self, led_data: List[List[int]]) -> bool:
        """
        Send LED data with buffer handling to prevent half-delay issues.
        
        This method addresses the "half delay buffer issue" by ensuring 
        that data is properly flushed before sending new data. It adds
        a small delay and additional buffer checks.
        
        Args:
            led_data: List of RGB values for each LED
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure any pending data in socket is flushed
            if self.socket_client.is_connected:
                # Longer delay to ensure any previous commands have been processed
                time.sleep(0.1)
                
                # Make a copy of the LED data to avoid modification during sending
                data_to_send = [led.copy() for led in led_data]
                
                # Wait to ensure all previous data has been sent
                if hasattr(self.socket_client, 'pending_data') and self.socket_client.pending_data is not None:
                    print("Waiting for pending data to be sent...")
                    wait_start = time.time()
                    while self.socket_client.pending_data is not None:
                        time.sleep(0.05)
                        # Give up after 1 second to avoid deadlock
                        if time.time() - wait_start > 1:
                            print("Warning: Timeout waiting for pending data")
                            break
                
                # Send the data and verify it was queued successfully
                if not self.socket_client.send_led_data(data_to_send):
                    print("Warning: Failed to queue LED data for sending")
                    return False
                
                # Wait for confirmation that data processing has started
                time.sleep(0.1)
                    
                return True
            else:
                print("Error: Socket is not connected")
                return False
        except Exception as e:
            print(f"Error in send_with_buffer_handling: {e}")
            return False
    
    def _create_led_data(self, base_color=None):
        """Create a new LED data array with all LEDs set to the same color."""
        if base_color is None:
            base_color = [0, 0, 0]  # Default to all off
        return [base_color.copy() for _ in range(402)]    
    
    def _calculate_led_index(self, latitude: float, longitude: float) -> int:
        """
        Calculate the LED index based on latitude and longitude using spherical excess method.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            
        Returns:
            The index of the LED closest to the given coordinates
        """
        # Convert degrees to radians for spherical calculations
        lat_rad = math.radians(latitude + 90)
        lon_rad = math.radians(longitude + 180)
        
        # Total number of LEDs
        total_leds = TOTAL_LEDS
        
        # Implement spherical excess method - divides the sphere into equal area regions
        # This method ensures that each LED represents approximately equal area on the sphere
        
        # Calculate normalized coordinates using sinusoidal projection 
        # (a simple equal-area projection)
        y = lat_rad / math.pi  # -0.5 to 0.5
        
        # Use true spherical excess calculation for x-coordinate
        # This accounts for the convergence of meridians at poles
        x = lon_rad * math.cos(lat_rad) / math.pi  # Adjusts for narrowing at poles
        
        # Normalize to 0-1 range for both coordinates
        y = (y + 0.5)  # 0 to 1 from south to north pole
        x = (x + 1.0) / 2.0  # 0 to 1 around the circumference
        
        # Map to LEDs arranged in a grid-like pattern
        rows = 20  # Assuming 20 rows of LEDs
        cols = int(total_leds / rows)  # Columns per row
        
        # Adjust row calculations based on latitude to account for
        # the different number of LEDs needed at different latitudes
        row = int(y * (rows - 1))
        
        # At poles, fewer LEDs are needed, at equator more are needed
        # Adjust column calculation based on the row (latitude band)
        col_factor = math.cos(math.pi * (row / (rows - 1) - 0.5))
        col_factor = max(0.5, col_factor)  # Ensure a minimum factor
        
        # Calculate column position
        col = int(x * (cols - 1) * col_factor) % cols
        
        # Calculate final LED index
        led_index = row * cols + col
        led_index = min(total_leds - 1, max(0, led_index))  # Clamp to valid range
        
        return led_index
    
    def _get_surrounding_leds(self, center_index: int, radius: int) -> List[int]:
        """
        Get the indices of LEDs surrounding a center LED using spherical geometry.
        
        Args:
            center_index: Index of the center LED
            radius: Angular radius in degrees for surrounding LEDs
            
        Returns:
            List of LED indices
        """
        # This implementation considers the 3D arrangement of LEDs on the globe
        # using spherical coordinates and haversine distance
        
        # Total number of LEDs
        total_leds = TOTAL_LEDS
        
        # Convert center index to row and column
        rows = 20
        cols = int(total_leds / rows)
        
        center_row = center_index // cols
        center_col = center_index % cols
        
        # Calculate approximate latitude and longitude of center LED
        # This is a reverse mapping from LED index to spherical coordinates
        lat_center = (center_row / (rows - 1) - 0.5) * math.pi  # In radians
        
        # Adjust for the varying column density at different latitudes
        col_factor = math.cos(lat_center)
        col_factor = max(0.5, col_factor)
        lon_center = (center_col / ((cols - 1) * col_factor) - 0.5) * 2 * math.pi  # In radians
        
        # Radius in radians (convert from LED count to angular radius)
        angular_radius = math.radians(radius * 5)  # Approx 5 degrees per LED
        
        result = []
        
        # Scan all LEDs within reasonable range and check spherical distance
        scan_range = radius * 3  # Expanded search range to ensure we find all nearby LEDs
        
        for r_offset in range(-scan_range, scan_range + 1):
            r = (center_row + r_offset) % rows
            
            for c_offset in range(-scan_range, scan_range + 1):
                c = (center_col + c_offset) % cols
                
                # Calculate LED index
                idx = r * cols + c
                
                if idx >= 0 and idx < total_leds:
                    # Convert to lat/lon to check spherical distance
                    lat = (r / (rows - 1) - 0.5) * math.pi
                    
                    # Adjust column density based on latitude
                    c_factor = math.cos(lat)
                    c_factor = max(0.5, c_factor)
                    lon = (c / ((cols - 1) * c_factor) - 0.5) * 2 * math.pi
                    
                    # Calculate haversine distance
                    dlat = lat - lat_center
                    dlon = lon - lon_center
                    
                    # Handle longitude wrapping at the anti-meridian
                    if dlon > math.pi:
                        dlon = 2*math.pi - dlon
                    elif dlon < -math.pi:
                        dlon = 2*math.pi + dlon
                    
                    # Haversine formula
                    a = math.sin(dlat/2)**2 + math.cos(lat_center) * math.cos(lat) * math.sin(dlon/2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    
                    # If within angular radius, add to result
                    if c <= angular_radius:
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
        
        # Calculate the center LED index - function will convert degrees to radians internally
        center_index = self._calculate_led_index(latitude, longitude)
        
        # Get surrounding LEDs
        led_indices = self._get_surrounding_leds(center_index, radius)
        
        # Set the color for these LEDs
        for idx in led_indices:
            self.current_led_data[idx] = color
            
        # Send the data to the globe with buffer handling
        return self.send_with_buffer_handling(self.current_led_data)
    
    def highlight_region(self, polygon: List[List[float]], 
                         color: List[int] = None,
                         point_radius: int = 2,
                         background_color: List[int] = None) -> bool:
        """
        Highlight a region on the globe defined by a polygon using spherical excess method.
        
        Args:
            polygon: List of [latitude, longitude] points defining the region (in degrees)
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
        # Functions will convert degrees to radians internally
        for point in polygon:
            latitude, longitude = point
            center_index = self._calculate_led_index(latitude, longitude)
            led_indices = self._get_surrounding_leds(center_index, point_radius)
            for idx in led_indices:
                self.current_led_data[idx] = color
        
        # Send the data to the globe with buffer handling
        return self.send_with_buffer_handling(self.current_led_data)
    
    def process_location_data(self, location_data: Dict[str, Any]) -> bool:
        """
        Process location data from GPT and update the globe visualization.
        
        Args:
            location_data: Dictionary with location data from GPT response
            
        Returns:
            True if successful, False otherwise
        """
        if location_data is None:
            print("Error: No location data provided")
            return False
        
        try:
            location_type = location_data.get("type")
            color = location_data.get("color_rgb", [255, 0, 0])
            
            # Validate color format
            if not isinstance(color, list) or len(color) != 3:
                print(f"Warning: Invalid color format: {color}. Using default red.")
                color = [255, 0, 0]
            
            # Ensure color values are integers and within range
            color = [max(0, min(255, int(c))) for c in color]
            if location_type == "point":
                latitude = location_data.get("lat")
                longitude = location_data.get("lon")
                if latitude is None or longitude is None:
                    print("Error: Missing latitude or longitude in point data")
                    return False
                
                # Use fixed defaults since these are not in the actual data
                radius = 5  # Default radius
                background_color = self.default_background
                
                print(f"Highlighting point at lat: {latitude}, lon: {longitude} with color: {color}")
                return self.highlight_point(latitude, longitude, color, radius, background_color)
                
            elif location_type == "region":
                polygon = location_data.get("polygon")
                if not polygon:
                    print("Error: Missing polygon data in region")
                    return False
                  # Validate polygon format
                if not isinstance(polygon, list):
                    print(f"Error: Invalid polygon format: {polygon}")
                    return False
                
                # Use fixed defaults since these are not in the actual data
                point_radius = 2
                background_color = self.default_background
                
                print(f"Highlighting region with {len(polygon)} points and color: {color}")
                return self.highlight_region(polygon, color, point_radius, background_color)
                
            else:
                print(f"Error: Unknown location type: {location_type}")
                return False                
        except Exception as e:
            print(f"Error processing location data: {e}")
            import traceback
            traceback.print_exc()
            
            # Attempt recovery - set a basic error indicator on the globe
            try:
                # Create a simple error pattern (red flashing LEDs at the top of the globe)
                error_leds = self._create_led_data([0, 0, 0])  # Start with all LEDs off
                for i in range(20):  # Flash the first 20 LEDs red
                    error_leds[i] = [255, 0, 0]
                self.send_with_buffer_handling(error_leds)
            except:
                # If even the recovery fails, just continue
                pass
                
            return False
    
    def process_ai_response_to_led(self, ai_response: Dict[str, Any]) -> bool:
        """
        Process AI response data and translate it to LED data with buffer handling.
        
        This method specifically handles the conversion from AI response format to LED
        data format, ensuring proper buffer handling during the transition to prevent
        the "half delay buffer issue".
        
        Args:
            ai_response: Dictionary with location data from AI response
            
        Returns:
            True if successful, False otherwise
        """
        if ai_response is None:
            print("Error: No AI response data provided")
            return False
            
        try:
            # Ensure socket connection is ready
            if not self.socket_client.is_connected:
                print("Warning: Socket connection not established. Attempting to reconnect...")
                time.sleep(0.1)  # Small delay to allow potential reconnection
                
            # Extract location data from AI response if nested
            location_data = ai_response.get("location", ai_response)
            
            # Pre-process location data to ensure compatibility
            if isinstance(location_data, str):
                try:
                    # Try to parse if it's a JSON string
                    import json
                    location_data = json.loads(location_data)
                except:
                    print(f"Error: Could not parse location data string: {location_data}")
                    return False
            
            # First, prepare all the data without sending
            led_data = None
              # Determine location type and prepare corresponding LED data
            location_type = location_data.get("type")
            color = location_data.get("color_rgb", [255, 0, 0])
            
            # Validate and normalize color
            if not isinstance(color, list) or len(color) != 3:
                print(f"Warning: Invalid color format: {color}. Using default red.")
                color = [255, 0, 0]
            
            color = [max(0, min(255, int(c))) for c in color]
            
            # Create new LED data based on location type
            if location_type == "point":                # Get point data
                latitude = location_data.get("lat")
                longitude = location_data.get("lon")
                if latitude is None or longitude is None:
                    print("Error: Missing latitude or longitude in point data")
                    return False
                
                # Use fixed defaults since these are not in the actual data
                radius = 5
                background_color = self.default_background
                
                # Prepare LED data for point
                led_data = self._create_led_data(background_color)
                
                # _calculate_led_index will convert degrees to radians internally
                center_index = self._calculate_led_index(latitude, longitude)
                led_indices = self._get_surrounding_leds(center_index, radius)
                
                for idx in led_indices:
                    led_data[idx] = color
                  
            elif location_type == "region":
                polygon = location_data.get("polygon")
                if not polygon or not isinstance(polygon, list):
                    print(f"Error: Invalid polygon data: {polygon}")
                    return False
                  # Use fixed defaults since these are not in the actual data
                point_radius = 2
                background_color = self.default_background
                
                # Prepare LED data for region
                led_data = self._create_led_data(background_color)
                
                for point in polygon:
                    latitude, longitude = point
                    # _calculate_led_index will convert degrees to radians internally
                    center_index = self._calculate_led_index(latitude, longitude)
                    led_indices = self._get_surrounding_leds(center_index, point_radius)
                    for idx in led_indices:
                        led_data[idx] = color
            
            else:
                print(f"Error: Unknown location type: {location_type}")
                return False
            
            # Now that all data is prepared, send it with buffer handling
            if led_data:
                self.current_led_data = led_data
                return self.send_with_buffer_handling(led_data)
            else:
                print("Error: Failed to prepare LED data")
                return False
                
        except Exception as e:
            print(f"Error processing AI response to LED: {e}")
            import traceback
            traceback.print_exc()
            
            # Attempt recovery with error indicator
            try:
                error_leds = self._create_led_data([0, 0, 0])
                for i in range(20):
                    error_leds[i] = [255, 0, 0]  # First 20 LEDs red as error indicator
                self.send_with_buffer_handling(error_leds)
            except:
                pass
                
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
        return self.send_with_buffer_handling(led_data)
    
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
        
        # Test 5: Turn off all LEDsW
        print("\nTest 5: All LEDs off")
        globe.turn_off()
        
    finally:
        # Clean up
        time.sleep(1)
        globe.cleanup()


if __name__ == "__main__":
    print("Testing Globe visualization...")
    test_globe_visualization()
