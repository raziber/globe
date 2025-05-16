"""
Test script to demonstrate controlling the globe LEDs through WebSocket.
This shows how to integrate the WebSocket client with the location data from GPT.
"""
import time
import random
from websocket_client import WebSocketClient

def create_led_data(base_color=None):
    """Create a sample LED data array with all LEDs set to the same color."""
    if base_color is None:
        base_color = [0, 0, 0]  # Default to all off
    return [base_color.copy() for _ in range(402)]

def highlight_point(led_data, latitude, longitude, color=None, radius=10):
    """
    Highlight a point on the globe by setting LEDs around that point.
    
    In a real implementation, you would have a mapping from lat/lon to LED indices.
    This is just a placeholder demonstrating the concept.
    
    Args:
        led_data: List of RGB values for all LEDs
        latitude: Latitude of the point (-90 to 90)
        longitude: Longitude of the point (-180 to 180)
        color: RGB color to set [R, G, B]
        radius: Number of LEDs around the center to highlight
    
    Returns:
        Modified led_data list
    """
    if color is None:
        color = [255, 0, 0]  # Default to red
    
    # This is a placeholder - in a real implementation you would have 
    # a mapping from lat/lon to specific LED indices
    
    # For demonstration purposes, we'll just highlight some random LEDs
    # to simulate highlighting a region on the globe
    
    # Convert lat/lon to a "seed" for reproducible randomness
    seed = int((latitude + 90) * 1000 + (longitude + 180))
    random.seed(seed)
    
    # Pick a "center" LED based on lat/lon
    center_led = int((latitude + 90) / 180 * 400)  # Very simplified mapping
    
    # Highlight LEDs around the center
    for i in range(radius):
        led_idx = (center_led + i) % 402
        led_data[led_idx] = color
    
    return led_data

def highlight_region(led_data, polygon, color=None):
    """
    Highlight a region on the globe defined by a polygon.
    
    Args:
        led_data: List of RGB values for all LEDs
        polygon: List of [latitude, longitude] points defining the region
        color: RGB color to set [R, G, B]
    
    Returns:
        Modified led_data list
    """
    if color is None:
        color = [0, 0, 255]  # Default to blue
        
    # For demonstration purposes, we'll highlight LEDs based on each point in the polygon
    for point in polygon:
        latitude, longitude = point
        # Use a smaller radius for each point in the polygon
        led_data = highlight_point(led_data, latitude, longitude, color, radius=5)
    
    return led_data

def test_globe_visualization():
    """Test the globe visualization with sample location data."""
    # Initialize the WebSocket client
    client = WebSocketClient(min_delay=0.5)  # Increase delay for testing
    client.start()
    
    try:
        # Test 1: Turn on all LEDs to a dim white
        print("\nTest 1: All LEDs dim white")
        led_data = create_led_data([30, 30, 30])
        client.send_led_data(led_data)
        time.sleep(2)
        
        # Test 2: Highlight Paris
        print("\nTest 2: Highlighting Paris")
        led_data = create_led_data([10, 10, 10])  # Dim background
        paris_data = {
            "type": "point",
            "lat": 48.8566,
            "lon": 2.3522,
            "color_rgb": [255, 0, 0]  # Red
        }
        led_data = highlight_point(
            led_data, 
            paris_data["lat"], 
            paris_data["lon"], 
            paris_data["color_rgb"]
        )
        client.send_led_data(led_data)
        time.sleep(3)
        
        # Test 3: Highlight a region (US)
        print("\nTest 3: Highlighting United States")
        led_data = create_led_data([10, 10, 10])  # Dim background
        us_data = {
            "type": "region",
            "polygon": [
                [47.13, -124.7],  # Northwest
                [48.78, -95.15],   # North central
                [45.01, -83.03],   # Northeast
                [25.78, -80.21],   # Southeast
                [32.55, -117.13]   # Southwest
            ],
            "color_rgb": [0, 0, 255]  # Blue
        }
        led_data = highlight_region(
            led_data,
            us_data["polygon"],
            us_data["color_rgb"]
        )
        client.send_led_data(led_data)
        time.sleep(3)
        
        # Test 4: Create a cool pattern
        print("\nTest 4: Creating a random pattern")
        led_data = []
        for i in range(402):
            # Create a rainbow-like effect
            hue = (i / 402) * 360
            if hue < 60:
                r, g, b = 255, int((hue / 60) * 255), 0
            elif hue < 120:
                r, g, b = int(((120 - hue) / 60) * 255), 255, 0
            elif hue < 180:
                r, g, b = 0, 255, int(((hue - 120) / 60) * 255)
            elif hue < 240:
                r, g, b = 0, int(((240 - hue) / 60) * 255), 255
            elif hue < 300:
                r, g, b = int(((hue - 240) / 60) * 255), 0, 255
            else:
                r, g, b = 255, 0, int(((360 - hue) / 60) * 255)
            led_data.append([r, g, b])
        
        client.send_led_data(led_data)
        time.sleep(3)
        
        # Test 5: Turn off all LEDs
        print("\nTest 5: All LEDs off")
        led_data = create_led_data([0, 0, 0])
        client.send_led_data(led_data)
        
    finally:
        # Always stop the client when done
        time.sleep(1)  # Make sure the last command is sent
        client.stop()

if __name__ == "__main__":
    print("Testing Globe LED visualization...")
    test_globe_visualization()
