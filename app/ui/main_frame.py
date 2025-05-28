import tkinter as tk
from tkinter import ttk

from app.ui.budget_frame import BudgetFrame
from app.ui.report_frame import ReportFrame


class MainFrame(ttk.Frame):

    def __init__(self, parent, user, logout_callback):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.logout_callback = logout_callback

        # grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()

        self.show_frame("budget")

    def create_widgets(self):
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # header grid
        header_frame.grid_columnconfigure(1, weight=1)

        # Welcome
        welcome_label = ttk.Label(header_frame, text=f"Welcome, {self.user.username}!", font=("Arial", 12, "bold"))
        welcome_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Spacer
        spacer = ttk.Frame(header_frame)
        spacer.grid(row=0, column=1, sticky="ew")

        # Logout button
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout_callback)
        logout_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Tab control
        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Budget
        self.budget_frame = BudgetFrame(self.tab_control, self.user)
        self.tab_control.add(self.budget_frame, text="Budget")

        # Reports
        self.report_frame = ReportFrame(self.tab_control, self.user)
        self.tab_control.add(self.report_frame, text="Reports")

        # Footer
        footer_frame = ttk.Frame(self)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(footer_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def show_frame(self, frame_name):
        if frame_name == "budget":
            self.tab_control.select(0)
        elif frame_name == "reports":
            self.tab_control.select(1)

    def set_status(self, message):
        self.status_var.set(message)