from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Table, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from database import Base

# Association table for wallet sharing
wallet_user_association = Table(
    'wallet_user_association',
    Base.metadata,
    Column('wallet_id', Integer, ForeignKey('wallets.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role', String, default='viewer')  # viewer, editor, admin
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    expenses = relationship("Expense", back_populates="user")
    owned_wallets = relationship("Wallet", back_populates="owner")
    shared_wallets = relationship(
        "Wallet",
        secondary=wallet_user_association,
        back_populates="shared_with"
    )
    budgets = relationship("Budget", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    people = relationship("Person", back_populates="user")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    category = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)
    person = Column(String, nullable=True)  # Legacy field - keeping for backward compatibility
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    is_recurring = Column(Boolean, default=False)
    tags = Column(ARRAY(String), nullable=True)
    image_url = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="expenses")
    wallet = relationship("Wallet", back_populates="expenses")
    person_rel = relationship("Person", back_populates="expenses")
    recurring = relationship("RecurringExpense", back_populates="expense", uselist=False)


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float, default=0.0)

    # Relationships
    owner = relationship("User", back_populates="owned_wallets")
    shared_with = relationship(
        "User",
        secondary=wallet_user_association,
        back_populates="shared_wallets"
    )
    expenses = relationship("Expense", back_populates="wallet")


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    frequency = Column(String)  # daily, weekly, monthly
    next_due = Column(DateTime)

    # Relationships
    expense = relationship("Expense", back_populates="recurring")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, index=True)
    monthly_limit = Column(Float)

    # Relationships
    user = relationship("User", back_populates="budgets")
    alerts = relationship("Alert", back_populates="budget")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    triggered_on = Column(DateTime, default=datetime.utcnow)
    message = Column(String)

    # Relationships
    budget = relationship("Budget", back_populates="alerts")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="goals")


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)

    # Relationships
    user = relationship("User", back_populates="people")
    expenses = relationship("Expense", back_populates="person_rel")