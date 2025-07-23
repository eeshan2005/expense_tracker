from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database import SessionLocal
import models

# Create scheduler
scheduler = BackgroundScheduler()


def process_recurring_expenses():
    """Process all recurring expenses that are due"""
    db = SessionLocal()
    try:
        # Get all recurring expenses that are due
        recurring_expenses = db.query(models.RecurringExpense).filter(
            models.RecurringExpense.next_due <= datetime.utcnow()
        ).all()
        
        for recurring in recurring_expenses:
            # Get the original expense
            original_expense = recurring.expense
            
            # Create a new expense based on the original
            new_expense = models.Expense(
                user_id=original_expense.user_id,
                amount=original_expense.amount,
                category=original_expense.category,
                date=datetime.utcnow(),
                note=original_expense.note,
                person=original_expense.person,
                wallet_id=original_expense.wallet_id,
                is_recurring=False,  # This is a one-time expense created from a recurring one
                tags=original_expense.tags
            )
            db.add(new_expense)
            
            # Update the next due date based on frequency
            if recurring.frequency == "daily":
                recurring.next_due = recurring.next_due + timedelta(days=1)
            elif recurring.frequency == "weekly":
                recurring.next_due = recurring.next_due + timedelta(weeks=1)
            elif recurring.frequency == "monthly":
                # Add one month (approximately)
                next_month = recurring.next_due.month + 1
                next_year = recurring.next_due.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                recurring.next_due = recurring.next_due.replace(year=next_year, month=next_month)
            
            db.commit()
    finally:
        db.close()


def check_budget_alerts():
    """Check if any budgets have been exceeded and create alerts"""
    db = SessionLocal()
    try:
        # Get all budgets
        budgets = db.query(models.Budget).all()
        
        for budget in budgets:
            # Get the current month's expenses for this category
            now = datetime.utcnow()
            start_of_month = datetime(now.year, now.month, 1)
            end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
            
            total_spent = db.query(models.Expense).filter(
                models.Expense.user_id == budget.user_id,
                models.Expense.category == budget.category,
                models.Expense.date >= start_of_month,
                models.Expense.date < end_of_month
            ).with_entities(models.Expense.amount).all()
            
            total_amount = sum(amount for (amount,) in total_spent)
            
            # Check if budget is exceeded
            if total_amount > budget.monthly_limit:
                # Check if an alert has already been created for this budget this month
                existing_alert = db.query(models.Alert).filter(
                    models.Alert.budget_id == budget.id,
                    models.Alert.triggered_on >= start_of_month
                ).first()
                
                if not existing_alert:
                    # Create a new alert
                    alert = models.Alert(
                        user_id=budget.user_id,
                        budget_id=budget.id,
                        message=f"Budget for {budget.category} exceeded! Limit: {budget.monthly_limit}, Spent: {total_amount}"
                    )
                    db.add(alert)
                    db.commit()
    finally:
        db.close()


def setup_scheduler():
    """Set up the scheduler with jobs"""
    # Add jobs to the scheduler
    scheduler.add_job(process_recurring_expenses, CronTrigger(hour=0, minute=0))  # Run daily at midnight
    scheduler.add_job(check_budget_alerts, CronTrigger(hour=0, minute=5))  # Run daily at 00:05
    
    # Start the scheduler
    scheduler.start()