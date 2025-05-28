import os
import datetime
import matplotlib

matplotlib.use('Agg')  # backend to non-interactive
import matplotlib.pyplot as plt
import io


def get_month_year_range():
    # Current month and year
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    # Months (1-12)
    months = list(range(1, 13))

    # Years (last 5 years to 5 years in the future)
    years = list(range(current_year - 5, current_year + 6))

    return months, years


def format_currency(amount):
    # Format a number as currency.
    return f"${amount:.2f}"


def validate_amount(amount_str):
    # проверка введенной суммы
    try:
        # Remove currency symbol and commas
        cleaned = amount_str.replace('$', '').replace(',', '')
        amount = float(cleaned)

        if amount < 0:
            return False, "Amount must be positive"

        return True, amount
    except ValueError:
        return False, "Invalid amount format"


def validate_date(year, month, day):
    # проверка введенной даты
    try:
        date = datetime.datetime(year, month, day)
        return True, date
    except ValueError:
        return False, "Invalid date"


def create_chart_image(plt_func, *args, **kwargs):
    plt.figure(figsize=(8, 5))

    # Call the plotting function
    plt_func(*args, **kwargs)

    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()

    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)

    # Close the plot to free memory
    plt.close()

    return buf.getvalue()


def create_expense_pie_chart(categories, amounts):
    def plot_func():
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Expenses by Category')

    return create_chart_image(plot_func)


def create_income_expense_bar_chart(periods, incomes, expenses):
    def plot_func():
        x = range(len(periods))
        width = 0.35

        plt.bar([i - width / 2 for i in x], incomes, width, label='Income')
        plt.bar([i + width / 2 for i in x], expenses, width, label='Expenses')

        plt.xlabel('Period')
        plt.ylabel('Amount ($)')
        plt.title('Income vs Expenses')
        plt.xticks(x, periods)
        plt.legend()

    return create_chart_image(plot_func)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)