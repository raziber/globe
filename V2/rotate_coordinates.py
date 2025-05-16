"""
Rotate LED coordinates by half pi (π/2) counter-clockwise.

This script reads the LED coordinates from coordinates_radians.json,
rotates each coordinate by π/2 counter-clockwise, and saves the result
to a new file coordinates_radians_rotated.json.

For spherical coordinates (theta, phi):
- Counter-clockwise rotation around Z-axis is: theta' = theta + π/2
"""
import json
import math
import numpy as np
from typing import List, Dict

# Constants
INPUT_FILE = "coordinates_radians.json"
OUTPUT_FILE = "coordinates_radians_rotated.json"
ROTATION = math.pi / 2  # Half pi counter-clockwise

def rotate_coordinates(led_data: List[Dict]) -> List[Dict]:
    """
    Rotate each LED coordinate by half pi counter-clockwise.
    
    In spherical coordinates, counter-clockwise rotation around Z-axis
    is achieved by adding the rotation angle to theta.
    
    Args:
        led_data: List of LED data dictionaries with id, theta, phi
        
    Returns:
        List of LED data with rotated coordinates
    """
    rotated_data = []
    
    for led in led_data:
        # Extract data
        led_id = led["id"]
        theta = led["theta"]
        phi = led["phi"]
        
        # Rotate theta by half pi counter-clockwise
        # For counter-clockwise rotation, add the rotation angle
        rotated_theta = (theta + ROTATION) % (2 * math.pi)
        
        # Create new LED data with rotated coordinates
        rotated_led = {
            "id": led_id,
            "theta": rotated_theta,
            "phi": phi  # phi remains unchanged for rotation around Z-axis
        }
        
        rotated_data.append(rotated_led)
    
    return rotated_data

def main():
    print("Starting coordinate rotation...")
    # Load the original LED data
    try:
        print(f"Attempting to open {INPUT_FILE}...")
        with open(INPUT_FILE, "r") as f:
            led_data = json.load(f)
        print(f"Successfully loaded {len(led_data)} LED positions from {INPUT_FILE}")
    except Exception as e:
        print(f"Error loading LED data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Rotate the coordinates
    rotated_data = rotate_coordinates(led_data)
    print(f"Rotated {len(rotated_data)} LED coordinates by {ROTATION:.4f} radians ({math.degrees(ROTATION):.2f} degrees)")
    
    # Save the rotated data
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(rotated_data, f, indent=2)
        print(f"Saved rotated coordinates to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving rotated data: {e}")
        return
    
    # Print some sample rotations for verification
    print("\nSample rotations (Original -> Rotated):")
    for i in range(min(5, len(led_data))):
        led = led_data[i]
        rotated = rotated_data[i]
        print(f"LED {led['id']}: θ={led['theta']:.4f} -> θ={rotated['theta']:.4f}, " 
              f"φ={led['phi']:.4f} (unchanged)")

if __name__ == "__main__":
    main()
