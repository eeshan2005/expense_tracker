from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# User schemas
class UserSettingBase(BaseModel):
    currency: Optional[str] = "USD"
    language: Optional[str] = "en"
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True
    expense_reminders: Optional[bool] = True
    budget_alerts: Optional[bool] = True
    goal_updates: Optional[bool] = True


class UserSettingCreate(UserSettingBase):
    pass


class UserSetting(UserSettingBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    settings: Optional[UserSetting] = None

    class Config:
        orm_mode = True


# Expense schemas
class ExpenseBase(BaseModel):
    amount: float
    category: str
    date: Optional[datetime] = None
    note: Optional[str] = None
    person: Optional[str] = None
    wallet_id: Optional[int] = None
    is_recurring: Optional[bool] = False
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    amount: Optional[float] = None
    category: Optional[str] = None


class Expense(ExpenseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# Wallet schemas
class WalletBase(BaseModel):
    name: str
    balance: Optional[float] = 0.0


class WalletCreate(WalletBase):
    pass


class Wallet(WalletBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# RecurringExpense schemas
class RecurringExpenseBase(BaseModel):
    frequency: str  # daily, weekly, monthly
    next_due: datetime


class RecurringExpenseCreate(RecurringExpenseBase):
    expense_id: int


class RecurringExpense(RecurringExpenseBase):
    id: int
    expense_id: int

    class Config:
        orm_mode = True


# Budget schemas
class BudgetBase(BaseModel):
    category: str
    monthly_limit: float
    current_amount: Optional[float] = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    alert_threshold: Optional[float] = 80.0


class BudgetCreate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# Alert schemas
class AlertBase(BaseModel):
    message: str


class AlertCreate(AlertBase):
    budget_id: int


class Alert(AlertBase):
    id: int
    user_id: int
    budget_id: int
    triggered_on: datetime

    class Config:
        orm_mode = True


# Goal schemas
class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0.0
    deadline: Optional[datetime] = None


class GoalCreate(GoalBase):
    pass


class Goal(GoalBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# Person schemas
class PersonBase(BaseModel):
    name: str


class PersonCreate(PersonBase):
    pass


class Person(PersonBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


# UserSetting schemas
class UserSettingBase(BaseModel):
    currency: Optional[str] = "USD"
    language: Optional[str] = "en"
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True
    expense_reminders: Optional[bool] = True
    budget_alerts: Optional[bool] = True
    goal_updates: Optional[bool] = True


class UserSettingCreate(UserSettingBase):
    pass


class UserSetting(UserSettingBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
