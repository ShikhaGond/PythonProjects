import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import argparse
import os

def extract_dominant_color(image_path, num_colors=5, display=True):
    """
    Extract dominant colors from an image using k-means clustering
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to extract
        display: Whether to display the image and colors
        
    Returns:
        List of dominant colors in RGB format
    """
    # Load image
    img = Image.open(image_path)
    img = img.convert('RGB')
    
    # Resize image to speed up processing
    img = img.resize((100, 100))
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Reshape the array to a 2D array of pixels
    pixels = img_array.reshape(-1, 3)
    
    # Perform k-means clustering
    kmeans = KMeans(n_clusters=num_colors, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Get the number of pixels in each cluster
    counts = np.bincount(kmeans.labels_)
    
    # Sort colors by count (descending)
    colors_sorted = [colors[i] for i in np.argsort(-counts)]
    
    # Display the results if requested
    if display:
        # Load original image at full size for display
        original_img = Image.open(image_path)
        
        plt.figure(figsize=(14, 8))
        
        # Display the original image
        plt.subplot(1, 2, 1)
        plt.imshow(original_img)
        plt.title('Original Image')
        plt.axis('off')
        
        # Display the color palette
        plt.subplot(1, 2, 2)
        height = 50
        width = 100
        color_palette = np.zeros((height*num_colors, width, 3), dtype=np.uint8)
        
        for i, color in enumerate(colors_sorted):
            color_palette[i*height:(i+1)*height, :] = color
        
        plt.imshow(color_palette)
        plt.title('Dominant Colors')
        plt.axis('off')
        
        # Add color values as text
        for i, color in enumerate(colors_sorted):
            plt.text(width + 10, i*height + height//2, f'RGB: {tuple(color)}', 
                     verticalalignment='center')
        
        plt.tight_layout()
        plt.show()
    
    return colors_sorted

def hex_color(rgb):
    """Convert RGB tuple to hex color code"""
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

def main():
    parser = argparse.ArgumentParser(description='Extract dominant colors from an image')
    parser.add_argument('image_path', type=str, help='Path to the image file')
    parser.add_argument('--colors', '-c', type=int, default=5, help='Number of dominant colors to extract')
    parser.add_argument('--no-display', '-nd', action='store_true', help='Do not display the results')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.image_path):
        print(f"Error: File '{args.image_path}' not found.")
        return
    
    try:
        dominant_colors = extract_dominant_color(args.image_path, args.colors, not args.no_display)
        
        print("\nDominant Colors:")
        for i, color in enumerate(dominant_colors):
            print(f"{i+1}. RGB: {tuple(color)}, HEX: {hex_color(color)}")
            
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    main()