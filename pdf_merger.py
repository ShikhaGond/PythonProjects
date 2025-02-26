import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfMerger
from tkinterdnd2 import TkinterDnD, DND_FILES

class PDFMergerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Merger")
        self.geometry("600x400")
        self.pdf_files = []
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.create_widgets()
        self.configure_grid()

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def create_widgets(self):
        # Top buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add PDFs", command=self.add_files).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_file).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Move Up", command=lambda: self.move_file(-1)).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Move Down", command=lambda: self.move_file(1)).pack(side='left', padx=2)

        # Output file selection
        output_frame = ttk.Frame(self)
        output_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(output_frame, text="Browse", command=self.select_output).pack(side='left', padx=2)

        # File list with drag-and-drop
        self.file_list = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.file_list.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.file_list.drop_target_register(DND_FILES)
        self.file_list.dnd_bind('<<Drop>>', self.handle_drop)

        # Progress bar
        self.progress = ttk.Progressbar(self, orient='horizontal', mode='determinate')
        self.progress.grid(row=3, column=0, sticky='ew', padx=5, pady=5)

        # Merge button
        ttk.Button(self, text="Merge PDFs", command=self.merge_files).grid(row=4, column=0, pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames (title="Select PDF files", filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))
        self.add_files_to_list(files)

    def handle_drop(self, event):
        files = event.data.split()
        cleaned_files = [f.strip('{').strip('}') for f in files]
        self.add_files_to_list(cleaned_files)

    def add_files_to_list(self, files):
        for f in files:
            if f.lower().endswith('.pdf'):
                if f not in self.pdf_files:
                    self.pdf_files.append(f)
                    self.file_list.insert(tk.END, os.path.basename(f))
            else:
                messagebox.showwarning("Invalid File", f"{f} is not a PDF file")

    def remove_file(self):
        selected = self.file_list.curselection()
        for index in reversed(selected):
            self.file_list.delete(index)
            del self.pdf_files[index]

    def move_file(self, direction):
        selected = self.file_list.curselection()
        if not selected:
            return
        
        index = selected[0]
        new_index = index + direction
        
        if 0 <= new_index < self.file_list.size():
            # Swap in listbox
            text = self.file_list.get(index)
            self.file_list.delete(index)
            self.file_list.insert(new_index, text)
            
            # Swap in files list
            self.pdf_files[index], self.pdf_files[new_index] = \
                self.pdf_files[new_index], self.pdf_files[index]
            
            self.file_list.select_set(new_index)

    def select_output(self):
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))
        if output_file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_file)

    def merge_files(self):
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files to merge")
            return
        
        output_path = self.output_entry.get()
        if not output_path:
            messagebox.showwarning("No Output", "Please select an output file")
            return
        
        try:
            merger = PdfMerger()
            total_files = len(self.pdf_files)
            self.progress['value'] = 0
            self.progress['maximum'] = total_files
            
            for i, pdf in enumerate(self.pdf_files, 1):
                merger.append(pdf)
                self.progress['value'] = i
                self.update_idletasks()
            
            merger.write(output_path)
            merger.close()
            
            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved to: {output_path}")
            self.progress['value'] = 0
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
            self.progress['value'] = 0

if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop();