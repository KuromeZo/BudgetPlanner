import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import io
import datetime
import calendar

from app.reports import BudgetReport, generate_documentation
from app.utils import get_month_year_range


class ReportFrame(ttk.Frame):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user

        # grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Report controls
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Report type
        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.report_type_var = tk.StringVar(value="Monthly")
        type_combobox = ttk.Combobox(controls_frame, textvariable=self.report_type_var, values=["Monthly", "Yearly"],
                                     state="readonly")
        type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        type_combobox.bind("<<ComboboxSelected>>", self.on_report_type_change)

        months, years = get_month_year_range()

        # Month
        ttk.Label(controls_frame, text="Month:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.month_var = tk.IntVar(value=datetime.datetime.now().month)
        self.month_combobox = ttk.Combobox(controls_frame, textvariable=self.month_var, values=[str(m) for m in months],
                                           state="readonly")
        self.month_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Year
        ttk.Label(controls_frame, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.year_var = tk.IntVar(value=datetime.datetime.now().year)
        self.year_combobox = ttk.Combobox(controls_frame, textvariable=self.year_var, values=[str(y) for y in years],
                                          state="readonly")
        self.year_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Generate button
        generate_button = ttk.Button(controls_frame, text="Generate Report", command=self.generate_report)
        generate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Export button
        export_button = ttk.Button(controls_frame, text="Export to PDF", command=self.export_report)
        export_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Documentation button
        doc_button = ttk.Button(controls_frame, text="Generate Documentation", command=self.generate_doc)
        doc_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Report display
        report_frame = ttk.LabelFrame(self, text="Report Preview")
        report_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # report grid
        report_frame.grid_columnconfigure(0, weight=1)
        report_frame.grid_rowconfigure(1, weight=1)

        # Report title
        self.report_title_var = tk.StringVar(value="")
        report_title = ttk.Label(report_frame, textvariable=self.report_title_var, font=("Arial", 14, "bold"))
        report_title.grid(row=0, column=0, padx=5, pady=5)

        # Report content (using a notebook for tabs)
        self.report_notebook = ttk.Notebook(report_frame)
        self.report_notebook.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Summary tab
        self.summary_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.summary_frame, text="Summary")

        # Transactions tab
        self.transactions_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.transactions_frame, text="Transactions")

        # Charts tab
        self.charts_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.charts_frame, text="Charts")

        # Goals tab
        self.goals_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(self.goals_frame, text="Goals")

        # Initialize report data
        self.report_data = None
        self.chart_image = None

    def on_report_type_change(self, event=None):
        # Enable/disable month combobox based on report type
        if self.report_type_var.get() == "Monthly":
            self.month_combobox.config(state="readonly")
        else:
            self.month_combobox.config(state="disabled")

    def generate_report(self):
        report = BudgetReport(self.user.id)

        report_type = self.report_type_var.get()

        year = self.year_var.get()
        month = self.month_var.get()

        try:
            # Generate report based on type
            if report_type == "Monthly":
                self.report_data = report.generate_monthly_report(year, month)
                month_name = calendar.month_name[month]
                self.report_title_var.set(f"Monthly Report - {month_name} {year}")
            else:  # Yearly
                self.report_data = report.generate_yearly_report(year)
                self.report_title_var.set(f"Yearly Report - {year}")

            # Update report display
            self.update_report_display()

            # Show the report notebook
            self.report_notebook.select(0)  # Show summary tab

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_report_display(self):
        if not self.report_data:
            return

        # Clear existing content
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        for widget in self.goals_frame.winfo_children():
            widget.destroy()

        # Update summary tab
        self.update_summary_tab()

        # Update transactions tab (only for monthly reports)
        if 'transactions' in self.report_data:
            self.update_transactions_tab()

        # Update charts tab
        self.update_charts_tab()

        # Update goals tab
        self.update_goals_tab()

    def update_summary_tab(self):
        summary_content = ttk.Frame(self.summary_frame)
        summary_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        if 'summary' in self.report_data:  # Monthly report
            # Income
            ttk.Label(summary_content, text="Total Income:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5,
                                                                                              pady=5, sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['summary']['total_income']:.2f}",
                      font=("Arial", 12)).grid(row=0, column=1, padx=5, pady=5, sticky="w")

            # Expenses
            ttk.Label(summary_content, text="Total Expenses:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5,
                                                                                                pady=5, sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['summary']['total_expenses']:.2f}",
                      font=("Arial", 12)).grid(row=1, column=1, padx=5, pady=5, sticky="w")

            # Net
            ttk.Label(summary_content, text="Net:", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=5, pady=5,
                                                                                     sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['summary']['net']:.2f}", font=("Arial", 12)).grid(
                row=2, column=1, padx=5, pady=5, sticky="w")

        else:  # Yearly report
            # Yearly income
            ttk.Label(summary_content, text="Yearly Income:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5,
                                                                                               pady=5, sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['yearly_income']:.2f}", font=("Arial", 12)).grid(row=0,
                                                                                                                  column=1,
                                                                                                                  padx=5,
                                                                                                                  pady=5,
                                                                                                                  sticky="w")

            # Yearly expenses
            ttk.Label(summary_content, text="Yearly Expenses:", font=("Arial", 12, "bold")).grid(row=1, column=0,
                                                                                                 padx=5, pady=5,
                                                                                                 sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['yearly_expenses']:.2f}", font=("Arial", 12)).grid(
                row=1, column=1, padx=5, pady=5, sticky="w")

            # Yearly net
            ttk.Label(summary_content, text="Yearly Net:", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=5,
                                                                                            pady=5, sticky="w")
            ttk.Label(summary_content, text=f"${self.report_data['yearly_net']:.2f}", font=("Arial", 12)).grid(row=2,
                                                                                                               column=1,
                                                                                                               padx=5,
                                                                                                               pady=5,
                                                                                                               sticky="w")

            # Monthly breakdown
            ttk.Label(summary_content, text="Monthly Breakdown:", font=("Arial", 12, "bold")).grid(row=3, column=0,
                                                                                                   columnspan=2, padx=5,
                                                                                                   pady=10, sticky="w")

            # Create a treeview for monthly data
            tree = ttk.Treeview(summary_content, columns=("month", "income", "expenses", "net"))
            tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

            # columns
            tree.heading("#0", text="")
            tree.heading("month", text="Month")
            tree.heading("income", text="Income")
            tree.heading("expenses", text="Expenses")
            tree.heading("net", text="Net")

            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("month", width=100)
            tree.column("income", width=100)
            tree.column("expenses", width=100)
            tree.column("net", width=100)

            # Add data
            for idx, month_data in enumerate(self.report_data['monthly_data']):
                tree.insert(
                    "", "end",
                    values=(
                        month_data['month'],
                        f"${month_data['income']:.2f}",
                        f"${month_data['expenses']:.2f}",
                        f"${month_data['net']:.2f}"
                    )
                )

    def update_transactions_tab(self):
        # frame for transactions
        transactions_content = ttk.Frame(self.transactions_frame)
        transactions_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # treeview for transactions
        tree = ttk.Treeview(transactions_content, columns=("date", "category", "amount", "description"))
        tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # columns
        tree.heading("#0", text="ID")
        tree.heading("date", text="Date")
        tree.heading("category", text="Category")
        tree.heading("amount", text="Amount")
        tree.heading("description", text="Description")

        tree.column("#0", width=50)
        tree.column("date", width=100)
        tree.column("category", width=150)
        tree.column("amount", width=100)
        tree.column("description", width=200)

        # Add data
        for transaction in self.report_data['transactions']:
            # Determine if it's income or expense based on category type
            amount_display = f"${abs(transaction.amount):.2f}"
            if transaction.category_is_income:
                amount_display += " (Income)"
            else:
                amount_display += " (Expense)"

            tree.insert(
                "", "end", text=str(transaction.id),
                values=(
                    transaction.date.strftime("%Y-%m-%d"),
                    transaction.category_name,
                    amount_display,
                    transaction.description or ""
                )
            )

    def update_charts_tab(self):
        # frame for charts
        charts_content = ttk.Frame(self.charts_frame)
        charts_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Generate chart
        report = BudgetReport(self.user.id)
        chart_data = report.generate_charts(self.report_data)

        # Convert bytes to image
        img = Image.open(io.BytesIO(chart_data))
        self.chart_image = ImageTk.PhotoImage(img)

        # Display image
        chart_label = ttk.Label(charts_content, image=self.chart_image)
        chart_label.pack(padx=5, pady=5)

    def update_goals_tab(self):
        goals_content = ttk.Frame(self.goals_frame)
        goals_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # treeview for goals
        tree = ttk.Treeview(goals_content, columns=("name", "current", "target", "progress"))
        tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # columns
        tree.heading("#0", text="ID")
        tree.heading("name", text="Goal")
        tree.heading("current", text="Current")
        tree.heading("target", text="Target")
        tree.heading("progress", text="Progress")

        tree.column("#0", width=50)
        tree.column("name", width=200)
        tree.column("current", width=100)
        tree.column("target", width=100)
        tree.column("progress", width=100)

        for goal in self.report_data['goals']:
            progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
            tree.insert(
                "", "end", text=str(goal.id),
                values=(
                    goal.name,
                    f"${goal.current_amount:.2f}",
                    f"${goal.target_amount:.2f}",
                    f"{progress:.1f}%"
                )
            )

    def export_report(self):
        if not self.report_data:
            messagebox.showerror("Error", "Please generate a report first")
            return

        # Ask for file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Report As"
        )

        if not file_path:
            return

        try:
            # Create a BudgetReport instance
            report = BudgetReport(self.user.id)

            # Export to PDF
            success = report.export_to_pdf(self.report_data, file_path)

            if success:
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export report")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def generate_doc(self):
        try:
            doc_path = generate_documentation()

            messagebox.showinfo("Success", f"Documentation generated at {doc_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")