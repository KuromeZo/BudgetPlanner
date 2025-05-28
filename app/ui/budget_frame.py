import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from app.budget import (
    get_categories, add_category, add_transaction, get_transactions,
    add_goal, update_goal, get_goals
)
from app.utils import (
    format_currency, validate_amount, validate_date,
    create_expense_pie_chart, create_income_expense_bar_chart
)


class BudgetFrame(ttk.Frame):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user

        #  the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

        self.load_data()

    def create_widgets(self):
        # Left frame - transactions
        left_frame = ttk.LabelFrame(self, text="Transactions")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # Transaction form
        form_frame = ttk.Frame(left_frame)
        form_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Type
        ttk.Label(form_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.transaction_type_var = tk.StringVar(value="Expense")
        type_combobox = ttk.Combobox(form_frame, textvariable=self.transaction_type_var, values=["Income", "Expense"],
                                     state="readonly")
        type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        type_combobox.bind("<<ComboboxSelected>>", self.on_transaction_type_change)

        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Category
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Category Button
        add_category_button = ttk.Button(form_frame, text="Add Category", command=self.show_add_category_dialog)
        add_category_button.grid(row=2, column=2, padx=5, pady=5)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Date
        ttk.Label(form_frame, text="Date:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Year
        self.year_var = tk.IntVar(value=datetime.datetime.now().year)
        ttk.Spinbox(date_frame, from_=2000, to=2100, textvariable=self.year_var, width=5).pack(side=tk.LEFT, padx=2)

        # Month
        self.month_var = tk.IntVar(value=datetime.datetime.now().month)
        ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.month_var, width=3).pack(side=tk.LEFT, padx=2)

        # Day
        self.day_var = tk.IntVar(value=datetime.datetime.now().day)
        ttk.Spinbox(date_frame, from_=1, to=31, textvariable=self.day_var, width=3).pack(side=tk.LEFT, padx=2)

        # Add button
        add_button = ttk.Button(form_frame, text="Add Transaction", command=self.add_transaction)
        add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

        # Transaction list
        ttk.Label(left_frame, text="Recent Transactions:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")

        # Treeview
        self.transaction_tree = ttk.Treeview(left_frame, columns=("date", "type", "category", "amount", "description"))

        # columns
        self.transaction_tree.heading("#0", text="ID")
        self.transaction_tree.heading("date", text="Date")
        self.transaction_tree.heading("type", text="Type")
        self.transaction_tree.heading("category", text="Category")
        self.transaction_tree.heading("amount", text="Amount")
        self.transaction_tree.heading("description", text="Description")

        self.transaction_tree.column("#0", width=50)
        self.transaction_tree.column("date", width=100)
        self.transaction_tree.column("type", width=80)
        self.transaction_tree.column("category", width=120)
        self.transaction_tree.column("amount", width=100)
        self.transaction_tree.column("description", width=150)

        self.transaction_tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.transaction_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)

        # Right frame - goals and charts
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # grid
        right_frame.grid_columnconfigure(0, weight=1)

        # Goals frame
        goals_frame = ttk.LabelFrame(right_frame, text="Financial Goals")
        goals_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Goals form
        goal_form_frame = ttk.Frame(goals_frame)
        goal_form_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Goal name
        ttk.Label(goal_form_frame, text="Goal:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.goal_name_var = tk.StringVar()
        ttk.Entry(goal_form_frame, textvariable=self.goal_name_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Target amount
        ttk.Label(goal_form_frame, text="Target Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.goal_target_var = tk.StringVar()
        ttk.Entry(goal_form_frame, textvariable=self.goal_target_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Add goal button
        add_goal_button = ttk.Button(goal_form_frame, text="Add Goal", command=self.add_goal)
        add_goal_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        # Goals list
        ttk.Label(goals_frame, text="Your Goals:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Goals treeview
        self.goals_tree = ttk.Treeview(goals_frame, columns=("name", "current", "target", "progress"))

        # columns
        self.goals_tree.heading("#0", text="ID")
        self.goals_tree.heading("name", text="Goal")
        self.goals_tree.heading("current", text="Current")
        self.goals_tree.heading("target", text="Target")
        self.goals_tree.heading("progress", text="Progress")

        self.goals_tree.column("#0", width=50)
        self.goals_tree.column("name", width=150)
        self.goals_tree.column("current", width=100)
        self.goals_tree.column("target", width=100)
        self.goals_tree.column("progress", width=100)

        self.goals_tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Goal progress button
        update_goal_button = ttk.Button(goals_frame, text="Update Goal Progress", command=self.show_update_goal_dialog)
        update_goal_button.grid(row=3, column=0, padx=5, pady=10)

        # Charts frame
        charts_frame = ttk.LabelFrame(right_frame, text="Charts")
        charts_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Stats label
        self.stats_text = tk.Text(charts_frame, height=4, width=40, wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.stats_text.config(state=tk.DISABLED)

        # Refresh button
        refresh_button = ttk.Button(charts_frame, text="Refresh Data", command=self.load_data)
        refresh_button.grid(row=1, column=0, padx=5, pady=5)

    def load_data(self):
        self.load_categories()

        self.load_transactions()

        self.load_goals()

        self.update_stats()

    def load_categories(self):
        # Get income categories
        income_categories = get_categories(self.user.id, is_income=True)
        self.income_categories = {cat.name: cat.id for cat in income_categories}

        # Get expense categories
        expense_categories = get_categories(self.user.id, is_income=False)
        self.expense_categories = {cat.name: cat.id for cat in expense_categories}

        # Update combobox values
        self.update_category_combobox()

    def update_category_combobox(self):
        transaction_type = self.transaction_type_var.get()

        if transaction_type == "Income":
            self.category_combobox['values'] = list(self.income_categories.keys())
        else:
            self.category_combobox['values'] = list(self.expense_categories.keys())

        # Reset selection
        self.category_var.set("")

    def on_transaction_type_change(self, event=None):
        self.update_category_combobox()

    def show_add_category_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Category")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Category name
        ttk.Label(dialog, text="Category Name:").pack(padx=10, pady=5, anchor="w")
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(padx=10, pady=5, fill="x")

        # Category type
        ttk.Label(dialog, text="Category Type:").pack(padx=10, pady=5, anchor="w")
        type_var = tk.StringVar(value="Expense")
        ttk.Radiobutton(dialog, text="Income", variable=type_var, value="Income").pack(padx=10, pady=2, anchor="w")
        ttk.Radiobutton(dialog, text="Expense", variable=type_var, value="Expense").pack(padx=10, pady=2, anchor="w")

        # Add button
        def submit():
            # Get values
            name = name_var.get().strip()
            is_income = type_var.get() == "Income"

            # Validate
            if not name:
                messagebox.showerror("Error", "Category name is required", parent=dialog)
                return

            # Add category
            success, message = add_category(self.user.id, name, is_income)

            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                dialog.destroy()

                # Reload categories
                self.load_categories()
            else:
                messagebox.showerror("Error", message, parent=dialog)

        ttk.Button(dialog, text="Add Category", command=submit).pack(padx=10, pady=10)

        # Cancel button
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(padx=10, pady=5)

    def add_transaction(self):
        # Get values
        transaction_type = self.transaction_type_var.get()
        amount_str = self.amount_var.get().strip()
        category_name = self.category_var.get()
        description = self.description_var.get().strip()

        # Validate
        if not amount_str:
            messagebox.showerror("Error", "Amount is required")
            return

        if not category_name:
            messagebox.showerror("Error", "Category is required")
            return

        # Validate amount
        valid, amount = validate_amount(amount_str)
        if not valid:
            messagebox.showerror("Error", amount)
            return

        # Get category ID
        if transaction_type == "Income":
            category_id = self.income_categories.get(category_name)
        else:  # Expense
            category_id = self.expense_categories.get(category_name)

        if not category_id:
            messagebox.showerror("Error", "Invalid category")
            return

        # Validate date
        year = self.year_var.get()
        month = self.month_var.get()
        day = self.day_var.get()

        valid, date = validate_date(year, month, day)
        if not valid:
            messagebox.showerror("Error", date)
            return

        # original amount (always positive)
        original_amount = abs(amount)

        # Add transaction with positive amount - the category determines if it's income or expense
        success, message = add_transaction(
            self.user.id, original_amount, description, category_id, date
        )

        if success:
            messagebox.showinfo("Success", message)

            # Clear form
            self.amount_var.set("")
            self.description_var.set("")

            # Force reload of all data
            print(f"Transaction added successfully. Reloading data...")
            self.load_data()  # Use load_data to reload everything
        else:
            messagebox.showerror("Error", message)

    def load_transactions(self):
        print(f"Loading transactions for user {self.user.id}...")

        # Clear treeview
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        # Get transactions (last 30 days)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)

        print(f"Date range: {start_date} to {end_date}")

        transactions = get_transactions(self.user.id, start_date, end_date)

        print(f"Found {len(transactions)} transactions")

        # Add to treeview
        for transaction in transactions:
            if transaction.category_is_income:
                type_str = "Income"
            else:
                type_str = "Expense"

            print(
                f"Adding transaction: {transaction.id}, {type_str}, {transaction.category_name}, {transaction.amount}")

            self.transaction_tree.insert(
                "", "end", text=str(transaction.id),
                values=(
                    transaction.date.strftime("%Y-%m-%d"),
                    type_str,
                    transaction.category_name,
                    format_currency(abs(transaction.amount)),
                    transaction.description or ""
                )
            )

        print(f"Transactions loaded successfully")

    def add_goal(self):
        # Get values
        name = self.goal_name_var.get().strip()
        target_str = self.goal_target_var.get().strip()

        # Validate
        if not name:
            messagebox.showerror("Error", "Goal name is required")
            return

        if not target_str:
            messagebox.showerror("Error", "Target amount is required")
            return

        # Validate target amount
        valid, target = validate_amount(target_str)
        if not valid:
            messagebox.showerror("Error", target)
            return

        # Add goal
        success, message = add_goal(self.user.id, name, target)

        if success:
            messagebox.showinfo("Success", message)

            # Clear form
            self.goal_name_var.set("")
            self.goal_target_var.set("")

            # Reload goals
            self.load_goals()
        else:
            messagebox.showerror("Error", message)

    def load_goals(self):
        # Clear treeview
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)

        # Get goals
        goals = get_goals(self.user.id)

        # Add to treeview
        for goal in goals:
            # Calculate progress
            if goal.target_amount > 0:
                progress = (goal.current_amount / goal.target_amount) * 100
            else:
                progress = 0

            # Add to treeview
            self.goals_tree.insert(
                "", "end", text=str(goal.id),
                values=(
                    goal.name,
                    format_currency(goal.current_amount),
                    format_currency(goal.target_amount),
                    f"{progress:.1f}%"
                )
            )

    def show_update_goal_dialog(self):
        # Get selected goal
        selection = self.goals_tree.selection()

        if not selection:
            messagebox.showerror("Error", "Please select a goal to update")
            return

        # Get goal ID
        goal_id = int(self.goals_tree.item(selection[0], "text"))

        # Get goal data
        goal_name = self.goals_tree.item(selection[0], "values")[0]

        dialog = tk.Toplevel(self)
        dialog.title(f"Update Goal: {goal_name}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Current amount
        ttk.Label(dialog, text="Current Amount:").pack(padx=10, pady=5, anchor="w")
        current_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=current_var).pack(padx=10, pady=5, fill="x")

        # Update button
        def submit():
            # Get values
            current_str = current_var.get().strip()

            # Validate
            if not current_str:
                messagebox.showerror("Error", "Current amount is required", parent=dialog)
                return

            # Validate amount
            valid, current = validate_amount(current_str)
            if not valid:
                messagebox.showerror("Error", current, parent=dialog)
                return

            # Update goal
            success, message = update_goal(goal_id, self.user.id, current_amount=current)

            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                dialog.destroy()

                # Reload goals
                self.load_goals()
            else:
                messagebox.showerror("Error", message, parent=dialog)

        ttk.Button(dialog, text="Update Goal", command=submit).pack(padx=10, pady=10)

        # Cancel button
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(padx=10, pady=5)

    def update_stats(self):
        # Get current month and year
        now = datetime.datetime.now()
        current_month = now.month
        current_year = now.year

        # Get monthly summary
        from app.budget import get_monthly_summary
        summary = get_monthly_summary(self.user.id, current_year, current_month)

        # Update text widget
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        import calendar
        month_name = calendar.month_name[current_month]

        stats_text = f"{month_name} {current_year} Summary:\n"
        stats_text += f"Income: {format_currency(summary['total_income'])}\n"
        stats_text += f"Expenses: {format_currency(summary['total_expenses'])}\n"
        stats_text += f"Net: {format_currency(summary['net'])}\n"

        print(
            f"Stats updated: Income={summary['total_income']}, Expenses={summary['total_expenses']}, Net={summary['net']}")

        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)