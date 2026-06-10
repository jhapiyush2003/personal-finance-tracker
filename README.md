# Personal Finance Tracker

A full-stack web application for tracking personal income and expenses,
built with Python FastAPI backend and a premium dark-themed dashboard UI.

## Live Features
- Add income and expense transactions
- Real-time summary cards (Total Income, Expenses, Net Balance)
- Interactive doughnut chart by spending category
- Monthly filter — view any month's data instantly
- Export transactions to CSV
- Filter by income / expense / all
- Persistent SQLite database storage

## Tech Stack
- **Backend:** Python, FastAPI, SQLite3, Pydantic, Uvicorn
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Architecture:** REST API + Server-rendered UI (single file)

## How to Run

1. Install dependencies:
   pip install fastapi uvicorn

2. Run the app:
   python finance_tracker.py

3. Open browser:
   http://127.0.0.1:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /transactions | Get all transactions |
| POST | /transactions | Add a transaction |
| DELETE | /transactions/{id} | Delete a transaction |
| GET | /summary | Get income/expense summary |
| GET | /export | Download CSV |
| GET | /months | Get available months |

## Screenshots



## Author
Piyush Jha — [LinkedIn](https://linkedin.com/in/piyushjha2003) | [Portfolio](https://piyush-jha-portfolio-html.vercel.app)
