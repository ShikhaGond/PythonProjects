import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class FileOrganizer:
    def __init__(self):
        self.file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xlsx', '.ppt', '.pptx', '.csv'],
            'Videos': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.java', '.cpp', '.c', '.html', '.css', '.js', '.php', '.rb', '.go', '.json'],
            'Executables': ['.exe', '.msi', '.app', '.bat', '.sh'],
            'Others': []
        }
        
    def organize_files(self, directory_path, categories=None, progress_callback=None):
        """
        Organize files in the given directory based on their file extensions.
        
        Args:
            directory_path: Path to the directory to organize
            categories: List of categories to organize (None for all)
            progress_callback: Function to call with progress updates
        
        Returns:
            Dictionary with stats about the operation
        """
        if not os.path.exists(directory_path):
            return {"status": "error", "message": "Directory does not exist"}
        
        # Prepare category list
        if categories is None:
            categories = list(self.file_types.keys())
            
        stats = {
            "total_files": 0,
            "organized_files": 0,
            "skipped_files": 0,
            "categories": {}
        }
        
        files = [f for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f))]
        stats["total_files"] = len(files)
        
        for i, filename in enumerate(files):
            if progress_callback:
                progress = (i + 1) / len(files) * 100
                progress_callback(progress, f"Processing: {filename}")
            
            file_path = os.path.join(directory_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Skip folders or files without extension
            if not file_ext:
                stats["skipped_files"] += 1
                continue
            
            # Find which category this file belongs to
            category = "Others"
            for cat, extensions in self.file_types.items():
                if file_ext in extensions:
                    category = cat
                    break
            
            # Skip if category is not in our target list
            if category not in categories:
                stats["skipped_files"] += 1
                continue
            
            # Create category folder if it doesn't exist
            category_path = os.path.join(directory_path, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            
            # Move file to category folder
            try:
                destination = os.path.join(category_path, filename)
                # Handle file name conflicts
                counter = 1
                original_name = os.path.splitext(filename)[0]
                while os.path.exists(destination):
                    new_name = f"{original_name}_{counter}{file_ext}"
                    destination = os.path.join(category_path, new_name)
                    counter += 1
                    
                shutil.move(file_path, destination)
                
                # Update statistics
                stats["organized_files"] += 1
                if category not in stats["categories"]:
                    stats["categories"][category] = 0
                stats["categories"][category] += 1
                
            except Exception as e:
                stats["skipped_files"] += 1
                
        return stats


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.organizer = FileOrganizer()
        self.selected_directory = ""
        self.is_organizing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="10")
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # Categories frame
        cat_frame = ttk.LabelFrame(main_frame, text="Categories to Organize", padding="10")
        cat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.category_vars = {}
        for i, category in enumerate(self.organizer.file_types.keys()):
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            
            # Create a checkbox for each category
            row = i // 2
            col = i % 2
            
            chk = ttk.Checkbutton(cat_frame, text=category, variable=var)
            chk.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to organize")
        self.status_label.pack(fill=tk.X)
        
        # Result frame
        self.result_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(self.result_frame, height=8, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.organize_btn = ttk.Button(btn_frame, text="Organize Files", command=self.start_organizing)
        self.organize_btn.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_organizing, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def update_progress(self, value, message):
        self.progress_bar["value"] = value
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_organizing(self):
        directory = self.dir_entry.get().strip()
        
        if not directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return
            
        if not os.path.exists(directory):
            messagebox.showerror("Error", "The selected directory does not exist.")
            return
        
        # Get selected categories
        selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]
        
        if not selected_categories:
            messagebox.showerror("Error", "Please select at least one category.")
            return
        
        self.is_organizing = True
        self.organize_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        # Clear previous results
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Start organizing in a separate thread
        self.organize_thread = threading.Thread(
            target=self.run_organization,
            args=(directory, selected_categories)
        )
        self.organize_thread.daemon = True
        self.organize_thread.start()
    
    def run_organization(self, directory, categories):
        try:
            stats = self.organizer.organize_files(
                directory,
                categories=categories,
                progress_callback=self.update_progress
            )
            
            self.root.after(0, lambda: self.display_results(stats))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, self.reset_ui)
    
    def cancel_organizing(self):
        self.is_organizing = False
        self.status_label.config(text="Organization canceled")
        self.reset_ui()
    
    def reset_ui(self):
        self.is_organizing = False
        self.organize_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
    
    def display_results(self, stats):
        if stats.get("status") == "error":
            messagebox.showerror("Error", stats.get("message", "An unknown error occurred"))
            return
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        result = f"Total files: {stats['total_files']}\n"
        result += f"Organized files: {stats['organized_files']}\n"
        result += f"Skipped files: {stats['skipped_files']}\n\n"
        
        if stats['categories']:
            result += "Files by category:\n"
            for cat, count in stats['categories'].items():
                result += f"- {cat}: {count} files\n"
        
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)
        
        self.status_label.config(text="Organization completed!")
        messagebox.showinfo("Success", f"Successfully organized {stats['organized_files']} files")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()