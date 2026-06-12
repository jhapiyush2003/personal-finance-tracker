Personal Finance Tracker
Full-stack finance tracker — FastAPI + PostgreSQL (Render) with Chart.js frontend.

Deploy to Render (Free) — Step by Step
Step 1 — Push these files to your GitHub repo
Make sure your repo has:

finance_tracker.py   ← your main app (already done)
requirements.txt     ← NEW (add this)
render.yaml          ← NEW (add this)
Step 2 — Create a free Render account
Go to https://render.com and sign up with GitHub.

Step 3 — New Web Service
Click New → Web Service
Connect your personal-finance-tracker GitHub repo
Fill in:
Name: personal-finance-tracker
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python finance_tracker.py
Click Create Web Service
Step 4 — Add a Free PostgreSQL Database
Click New → PostgreSQL
Name: finance-db
Plan: Free
Click Create Database
Copy the Internal Database URL
Step 5 — Link DB to your Web Service
Go to your Web Service → Environment
Add environment variable:
Key: DATABASE_URL
Value: paste the Internal Database URL
Click Save — Render will redeploy automatically
Step 6 — Done!
Your live URL will be: https://personal-finance-tracker-xxxx.onrender.com

Note: Free Render services sleep after 15 min of inactivity and take ~30s to wake up. This is fine for a portfolio project.

Tech Stack
Backend: Python, FastAPI, PostgreSQL (prod) / SQLite (local)
Frontend: HTML, CSS, JavaScript, Chart.js
Hosting: Render (free tier)
Run Locally
pip install -r requirements.txt
python finance_tracker.py
# Open http://127.0.0.1:8000
Author
Piyush Jha — LinkedIn | Portfolio
