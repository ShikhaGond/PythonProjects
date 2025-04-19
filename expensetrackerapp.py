import os
import sys
import datetime
import calendar
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
import sqlite3
from PIL import Image, ImageTk
import numpy as np

# Set backend for matplotlib
matplotlib.use("TkAgg")

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f5f5f5")
        
        # Database setup
        self.conn = sqlite3.connect("expense_tracker.db")
        self.create_tables()
        
        # Variables
        self.transaction_id = None
        self.selected_category = tk.StringVar()
        self.selected_type = tk.StringVar(value="Expense")
        self.selected_payment = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_month = tk.StringVar(value=datetime.datetime.now().strftime("%B"))
        self.filter_year = tk.StringVar(value=str(datetime.datetime.now().year))
        
        # Pre-populate categories
        self.expense_categories = ["Food", "Transport", "Housing", "Entertainment", "Shopping", "Utilities", "Health", "Education", "Other"]
        self.income_categories = ["Salary", "Freelance", "Investments", "Gifts", "Other"]
        self.payment_methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Mobile Payment", "Other"]
        
        # Create initial monthly budgets
        self.initialize_budgets()
        
        # Create main frames
        self.create_main_frames()
        
        # Create widgets
        self.create_sidebar()
        self.create_transaction_form()
        self.create_transaction_list()
        self.create_visualization_panel()
        self.create_budget_panel()
        
        # Load initial data
        self.load_transactions()
        self.load_summary()
        self.load_budget_view()
        
        # Set default active tab
        self.show_frame("transactions")

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount REAL,
            type TEXT,
            category TEXT,
            payment_method TEXT,
            description TEXT
        )
        ''')
        
        # Budgets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            month TEXT,
            year TEXT
        )
        ''')
        
        self.conn.commit()
    
    def initialize_budgets(self):
        cursor = self.conn.cursor()
        current_month = datetime.datetime.now().strftime("%B")
        current_year = str(datetime.datetime.now().year)
        
        # Check if budgets exist for the current month
        cursor.execute("SELECT COUNT(*) FROM budgets WHERE month = ? AND year = ?", (current_month, current_year))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Initialize with default budgets
            for category in self.expense_categories:
                cursor.execute(
                    "INSERT INTO budgets (category, amount, month, year) VALUES (?, ?, ?, ?)",
                    (category, 0.0, current_month, current_year)
                )
            self.conn.commit()
    
    def create_main_frames(self):
        # Container for all frames
        self.container = tk.Frame(self.root, bg="#f5f5f5")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar frame
        self.sidebar = tk.Frame(self.container, width=200, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Content frame
        self.content = tk.Frame(self.container, bg="#f5f5f5")
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Create frames for different views
        self.frames = {}
        
        # Transactions frame
        self.frames["transactions"] = tk.Frame(self.content, bg="#f5f5f5")
        
        # Dashboard frame
        self.frames["dashboard"] = tk.Frame(self.content, bg="#f5f5f5")
        
        # Reports frame
        self.frames["reports"] = tk.Frame(self.content, bg="#f5f5f5")
        
        # Budget frame
        self.frames["budget"] = tk.Frame(self.content, bg="#f5f5f5")
        
        for frame in self.frames.values():
            frame.pack(fill="both", expand=True)
            frame.pack_forget()
    
    def create_sidebar(self):
        # App title
        title_label = tk.Label(self.sidebar, text="Expense Tracker", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("Transactions", "transactions"),
            ("Dashboard", "dashboard"),
            ("Reports", "reports"),
            ("Budget", "budget")
        ]
        
        for text, view in nav_buttons:
            button = tk.Button(
                self.sidebar, 
                text=text, 
                font=("Arial", 12), 
                bg="#34495e", 
                fg="white",
                bd=0,
                padx=10,
                pady=8,
                width=15,
                activebackground="#1abc9c",
                activeforeground="white",
                cursor="hand2",
                command=lambda v=view: self.show_frame(v)
            )
            button.pack(pady=5, padx=10, fill="x")
        
        # Version and credits
        version_label = tk.Label(self.sidebar, text="v1.0", font=("Arial", 8), bg="#2c3e50", fg="#95a5a6")
        version_label.pack(side="bottom", pady=10)
    
    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        self.frames[frame_name].pack(fill="both", expand=True)
        
        # Refresh data
        if frame_name == "transactions":
            self.load_transactions()
        elif frame_name == "dashboard":
            self.load_summary()
        elif frame_name == "reports":
            self.generate_reports()
        elif frame_name == "budget":
            self.load_budget_view()
    
    def create_transaction_form(self):
        form_frame = tk.LabelFrame(self.frames["transactions"], text="Add Transaction", font=("Arial", 12, "bold"), bg="#f5f5f5", padx=10, pady=10)
        form_frame.pack(fill="x", pady=10)
        
        # Form layout
        form_grid = tk.Frame(form_frame, bg="#f5f5f5")
        form_grid.pack(fill="x", padx=10, pady=10)
        
        # Date picker
        tk.Label(form_grid, text="Date:", bg="#f5f5f5", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_picker = DateEntry(form_grid, width=15, background='#1abc9c', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Transaction type selector
        tk.Label(form_grid, text="Type:", bg="#f5f5f5", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        type_frame = tk.Frame(form_grid, bg="#f5f5f5")
        type_frame.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        tk.Radiobutton(type_frame, text="Expense", variable=self.selected_type, value="Expense", bg="#f5f5f5", command=self.update_categories).pack(side="left")
        tk.Radiobutton(type_frame, text="Income", variable=self.selected_type, value="Income", bg="#f5f5f5", command=self.update_categories).pack(side="left")
        
        # Amount
        tk.Label(form_grid, text="Amount:", bg="#f5f5f5", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = tk.Entry(form_grid, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Category
        tk.Label(form_grid, text="Category:", bg="#f5f5f5", font=("Arial", 10)).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.category_combo = ttk.Combobox(form_grid, textvariable=self.selected_category, state="readonly", width=15)
        self.category_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Payment method
        tk.Label(form_grid, text="Payment Method:", bg="#f5f5f5", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.payment_combo = ttk.Combobox(form_grid, textvariable=self.selected_payment, state="readonly", width=15, values=self.payment_methods)
        self.payment_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Description
        tk.Label(form_grid, text="Description:", bg="#f5f5f5", font=("Arial", 10)).grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.description_entry = tk.Entry(form_grid, textvariable=self.description_var, width=25)
        self.description_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        # Action buttons
        button_frame = tk.Frame(form_frame, bg="#f5f5f5")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_button = tk.Button(button_frame, text="Add Transaction", bg="#1abc9c", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, command=self.add_transaction)
        self.add_button.pack(side="left", padx=5)
        
        self.update_button = tk.Button(button_frame, text="Update", bg="#3498db", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, command=self.update_transaction)
        self.update_button.pack(side="left", padx=5)
        self.update_button.config(state="disabled")
        
        self.cancel_button = tk.Button(button_frame, text="Cancel", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5, command=self.cancel_edit)
        self.cancel_button.pack(side="left", padx=5)
        self.cancel_button.config(state="disabled")
        
        # Initialize category dropdown
        self.update_categories()
    
    def update_categories(self):
        if self.selected_type.get() == "Expense":
            self.category_combo['values'] = self.expense_categories
        else:
            self.category_combo['values'] = self.income_categories
        
        # Set default value
        if self.category_combo['values']:
            self.selected_category.set(self.category_combo['values'][0])
    
    def create_transaction_list(self):
        # Create filter frame
        filter_frame = tk.Frame(self.frames["transactions"], bg="#f5f5f5")
        filter_frame.pack(fill="x", pady=5)
        
        # Month filter
        months = list(calendar.month_name)[1:]
        current_month = datetime.datetime.now().strftime("%B")
        
        tk.Label(filter_frame, text="Filter by:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        month_combo = ttk.Combobox(filter_frame, textvariable=self.filter_month, values=months, width=10, state="readonly")
        month_combo.pack(side="left", padx=5)
        self.filter_month.set(current_month)
        
        # Year filter
        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        year_combo = ttk.Combobox(filter_frame, textvariable=self.filter_year, values=years, width=6, state="readonly")
        year_combo.pack(side="left", padx=5)
        self.filter_year.set(str(current_year))
        
        # Apply filter button
        apply_filter_btn = tk.Button(filter_frame, text="Apply", bg="#3498db", fg="white", command=self.load_transactions)
        apply_filter_btn.pack(side="left", padx=5)
        
        # Search field
        tk.Label(filter_frame, text="Search:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=20)
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        search_btn = tk.Button(filter_frame, text="Search", bg="#3498db", fg="white", command=self.search_transactions)
        search_btn.pack(side="left", padx=5)
        
        # Transactions list
        list_frame = tk.Frame(self.frames["transactions"], bg="white")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Create treeview
        columns = ("id", "date", "amount", "type", "category", "payment", "description")
        self.transaction_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define headings
        self.transaction_tree.heading("id", text="ID")
        self.transaction_tree.heading("date", text="Date")
        self.transaction_tree.heading("amount", text="Amount")
        self.transaction_tree.heading("type", text="Type")
        self.transaction_tree.heading("category", text="Category")
        self.transaction_tree.heading("payment", text="Payment Method")
        self.transaction_tree.heading("description", text="Description")
        
        # Define columns
        self.transaction_tree.column("id", width=50)
        self.transaction_tree.column("date", width=100)
        self.transaction_tree.column("amount", width=100)
        self.transaction_tree.column("type", width=80)
        self.transaction_tree.column("category", width=100)
        self.transaction_tree.column("payment", width=120)
        self.transaction_tree.column("description", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.transaction_tree.pack(fill="both", expand=True)
        
        # Bind select event
        self.transaction_tree.bind("<ButtonRelease-1>", self.select_transaction)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self.transaction_tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_transaction)
        self.context_menu.add_command(label="Delete", command=self.delete_transaction)
        
        self.transaction_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        # Check if an item is selected
        selected_item = self.transaction_tree.selection()
        if selected_item:
            # Display context menu
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def create_visualization_panel(self):
        # Create visualization tabs
        tab_control = ttk.Notebook(self.frames["dashboard"])
        tab_control.pack(fill="both", expand=True)
        
        # Overview tab
        overview_tab = ttk.Frame(tab_control)
        tab_control.add(overview_tab, text="Overview")
        
        # Summary section
        summary_frame = tk.LabelFrame(overview_tab, text="Monthly Summary", font=("Arial", 12, "bold"), bg="#f5f5f5")
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        # Summary cards
        cards_frame = tk.Frame(summary_frame, bg="#f5f5f5")
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        # Income card
        self.income_card = tk.Frame(cards_frame, bg="#2ecc71", padx=15, pady=15, width=200)
        self.income_card.pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Label(self.income_card, text="Income", font=("Arial", 14), bg="#2ecc71", fg="white").pack()
        self.income_amount = tk.Label(self.income_card, text="$0.00", font=("Arial", 18, "bold"), bg="#2ecc71", fg="white")
        self.income_amount.pack(pady=5)
        
        # Expense card
        self.expense_card = tk.Frame(cards_frame, bg="#e74c3c", padx=15, pady=15, width=200)
        self.expense_card.pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Label(self.expense_card, text="Expenses", font=("Arial", 14), bg="#e74c3c", fg="white").pack()
        self.expense_amount = tk.Label(self.expense_card, text="$0.00", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white")
        self.expense_amount.pack(pady=5)
        
        # Balance card
        self.balance_card = tk.Frame(cards_frame, bg="#3498db", padx=15, pady=15, width=200)
        self.balance_card.pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Label(self.balance_card, text="Balance", font=("Arial", 14), bg="#3498db", fg="white").pack()
        self.balance_amount = tk.Label(self.balance_card, text="$0.00", font=("Arial", 18, "bold"), bg="#3498db", fg="white")
        self.balance_amount.pack(pady=5)
        
        # Charts frame
        charts_frame = tk.Frame(overview_tab, bg="#f5f5f5")
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Category chart
        category_chart_frame = tk.LabelFrame(charts_frame, text="Spending by Category", font=("Arial", 12, "bold"), bg="#f5f5f5")
        category_chart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.category_chart_canvas = tk.Canvas(category_chart_frame, bg="white")
        self.category_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Date chart
        date_chart_frame = tk.LabelFrame(charts_frame, text="Daily Spending", font=("Arial", 12, "bold"), bg="#f5f5f5")
        date_chart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.date_chart_canvas = tk.Canvas(date_chart_frame, bg="white")
        self.date_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Trends tab
        trends_tab = ttk.Frame(tab_control)
        tab_control.add(trends_tab, text="Trends")
        
        trends_chart_frame = tk.LabelFrame(trends_tab, text="Monthly Trends", font=("Arial", 12, "bold"), bg="#f5f5f5")
        trends_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.trends_chart_canvas = tk.Canvas(trends_chart_frame, bg="white")
        self.trends_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_budget_panel(self):
        # Budget frame
        budget_frame = tk.LabelFrame(self.frames["budget"], text="Monthly Budget", font=("Arial", 12, "bold"), bg="#f5f5f5")
        budget_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Month selector
        month_frame = tk.Frame(budget_frame, bg="#f5f5f5")
        month_frame.pack(fill="x", padx=10, pady=10)
        
        months = list(calendar.month_name)[1:]
        current_month = datetime.datetime.now().strftime("%B")
        
        tk.Label(month_frame, text="Month:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        self.budget_month = tk.StringVar(value=current_month)
        month_combo = ttk.Combobox(month_frame, textvariable=self.budget_month, values=months, width=10, state="readonly")
        month_combo.pack(side="left", padx=5)
        
        # Year selector
        tk.Label(month_frame, text="Year:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        self.budget_year = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(month_frame, textvariable=self.budget_year, values=years, width=6, state="readonly")
        year_combo.pack(side="left", padx=5)
        
        # Load button
        load_btn = tk.Button(month_frame, text="Load", bg="#3498db", fg="white", command=self.load_budget_view)
        load_btn.pack(side="left", padx=5)
        
        # Budget list
        list_frame = tk.Frame(budget_frame, bg="white")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Create treeview
        columns = ("category", "budget", "spent", "remaining", "percentage")
        self.budget_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define headings
        self.budget_tree.heading("category", text="Category")
        self.budget_tree.heading("budget", text="Budget")
        self.budget_tree.heading("spent", text="Spent")
        self.budget_tree.heading("remaining", text="Remaining")
        self.budget_tree.heading("percentage", text="% Used")
        
        # Define columns
        self.budget_tree.column("category", width=150)
        self.budget_tree.column("budget", width=100)
        self.budget_tree.column("spent", width=100)
        self.budget_tree.column("remaining", width=100)
        self.budget_tree.column("percentage", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.budget_tree.pack(fill="both", expand=True)
        
        # Add right-click menu
        self.budget_menu = tk.Menu(self.budget_tree, tearoff=0)
        self.budget_menu.add_command(label="Set Budget", command=self.set_budget)
        
        self.budget_tree.bind("<Button-3>", self.show_budget_menu)
        
        # Budget progress visualization
        progress_frame = tk.LabelFrame(self.frames["budget"], text="Budget Progress", font=("Arial", 12, "bold"), bg="#f5f5f5")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.budget_chart_canvas = tk.Canvas(progress_frame, bg="white")
        self.budget_chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_budget_menu(self, event):
        # Check if an item is selected
        selected_item = self.budget_tree.selection()
        if selected_item:
            # Display context menu
            try:
                self.budget_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.budget_menu.grab_release()
    
    def set_budget(self):
        selected_item = self.budget_tree.selection()[0]
        category = self.budget_tree.item(selected_item, "values")[0]
        
        # Get current budget
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT amount FROM budgets WHERE category = ? AND month = ? AND year = ?",
            (category, self.budget_month.get(), self.budget_year.get())
        )
        result = cursor.fetchone()
        current_budget = result[0] if result else 0
        
        # Ask for new budget
        new_budget = simpledialog.askfloat(
            "Set Budget", 
            f"Enter budget amount for {category}:",
            initialvalue=current_budget,
            minvalue=0
        )
        
        if new_budget is not None:
            # Update budget
            cursor.execute(
                "UPDATE budgets SET amount = ? WHERE category = ? AND month = ? AND year = ?",
                (new_budget, category, self.budget_month.get(), self.budget_year.get())
            )
            self.conn.commit()
            
            # Refresh budget view
            self.load_budget_view()
    
    def load_budget_view(self):
        # Clear existing items
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        # Get all categories
        categories = self.expense_categories
        
        # Get budgets for selected month and year
        cursor = self.conn.cursor()
        
        for category in categories:
            # Get budget
            cursor.execute(
                "SELECT amount FROM budgets WHERE category = ? AND month = ? AND year = ?",
                (category, self.budget_month.get(), self.budget_year.get())
            )
            result = cursor.fetchone()
            budget = result[0] if result else 0
            
            # Get spending for this category in selected month
            month_num = list(calendar.month_name).index(self.budget_month.get())
            start_date = f"{self.budget_year.get()}-{month_num:02d}-01"
            end_date = f"{self.budget_year.get()}-{month_num:02d}-{calendar.monthrange(int(self.budget_year.get()), month_num)[1]}"
            
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE category = ? AND type = 'Expense' AND date BETWEEN ? AND ?",
                (category, start_date, end_date)
            )
            result = cursor.fetchone()
            spent = result[0] if result and result[0] else 0
            
            # Calculate remaining and percentage
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0
            
            # Add to treeview
            self.budget_tree.insert("", "end", values=(
                category,
                f"${budget:.2f}",
                f"${spent:.2f}",
                f"${remaining:.2f}",
                f"{percentage:.1f}%"
            ))
        
        # Create budget chart
        self.create_budget_chart()
    
    def create_budget_chart(self):
        # Clear previous chart
        for widget in self.budget_chart_canvas.winfo_children():
            widget.destroy()
        
        # Get data from treeview
        categories = []
        budgets = []
        spent = []
        
        for item in self.budget_tree.get_children():
            values = self.budget_tree.item(item, "values")
            categories.append(values[0])
            budgets.append(float(values[1].replace("$", "")))
            spent.append(float(values[2].replace("$", "")))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Set width of bars
        bar_width = 0.35
        index = np.arange(len(categories))
        
        # Create bars
        budget_bars = ax.bar(index, budgets, bar_width, label='Budget', color='#3498db')
        spent_bars = ax.bar(index + bar_width, spent, bar_width, label='Spent', color='#e74c3c')
        
        # Add labels
        ax.set_xlabel('Categories')
        ax.set_ylabel('Amount ($)')
        ax.set_title(f'Budget vs Spent - {self.budget_month.get()} {self.budget_year.get()}')
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.budget_chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def generate_reports(self):
        # Clear previous content
        for widget in self.frames["reports"].winfo_children():
            widget.destroy()
        
        # Create report controls
        controls_frame = tk.Frame(self.frames["reports"], bg="#f5f5f5")
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Report type
        tk.Label(controls_frame, text="Report Type:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        report_type = tk.StringVar(value="Monthly Summary")
        report_types = ["Monthly Summary", "Category Analysis", "Income vs Expenses", "Annual Overview"]
        report_combo = ttk.Combobox(controls_frame, textvariable=report_type, values=report_types, width=15, state="readonly")
        report_combo.pack(side="left", padx=5)
        
        # Month selector
        months = list(calendar.month_name)[1:]
        current_month = datetime.datetime.now().strftime("%B")
        
        tk.Label(controls_frame, text="Month:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        report_month = tk.StringVar(value=current_month)
        month_combo = ttk.Combobox(controls_frame, textvariable=report_month, values=months, width=10, state="readonly")
        month_combo.pack(side="left", padx=5)
        
        # Year selector
        tk.Label(controls_frame, text="Year:", bg="#f5f5f5", font=("Arial", 10)).pack(side="left", padx=5)
        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        report_year = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(controls_frame, textvariable=report_year, values=years, width=6, state="readonly")
        year_combo.pack(side="left", padx=5)
        
        # Generate button
        generate_btn = tk.Button(
            controls_frame, 
            text="Generate Report", 
            bg="#1abc9c", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=lambda: self.generate_specific_report(report_type.get(), report_month.get(), report_year.get())
        )
        generate_btn.pack(side="left", padx=15)
        
        # Export button
        export_btn = tk.Button(
            controls_frame, 
            text="Export to CSV", 
            bg="#3498db", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=lambda: self.export_report(report_type.get(), report_month.get(), report_year.get())
        )
        export_btn.pack(side="left", padx=5)
        
        # Report content frame
        self.report_frame = tk.Frame(self.frames["reports"], bg="white")
        self.report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Generate default report
        self.generate_specific_report(report_type.get(), report_month.get(), report_year.get())
    
    def generate_specific_report(self, report_type, month, year):
        # Clear previous report
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = tk.Frame(self.report_frame, bg="white")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text=f"{report_type}: {month} {year}", 
            font=("Arial", 16, "bold"), 
            bg="white"
        ).pack()
        
        if report_type == "Monthly Summary":
            self.generate_monthly_summary(month, year)
        elif report_type == "Category Analysis":
            self.generate_category_analysis(month, year)
        elif report_type == "Income vs Expenses":
            self.generate_income_expense_comparison(month, year)
        elif report_type == "Annual Overview":
            self.generate_annual_overview(year)
    
    def generate_monthly_summary(self, month, year):
        # Create summary frame
        summary_frame = tk.Frame(self.report_frame, bg="white")
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get month number
        month_num = list(calendar.month_name).index(month)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
        
        # Get data
        cursor = self.conn.cursor()
        
        # Total income
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_income = cursor.fetchone()[0] or 0
        
        # Total expenses
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        total_expenses = cursor.fetchone()[0] or 0
        
        # Balance
        balance = total_income - total_expenses
        
        # Create summary labels
        tk.Label(summary_frame, text=f"Total Income: ${total_income:.2f}", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        tk.Label(summary_frame, text=f"Total Expenses: ${total_expenses:.2f}", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        tk.Label(summary_frame, text=f"Net Balance: ${balance:.2f}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=5)
        
        # Get category breakdown
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date)
        )
        categories = cursor.fetchall()
        
        # Create charts frame
        charts_frame = tk.Frame(summary_frame, bg="white")
        charts_frame.pack(fill="both", expand=True, pady=10)
        
        # Create pie chart
        if categories:
            fig, ax = plt.subplots(figsize=(6, 4))
            
            labels = [category[0] for category in categories]
            sizes = [category[1] for category in categories]
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title('Expense Categories')
            
            pie_canvas = FigureCanvasTkAgg(fig, master=charts_frame)
            pie_canvas.draw()
            pie_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)
        
        # Daily spending
        cursor.execute(
            """
            SELECT strftime('%d', date) as day, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND date BETWEEN ? AND ?
            GROUP BY day
            ORDER BY day
            """,
            (start_date, end_date)
        )
        daily_spending = cursor.fetchall()
        
        if daily_spending:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            
            days = [int(day[0]) for day in daily_spending]
            amounts = [day[1] for day in daily_spending]
            
            ax2.bar(days, amounts, color='#3498db')
            ax2.set_xlabel('Day of Month')
            ax2.set_ylabel('Amount ($)')
            ax2.set_title('Daily Spending')
            
            # Set x-axis ticks
            ax2.set_xticks(range(1, 32, 5))
            
            bar_canvas = FigureCanvasTkAgg(fig2, master=charts_frame)
            bar_canvas.draw()
            bar_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)
    
    def generate_category_analysis(self, month, year):
        # Create analysis frame
        analysis_frame = tk.Frame(self.report_frame, bg="white")
        analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get month number
        month_num = list(calendar.month_name).index(month)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
        
        # Get category data
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date)
        )
        categories = cursor.fetchall()
        
        if not categories:
            tk.Label(analysis_frame, text="No expense data available for this period", font=("Arial", 12), bg="white").pack(pady=20)
            return
        
        # Create category table
        table_frame = tk.Frame(analysis_frame, bg="white")
        table_frame.pack(fill="x", pady=10)
        
        # Headers
        tk.Label(table_frame, text="Category", font=("Arial", 12, "bold"), bg="white", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(table_frame, text="Amount", font=("Arial", 12, "bold"), bg="white", width=10, anchor="e").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(table_frame, text="% of Total", font=("Arial", 12, "bold"), bg="white", width=10, anchor="e").grid(row=0, column=2, padx=5, pady=5)
        
        # Calculate total expenses
        total_expenses = sum(category[1] for category in categories)
        
        # Add rows
        for i, (category, amount) in enumerate(categories):
            percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
            
            tk.Label(table_frame, text=category, font=("Arial", 11), bg="white", anchor="w").grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            tk.Label(table_frame, text=f"${amount:.2f}", font=("Arial", 11), bg="white", anchor="e").grid(row=i+1, column=1, padx=5, pady=3, sticky="e")
            tk.Label(table_frame, text=f"{percentage:.1f}%", font=("Arial", 11), bg="white", anchor="e").grid(row=i+1, column=2, padx=5, pady=3, sticky="e")
        
        # Add total row
        separator = ttk.Separator(table_frame, orient="horizontal")
        separator.grid(row=len(categories)+1, column=0, columnspan=3, sticky="ew", pady=5)
        
        tk.Label(table_frame, text="Total", font=("Arial", 11, "bold"), bg="white", anchor="w").grid(row=len(categories)+2, column=0, padx=5, pady=3, sticky="w")
        tk.Label(table_frame, text=f"${total_expenses:.2f}", font=("Arial", 11, "bold"), bg="white", anchor="e").grid(row=len(categories)+2, column=1, padx=5, pady=3, sticky="e")
        tk.Label(table_frame, text="100.0%", font=("Arial", 11, "bold"), bg="white", anchor="e").grid(row=len(categories)+2, column=2, padx=5, pady=3, sticky="e")
        
        # Create visualization
        chart_frame = tk.Frame(analysis_frame, bg="white")
        chart_frame.pack(fill="both", expand=True, pady=10)
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(8, 6))
        
        category_names = [category[0] for category in categories]
        category_amounts = [category[1] for category in categories]
        
        # Sort for better visualization
        y_pos = range(len(category_names))
        
        ax.barh(y_pos, category_amounts, align='center', color='#3498db')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(category_names)
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('Amount ($)')
        ax.set_title('Expenses by Category')
        
        # Add amount labels
        for i, v in enumerate(category_amounts):
            ax.text(v + 0.1, i, f'${v:.2f}', va='center')
        
        plt.tight_layout()
        
        bar_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        bar_canvas.draw()
        bar_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def generate_income_expense_comparison(self, month, year):
        # Create comparison frame
        comparison_frame = tk.Frame(self.report_frame, bg="white")
        comparison_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get month number
        month_num = list(calendar.month_name).index(month)
        
        # Get data for the last 6 months
        months_data = []
        
        for i in range(5, -1, -1):
            # Calculate month and year
            target_month = month_num - i
            target_year = int(year)
            
            if target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_name = calendar.month_name[target_month]
            start_date = f"{target_year}-{target_month:02d}-01"
            end_date = f"{target_year}-{target_month:02d}-{calendar.monthrange(target_year, target_month)[1]}"
            
            # Get income
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            income = cursor.fetchone()[0] or 0
            
            # Get expenses
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            expenses = cursor.fetchone()[0] or 0
            
            months_data.append((month_name, income, expenses, income - expenses))
        
        # Create table
        table_frame = tk.Frame(comparison_frame, bg="white")
        table_frame.pack(fill="x", pady=10)
        
        # Headers
        tk.Label(table_frame, text="Month", font=("Arial", 12, "bold"), bg="white", width=10, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(table_frame, text="Income", font=("Arial", 12, "bold"), bg="white", width=12, anchor="e").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(table_frame, text="Expenses", font=("Arial", 12, "bold"), bg="white", width=12, anchor="e").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(table_frame, text="Net", font=("Arial", 12, "bold"), bg="white", width=12, anchor="e").grid(row=0, column=3, padx=5, pady=5)
        
        # Add rows
        for i, (month_name, income, expenses, net) in enumerate(months_data):
            tk.Label(table_frame, text=month_name, font=("Arial", 11), bg="white", anchor="w").grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            tk.Label(table_frame, text=f"${income:.2f}", font=("Arial", 11), bg="white", anchor="e").grid(row=i+1, column=1, padx=5, pady=3, sticky="e")
            tk.Label(table_frame, text=f"${expenses:.2f}", font=("Arial", 11), bg="white", anchor="e").grid(row=i+1, column=2, padx=5, pady=3, sticky="e")
            
            # Color code net values
            if net >= 0:
                net_label = tk.Label(table_frame, text=f"${net:.2f}", font=("Arial", 11), bg="white", fg="#27ae60", anchor="e")
            else:
                net_label = tk.Label(table_frame, text=f"${net:.2f}", font=("Arial", 11), bg="white", fg="#e74c3c", anchor="e")
            net_label.grid(row=i+1, column=3, padx=5, pady=3, sticky="e")
        
        # Create chart
        chart_frame = tk.Frame(comparison_frame, bg="white")
        chart_frame.pack(fill="both", expand=True, pady=10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        months = [data[0] for data in months_data]
        incomes = [data[1] for data in months_data]
        expenses = [data[2] for data in months_data]
        nets = [data[3] for data in months_data]
        
        # Create bars
        x = np.arange(len(months))
        width = 0.35
        
        income_bars = ax.bar(x - width/2, incomes, width, label='Income', color='#2ecc71')
        expense_bars = ax.bar(x + width/2, expenses, width, label='Expenses', color='#e74c3c')
        
        # Add net line
        ax.plot(x, nets, 'o-', label='Net', color='#3498db', linewidth=2)
        
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        
        # Add labels and legend
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses')
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        ax.legend()
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def generate_annual_overview(self, year):
        # Create overview frame
        overview_frame = tk.Frame(self.report_frame, bg="white")
        overview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get yearly totals
        cursor = self.conn.cursor()
        
        # Total income
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND strftime('%Y', date) = ?",
            (year,)
        )
        total_income = cursor.fetchone()[0] or 0
        
        # Total expenses
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND strftime('%Y', date) = ?",
            (year,)
        )
        total_expenses = cursor.fetchone()[0] or 0
        
        # Net
        net = total_income - total_expenses
        
        # Create summary
        summary_frame = tk.Frame(overview_frame, bg="white")
        summary_frame.pack(fill="x", pady=10)
        
        tk.Label(summary_frame, text=f"Annual Income: ${total_income:.2f}", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        tk.Label(summary_frame, text=f"Annual Expenses: ${total_expenses:.2f}", font=("Arial", 12), bg="white").pack(anchor="w", pady=5)
        tk.Label(summary_frame, text=f"Annual Net: ${net:.2f}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=5)
        
        # Get monthly breakdown
        monthly_data = []
        
        for month_num in range(1, 13):
            month_name = calendar.month_name[month_num]
            start_date = f"{year}-{month_num:02d}-01"
            end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
            
            # Get income
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            income = cursor.fetchone()[0] or 0
            
            # Get expenses
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            expenses = cursor.fetchone()[0] or 0
            
            monthly_data.append((month_name, income, expenses, income - expenses))
        
        # Create chart
        charts_frame = tk.Frame(overview_frame, bg="white")
        charts_frame.pack(fill="both", expand=True, pady=10)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Monthly comparison chart
        months = [data[0] for data in monthly_data]
        incomes = [data[1] for data in monthly_data]
        expenses = [data[2] for data in monthly_data]
        nets = [data[3] for data in monthly_data]
        
        x = np.arange(len(months))
        width = 0.35
        
        ax1.bar(x - width/2, incomes, width, label='Income', color='#2ecc71')
        ax1.bar(x + width/2, expenses, width, label='Expenses', color='#e74c3c')
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Amount ($)')
        ax1.set_title(f'Monthly Income vs Expenses - {year}')
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, rotation=45)
        ax1.legend()
        
        # Get category breakdown for the year
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND strftime('%Y', date) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (year,)
        )
        categories = cursor.fetchall()
        
        if categories:
            category_names = [category[0] for category in categories]
            category_amounts = [category[1] for category in categories]
            
            # Create pie chart
            ax2.pie(category_amounts, labels=category_names, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            ax2.set_title(f'Expense Categories - {year}')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_report(self, report_type, month, year):
        try:
            # Get month number
            month_num = list(calendar.month_name).index(month)
            
            if report_type == "Monthly Summary" or report_type == "Category Analysis":
                # Export monthly transactions
                start_date = f"{year}-{month_num:02d}-01"
                end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
                
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT date, amount, type, category, payment_method, description FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date",
                    (start_date, end_date)
                )
                transactions = cursor.fetchall()
                
                # Create DataFrame
                df = pd.DataFrame(transactions, columns=["Date", "Amount", "Type", "Category", "Payment Method", "Description"])
                
                # Save to CSV
                filename = f"expense_report_{month}_{year}.csv"
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Export Successful", f"Report has been saved as {filename}")
                
            elif report_type == "Annual Overview":
                # Export annual transactions
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT date, amount, type, category, payment_method, description FROM transactions WHERE strftime('%Y', date) = ? ORDER BY date",
                    (year,)
                )
                transactions = cursor.fetchall()
                
                # Create DataFrame
                df = pd.DataFrame(transactions, columns=["Date", "Amount", "Type", "Category", "Payment Method", "Description"])
                
                # Save to CSV
                filename = f"annual_expense_report_{year}.csv"
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Export Successful", f"Report has been saved as {filename}")
                
            elif report_type == "Income vs Expenses":
                # Export monthly summaries
                monthly_data = []
                
                for m in range(1, 13):
                    m_name = calendar.month_name[m]
                    start_date = f"{year}-{m:02d}-01"
                    end_date = f"{year}-{m:02d}-{calendar.monthrange(int(year), m)[1]}"
                    
                    # Get income
                    cursor = self.conn.cursor()
                    cursor.execute(
                        "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
                        (start_date, end_date)
                    )
                    income = cursor.fetchone()[0] or 0
                    
                    # Get expenses
                    cursor.execute(
                        "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
                        (start_date, end_date)
                    )
                    expenses = cursor.fetchone()[0] or 0
                    
                    monthly_data.append((m_name, income, expenses, income - expenses))
                
                # Create DataFrame
                df = pd.DataFrame(monthly_data, columns=["Month", "Income", "Expenses", "Net"])
                
                # Save to CSV
                filename = f"income_vs_expenses_{year}.csv"
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Export Successful", f"Report has been saved as {filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")
    
    def load_summary(self):
        # Get current month and year
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        
        start_date = f"{current_year}-{current_month:02d}-01"
        end_date = f"{current_year}-{current_month:02d}-{calendar.monthrange(current_year, current_month)[1]}"
        
        # Get totals
        cursor = self.conn.cursor()
        
        # Income
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        income = cursor.fetchone()[0] or 0
        
        # Expenses
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        expenses = cursor.fetchone()[0] or 0
        
        # Balance
        balance = income - expenses
        
        # Update summary cards
        self.income_amount.config(text=f"${income:.2f}")
        self.expense_amount.config(text=f"${expenses:.2f}")
        self.balance_amount.config(text=f"${balance:.2f}")
        
        # Create category chart
        self.create_category_chart(start_date, end_date)
        
        # Create daily spending chart
        self.create_daily_chart(start_date, end_date)
        
        # Create trends chart
        self.create_trends_chart()
    
    def create_category_chart(self, start_date, end_date):
        # Clear previous chart
        for widget in self.category_chart_canvas.winfo_children():
            widget.destroy()
        
        # Get category data
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date)
        )
        categories = cursor.fetchall()
        
        if not categories:
            # No data
            tk.Label(self.category_chart_canvas, text="No data available", font=("Arial", 12), bg="white").pack(pady=50)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4))
        
        labels = [category[0] for category in categories]
        sizes = [category[1] for category in categories]
        
        # Create pie chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.category_chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_daily_chart(self, start_date, end_date):
        # Clear previous chart
        for widget in self.date_chart_canvas.winfo_children():
            widget.destroy()
        
        # Get daily data
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT strftime('%d', date) as day, SUM(amount) as total
            FROM transactions
            WHERE type = 'Expense' AND date BETWEEN ? AND ?
            GROUP BY day
            ORDER BY day
            """,
            (start_date, end_date)
        )
        daily_spending = cursor.fetchall()
        
        if not daily_spending:
            # No data
            tk.Label(self.date_chart_canvas, text="No data available", font=("Arial", 12), bg="white").pack(pady=50)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4))
        
        days = [int(day[0]) for day in daily_spending]
        amounts = [day[1] for day in daily_spending]
        
        # Create bar chart
        ax.bar(days, amounts, color='#3498db')
        ax.set_xlabel('Day of Month')
        ax.set_ylabel('Amount ($)')
        
        # Set x-axis ticks
        ax.set_xticks(range(1, 32, 5))
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.date_chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_trends_chart(self):
        # Clear previous chart
        for widget in self.trends_chart_canvas.winfo_children():
            widget.destroy()
        
        # Get data for the last 6 months
        current_date = datetime.datetime.now()
        months_data = []
        
        for i in range(5, -1, -1):
            # Calculate month and year
            target_date = current_date - datetime.timedelta(days=30 * i)
            target_month = target_date.month
            target_year = target_date.year
            
            month_name = calendar.month_name[target_month]
            start_date = f"{target_year}-{target_month:02d}-01"
            end_date = f"{target_year}-{target_month:02d}-{calendar.monthrange(target_year, target_month)[1]}"
            
            # Get income
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Income' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            income = cursor.fetchone()[0] or 0
            
            # Get expenses
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE type = 'Expense' AND date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            expenses = cursor.fetchone()[0] or 0
            
            months_data.append((month_name, income, expenses, income - expenses))
        
        if all(data[1] == 0 and data[2] == 0 for data in months_data):
            # No data
            tk.Label(self.trends_chart_canvas, text="No data available", font=("Arial", 12), bg="white").pack(pady=50)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))
        
        months = [data[0] for data in months_data]
        incomes = [data[1] for data in months_data]
        expenses = [data[2] for data in months_data]
        nets = [data[3] for data in months_data]
        
        # Create line chart
        ax.plot(months, incomes, 'o-', label='Income', color='#2ecc71', linewidth=2)
        ax.plot(months, expenses, 'o-', label='Expenses', color='#e74c3c', linewidth=2)
        ax.plot(months, nets, 'o-', label='Net', color='#3498db', linewidth=2)
        
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        
        # Add labels and legend
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('6-Month Financial Trend')
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.trends_chart_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def add_transaction(self):
        # Validate inputs
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        # Get values
        date = self.date_picker.get_date().strftime("%Y-%m-%d")
        transaction_type = self.selected_type.get()
        category = self.selected_category.get()
        payment_method = self.selected_payment.get()
        description = self.description_var.get()
        
        # Validate required fields
        if not category:
            messagebox.showerror("Invalid Input", "Please select a category")
            return
        
        if not payment_method and transaction_type == "Expense":
            messagebox.showerror("Invalid Input", "Please select a payment method")
            return
        
        # Add to database
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (date, amount, type, category, payment_method, description) VALUES (?, ?, ?, ?, ?, ?)",
            (date, amount, transaction_type, category, payment_method, description)
        )
        self.conn.commit()
        
        # Clear form
        self.clear_form()
        
        # Refresh data
        self.load_transactions()
        self.load_summary()
        
        messagebox.showinfo("Success", "Transaction added successfully!")
    
    def update_transaction(self):
        if not self.transaction_id:
            return
        
        # Validate inputs
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        # Get values
        date = self.date_picker.get_date().strftime("%Y-%m-%d")
        transaction_type = self.selected_type.get()
        category = self.selected_category.get()
        payment_method = self.selected_payment.get()
        description = self.description_var.get()
        
        # Update database
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE transactions 
            SET date = ?, amount = ?, type = ?, category = ?, payment_method = ?, description = ? 
            WHERE id = ?
            """,
            (date, amount, transaction_type, category, payment_method, description, self.transaction_id)
        )
        self.conn.commit()
        
        # Clear form
        self.cancel_edit()
        
        # Refresh data
        self.load_transactions()
        self.load_summary()
        
        messagebox.showinfo("Success", "Transaction updated successfully!")
    
    def delete_transaction(self):
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            return
        
        # Get transaction ID
        transaction_id = self.transaction_tree.item(selected_item, "values")[0]
        
        # Delete from database
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
        
        # Clear form if editing
        if self.transaction_id == transaction_id:
            self.cancel_edit()
        
        # Refresh data
        self.load_transactions()
        self.load_summary()
        
        messagebox.showinfo("Success", "Transaction deleted successfully!")
    
    def edit_transaction(self):
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            return
        
        # Get transaction data
        values = self.transaction_tree.item(selected_item, "values")
        self.transaction_id = values[0]
        
        # Set form values
        date_parts = values[1].split("-")
        self.date_picker.set_date(datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
        self.amount_var.set(values[2])
        self.selected_type.set(values[3])
        self.update_categories()
        self.selected_category.set(values[4])
        self.selected_payment.set(values[5])
        self.description_var.set(values[6])
        
        # Update buttons
        self.add_button.config(state="disabled")
        self.update_button.config(state="normal")
        self.cancel_button.config(state="normal")
    
    def cancel_edit(self):
        # Clear form
        self.clear_form()
        
        # Reset buttons
        self.add_button.config(state="normal")
        self.update_button.config(state="disabled")
        self.cancel_button.config(state="disabled")
        
        # Clear selection
        self.transaction_id = None
        for item in self.transaction_tree.selection():
            self.transaction_tree.selection_remove(item)
    
    def clear_form(self):
        self.date_picker.set_date(datetime.datetime.now())
        self.amount_var.set("")
        self.selected_type.set("Expense")
        self.update_categories()
        self.selected_payment.set("")
        self.description_var.set("")
    
    def select_transaction(self, event):
        selected_item = self.transaction_tree.selection()
        if not selected_item:
            return
        
        # Check if selection changed
        if self.transaction_id != self.transaction_tree.item(selected_item, "values")[0]:
            self.edit_transaction()
    
    def load_transactions(self):
        # Clear existing data
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Get filter values
        month = self.filter_month.get()
        year = self.filter_year.get()
        
        # Convert month name to number
        month_num = list(calendar.month_name).index(month)
        
        # Date range
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
        
        # Get transactions
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, date, amount, type, category, payment_method, description FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC",
            (start_date, end_date)
        )
        transactions = cursor.fetchall()
        
        # Add to treeview
        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=transaction)
    
    def search_transactions(self):
        search_term = self.search_var.get().lower()
        if not search_term:
            self.load_transactions()
            return
        
        # Clear existing data
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Get filter values
        month = self.filter_month.get()
        year = self.filter_year.get()
        
        # Convert month name to number
        month_num = list(calendar.month_name).index(month)
        
        # Date range
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{calendar.monthrange(int(year), month_num)[1]}"
        
        # Search in transactions
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, date, amount, type, category, payment_method, description 
            FROM transactions 
            WHERE date BETWEEN ? AND ? AND (LOWER(category) LIKE ? OR LOWER(payment_method) LIKE ? OR LOWER(description) LIKE ? OR LOWER(type) LIKE ?)
            ORDER BY date DESC
            """,
            (start_date, end_date, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        )
        transactions = cursor.fetchall()
        
        # Add to treeview
        for transaction in transactions:
            self.transaction_tree.insert("", "end", values=transaction)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()