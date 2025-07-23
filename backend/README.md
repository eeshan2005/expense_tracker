# Smart Expense Tracker - Backend

This is the backend API for the Smart Expense Tracker application, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- JWT-based authentication
- Expense tracking and management
- Budget alerts
- Recurring transactions
- AI-powered expense categorization and suggestions
- OCR for receipt scanning
- Financial goals tracking
- Shared wallets

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Tesseract OCR (for receipt scanning)

### Database Setup

1. Create a PostgreSQL database named `expense`:

```sql
CREATE DATABASE expense;
```

2. Set the password for the PostgreSQL user to `2005` or update the connection string in `database.py` and `alembic.ini`.

### Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run database migrations:

```bash
alembic upgrade head
```

### Running the API

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

For production, you should set the following environment variables:

- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection URL
- `OPENAI_API_KEY`: OpenAI API key for AI features

## Project Structure

- `main.py`: FastAPI application and routes
- `database.py`: Database connection setup
- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic schemas for request/response validation
- `auth.py`: Authentication utilities
- `scheduler.py`: APScheduler setup for recurring transactions
- `ai_service.py`: AI-powered features
- `utils.py`: Utility functions
- `alembic/`: Database migration files