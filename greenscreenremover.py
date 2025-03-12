import cv2
import numpy as np
import os
from tkinter import Tk, filedialog, Button, Label, Scale, HORIZONTAL
from PIL import Image, ImageTk
import threading

class GreenScreenRemover:
    def __init__(self):
        self.root = Tk()
        self.root.title("Green Screen Remover")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        
        self.input_image_path = None
        self.background_image_path = None
        self.processed_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Input image section
        Label(self.root, text="Green Screen Remover", font=("Arial", 18, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=4, pady=10)
        
        Button(self.root, text="Select Green Screen Image", command=self.load_input_image, width=20).grid(row=1, column=0, padx=10, pady=10)
        self.input_label = Label(self.root, text="No image selected", bg="#f0f0f0")
        self.input_label.grid(row=1, column=1, padx=10, pady=10)
        
        # Background image section
        Button(self.root, text="Select Background Image", command=self.load_background_image, width=20).grid(row=2, column=0, padx=10, pady=10)
        self.bg_label = Label(self.root, text="No background selected", bg="#f0f0f0")
        self.bg_label.grid(row=2, column=1, padx=10, pady=10)
        
        # Threshold sliders
        Label(self.root, text="Green Color Threshold:", bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=5)
        self.green_threshold = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, length=200, command=self.update_preview)
        self.green_threshold.set(40)
        self.green_threshold.grid(row=3, column=1, padx=10, pady=5)
        
        Label(self.root, text="Sensitivity:", bg="#f0f0f0").grid(row=4, column=0, padx=10, pady=5)
        self.sensitivity = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, length=200, command=self.update_preview)
        self.sensitivity.set(15)
        self.sensitivity.grid(row=4, column=1, padx=10, pady=5)
        
        # Preview section
        self.preview_label = Label(self.root, text="Preview will appear here", bg="#f0f0f0", width=50, height=20)
        self.preview_label.grid(row=1, column=2, rowspan=6, columnspan=2, padx=10, pady=10)
        
        # Process button
        Button(self.root, text="Process Image", command=self.process_image, width=20).grid(row=5, column=0, padx=10, pady=10)
        
        # Save button
        Button(self.root, text="Save Result", command=self.save_result, width=20).grid(row=5, column=1, padx=10, pady=10)
        
        # Status label
        self.status_label = Label(self.root, text="Ready", bg="#f0f0f0")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    
    def load_input_image(self):
        self.input_image_path = filedialog.askopenfilename(
            title="Select Green Screen Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if self.input_image_path:
            self.input_label.config(text=os.path.basename(self.input_image_path))
            self.update_preview()
    
    def load_background_image(self):
        self.background_image_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if self.background_image_path:
            self.bg_label.config(text=os.path.basename(self.background_image_path))
            self.update_preview()
    
    def update_preview(self, *args):
        if self.input_image_path and self.background_image_path:
            threading.Thread(target=self.generate_preview).start()
    
    def generate_preview(self):
        self.status_label.config(text="Generating preview...")
        try:
            result = self.remove_green_screen(
                self.input_image_path, 
                self.background_image_path, 
                self.green_threshold.get(),
                self.sensitivity.get()
            )
            
            # Resize for preview
            h, w = result.shape[:2]
            max_size = 400
            if h > w:
                new_h = max_size
                new_w = int(w * (max_size / h))
            else:
                new_w = max_size
                new_h = int(h * (max_size / w))
                
            preview = cv2.resize(result, (new_w, new_h))
            preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            preview_img = Image.fromarray(preview)
            preview_tk = ImageTk.PhotoImage(image=preview_img)
            
            self.preview_label.config(image=preview_tk)
            self.preview_label.image = preview_tk
            self.processed_image = result
            self.status_label.config(text="Preview generated")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def remove_green_screen(self, input_path, bg_path, green_threshold=40, sensitivity=15):
        # Read images
        img = cv2.imread(input_path)
        bg = cv2.imread(bg_path)
        
        # Resize background to match input image dimensions
        bg = cv2.resize(bg, (img.shape[1], img.shape[0]))
        
        # Convert threshold from scale (0-100) to actual color values
        green_threshold = int(green_threshold * 2.55)  # Convert from percentage to 0-255
        sensitivity = int(sensitivity * 2.55)
        
        # Create a mask based on green color
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define range for green color
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        
        # Adjust the green range based on sensitivity
        lower_green[0] = max(0, 60 - sensitivity//2)
        upper_green[0] = min(180, 60 + sensitivity//2)
        
        # Create a mask
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Create inverse mask
        mask_inv = cv2.bitwise_not(mask)
        
        # Extract foreground from original image
        fg = cv2.bitwise_and(img, img, mask=mask_inv)
        
        # Extract background where there is green
        bg_part = cv2.bitwise_and(bg, bg, mask=mask)
        
        # Combine foreground and background
        result = cv2.add(fg, bg_part)
        
        return result
    
    def process_image(self):
        if not self.input_image_path or not self.background_image_path:
            self.status_label.config(text="Please select both images first")
            return
        
        self.status_label.config(text="Processing...")
        threading.Thread(target=self.process_in_thread).start()
    
    def process_in_thread(self):
        try:
            self.processed_image = self.remove_green_screen(
                self.input_image_path, 
                self.background_image_path, 
                self.green_threshold.get(),
                self.sensitivity.get()
            )
            self.status_label.config(text="Processing complete")
            self.update_preview()
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def save_result(self):
        if self.processed_image is None:
            self.status_label.config(text="No processed image to save")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        
        if save_path:
            cv2.imwrite(save_path, self.processed_image)
            self.status_label.config(text=f"Image saved to {save_path}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GreenScreenRemover()
    app.run()