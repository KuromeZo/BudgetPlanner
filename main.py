import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add the current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.database import init_db
from app.ui.login_frame import LoginFrame
from app.ui.main_frame import MainFrame


class BudgetPlannerApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Budget Planner")
        self.geometry("900x600")
        self.resizable(True, True)

        # Initialize database
        init_db()

        # grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}

        # Initialize the user session
        self.current_user = None

        # Show login frame
        self.show_login_frame()

    def show_login_frame(self):
        if 'login' in self.frames:
            self.frames['login'].destroy()

        self.frames['login'] = LoginFrame(self, self.login_callback)
        self.frames['login'].grid(row=0, column=0, sticky="nsew")

    def show_main_frame(self):
        if 'main' in self.frames:
            self.frames['main'].destroy()

        self.frames['main'] = MainFrame(self, self.current_user, self.logout_callback)
        self.frames['main'].grid(row=0, column=0, sticky="nsew")

    def login_callback(self, user):
        # Callback function for successful login
        self.current_user = user
        self.show_main_frame()

    def logout_callback(self):
        # Callback function for logout
        self.current_user = None
        self.show_login_frame()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()


if __name__ == "__main__":
    app = BudgetPlannerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()