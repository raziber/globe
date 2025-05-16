"""
3D Visualization tool for the LED Globe

This module provides a 3D visualization of the LED globe to help debug which LEDs
are lighting up and better understand the mapping between geographic coordinates
and LED positions.
"""
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from typing import List, Dict, Any, Optional, Tuple, Union

# Constants
LED_LAYOUT_FILE = "coordinates_radians_rotated.json"
RADIUS = 1.0  # Unit sphere for visualization
MIN_LED_ID = 46  # First valid LED ID

class Globe3DVisualizer:
    def __init__(self):
        """Initialize the 3D globe visualizer."""
        self.fig = None
        self.ax = None
        self.leds = self._load_led_layout()
        print(f"Loaded {len(self.leds)} LED positions from layout file")
        
    def _load_led_layout(self) -> List[Dict[str, Any]]:
        """Load LED layout data from JSON file."""
        try:
            with open(LED_LAYOUT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading LED layout: {e}")
            return []
    
    def _sph_to_cart(self, theta: float, phi: float, r: float = RADIUS) -> np.ndarray:
        """Convert spherical coordinates to Cartesian coordinates."""
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        return np.array([x, y, z])
    
    def _lat_lon_to_sph(self, lat: float, lon: float) -> Tuple[float, float]:
        """Convert latitude and longitude to spherical coordinates."""
        lat_rad = math.radians(90 - lat)
        lon_rad = math.radians(lon % 360)
        return lon_rad, lat_rad
        
    def visualize_all_leds(self, highlight_ids: List[int] = None, title: str = "3D LED Globe Visualization"):
        """
        Visualize all LEDs on the globe with optional highlighting.
        
        Args:
            highlight_ids: List of LED IDs to highlight (in red)
            title: Title for the plot
        """
        # Create a new figure
        self.fig = plt.figure(figsize=(12, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Plot the sphere wireframe
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 30)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        self.ax.plot_wireframe(x, y, z, color='gray', alpha=0.2)
        
        # Highlight special points on the globe (poles and equator)
        # North Pole
        self.ax.scatter(0, 0, 1, color='blue', s=100, label='North Pole')
        # South Pole
        self.ax.scatter(0, 0, -1, color='green', s=100, label='South Pole')
        
        # Convert highlight_ids to a set for faster lookup
        highlight_set = set(highlight_ids) if highlight_ids else set()
        
        # Plot all LEDs
        for led in self.leds:
            led_id = led["id"]
            theta = led["theta"]
            phi = led["phi"]
            
            # Convert spherical to cartesian coordinates
            x, y, z = self._sph_to_cart(theta, phi)
            
            # Determine color and size based on whether it's highlighted
            if led_id in highlight_set:
                color = 'red'
                size = 50
                alpha = 1.0
                # Add label for highlighted LEDs
                self.ax.text(x, y, z, str(led_id), color='black', fontsize=8)
            else:
                color = 'blue' if led_id >= MIN_LED_ID else 'orange'
                size = 20
                alpha = 0.5
            
            self.ax.scatter(x, y, z, color=color, s=size, alpha=alpha)
        
        # Customize the plot
        self.ax.set_title(title)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([-1.1, 1.1])
        self.ax.set_ylim([-1.1, 1.1])
        self.ax.set_zlim([-1.1, 1.1])
        
        # Add a legend
        self.ax.legend()
        
        # Show the plot
        plt.tight_layout()
        plt.show()
    
    def visualize_point_highlight(self, latitude: float, longitude: float, radius: int = 5):
        """
        Visualize LEDs that would be lit up for a specific latitude and longitude.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            radius: Angular radius for surrounding LEDs
        """
        # Convert lat/lon to spherical coordinates
        theta, phi = self._lat_lon_to_sph(latitude, longitude)
        target = self._sph_to_cart(theta, phi)
        
        # Find closest LED (ignoring LEDs with id < MIN_LED_ID)
        closest_led = min(
            (led for led in self.leds if led["id"] >= MIN_LED_ID),
            key=lambda led: np.linalg.norm(self._sph_to_cart(led["theta"], led["phi"]) - target)
        )
        
        center_index = closest_led["id"]
        print(f"Closest LED to lat: {latitude}, lon: {longitude} is LED ID: {center_index}")
        
        # Calculate surrounding LEDs (simplified for visualization)
        highlighted_leds = [center_index]
        
        # Calculate approximate surrounding LEDs (simple Euclidean distance for visualization)
        for led in self.leds:
            led_id = led["id"]
            if led_id < MIN_LED_ID:
                continue
                
            led_pos = self._sph_to_cart(led["theta"], led["phi"])
            dist = np.linalg.norm(led_pos - self._sph_to_cart(closest_led["theta"], closest_led["phi"]))
            
            # Use a threshold based on chord length instead of angular distance
            # This is a simplified approach compared to the actual algorithm
            if dist < 0.3 * (radius / 5):  # Scale by radius parameter
                highlighted_leds.append(led_id)
        
        # Create visualization
        title = f"Point Highlight: Lat {latitude}, Lon {longitude} (Radius {radius})"
        self.visualize_all_leds(highlighted_leds, title)
    
    def visualize_region_highlight(self, polygon: List[List[float]], point_radius: int = 2):
        """
        Visualize LEDs that would be lit up for a polygon region.
        
        Args:
            polygon: List of [latitude, longitude] points defining the region
            point_radius: Radius for each point in the polygon
        """
        highlighted_leds = []
        
        # Process each point in the polygon
        for point in polygon:
            latitude, longitude = point
            
            # Convert lat/lon to spherical coordinates
            theta, phi = self._lat_lon_to_sph(latitude, longitude)
            target = self._sph_to_cart(theta, phi)
            
            # Find closest LED
            closest_led = min(
                (led for led in self.leds if led["id"] >= MIN_LED_ID),
                key=lambda led: np.linalg.norm(self._sph_to_cart(led["theta"], led["phi"]) - target)
            )
            
            center_index = closest_led["id"]
            
            # Add center LED to highlights
            highlighted_leds.append(center_index)
            
            # Calculate surrounding LEDs (simplified for visualization)
            for led in self.leds:
                led_id = led["id"]
                if led_id < MIN_LED_ID:
                    continue
                    
                led_pos = self._sph_to_cart(led["theta"], led["phi"])
                dist = np.linalg.norm(led_pos - self._sph_to_cart(closest_led["theta"], closest_led["phi"]))
                
                # Similar simplified approach as in visualize_point_highlight
                if dist < 0.3 * (point_radius / 5):
                    highlighted_leds.append(led_id)
        
        # Create visualization
        title = f"Region Highlight: {len(polygon)} points (Radius {point_radius})"
        self.visualize_all_leds(list(set(highlighted_leds)), title)
    
    def visualize_led_ids(self, min_id: int = MIN_LED_ID):
        """
        Visualize LED IDs on the globe, color-coding by ID range.
        
        Args:
            min_id: Minimum LED ID to consider
        """
        # Create a new figure
        self.fig = plt.figure(figsize=(14, 12))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Plot the sphere wireframe
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        self.ax.plot_wireframe(x, y, z, color='gray', alpha=0.1)
        
        # Plot all LEDs with color based on ID
        max_id = max(led["id"] for led in self.leds)
        normalizer = plt.Normalize(min_id, max_id)
        
        # Create colormap
        cmap = cm.viridis
        
        # Plot LEDs
        led_points = []
        for led in self.leds:
            led_id = led["id"]
            if led_id < min_id:
                continue
                
            theta = led["theta"]
            phi = led["phi"]
            
            # Convert spherical to cartesian coordinates
            x, y, z = self._sph_to_cart(theta, phi)
            
            # Color based on ID
            color = cmap(normalizer(led_id))
            
            # Add to plot with color based on ID
            point = self.ax.scatter(x, y, z, color=color, s=30)
            led_points.append(point)
            
            # Add text label for LED ID
            if led_id % 20 == 0:  # Only label every 20th LED to avoid clutter
                self.ax.text(x, y, z, str(led_id), fontsize=8)
        
        # Add a colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=normalizer)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=self.ax, shrink=0.6)
        cbar.set_label('LED ID')
        
        # Customize the plot
        self.ax.set_title(f"LED IDs (Min ID: {min_id})")
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([-1.1, 1.1])
        self.ax.set_ylim([-1.1, 1.1])
        self.ax.set_zlim([-1.1, 1.1])
        
        plt.tight_layout()
        plt.show()
    
    def visualize_led_coverage(self, min_led_id: int = MIN_LED_ID):
        """
        Visualize the geographic coverage of LEDs on the globe.
        Shows how latitude and longitude map to LED IDs.
        
        Args:
            min_led_id: Minimum LED ID to consider (typically 46)
        """
        # Create a new figure with 2 subplots
        plt.figure(figsize=(14, 10))
        
        # Plot 1: LED IDs by latitude
        plt.subplot(2, 1, 1)
        
        # Extract latitudes and IDs
        valid_leds = [led for led in self.leds if led["id"] >= min_led_id]
        latitudes = []
        ids = []
        
        for led in valid_leds:
            # Convert spherical coords to lat/lon
            theta = led["theta"]
            phi = led["phi"]
            
            # Spherical to lat/lon conversion (reverse of latlon_to_sph)
            lat = 90 - math.degrees(phi)
            lon = math.degrees(theta) % 360
            if lon > 180:
                lon -= 360
            
            latitudes.append(lat)
            ids.append(led["id"])
        
        # Plot LED IDs by latitude
        plt.scatter(latitudes, ids, c=ids, cmap='viridis', alpha=0.7)
        plt.xlabel('Latitude (degrees)')
        plt.ylabel('LED ID')
        plt.title('LED IDs by Latitude')
        plt.grid(True, alpha=0.3)
        plt.colorbar(label='LED ID')
        
        # Plot 2: LED positions on a flat map projection
        plt.subplot(2, 1, 2)
        
        # Extract longitudes
        longitudes = []
        for led in valid_leds:
            theta = led["theta"]
            phi = led["phi"]
            
            # Spherical to lat/lon conversion
            lat = 90 - math.degrees(phi)
            lon = math.degrees(theta) % 360
            if lon > 180:
                lon -= 360
            
            longitudes.append(lon)
        
        # Plot LED positions on a world map
        plt.scatter(longitudes, latitudes, c=ids, cmap='viridis', alpha=0.7)
        plt.xlabel('Longitude (degrees)')
        plt.ylabel('Latitude (degrees)')
        plt.title('LED Positions on World Map')
        plt.grid(True, alpha=0.3)
        
        # Add lat/lon grid lines
        lat_lines = np.arange(-90, 91, 30)
        lon_lines = np.arange(-180, 181, 30)
        
        for lat in lat_lines:
            plt.axhline(lat, color='gray', linestyle='--', alpha=0.3)
        
        for lon in lon_lines:
            plt.axvline(lon, color='gray', linestyle='--', alpha=0.3)
            
        # Add colorbar
        plt.colorbar(label='LED ID')
        
        # Equalize aspect ratio for map (make it look like a map)
        plt.axis('equal')
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        
        plt.tight_layout()
        plt.show()


# Test function
def test_visualizer():
    visualizer = Globe3DVisualizer()
    
    # Test basic visualization of all LEDs
    visualizer.visualize_all_leds()
    
    # Test visualization of specific point (New York City)
    visualizer.visualize_point_highlight(40.7128, -74.0060, 5)
    
    # Test visualization of a region (Australia)
    australia_polygon = [
        [-12.46, 130.84],  # Darwin
        [-33.87, 151.21],  # Sydney
        [-37.81, 144.96],  # Melbourne
        [-31.95, 115.86]   # Perth
    ]
    visualizer.visualize_region_highlight(australia_polygon)
    
    # Test LED ID visualization
    visualizer.visualize_led_ids()
    
    # Test LED coverage visualization
    visualizer.visualize_led_coverage()
    
    # Test LED coverage visualization
    visualizer.visualize_led_coverage()


if __name__ == "__main__":
    print("Testing Globe 3D Visualizer...")
    test_visualizer()
