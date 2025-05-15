import json
import math

INPUT_FILE = "coordinates.json"
OUTPUT_FILE = "coordinates_rotated.json"

def spherical_to_cartesian(r, theta_deg, phi_deg):
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z

def cartesian_to_spherical(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    theta = math.degrees(math.atan2(y, x)) % 360
    phi = math.degrees(math.acos(z / r)) if r != 0 else 0
    return r, theta, phi

with open(INPUT_FILE, "r") as f:
    coords = json.load(f)

rotated = []
for entry in coords:
    theta, phi = entry["theta"], entry["phi"]
    r = 1  # radius is ignored, use unit sphere
    x, y, z = spherical_to_cartesian(r, theta, phi)

    # Rotate 90° around X axis
    y_new = z
    z_new = -y

    _, theta_new, phi_new = cartesian_to_spherical(x, y_new, z_new)

    rotated.append({
        "id": entry["id"],
        "theta": round(theta_new, 2),
        "phi": round(phi_new, 2)
    })

with open(OUTPUT_FILE, "w") as f:
    json.dump(rotated, f, indent=2)

print(f"Saved rotated coordinates to {OUTPUT_FILE}")
