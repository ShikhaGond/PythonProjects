import tkinter as tk   # Mini art studio handles the movements
from tkinter import colorchooser # This is for the colorpicking option for our pencil

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Drawing App")

        # This is the canvas for drawing
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # These are our variables for drawing
        self.last_x, self.last_y = None, None
        self.color = "black"
        self.line_width = 2

        # Here we are binding  our mouse events 
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # This is our toolbar
        self.toolbar = tk.Frame(root, bg="lightgray")
        self.toolbar.pack(fill=tk.X)

        # The color picker pallette
        self.color_button = tk.Button(self.toolbar, text="Choose Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5, pady=5)

        # We can adjust our line width with this
        self.line_width_label = tk.Label(self.toolbar, text="Line Width:")
        self.line_width_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.line_width_slider = tk.Scale(self.toolbar, from_=1, to=10, orient=tk.HORIZONTAL, command=self.set_line_width)
        self.line_width_slider.set(self.line_width)
        self.line_width_slider.pack(side=tk.LEFT, padx=5, pady=5)

        # canvas clear button
        self.clear_button = tk.Button(self.toolbar, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def start_draw(self, event):
        """Record the starting point of the drawing."""
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        """Draw a line from the last point to the current point."""
        if self.last_x and self.last_y:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.line_width, fill=self.color, capstyle=tk.ROUND, smooth=True
            )
        self.last_x, self.last_y = event.x, event.y

    def stop_draw(self, event):
        """Reset the last point when the mouse button is released."""
        self.last_x, self.last_y = None, None

    def choose_color(self):
        """Open a color picker dialog and set the drawing color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def set_line_width(self, value):
        """Set the line width based on the slider value."""
        self.line_width = int(value)

    def clear_canvas(self):
        """Clear the entire canvas."""
        self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
