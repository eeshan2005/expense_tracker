# Expense Tracker Application

This is a full-stack expense tracker application with a React/Next.js frontend and a FastAPI/Python backend.

## Project Structure

- `backend/`: Contains the FastAPI backend application.
  - `main.py`: Main application file with API endpoints.
  - `models.py`: SQLAlchemy models for database interaction.
  - `schemas.py`: Pydantic schemas for data validation and serialization.
  - `auth.py`: Authentication and authorization logic.
  - `database.py`: Database connection and session management.
  - `alembic/`: Database migrations.
- `frontend/`: Contains the React/Next.js frontend application.
  - `app/`: Next.js pages and components.
    - `dashboard/`: Dashboard page.
    - `budgets/`: Budget management pages.
    - `expenses/`: Expense management pages.
    - `wallets/`: Wallet management pages.
    - `goals/`: Goal management pages.
    - `people/`: People management pages.
    - `settings/`: User settings page.
    - `login/`, `register/`: Authentication pages.
    - `components/`: Reusable React components.
    - `contexts/`: React contexts (e.g., AuthContext).
    - `services/`: API service integration.

## Setup Instructions

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd e:\web dev\e\backend
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run database migrations:
    ```bash
    alembic upgrade head
    ```
6.  Start the FastAPI development server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd e:\web dev\e\frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the Next.js development server:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

## Key Functionalities and Verification Steps

Below is a list of core functionalities and steps to verify they are working correctly.

### 1. User Authentication

-   **Register:**
    1.  Go to `http://localhost:3000/register`.
    2.  Fill in a new username and password.
    3.  Click "Register".
    *Expected:* User is registered and redirected to the dashboard.

-   **Login:**
    1.  Go to `http://localhost:3000/login`.
    2.  Enter registered username and password.
    3.  Click "Login".
    *Expected:* User is logged in and redirected to the dashboard.

-   **Logout:**
    1.  From the dashboard, click on the profile icon/menu.
    2.  Select "Logout".
    *Expected:* User is logged out and redirected to the login page.

### 2. Expense Management

-   **Add Expense:**
    1.  Log in and go to the dashboard.
    2.  Click "Add Expense" or navigate to `http://localhost:3000/expenses/new`.
    3.  Fill in expense details (amount, category, date, note, wallet, person).
    4.  Click "Create Expense".
    *Expected:* Expense is added, and you see a success message. The expense should appear in the expenses list.

-   **View Expenses:**
    1.  Log in and navigate to `http://localhost:3000/expenses`.
    *Expected:* A list of all your expenses is displayed.

-   **Edit Expense:**
    1.  From the expenses list, click "Edit" next to an expense.
    2.  Modify any expense detail.
    3.  Click "Update Expense".
    *Expected:* Expense details are updated, and you see a success message.

-   **Delete Expense:**
    1.  From the expenses list, click "Delete" next to an expense.
    2.  Confirm deletion.
    *Expected:* Expense is removed from the list, and you see a success message.

### 3. Budget Management

-   **Create Budget:**
    1.  Log in and navigate to `http://localhost:3000/budgets/new`.
    2.  Select a category, set a monthly limit, start date, end date, and alert threshold.
    3.  Click "Create Budget".
    *Expected:* Budget is created and appears in the budgets list. The `monthly_limit` should be correctly saved.

-   **View Budgets:**
    1.  Log in and navigate to `http://localhost:3000/budgets`.
    *Expected:* A list of all your budgets is displayed, showing `current_amount` and `monthly_limit`.

-   **Edit Budget:**
    1.  From the budgets list, click "Edit" next to a budget.
    2.  Modify any budget detail (e.g., `monthly_limit`).
    3.  Click "Update Budget".
    *Expected:* Budget details are updated, and you see a success message.

-   **Delete Budget:**
    1.  From the budgets list, click "Delete" next to a budget.
    2.  Confirm deletion.
    *Expected:* Budget is removed from the list, and you see a success message.

### 4. Wallet Management

-   **Create Wallet:**
    1.  Log in and navigate to `http://localhost:3000/wallets/new`.
    2.  Enter wallet name and initial balance.
    3.  Click "Create Wallet".
    *Expected:* Wallet is created and appears in the wallets list.

-   **View Wallets:**
    1.  Log in and navigate to `http://localhost:3000/wallets`.
    *Expected:* A list of all your wallets is displayed.

-   **Edit Wallet:**
    1.  From the wallets list, click "Edit" next to a wallet.
    2.  Modify wallet name or balance.
    3.  Click "Update Wallet".
    *Expected:* Wallet details are updated.

-   **Delete Wallet:**
    1.  From the wallets list, click "Delete" next to a wallet.
    2.  Confirm deletion.
    *Expected:* Wallet is removed.

### 5. Goal Management

-   **Create Goal:**
    1.  Log in and navigate to `http://localhost:3000/goals/new`.
    2.  Enter goal name, target amount, and target date.
    3.  Click "Create Goal".
    *Expected:* Goal is created and appears in the goals list.

-   **View Goals:**
    1.  Log in and navigate to `http://localhost:3000/goals`.
    *Expected:* A list of all your goals is displayed.

-   **Edit Goal:**
    1.  From the goals list, click "Edit" next to a goal.
    2.  Modify goal details.
    3.  Click "Update Goal".
    *Expected:* Goal details are updated.

-   **Delete Goal:**
    1.  From the goals list, click "Delete" next to a goal.
    2.  Confirm deletion.
    *Expected:* Goal is removed.

### 6. People Management

-   **Create Person:**
    1.  Log in and navigate to `http://localhost:3000/people/new`.
    2.  Enter person's name.
    3.  Click "Create Person".
    *Expected:* Person is created and appears in the people list.

-   **View People:**
    1.  Log in and navigate to `http://localhost:3000/people`.
    *Expected:* A list of all people is displayed.

-   **Edit Person:**
    1.  From the people list, click "Edit" next to a person.
    2.  Modify person's name.
    3.  Click "Update Person".
    *Expected:* Person's name is updated.

-   **Delete Person:**
    1.  From the people list, click "Delete" next to a person.
    2.  Confirm deletion.
    *Expected:* Person is removed.

### 7. Analytics Dashboard

-   **View Summary:**
    1.  Log in and go to `http://localhost:3000/dashboard`.
    *Expected:* The dashboard displays `Total Spent`, `Monthly Change`, `Savings Rate`, `Weekly Spending`, `Top Category`, and `Top Spender`.

-   **Category Breakdown:**
    1.  Log in and navigate to `http://localhost:3000/analytics/category-breakdown`.
    *Expected:* Expense breakdown by category is displayed for various time ranges.

-   **Daily/Monthly Trends:**
    1.  Log in and navigate to `http://localhost:3000/analytics/daily` or `http://localhost:3000/analytics/monthly-trends`.
    *Expected:* Daily and monthly spending trends are displayed.

-   **Wallet Distribution:**
    1.  Log in and navigate to `http://localhost:3000/analytics/wallet-distribution`.
    *Expected:* Expense distribution across wallets is displayed.

### 8. Settings

-   **Update Settings:**
    1.  Log in and navigate to `http://localhost:3000/settings`.
    2.  Change currency or language.
    3.  Click "Save Settings".
    *Expected:* Settings are updated, and you see a success message.