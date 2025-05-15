import math
import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

OUTPUT_FILE = "led_output.json"

def write_led_output(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Wrote LED data to {OUTPUT_FILE}")

class LocationProcessor:
    def __init__(self, led_layout):
        self.leds = led_layout

    def spherical_from_latlon(self, lat, lon):
        phi = math.radians(lon)
        theta = math.radians(90 - lat)
        return theta, phi

    def debug_latlon_to_spherical(self, lat, lon):
        theta, phi = self.spherical_from_latlon(lat, lon)
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)
        print(f"LAT={lat:.2f}, LON={lon:.2f} → θ={theta:.2f}, ϕ={phi:.2f} → x={x:.2f}, y={y:.2f}, z={z:.2f}")
        return theta, phi

    def find_closest_led(self, theta, phi):
        min_dist = float("inf")
        closest_led = None
        for led in self.leds:
            dtheta = theta - led["theta"]
            dphi = phi - led["phi"]
            dist = math.sqrt(dtheta**2 + dphi**2)
            if dist < min_dist:
                min_dist = dist
                closest_led = led
        return closest_led

    def find_leds_in_region(self, polygon, radius=0.4):
        led_ids = set()
        for theta, phi in polygon:
            for led in self.leds:
                dtheta = theta - led["theta"]
                dphi = phi - led["phi"]
                dist = math.sqrt(dtheta**2 + dphi**2)
                if dist < radius:
                    led_ids.add(led["id"])
        return sorted(list(led_ids))

    def print_nearby_leds(self, lat, lon, max_dist=0.1):
        theta, phi = self.spherical_from_latlon(lat, lon)
        print(f"🔍 Nearby LEDs to θ={theta:.2f}, ϕ={phi:.2f} (from LAT={lat}, LON={lon})")
        for led in self.leds:
            dtheta = theta - led["theta"]
            dphi = phi - led["phi"]
            dist = math.sqrt(dtheta**2 + dphi**2)
            if dist < max_dist:
                print(f"  LED #{led['id']}: θ={led['theta']:.2f}, ϕ={led['phi']:.2f}, dist={dist:.3f}")

    def plot_region_and_leds(self, spherical_polygon, lit_led_ids):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot all LEDs
        for led in self.leds:
            theta = led["theta"]
            phi = led["phi"]
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            is_lit = led["id"] in lit_led_ids

            color = 'r' if is_lit else 'k'
            size = 20 if is_lit else 5
            ax.scatter(x, y, z, c=color, s=size)

            # Label lit LEDs
            if is_lit:
                ax.text(x, y, z, str(led["id"]), color='red', fontsize=8)

        # Plot polygon vertices
        for theta, phi in spherical_polygon:
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            ax.plot([x], [y], [z], marker='o', color='blue', markersize=5)

        ax.set_title("LED Globe - 3D View")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_box_aspect([1, 1, 1])
        plt.show()

    def process_location(self, location_data):
        color = location_data.get("color_rgb", [255, 255, 255])
        print(f"🎨 Color for highlight: RGB{tuple(color)}")

        # Radius scaling: LED sphere to globe radius
        self.radius_scale = 135.8 / 168.3

        def spherical_to_cartesian(theta, phi):
            r = self.radius_scale
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            return (x, y, z)

        def vector_distance(v1, v2):
            dot = sum(a * b for a, b in zip(v1, v2))
            return math.acos(max(-1.0, min(1.0, dot)))  # safe clamp

        if location_data.get("type") == "point":
            lat = location_data.get("lat")
            lon = location_data.get("lon")
            if lat is not None and lon is not None:
                theta, phi = self.debug_latlon_to_spherical(lat, lon)
                closest_led = self.find_closest_led(theta, phi)
                processed = {
                    "type": "point",
                    "theta": theta,
                    "phi": phi,
                    "color_rgb": color,
                    "led_id": closest_led["id"]
                }
                print(f"📍 Lighting LED #{closest_led['id']} at θ={theta:.2f}, ϕ={phi:.2f}")
                write_led_output(processed)
                return processed

        elif location_data.get("type") == "region":
            polygon = location_data.get("polygon")
            spherical_polygon = []
            if polygon:
                print("📐 Lighting region polygon:")
                for entry in polygon:
                    if isinstance(entry, list) and len(entry) == 2:
                        lat, lon = entry
                        theta, phi = self.debug_latlon_to_spherical(lat, lon)
                        spherical_polygon.append([theta, phi])

                # Step 1: Check which LEDs fall inside the polygon
                region_leds = [
                    led["id"]
                    for led in self.leds
                    if self.point_in_polygon(led["theta"], led["phi"], spherical_polygon)
                ]

                # Step 2: Fallback to nearest LEDs if none found
                if not region_leds:
                    print("⚠️ No LEDs found inside polygon. Finding closest fallback LEDs...")

                    center_theta = sum(p[0] for p in spherical_polygon) / len(spherical_polygon)
                    center_phi = sum(p[1] for p in spherical_polygon) / len(spherical_polygon)
                    center_vec = spherical_to_cartesian(center_theta, center_phi)

                    sorted_leds = sorted(
                        self.leds,
                        key=lambda led: vector_distance(
                            spherical_to_cartesian(led["theta"], led["phi"]),
                            center_vec
                        )
                    )

                    fallback_leds = sorted_leds[:5]
                    region_leds = [led["id"] for led in fallback_leds]
                    print(f"✅ Using fallback LEDs: {region_leds}")

                processed = {
                    "type": "region",
                    "polygon": spherical_polygon,
                    "color_rgb": color,
                    "led_ids": region_leds
                }

                self.plot_region_and_leds(spherical_polygon, region_leds)
                write_led_output(processed)
                return processed

        print("⚠️ Unknown or incomplete location data.")
        write_led_output({"type": "none"})
        return None


    def point_in_polygon(self, x, y, poly):
        """
        Ray-casting algorithm in θ/ϕ space. Not true spherical geometry,
        but acceptable for small regions.
        """
        num = len(poly)
        j = num - 1
        inside = False
        for i in range(num):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi
            ):
                inside = not inside
            j = i
        return inside
