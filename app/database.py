import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# base class for ORM
Base = declarative_base()


class User(Base):
    # User model for authentication
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Will store encrypted password
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Category(Base):
    # Budget category model
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_income = Column(Boolean, default=False)  # True for income, False for expense
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(name='{self.name}', type='{'Income' if self.is_income else 'Expense'}')>"


class Transaction(Base):
    # Transaction model for income and expenses
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(amount={self.amount}, category='{self.category.name}', date='{self.date}')>"


class Goal(Base):
    # Financial goal model
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal(name='{self.name}', progress={self.current_amount}/{self.target_amount})>"


def init_db():
    """init_db, creating tables if they don't exist"""
    # Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Create engine
    db_path = os.path.join(data_dir, 'budget.db')
    engine = create_engine(f'sqlite:///{db_path}')

    # Create tables
    Base.metadata.create_all(engine)

    return engine


# Create a session factory
def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()