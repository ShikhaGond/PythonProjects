import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk, ImageEnhance
import numpy as np
from typing import Dict, List

class ASCIIArtGenerator:
    
    # Different ASCII character sets for various styles
    ASCII_STYLES: Dict[str, str] = {
        'Standard': '@%#*+=-:. ',
        'Detailed': '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'. ',
        'Blocks': '█▓▒░ ',
        'Simple': '#@$%*+-:. ',
        'Letters': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'Numbers': '0123456789',
    }
    
    def __init__(self, width=100, style='Standard'):
        self.width = width
        self.style = style
        self.brightness = 1.0
        self.contrast = 1.0
        self.color_enabled = False
        
    def load_image(self, image_path: str) -> Image.Image:
        """Load an image and return it as a PIL Image object."""
        try:
            return Image.open(image_path)
        except Exception as e:
            raise Exception(f"Error loading image: {e}")
    
    def apply_image_processing(self, image: Image.Image) -> Image.Image:
        """Apply preprocessing adjustments to the image."""
        # Apply brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.brightness)
        
        # Apply contrast adjustment
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.contrast)
        
        return image
    
    def resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image to match desired width while maintaining aspect ratio."""
        aspect_ratio = image.size[1] / image.size[0]
        height = int(self.width * aspect_ratio)
        return image.resize((self.width, height))
    
    def pixel_to_ascii(self, pixel_value: int, color: tuple = None) -> str:
        """Convert a pixel value to an ASCII character."""
        chars = self.ASCII_STYLES[self.style]
        char_idx = int(pixel_value * (len(chars) - 1) / 255)
        char = chars[char_idx]
        
        if self.color_enabled and color:
            # Return colored ASCII character using ANSI escape codes
            r, g, b = color
            return f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        return char
    
    def convert_to_ascii(self, image_path: str) -> str:
        """Convert an image to ASCII art with optional color support."""
        # Load and process image
        image = self.load_image(image_path)
        image = self.apply_image_processing(image)
        image = self.resize_image(image)
        
        # Convert to ASCII
        if self.color_enabled:
            pixels = np.array(image)
            ascii_str = ''
            for row in pixels:
                for pixel in row:
                    if len(pixel) == 3:  # RGB
                        brightness = sum(pixel) // 3
                        ascii_str += self.pixel_to_ascii(brightness, pixel)
                    else:  # Grayscale
                        ascii_str += self.pixel_to_ascii(pixel)
                ascii_str += '\n'
        else:
            grayscale = image.convert('L')
            pixels = np.array(grayscale)
            ascii_str = ''
            for row in pixels:
                for pixel in row:
                    ascii_str += self.pixel_to_ascii(pixel)
                ascii_str += '\n'
        
        return ascii_str

class ASCIIArtGUI:
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ASCII Art Generator")
        self.window.geometry("1200x800")
        
        self.generator = ASCIIArtGenerator()
        self.setup_gui()
        
    def setup_gui(self):
        # Create main frames
        self.control_frame = ttk.Frame(self.window, padding="10")
        self.control_frame.pack(fill=tk.X)
        
        self.display_frame = ttk.Frame(self.window, padding="10")
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        self.setup_controls()
        
        # Display area
        self.output_text = tk.Text(self.display_frame, wrap=tk.NONE, font=('Courier', 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        self.setup_scrollbars()
        
    def setup_controls(self):
        # File selection
        ttk.Button(self.control_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT, padx=5)
        
        # Style selection
        style_var = tk.StringVar(value='Standard')
        style_menu = ttk.OptionMenu(self.control_frame, style_var, 'Standard', 
                                  *self.generator.ASCII_STYLES.keys(), command=self.update_style)
        style_menu.pack(side=tk.LEFT, padx=5)
        
        # Width control
        ttk.Label(self.control_frame, text="Width:").pack(side=tk.LEFT, padx=5)
        width_var = tk.StringVar(value='100')
        width_entry = ttk.Entry(self.control_frame, textvariable=width_var, width=5)
        width_entry.pack(side=tk.LEFT, padx=5)
        width_entry.bind('<Return>', lambda e: self.update_width(width_var.get()))
        
        # Brightness control
        ttk.Label(self.control_frame, text="Brightness:").pack(side=tk.LEFT, padx=5)
        brightness_scale = ttk.Scale(self.control_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=self.update_brightness)
        brightness_scale.set(1.0)
        brightness_scale.pack(side=tk.LEFT, padx=5)
        
        # Contrast control
        ttk.Label(self.control_frame, text="Contrast:").pack(side=tk.LEFT, padx=5)
        contrast_scale = ttk.Scale(self.control_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=self.update_contrast)
        contrast_scale.set(1.0)
        contrast_scale.pack(side=tk.LEFT, padx=5)
        
        # Color toggle
        self.color_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.control_frame, text="Enable Color", variable=self.color_var, command=self.toggle_color).pack(side=tk.LEFT, padx=5)
        
        # Save button
        ttk.Button(self.control_frame, text="Save ASCII Art", command=self.save_ascii_art).pack(side=tk.RIGHT, padx=5)
        
    def setup_scrollbars(self):
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.display_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.display_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure text widget
        self.output_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.current_image_path = file_path
            self.generate_ascii_art()
    
    def generate_ascii_art(self):
        try:
            ascii_art = self.generator.convert_to_ascii(self.current_image_path)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, ascii_art)
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))
    
    def save_ascii_art(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.output_text.get(1.0, tk.END))
    
    def update_style(self, style):
        self.generator.style = style
        if hasattr(self, 'current_image_path'):
            self.generate_ascii_art()
    
    def update_width(self, width):
        try:
            self.generator.width = int(width)
            if hasattr(self, 'current_image_path'):
                self.generate_ascii_art()
        except ValueError:
            tk.messagebox.showerror("Error", "Width must be a number")
    
    def update_brightness(self, value):
        self.generator.brightness = float(value)
        if hasattr(self, 'current_image_path'):
            self.generate_ascii_art()
    
    def update_contrast(self, value):
        self.generator.contrast = float(value)
        if hasattr(self, 'current_image_path'):
            self.generate_ascii_art()
    
    def toggle_color(self):
        self.generator.color_enabled = self.color_var.get()
        if hasattr(self, 'current_image_path'):
            self.generate_ascii_art()
    
    def run(self):
        self.window.mainloop()

def main():
    app = ASCIIArtGUI()
    app.run()

if __name__ == "__main__":
    main()