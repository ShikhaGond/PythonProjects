import time
from datetime import datetime
from plyer import notification
import tkinter as tk
from tkinter import messagebox, simpledialog

class NotifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Notifier")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.notifications = []
        
        # Configure the GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Title
        title_label = tk.Label(self.root, text="Desktop Notifier", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Create notification button
        create_btn = tk.Button(button_frame, text="Create Notification", command=self.create_notification, 
                              bg="#4CAF50", fg="white", width=15, height=2)
        create_btn.grid(row=0, column=0, padx=10)
        
        # View scheduled notifications button
        view_btn = tk.Button(button_frame, text="View Scheduled", command=self.view_notifications,
                            bg="#2196F3", fg="white", width=15, height=2)
        view_btn.grid(row=0, column=1, padx=10)
        
        # Notifications list frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.notification_listbox = tk.Listbox(list_frame, width=45, height=8)
        self.notification_listbox.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notification_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.notification_listbox.yview)
        
        # Delete button
        delete_btn = tk.Button(self.root, text="Delete Selected", command=self.delete_notification,
                              bg="#F44336", fg="white", width=15)
        delete_btn.pack(pady=10)
        
        # Start monitoring notifications in a separate thread
        self.root.after(1000, self.check_notifications)
        
    def create_notification(self):
        title = simpledialog.askstring("Notification", "Enter notification title:")
        if not title:
            return
            
        message = simpledialog.askstring("Notification", "Enter notification message:")
        if not message:
            return
            
        time_str = simpledialog.askstring("Notification", "Enter time (HH:MM):")
        if not time_str:
            return
            
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
                
            now = datetime.now()
            notification_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time is in the past, schedule it for tomorrow
            if notification_time < now:
                messagebox.showinfo("Info", "Time is in the past. Scheduling for tomorrow.")
                
            notification_entry = {
                "title": title,
                "message": message,
                "time": notification_time.strftime("%H:%M"),
                "triggered": False
            }
            
            self.notifications.append(notification_entry)
            self.update_listbox()
            messagebox.showinfo("Success", f"Notification scheduled for {notification_time.strftime('%H:%M')}")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM (e.g., 14:30)")
    
    def view_notifications(self):
        if not self.notifications:
            messagebox.showinfo("Info", "No notifications scheduled.")
        else:
            notification_list = "\n".join([f"{n['time']} - {n['title']}" for n in self.notifications])
            messagebox.showinfo("Scheduled Notifications", notification_list)
    
    def delete_notification(self):
        try:
            selected_idx = self.notification_listbox.curselection()[0]
            del self.notifications[selected_idx]
            self.update_listbox()
        except IndexError:
            messagebox.showerror("Error", "No notification selected")
    
    def update_listbox(self):
        self.notification_listbox.delete(0, tk.END)
        for notification in self.notifications:
            status = " (Sent)" if notification["triggered"] else ""
            self.notification_listbox.insert(tk.END, f"{notification['time']} - {notification['title']}{status}")
    
    def check_notifications(self):
        current_time = datetime.now().strftime("%H:%M")
        
        for notification in self.notifications:
            if notification["time"] == current_time and not notification["triggered"]:
                self.show_notification(notification["title"], notification["message"])
                notification["triggered"] = True
                self.update_listbox()
        
        # Check again after 10 seconds
        self.root.after(10000, self.check_notifications)
    
    def show_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Desktop Notifier",
            timeout=10
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = NotifierApp(root)
    root.mainloop()