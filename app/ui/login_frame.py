import tkinter as tk
from tkinter import ttk, messagebox

from app.auth import register_user, login_user


class LoginFrame(ttk.Frame):

    def __init__(self, parent, login_callback):
        super().__init__(parent)
        self.parent = parent
        self.login_callback = login_callback

        # grid
        self.grid_columnconfigure(0, weight=1)

        # login container
        self.create_widgets()

    def create_widgets(self):
        # Frame for login form
        login_frame = ttk.LabelFrame(self, text="Login")
        login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # grid
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)

        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=5,
                                                                              sticky="ew")

        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        # Register section
        register_frame = ttk.LabelFrame(self, text="Register")
        register_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # grid
        register_frame.grid_columnconfigure(0, weight=1)
        register_frame.grid_columnconfigure(1, weight=1)

        # Username
        ttk.Label(register_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.reg_username_var = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_username_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Password
        ttk.Label(register_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.reg_password_var = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_password_var, show="*").grid(row=1, column=1, padx=5, pady=5,
                                                                                     sticky="ew")

        # Confirm Password
        ttk.Label(register_frame, text="Confirm Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.reg_confirm_password_var = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_confirm_password_var, show="*").grid(row=2, column=1, padx=5,
                                                                                             pady=5, sticky="ew")

        # Register button
        register_button = ttk.Button(register_frame, text="Register", command=self.register)
        register_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # title
        title_label = ttk.Label(self, text="Budget Planner", font=("Arial", 18, "bold"))
        title_label.grid(row=2, column=0, padx=20, pady=20)

        desc_label = ttk.Label(self, text="Track your finances, set goals, and plan your budget.")
        desc_label.grid(row=3, column=0, padx=20, pady=5)

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # Validate inputs
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return

        # Authenticate user
        success, result = login_user(username, password)

        if success:
            self.login_callback(result)
        else:
            messagebox.showerror("Login Failed", result)

    def register(self):
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        confirm_password = self.reg_confirm_password_var.get().strip()

        # Validate inputs
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        # Register user
        success, message = register_user(username, password)

        if success:
            messagebox.showinfo("Success", message)
            self.reg_username_var.set("")
            self.reg_password_var.set("")
            self.reg_confirm_password_var.set("")
        else:
            messagebox.showerror("Registration Failed", message)