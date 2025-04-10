import tkinter as tk
from time import strftime

def update_time():
    """Update the time display"""
    string_time = strftime('%H:%M:%S %p')
    time_label.config(text=string_time)
    # Schedule the update_time function to run again after 1000ms (1 second)
    window.after(1000, update_time)

# Create the main window
window = tk.Tk()
window.title("Digital Clock")
window.geometry("300x100")
window.resizable(True, True)
window.configure(bg="black")

# Create the time display label
time_label = tk.Label(
    window,
    font=('Helvetica', 40, 'bold'),
    background='black',
    foreground='#00FF00'  # Green color
)
time_label.pack(anchor='center', fill='both', expand=True)

# Initial call to update_time to display the time immediately
update_time()

# Start the main event loop
window.mainloop()