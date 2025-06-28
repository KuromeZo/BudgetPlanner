# Budget Planner

A personal finance application built with Python and Tkinter that helps you track your income and expenses, set financial goals, and generate detailed reports.

## Features

### 🔐 User Authentication
- Secure user registration and login system
- Password encryption for data protection
- Multi-user support with isolated data

### 💰 Transaction Management
- Track income and expenses with detailed categorization
- Add custom categories for better organization
- Date-based transaction recording
- Transaction history with filtering options

### 🎯 Financial Goals
- Set and track financial goals with target amounts
- Monitor progress towards your objectives
- Update goal progress as you save

### 📊 Reports & Analytics
- Generate monthly and yearly financial reports
- Visual charts and graphs for expense breakdown
- Income vs. expenses comparison
- Export reports to PDF format

### 📈 Data Visualization
- Pie charts for expense category breakdown
- Bar charts for income vs. expenses analysis
- Monthly trend visualization for yearly reports

## Requirements

### Python Dependencies
```
tkinter (usually included with Python)
sqlalchemy
matplotlib
fpdf2
pillow (PIL)
```

### System Requirements
- Python 3.7 or higher
- Windows, macOS, or Linux

## Installation

1. **Clone the repository:**
```bash
git clone link
cd budget-planner
```

2. **Install required packages:**
```bash
pip install sqlalchemy matplotlib fpdf2 pillow
```

3. **Run the application:**
```bash
python main.py
```

## Usage

### Getting Started
1. **First Launch:** Run `python main.py` to start the application
2. **Register:** Create a new account with your username and password
3. **Login:** Use your credentials to access your personal budget tracker

### Managing Transactions
1. **Add Income/Expenses:** Select transaction type, enter amount, choose category, and add description
2. **Custom Categories:** Create personalized income and expense categories
3. **View History:** Browse your recent transactions in the main interface

### Setting Goals
1. **Create Goals:** Set financial targets with specific amounts
2. **Track Progress:** Update your progress as you save money
3. **Monitor Achievement:** View goal completion percentages

### Generating Reports
1. **Choose Report Type:** Select monthly or yearly reports
2. **Set Time Period:** Pick the specific month/year for analysis
3. **View Results:** Browse summary, transactions, charts, and goals
4. **Export PDF:** Save reports for external use

## Project Structure

```
budget-planner/
├── main.py                     # Application entry point
├── app/
│   ├── auth.py                 # User authentication
│   ├── budget.py               # Budget management functions
│   ├── database.py             # Database models and initialization
│   ├── reports.py              # Report generation and PDF export
│   ├── utils.py                # Utility functions and validation
│   └── ui/
│       ├── login_frame.py      # Login interface
│       ├── main_frame.py       # Main application frame
│       ├── budget_frame.py     # Budget management interface
│       └── report_frame.py     # Reports interface
├── data/                       # Database storage (auto-created)
│   └── budget.db              # SQLite database
└── docs/                      # Generated documentation (auto-created)
    └── budget_planner_documentation.pdf
```

## Database Schema

The application uses SQLite with the following main tables:
- **Users:** User account information
- **Categories:** Income and expense categories
- **Transactions:** Financial transactions
- **Goals:** Financial goals and progress

## Security Notes

⚠️ **Important:** This application is designed for personal use and learning purposes. The password encryption used is basic and should not be considered production-ready for sensitive financial data.

## Technical Details

- **GUI Framework:** Tkinter
- **Database:** SQLite with SQLAlchemy ORM
- **Charts:** Matplotlib
- **PDF Generation:** FPDF
- **Image Processing:** PIL/Pillow

## Acknowledgments

- Built with Python and Tkinter for cross-platform compatibility
- Uses SQLAlchemy for robust database operations
- Matplotlib for beautiful data visualizations
- FPDF for professional report generation

---
