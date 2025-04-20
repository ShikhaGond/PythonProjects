import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Notepad")
        self.root.geometry("800x600")
        
        self.file_path = None
        self.text_changed = False
        
        # Create the text widget
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
        self.text_area.pack(expand=True, fill='both')
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        
        # Create the menu bar
        self.menu_bar = tk.Menu(root)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Alt+F4")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # Format menu
        self.format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        self.format_menu.add_command(label="Font...", command=self.choose_font)
        self.menu_bar.add_cascade(label="Format", menu=self.format_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        
        # Protocol for closing window
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
    def on_text_modified(self, event=None):
        if self.text_area.edit_modified():
            self.text_changed = True
            if self.file_path:
                self.root.title(f"*{os.path.basename(self.file_path)} - Notepad")
            else:
                self.root.title("*Untitled - Notepad")
            self.text_area.edit_modified(False)
    
    def new_file(self):
        if self.text_changed:
            response = messagebox.askyesnocancel("Notepad", "Do you want to save changes?")
            if response is None:  # Cancel was clicked
                return
            if response:  # Yes was clicked
                if not self.save_file():
                    return  # User canceled save dialog
        
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.text_changed = False
        self.root.title("Untitled - Notepad")
    
    def open_file(self):
        if self.text_changed:
            response = messagebox.askyesnocancel("Notepad", "Do you want to save changes?")
            if response is None:  # Cancel was clicked
                return
            if response:  # Yes was clicked
                if not self.save_file():
                    return  # User canceled save dialog
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.text_changed = False
                self.root.title(f"{os.path.basename(file_path)} - Notepad")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        if not self.file_path:
            return self.save_as()
        
        try:
            content = self.text_area.get(1.0, tk.END)
            with open(self.file_path, 'w') as file:
                file.write(content)
            self.text_changed = False
            self.root.title(f"{os.path.basename(self.file_path)} - Notepad")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
        
        self.file_path = file_path
        return self.save_file()
    
    def exit_app(self):
        if self.text_changed:
            response = messagebox.askyesnocancel("Notepad", "Do you want to save changes?")
            if response is None:  # Cancel was clicked
                return
            if response:  # Yes was clicked
                if not self.save_file():
                    return  # User canceled save dialog
        
        self.root.destroy()
    
    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")
    
    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")
    
    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")
    
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"
    
    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget("wrap")
        new_wrap = tk.NONE if current_wrap == tk.WORD else tk.WORD
        self.text_area.config(wrap=new_wrap)
    
    def choose_font(self):
        # A very simple font selector for demonstration purposes
        font_window = tk.Toplevel(self.root)
        font_window.title("Choose Font")
        font_window.geometry("300x200")
        font_window.resizable(False, False)
        
        tk.Label(font_window, text="Select Font:").pack(pady=10)
        
        fonts = ["Consolas", "Arial", "Times New Roman", "Courier New", "Verdana"]
        font_var = tk.StringVar(font_window)
        font_var.set(fonts[0])
        
        font_menu = tk.OptionMenu(font_window, font_var, *fonts)
        font_menu.pack(pady=5)
        
        size_label = tk.Label(font_window, text="Size:")
        size_label.pack(pady=5)
        
        size_var = tk.IntVar(font_window)
        size_var.set(11)
        
        size_entry = tk.Spinbox(font_window, from_=8, to=72, textvariable=size_var)
        size_entry.pack(pady=5)
        
        def apply_font():
            selected_font = font_var.get()
            selected_size = size_var.get()
            self.text_area.config(font=(selected_font, selected_size))
            font_window.destroy()
        
        apply_button = tk.Button(font_window, text="Apply", command=apply_font)
        apply_button.pack(pady=10)
    
    def show_about(self):
        messagebox.showinfo(
            "About Notepad Clone",
            "Python Notepad Clone\n\nA simple text editor created with Python and Tkinter\n\nVersion 1.0"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = Notepad(root)
    root.mainloop()