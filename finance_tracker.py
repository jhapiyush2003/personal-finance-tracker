from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import csv
import io
import os
 
app = FastAPI()
 
# ── CORS ──────────────────────────────────────────────────────
# Allow the Vercel frontend (and local dev) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace "*" with your Vercel URL after deploy
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── DB ────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")
 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT    NOT NULL,
            amount   REAL    NOT NULL,
            category TEXT    NOT NULL,
            type     TEXT    NOT NULL,
            date     TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
 
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
# ── MODELS ────────────────────────────────────────────────────
class Transaction(BaseModel):
    title:    str
    amount:   float
    category: str
    type:     str
    date:     str
 
# ── ROUTES ────────────────────────────────────────────────────
@app.get("/transactions")
def get_transactions(month: Optional[str] = Query(None)):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC",
            (month,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY date DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
@app.post("/transactions")
def add_transaction(t: Transaction):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO transactions (title, amount, category, type, date) VALUES (?,?,?,?,?)",
        (t.title, t.amount, t.category, t.type, t.date)
    )
    conn.commit()
    conn.close()
    return {"message": "Added", "id": cursor.lastrowid}
 
@app.delete("/transactions/{tid}")
def delete_transaction(tid: int):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id = ?", (tid,))
    conn.commit()
    conn.close()
    return {"message": "Deleted"}
 
@app.get("/summary")
def get_summary(month: Optional[str] = Query(None)):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ?",
            (month,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM transactions").fetchall()
    conn.close()
    income  = sum(r["amount"] for r in rows if r["type"] == "income")
    expense = sum(r["amount"] for r in rows if r["type"] == "expense")
    return {"income": income, "expense": expense, "balance": income - expense}
 
@app.get("/export")
def export_csv(month: Optional[str] = Query(None)):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC",
            (month,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY date DESC"
        ).fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Amount", "Category", "Type", "Date"])
    for r in rows:
        writer.writerow([r["id"], r["title"], r["amount"], r["category"], r["type"], r["date"]])
    output.seek(0)
    filename = f"transactions_{month}.csv" if month else "transactions_all.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
 
@app.get("/months")
def get_months():
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT strftime('%Y-%m', date) as month FROM transactions ORDER BY month DESC"
    ).fetchall()
    conn.close()
    return [r["month"] for r in rows]
 
# ── LOCAL DEV ─────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
 
init_db()
