import math
import json
import os

OUTPUT_FILE = "led_output.json"

def write_led_output(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Wrote LED data to {OUTPUT_FILE}")

class LocationProcessor:
    def __init__(self, led_layout):
        self.leds = led_layout

    def spherical_from_latlon(self, lat, lon):
        theta = math.radians(lon)
        phi = math.radians(90 - lat)
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

    def find_leds_in_region(self, polygon, radius=0.2):
        led_ids = set()
        for theta, phi in polygon:
            for led in self.leds:
                dtheta = theta - led["theta"]
                dphi = phi - led["phi"]
                dist = math.sqrt(dtheta**2 + dphi**2)
                if dist < radius:
                    led_ids.add(led["id"])
        return sorted(list(led_ids))

    def process_location(self, location_data):
        color = location_data.get("color_rgb", [255, 255, 255])
        print(f"🎨 Color for highlight: RGB{tuple(color)}")

        if location_data.get("type") == "point":
            lat = location_data.get("lat")
            lon = location_data.get("lon")
            if lat is not None and lon is not None:
                theta, phi = self.spherical_from_latlon(lat, lon)
                closest_led = self.find_closest_led(theta, phi)
                processed = {
                    "type": "point",
                    "theta": theta,
                    "phi": phi,
                    "color_rgb": color,
                    "led_id": closest_led["id"]
                }
                print(f"Lighting LED #{closest_led['id']} at θ={theta:.2f}, ϕ={phi:.2f}")
                write_led_output(processed)
                return processed

        elif location_data.get("type") == "region":
            polygon = location_data.get("polygon")
            spherical_polygon = []
            if polygon:
                print("Lighting region polygon:")
                for entry in polygon:
                    if isinstance(entry, list) and len(entry) == 2:
                        lat, lon = entry
                        theta, phi = self.spherical_from_latlon(lat, lon)
                        spherical_polygon.append([theta, phi])
                        print(f"- Point: lat={lat}, lon={lon} → θ={theta:.2f}, ϕ={phi:.2f}")

                # Approximate region fill using bounding box
                thetas = [pt[0] for pt in spherical_polygon]
                phis = [pt[1] for pt in spherical_polygon]
                theta_min, theta_max = min(thetas), max(thetas)
                phi_min, phi_max = min(phis), max(phis)

                region_leds = [
                    led["id"]
                    for led in self.leds
                    if theta_min <= led["theta"] <= theta_max and phi_min <= led["phi"] <= phi_max
                ]

                processed = {
                    "type": "region",
                    "polygon": spherical_polygon,
                    "color_rgb": color,
                    "led_ids": region_leds
                }
                write_led_output(processed)
                return processed

        print("⚠️ Unknown or incomplete location data.")
        write_led_output({"type": "none"})
        return None
