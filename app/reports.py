import os
import datetime
import calendar
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

from app.budget import get_transactions, get_monthly_summary, get_categories, get_goals


class BudgetReport:
    def __init__(self, user_id):
        self.user_id = user_id

    def generate_monthly_report(self, year, month):
        month_name = calendar.month_name[month]

        start_date = datetime.datetime(year, month, 1)
        # Get last day of the month
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime.datetime(year, month, last_day, 23, 59, 59)

        transactions = get_transactions(self.user_id, start_date, end_date)

        summary = get_monthly_summary(self.user_id, year, month)

        income_categories = get_categories(self.user_id, is_income=True)
        expense_categories = get_categories(self.user_id, is_income=False)

        goals = get_goals(self.user_id)

        return {
            'title': f"Monthly Budget Report - {month_name} {year}",
            'period': f"{month_name} {year}",
            'transactions': transactions,
            'summary': summary,
            'income_categories': income_categories,
            'expense_categories': expense_categories,
            'goals': goals
        }

    def generate_yearly_report(self, year):
        # Initialize monthly data
        monthly_data = []

        # Get data for each month
        for month in range(1, 13):
            summary = get_monthly_summary(self.user_id, year, month)
            monthly_data.append({
                'month': calendar.month_name[month],
                'income': summary['total_income'],
                'expenses': summary['total_expenses'],
                'net': summary['net']
            })

        # Get yearly totals
        yearly_income = sum(month['income'] for month in monthly_data)
        yearly_expenses = sum(month['expenses'] for month in monthly_data)
        yearly_net = yearly_income - yearly_expenses

        goals = get_goals(self.user_id)

        return {
            'title': f"Yearly Budget Report - {year}",
            'period': str(year),
            'monthly_data': monthly_data,
            'yearly_income': yearly_income,
            'yearly_expenses': yearly_expenses,
            'yearly_net': yearly_net,
            'goals': goals
        }

    def export_to_pdf(self, report_data, output_path):
        try:
            # Create PDF object
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", size=12)

            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=report_data['title'], ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"Period: {report_data['period']}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="Summary", ln=True)
            pdf.ln(5)

            if 'summary' in report_data:  # Monthly report
                pdf.set_font("Arial", size=12)
                pdf.cell(100, 10, txt=f"Total Income: ${report_data['summary']['total_income']:.2f}", ln=True)
                pdf.cell(100, 10, txt=f"Total Expenses: ${report_data['summary']['total_expenses']:.2f}", ln=True)
                pdf.cell(100, 10, txt=f"Net: ${report_data['summary']['net']:.2f}", ln=True)
                pdf.ln(5)

                # Transactions
                if report_data['transactions']:
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(200, 10, txt="Transactions", ln=True)
                    pdf.ln(5)

                    # Table header
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(40, 10, txt="Date", border=1)
                    pdf.cell(60, 10, txt="Description", border=1)
                    pdf.cell(50, 10, txt="Category", border=1)
                    pdf.cell(40, 10, txt="Amount", border=1, ln=True)

                    # Table content
                    pdf.set_font("Arial", size=10)
                    for transaction in report_data['transactions'][:20]:  # Limit to 20 transactions
                        pdf.cell(40, 10, txt=transaction.date.strftime('%Y-%m-%d'), border=1)
                        pdf.cell(60, 10, txt=transaction.description or "", border=1)
                        pdf.cell(50, 10, txt=transaction.category_name, border=1)
                        pdf.cell(40, 10, txt=f"${transaction.amount:.2f}", border=1, ln=True)

                    # Add note if there are more transactions
                    if len(report_data['transactions']) > 20:
                        pdf.cell(200, 10, txt="(Showing first 20 transactions)", ln=True, align='C')
                    pdf.ln(10)
            else:  # Yearly report
                pdf.set_font("Arial", size=12)
                pdf.cell(100, 10, txt=f"Yearly Income: ${report_data['yearly_income']:.2f}", ln=True)
                pdf.cell(100, 10, txt=f"Yearly Expenses: ${report_data['yearly_expenses']:.2f}", ln=True)
                pdf.cell(100, 10, txt=f"Yearly Net: ${report_data['yearly_net']:.2f}", ln=True)
                pdf.ln(5)

                # Monthly breakdown
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="Monthly Breakdown", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", 'B', 12)
                pdf.cell(50, 10, txt="Month", border=1)
                pdf.cell(50, 10, txt="Income", border=1)
                pdf.cell(50, 10, txt="Expenses", border=1)
                pdf.cell(40, 10, txt="Net", border=1, ln=True)

                pdf.set_font("Arial", size=10)
                for month_data in report_data['monthly_data']:
                    pdf.cell(50, 10, txt=month_data['month'], border=1)
                    pdf.cell(50, 10, txt=f"${month_data['income']:.2f}", border=1)
                    pdf.cell(50, 10, txt=f"${month_data['expenses']:.2f}", border=1)
                    pdf.cell(40, 10, txt=f"${month_data['net']:.2f}", border=1, ln=True)
                pdf.ln(10)

            if report_data['goals']:
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="Financial Goals", ln=True)
                pdf.ln(5)

                pdf.set_font("Arial", 'B', 12)
                pdf.cell(70, 10, txt="Goal", border=1)
                pdf.cell(40, 10, txt="Current", border=1)
                pdf.cell(40, 10, txt="Target", border=1)
                pdf.cell(40, 10, txt="Progress", border=1, ln=True)

                pdf.set_font("Arial", size=10)
                for goal in report_data['goals']:
                    progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
                    pdf.cell(70, 10, txt=goal.name, border=1)
                    pdf.cell(40, 10, txt=f"${goal.current_amount:.2f}", border=1)
                    pdf.cell(40, 10, txt=f"${goal.target_amount:.2f}", border=1)
                    pdf.cell(40, 10, txt=f"{progress:.1f}%", border=1, ln=True)

            # Save PDF
            pdf.output(output_path)

            return True

        except Exception as e:
            print(f"Error exporting PDF: {str(e)}")
            return False

    def generate_charts(self, report_data):
        plt.figure(figsize=(10, 8))

        # Income vs Expenses chart
        if 'summary' in report_data:  # Monthly report
            # Pie chart
            plt.subplot(2, 1, 1)
            labels = []
            sizes = []

            for name, amount in report_data['summary'].get('category_breakdown', {}).items():
                if amount > 0:
                    labels.append(name)
                    sizes.append(amount)

            if sizes:
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')
                plt.title('Expense Breakdown')

            # bar chart income vs expenses
            plt.subplot(2, 1, 2)
            plt.bar(['Income', 'Expenses'],
                    [report_data['summary']['total_income'], report_data['summary']['total_expenses']])
            plt.title('Income vs Expenses')
            plt.ylabel('Amount ($)')

        else:  # Yearly report
            # Line chart
            months = [data['month'][:3] for data in report_data['monthly_data']]  # Abbreviate month names
            income = [data['income'] for data in report_data['monthly_data']]
            expenses = [data['expenses'] for data in report_data['monthly_data']]

            plt.subplot(2, 1, 1)
            plt.plot(months, income, label='Income', marker='o')
            plt.plot(months, expenses, label='Expenses', marker='o')
            plt.title('Monthly Income and Expenses')
            plt.legend()
            plt.grid(True)

            # Bar chart
            plt.subplot(2, 1, 2)
            plt.bar(['Income', 'Expenses'],
                    [report_data['yearly_income'], report_data['yearly_expenses']])
            plt.title('Yearly Income vs Expenses')
            plt.ylabel('Amount ($)')

        plt.tight_layout()

        # Save chart to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Close the plot to free memory
        plt.close()

        return buf.getvalue()


def generate_documentation():
    """
    Generate PDF documentation for the Budget Planner application.

    Returns:
        str: Path to the generated PDF
    """
    # Create a PDF with documentation
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Budget Planner - Documentation", ln=True, align='C')
    pdf.ln(10)

    # Application overview
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="1. Application Overview", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="The Budget Planner is a personal finance application that allows users to track their income and expenses, set financial goals, and generate reports. This documentation provides an overview of the application's features and how to use them.")
    pdf.ln(5)

    # Features
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="2. Features", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.1 User Authentication", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="The application provides user registration and login functionality. User passwords are securely encrypted.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.2 Budget Categories", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="Users can create and manage budget categories for both income and expenses. Default categories are created automatically when a user registers.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.3 Transaction Tracking", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="Users can add transactions for both income and expenses, associating them with categories and dates.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.4 Financial Goals", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="Users can set financial goals with target amounts and deadlines, and track their progress.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.5 Reports", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="The application can generate monthly and yearly reports with income and expense summaries, transaction details, and progress towards financial goals. Reports can be exported to PDF format.")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2.6 Data Visualization", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="Reports include charts and graphs for visualizing budget data, such as expense breakdowns and income vs expenses comparisons.")
    pdf.ln(5)

    # How to use
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="3. How to Use", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="1. Register an account or log in\n2. Add income and expense transactions\n3. Create budget categories as needed\n4. Set financial goals\n5. Generate monthly or yearly reports\n6. Export reports to PDF as needed")
    pdf.ln(5)

    # Technical details
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="4. Technical Details", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10,
                   txt="The Budget Planner is built with Python and uses the following technologies:\n\n- Tkinter for the GUI interface\n- SQLAlchemy ORM for database operations\n- SQLite for data storage\n- Matplotlib for data visualization\n- FPDF for generating PDF reports\n- Simple encryption for user data")
    pdf.ln(5)

    # Determine output directory and file path
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(script_dir, 'docs')
    os.makedirs(docs_dir, exist_ok=True)

    output_path = os.path.join(docs_dir, 'budget_planner_documentation.pdf')

    # Save PDF
    pdf.output(output_path)

    return output_path