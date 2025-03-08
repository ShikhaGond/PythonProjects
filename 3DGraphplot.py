import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

def matplotlib_surface_plot():
    """Create a 3D surface plot using Matplotlib."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R) / (R + 0.001)  
    
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('3D Surface Plot: z = sin(r)/r')
    
    plt.tight_layout()
    plt.show()

def matplotlib_scatter_plot():
    """Create a 3D scatter plot using Matplotlib."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    n = 100
    xs = np.random.rand(n) * 4 - 2
    ys = np.random.rand(n) * 4 - 2
    zs = np.random.rand(n) * 4 - 2
    
    colors = np.sqrt(xs**2 + ys**2 + zs**2)
    
    scatter = ax.scatter(xs, ys, zs, c=colors, cmap='viridis', marker='o', s=50, alpha=0.8)
    
    fig.colorbar(scatter, shrink=0.5, aspect=5)
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('3D Scatter Plot')
    
    ax.set_box_aspect([1, 1, 1])
    
    plt.tight_layout()
    plt.show()

def matplotlib_line_plot():
    """Create a 3D line plot (parametric curve) using Matplotlib."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    t = np.linspace(0, 10 * np.pi, 1000)
    x = np.cos(t)
    y = np.sin(t)
    z = t / 3
    
    ax.plot(x, y, z, label='Helix', color='blue', linewidth=2)
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('3D Parametric Curve: Helix')
    
    ax.legend()
    
    plt.tight_layout()
    plt.show()

def matplotlib_wireframe_plot():
    """Create a 3D wireframe plot using Matplotlib."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    X = np.arange(-5, 5, 0.5)
    Y = np.arange(-5, 5, 0.5)
    X, Y = np.meshgrid(X, Y)
    Z = np.sin(np.sqrt(X**2 + Y**2))
    
    ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1, color='black', linewidth=0.5)
    
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_title('3D Wireframe Plot')
    
    plt.tight_layout()
    plt.show()

import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'  

def plotly_surface_plot():
    """Create an interactive 3D surface plot using Plotly."""
    # Create data
    X = np.arange(-5, 5, 0.1)
    Y = np.arange(-5, 5, 0.1)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R) / (R + 0.001)
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='viridis')])
    
    fig.update_layout(
        title='Interactive 3D Surface Plot with Plotly',
        scene=dict(
            xaxis_title='X axis',
            yaxis_title='Y axis',
            zaxis_title='Z axis'
        ),
        width=800,
        height=800
    )
    
    fig.show()

def plotly_scatter_plot():
    """Create an interactive 3D scatter plot using Plotly."""
    n = 200
    xs = np.random.rand(n) * 4 - 2
    ys = np.random.rand(n) * 4 - 2
    zs = np.random.rand(n) * 4 - 2
    
    colors = xs + ys + zs
    
    fig = go.Figure(data=[go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers',
        marker=dict(
            size=6,
            color=colors,
            colorscale='Viridis',
            opacity=0.8
        )
    )])
    
    fig.update_layout(
        title='Interactive 3D Scatter Plot with Plotly',
        scene=dict(
            xaxis_title='X axis',
            yaxis_title='Y axis',
            zaxis_title='Z axis'
        ),
        width=800,
        height=800
    )
    
    fig.show()

import plotly.express as px
from ipywidgets import interact, FloatSlider

def advanced_plotly_example():
    """Create an interactive 3D surface with a more complex function."""
    def create_plot(a=1.0, b=1.0, c=1.0):
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        x_grid, y_grid = np.meshgrid(x, y)
        
        z_grid = a * np.sin(b * x_grid) * np.cos(c * y_grid)
        
        fig = go.Figure(data=[go.Surface(z=z_grid, x=x_grid, y=y_grid)])
        
        fig.update_layout(
            title=f'z = {a:.1f} * sin({b:.1f}x) * cos({c:.1f}y)',
            scene=dict(
                xaxis_title='X axis',
                yaxis_title='Y axis',
                zaxis_title='Z axis'
            ),
            width=800,
            height=800
        )
        
        return fig
    
    interact(
        create_plot,
        a=FloatSlider(min=0.1, max=2.0, step=0.1, value=1.0),
        b=FloatSlider(min=0.1, max=2.0, step=0.1, value=1.0),
        c=FloatSlider(min=0.1, max=2.0, step=0.1, value=1.0)
    )

if __name__ == "__main__":
    # Uncomment any of these to run the examples:
    # matplotlib_surface_plot()
    # matplotlib_scatter_plot()
    # matplotlib_line_plot()
    # matplotlib_wireframe_plot()
    # plotly_surface_plot()
    # plotly_scatter_plot()
    # advanced_plotly_example()  # Note: This requires Jupyter notebook for the interactive sliders
    
    print("Run any of the example functions to generate 3D plots!")