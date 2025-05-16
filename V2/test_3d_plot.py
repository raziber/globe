"""
Simple test to check if matplotlib 3D visualization is working
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def test_plot():
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
    
    # Show the plot (should be blocking)
    print("Plot created, showing now...")
    plt.show()
    print("Plot window closed")

if __name__ == "__main__":
    print("Testing matplotlib 3D visualization...")
    test_plot()
    print("Test complete")
