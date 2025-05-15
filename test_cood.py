import json
import math
import plotly.graph_objects as go

def spherical_to_xyz(theta_deg, phi_deg):
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return x, y, z

# Load coordinates
with open("coordinates_shifted_2.json") as f:
    coordinates = json.load(f)

x_vals, y_vals, z_vals, labels = [], [], [], []
for point in coordinates:
    x, y, z = spherical_to_xyz(point["theta"], point["phi"])
    x_vals.append(x)
    y_vals.append(y)
    z_vals.append(z)
    labels.append(str(point["id"]))

# Create interactive plot
fig = go.Figure(data=[
    go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals,
        mode='markers+text',
        marker=dict(size=3, color='blue'),
        text=labels,
        textposition='top center',
        hoverinfo='text'
    )
])

fig.update_layout(
    title='Interactive 3D LED Globe',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    showlegend=False
)

fig.show()
