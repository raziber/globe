"""
Modified 3D test to save plots to files
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os

def test_plot_save():
    # Create a simple 3D plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a sphere
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Plot the sphere
    ax.plot_wireframe(x, y, z, color='blue', alpha=0.3)
    
    # Add some points
    for i in range(10):
        # Random points on the sphere
        theta = np.random.random() * 2 * np.pi
        phi = np.random.random() * np.pi
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        ax.scatter(x, y, z, color='red', s=100)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Test 3D Globe')
    
    # Save the plot as a PNG file
    output_file = 'test_globe_3d.png'
    print(f"Saving plot to {output_file}...")
    plt.savefig(output_file)
    print(f"Plot saved to {os.path.abspath(output_file)}")
    
    # No need to show the plot, just save it
    plt.close()

if __name__ == "__main__":
    print("Testing matplotlib 3D visualization with file save...")
    test_plot_save()
    print("Test complete")
