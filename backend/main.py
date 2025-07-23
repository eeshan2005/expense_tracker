from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import List, Optional
import uvicorn
from sqlalchemy import func
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from database import get_db, engine
import models
import schemas
from auth import create_access_token, get_current_user, get_password_hash, verify_password
from scheduler import setup_scheduler

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Expense Tracker API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup scheduler for recurring transactions
setup_scheduler()

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# Expense routes
@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_expense = models.Expense(
        **expense.dict(),
        user_id=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).offset(skip).limit(limit).all()
    return expenses


@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(expense_id: int, expense: schemas.ExpenseUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete("/expenses/{expense_id}", response_model=schemas.Expense)
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return expense


# Wallet routes
@app.post("/wallets/", response_model=schemas.Wallet)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_wallet = models.Wallet(
        **wallet.dict(),
        owner_id=current_user.id
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


@app.get("/wallets/", response_model=List[schemas.Wallet])
def read_wallets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wallets = db.query(models.Wallet).filter(models.Wallet.owner_id == current_user.id).all()
    return wallets


# Budget routes
@app.post("/budgets/", response_model=schemas.Budget)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    print(f"Received budget data for creation: {budget.dict()}")
    db_budget = models.Budget(
        **budget.dict(),
        user_id=current_user.id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.get("/budgets/", response_model=List[schemas.Budget])
def read_budgets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    budgets = db.query(models.Budget).filter(models.Budget.user_id == current_user.id).all()
    
    # Calculate current amount for each budget
    for budget in budgets:
        # Get the start of the current month
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
        
        # Calculate total spent in this category for the current month
        total_spent = db.query(func.sum(models.Expense.amount)).\
            filter(models.Expense.user_id == current_user.id,\
                models.Expense.category == budget.category,\
                models.Expense.date >= start_of_month,\
                models.Expense.date <= end_of_month).scalar() or 0.0
        
        budget.current_amount = total_spent
    
    return budgets


@app.get("/budgets/{budget_id}", response_model=schemas.Budget)
def read_budget(budget_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Calculate current amount
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
    
    total_spent = db.query(func.sum(models.Expense.amount)).\
        filter(models.Expense.user_id == current_user.id,\
            models.Expense.category == budget.category,\
            models.Expense.date >= start_of_month,\
            models.Expense.date <= end_of_month).scalar() or 0.0
    
    budget.current_amount = total_spent
    
    return budget


@app.put("/budgets/{budget_id}", response_model=schemas.Budget)
def update_budget(budget_id: int, budget: schemas.BudgetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    print(f"Received budget data for update: {budget.dict()}")
    update_data = budget.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.delete("/budgets/{budget_id}", response_model=schemas.Budget)
def delete_budget(budget_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    budget = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id).first()
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return budget


# Goal routes
@app.post("/goals/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_goal = models.Goal(
        **goal.dict(),
        user_id=current_user.id
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@app.get("/goals/", response_model=List[schemas.Goal])
def read_goals(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return goals


# People routes
@app.post("/people/", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_person = models.Person(
        **person.dict(),
        user_id=current_user.id
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.get("/people/", response_model=List[schemas.Person])
def read_people(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    people = db.query(models.Person).filter(models.Person.user_id == current_user.id).all()
    return people


# User Settings routes
@app.get("/users/settings", response_model=schemas.UserSetting)
def get_user_settings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings = db.query(models.UserSetting).filter(models.UserSetting.user_id == current_user.id).first()
    if not settings:
        # Create default settings if none exist
        settings = models.UserSetting(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@app.put("/users/settings", response_model=schemas.UserSetting)
def update_user_settings(settings_in: schemas.UserSettingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    settings = db.query(models.UserSetting).filter(models.UserSetting.user_id == current_user.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    for field, value in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return settings


# Analytics routes
@app.get("/analytics/category")
def get_category_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    categories = db.query(models.Expense.category).filter(models.Expense.user_id == current_user.id).distinct().all()
    category_list = [category[0] for category in categories]
    if not category_list:
        return ["Uncategorized"]
    return category_list

@app.get("/analytics/summary")
def get_summary_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Get current month's start and end dates
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)

    # Total spent this month
    total_spent_this_month = db.query(func.sum(models.Expense.amount)).\
        filter(models.Expense.user_id == current_user.id,\
               models.Expense.date >= start_of_month,\
               models.Expense.date <= end_of_month).scalar() or 0.0

    # Top category this month
    top_category_query = db.query(models.Expense.category, func.sum(models.Expense.amount).label('total_amount')).\
        filter(models.Expense.user_id == current_user.id,\
               models.Expense.date >= start_of_month,\
               models.Expense.date <= end_of_month).\
        group_by(models.Expense.category).\
        order_by(func.sum(models.Expense.amount).desc()).first()
    top_category = top_category_query.category if top_category_query else "N/A"

    # Top person this month (using person_id relationship)
    try:
        # First try to get top person using the relationship
        top_person_query = db.query(models.Person.name, func.sum(models.Expense.amount).label('total_amount')).\
            join(models.Expense, models.Expense.person_id == models.Person.id).\
            filter(models.Expense.user_id == current_user.id,\
                models.Expense.date >= start_of_month,\
                models.Expense.date <= end_of_month,\
                models.Expense.person_id != None).\
            group_by(models.Person.name).\
            order_by(func.sum(models.Expense.amount).desc()).first()
        
        # If no results with relationship, try using the string field
        if not top_person_query:
            # Fallback to using the string person field
            person_string_query = db.query(models.Expense.person, func.sum(models.Expense.amount).label('total_amount')).\
                filter(models.Expense.user_id == current_user.id,\
                    models.Expense.date >= start_of_month,\
                    models.Expense.date <= end_of_month,\
                    models.Expense.person != None).\
                group_by(models.Expense.person).\
                order_by(func.sum(models.Expense.amount).desc()).first()
            top_person = person_string_query.person if person_string_query else "You"
        else:
            top_person = top_person_query.name
    except Exception as e:
        # If any error occurs, just use a default value
        top_person = "You"

    # Weekly spending (last 7 days)
    start_of_week = today - timedelta(days=7)
    weekly_total = db.query(func.sum(models.Expense.amount)).\
        filter(models.Expense.user_id == current_user.id,\
               models.Expense.date >= start_of_week,\
               models.Expense.date <= today).scalar() or 0.0

    # Previous month's spending
    prev_month_start = (start_of_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_end = start_of_month - timedelta(microseconds=1)
    
    total_spent_prev_month = db.query(func.sum(models.Expense.amount)).\
        filter(models.Expense.user_id == current_user.id,\
               models.Expense.date >= prev_month_start,\
               models.Expense.date <= prev_month_end).scalar() or 0.0
    
    # Calculate monthly change
    monthly_change = 0
    if total_spent_prev_month > 0:
        monthly_change = ((total_spent_this_month - total_spent_prev_month) / total_spent_prev_month) * 100
    
    # Calculate savings rate (assuming income is stored or can be calculated)
    # For now, we'll use a placeholder or estimate
    # In a real app, you would get this from income data
    estimated_income = 5000  # Placeholder
    savings_rate = 0
    if estimated_income > 0:
        savings_rate = ((estimated_income - total_spent_this_month) / estimated_income) * 100
    
    return {
        "total": total_spent_this_month,
        "topCategory": top_category,
        "topPerson": top_person,
        "weeklyTotal": weekly_total,
        "monthlyChange": monthly_change,
        "savingsRate": savings_rate
    }

@app.get("/analytics/category-breakdown")
def get_category_breakdown_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), time_range: str = "month"):
    today = datetime.now()
    if time_range == "week":
        start_date = today - timedelta(days=7)
    elif time_range == "month":
        start_date = today.replace(day=1)
    elif time_range == "year":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today.replace(day=1)

    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id, models.Expense.date >= start_date).all()
    category_data = {}
    total_amount = 0
    for expense in expenses:
        if expense.category in category_data:
            category_data[expense.category] += expense.amount
        else:
            category_data[expense.category] = expense.amount
        total_amount += expense.amount

    breakdown = []
    for category, amount in category_data.items():
        percentage = (amount / total_amount) * 100 if total_amount > 0 else 0
        breakdown.append({
            "category": category,
            "amount": amount,
            "percentage": percentage
        })
    return breakdown


@app.get("/analytics/daily")
def get_daily_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Get expenses grouped by date
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    daily_data = {}
    for expense in expenses:
        date_str = expense.date.strftime("%Y-%m-%d")
        if date_str in daily_data:
            daily_data[date_str] += expense.amount
        else:
            daily_data[date_str] = expense.amount
    
    return daily_data

@app.get("/analytics/monthly-trends")
def get_monthly_trends_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), months: int = 6):
    trends = []
    for i in range(months):
        date = datetime.now() - timedelta(days=30 * i)
        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)

        total_spent = db.query(func.sum(models.Expense.amount)).\
            filter(models.Expense.user_id == current_user.id,\
                   models.Expense.date >= start_of_month,\
                   models.Expense.date <= end_of_month).scalar() or 0.0
        trends.append({
            "month": date.strftime("%b %Y"),
            "amount": total_spent
        })
    return list(reversed(trends))


@app.get("/analytics/person")
def get_person_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Get expenses grouped by person
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    person_data = {}
    for expense in expenses:
        if expense.person in person_data:
            person_data[expense.person] += expense.amount
        else:
            person_data[expense.person] = expense.amount
    
    return person_data

@app.get("/analytics/wallet-distribution")
def get_wallet_distribution_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), time_range: str = "month"):
    today = datetime.now()
    if time_range == "week":
        start_date = today - timedelta(days=7)
    elif time_range == "month":
        start_date = today.replace(day=1)
    elif time_range == "year":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today.replace(day=1)

    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id, models.Expense.date >= start_date).all()
    wallet_data = {}
    total_amount = 0
    for expense in expenses:
        wallet_name = db.query(models.Wallet.name).filter(models.Wallet.id == expense.wallet_id).scalar()
        if wallet_name in wallet_data:
            wallet_data[wallet_name] += expense.amount
        else:
            wallet_data[wallet_name] = expense.amount
        total_amount += expense.amount

    distribution = []
    for wallet_name, amount in wallet_data.items():
        percentage = (amount / total_amount) * 100 if total_amount > 0 else 0
        distribution.append({
            "wallet_name": wallet_name,
            "amount": amount,
            "percentage": percentage
        })
    return distribution


# AI Suggestions
@app.get("/ai/categorize")
def categorize_expense(note: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # This would use OpenAI or BoltAI to categorize expenses based on the note
    # For now, we'll use a simple rule-based approach
    note = note.lower()
    if "food" in note or "restaurant" in note or "meal" in note:
        return {"category": "Food"}
    elif "transport" in note or "uber" in note or "taxi" in note or "bus" in note:
        return {"category": "Transport"}
    elif "rent" in note or "house" in note:
        return {"category": "Housing"}
    else:
        return {"category": "Miscellaneous"}


@app.get("/ai/budget-suggestions")
def get_budget_suggestions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # This would use AI to suggest budgets based on spending habits
    # For now, we'll use a simple rule-based approach
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()
    category_data = {}
    for expense in expenses:
        if expense.category in category_data:
            category_data[expense.category] += expense.amount
        else:
            category_data[expense.category] = expense.amount
    
    suggestions = {}
    for category, amount in category_data.items():
        # Suggest a budget 20% higher than current spending
        suggestions[category] = amount * 1.2
    
    return suggestions


@app.get("/ai/savings-tips")
def get_savings_tips(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # This would use AI to suggest ways to save money
    # For now, we'll return some generic tips
    return {
        "tips": [
            "Consider making coffee at home instead of buying it",
            "Look for sales and discounts when shopping",
            "Use public transportation instead of taxis when possible",
            "Cook meals at home instead of eating out",
            "Cancel unused subscriptions"
        ]
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)