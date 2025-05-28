import datetime
from sqlalchemy import extract, func

from app.database import Category, Transaction, Goal, get_session


def create_default_categories(user_id):
    session = get_session()

    income_categories = ["Salary", "Investments", "Gifts", "Other Income"]
    for name in income_categories:
        category = Category(name=name, is_income=True, user_id=user_id)
        session.add(category)

    expense_categories = ["Housing", "Food", "Transportation", "Utilities",
                          "Healthcare", "Entertainment", "Education", "Shopping",
                          "Savings", "Debt Payments", "Miscellaneous"]
    for name in expense_categories:
        category = Category(name=name, is_income=False, user_id=user_id)
        session.add(category)

    session.commit()
    session.close()


def get_categories(user_id, is_income=None):
    session = get_session()

    query = session.query(Category).filter_by(user_id=user_id)
    if is_income is not None:
        query = query.filter_by(is_income=is_income)

    categories = query.all()
    session.close()

    return categories


def add_category(user_id, name, is_income):
    session = get_session()

    try:
        # Check if exists
        existing = session.query(Category).filter_by(
            user_id=user_id, name=name, is_income=is_income).first()

        if existing:
            session.close()
            return False, "Category already exists"

        # Create new category
        category = Category(name=name, is_income=is_income, user_id=user_id)
        session.add(category)
        session.commit()

        session.close()
        return True, "Category added successfully"

    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"


def add_transaction(user_id, amount, description, category_id, date=None):
    session = get_session()

    try:
        # validate category and get type
        category = session.query(Category).filter_by(id=category_id, user_id=user_id).first()
        if not category:
            session.close()
            return False, "Invalid category"

        # Ensure amount is positive (we'll use category type to determine income/expense)
        amount = abs(amount)

        # Create transaction
        transaction = Transaction(
            amount=amount,
            description=description or "",
            category_id=category_id,
            user_id=user_id,
            date=date or datetime.datetime.now()
        )

        session.add(transaction)
        session.commit()

        print(
            f"Transaction saved: ID={transaction.id}, Amount={amount}, Category={category.name}, Type={'Income' if category.is_income else 'Expense'}")

        session.close()
        return True, "Transaction added successfully"

    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error adding transaction: {str(e)}")
        return False, f"An error occurred: {str(e)}"


def get_transactions(user_id, start_date=None, end_date=None, category_id=None):
    session = get_session()

    # Use joinedload to eagerly(active) load the category relationship
    from sqlalchemy.orm import joinedload

    query = session.query(Transaction).options(joinedload(Transaction.category)).filter_by(user_id=user_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if category_id:
        query = query.filter_by(category_id=category_id)

    # newest first
    query = query.order_by(Transaction.date.desc())

    transactions = query.all()

    class TransactionData:
        def __init__(self, trans, cat):
            self.id = trans.id
            self.amount = trans.amount
            self.description = trans.description
            self.date = trans.date
            self.category_id = trans.category_id
            self.user_id = trans.user_id
            # Store category data to avoid lazy loading issues
            self.category_name = cat.name
            self.category_is_income = cat.is_income

    # Convert to TransactionData objects
    result = []
    for transaction in transactions:
        result.append(TransactionData(transaction, transaction.category))

    session.close()

    return result


def get_monthly_summary(user_id, year, month):
    session = get_session()

    # get income based on category type
    income_query = session.query(func.sum(Transaction.amount)).join(Category).filter(
        Transaction.user_id == user_id,
        Category.is_income == True,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    )

    # get expenses based on category type
    expense_query = session.query(func.sum(Transaction.amount)).join(Category).filter(
        Transaction.user_id == user_id,
        Category.is_income == False,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    )

    # Category breakdown
    category_breakdown = session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Category).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    ).group_by(Category.name).all()

    total_income = income_query.scalar() or 0
    total_expenses = expense_query.scalar() or 0

    print(f"Monthly summary: Income={total_income}, Expenses={total_expenses}")

    session.close()

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net': total_income - total_expenses,
        'category_breakdown': dict(category_breakdown)
    }


def add_goal(user_id, name, target_amount, deadline=None):
    session = get_session()

    try:
        goal = Goal(
            name=name,
            target_amount=target_amount,
            current_amount=0,
            deadline=deadline,
            user_id=user_id
        )

        session.add(goal)
        session.commit()

        session.close()
        return True, "Goal added successfully"

    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"


def update_goal(goal_id, user_id, current_amount=None, target_amount=None, deadline=None):
    session = get_session()

    try:
        # Find goal
        goal = session.query(Goal).filter_by(id=goal_id, user_id=user_id).first()

        if not goal:
            session.close()
            return False, "Goal not found"

        # Update fields
        if current_amount is not None:
            goal.current_amount = current_amount

        if target_amount is not None:
            goal.target_amount = target_amount

        if deadline is not None:
            goal.deadline = deadline

        session.commit()

        session.close()
        return True, "Goal updated successfully"

    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"


def get_goals(user_id):
    session = get_session()

    goals = session.query(Goal).filter_by(user_id=user_id).all()

    session.close()

    return goals