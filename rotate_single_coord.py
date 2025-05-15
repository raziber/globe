import math

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

# Input from user
theta_input = float(input("Enter theta (in degrees): "))
phi_input = float(input("Enter phi (in degrees): "))
r = 1  # unit sphere

# Convert to Cartesian
x, y, z = spherical_to_cartesian(r, theta_input, phi_input)

# Rotate 90° around X-axis
y_new = z
z_new = -y

# Convert back to spherical
_, theta_rotated, phi_rotated = cartesian_to_spherical(x, y_new, z_new)

print(f"Rotated theta: {round(theta_rotated, 2)}°")
print(f"Rotated phi:   {round(phi_rotated, 2)}°")
