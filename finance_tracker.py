from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import csv
import io

app = FastAPI()

def init_db():
    conn = sqlite3.connect("finance.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn

class Transaction(BaseModel):
    title: str
    amount: float
    category: str
    type: str
    date: str

@app.get("/transactions")
def get_transactions(month: Optional[str] = Query(None)):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC",
            (month,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
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
    income = sum(r["amount"] for r in rows if r["type"] == "income")
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
        rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
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

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Finance Tracker</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }
header {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #2a2a4a;
}
header h1 { font-size: 24px; color: #a78bfa; font-weight: 600; letter-spacing: 1px; }
.header-right { display: flex; align-items: center; gap: 12px; }
header span { font-size: 13px; color: #666; }
.month-select {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 7px 12px;
  color: #a78bfa;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}
.month-select:focus { border-color: #a78bfa; }
.export-btn {
  background: linear-gradient(135deg, #065f46, #34d399);
  border: none;
  border-radius: 8px;
  padding: 7px 14px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.export-btn:hover { opacity: 0.85; }
.container { max-width: 1100px; margin: 0 auto; padding: 30px 20px; }
.filter-bar {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.filter-bar span { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.filter-pill {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #2a2a4a;
  background: transparent;
  color: #888;
  transition: all 0.2s;
}
.filter-pill:hover { border-color: #a78bfa; color: #a78bfa; }
.filter-pill.active { background: #a78bfa; color: white; border-color: #a78bfa; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
.card {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #2a2a4a;
  transition: transform 0.2s;
}
.card:hover { transform: translateY(-4px); }
.card .label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.card .value { font-size: 32px; font-weight: 700; }
.card.income .value { color: #34d399; }
.card.expense .value { color: #f87171; }
.card.balance .value { color: #a78bfa; }
.card .icon { font-size: 28px; float: right; margin-top: -10px; }
.card .sub { font-size: 11px; color: #555; margin-top: 8px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
.panel {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #2a2a4a;
}
.panel h2 { font-size: 15px; color: #a78bfa; margin-bottom: 20px; font-weight: 500; }
.form-group { margin-bottom: 14px; }
.form-group label { font-size: 12px; color: #888; display: block; margin-bottom: 6px; }
.form-group input, .form-group select {
  width: 100%;
  background: #0f0f1a;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 10px 14px;
  color: #e0e0e0;
  font-size: 14px;
  outline: none;
  transition: border 0.2s;
}
.form-group input:focus, .form-group select:focus { border-color: #a78bfa; }
.btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 6px;
  transition: opacity 0.2s;
}
.btn:hover { opacity: 0.85; }
.tx-list { max-height: 340px; overflow-y: auto; }
.tx-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #1e1e3a;
}
.tx-item:last-child { border-bottom: none; }
.tx-left .tx-title { font-size: 14px; font-weight: 500; }
.tx-left .tx-meta { font-size: 11px; color: #666; margin-top: 2px; }
.tx-right { text-align: right; }
.tx-amount { font-size: 15px; font-weight: 600; }
.tx-amount.income { color: #34d399; }
.tx-amount.expense { color: #f87171; }
.tx-delete {
  font-size: 11px;
  margin-top: 3px;
  display: block;
  background: none;
  border: none;
  color: #f87171;
  cursor: pointer;
}
.tx-delete:hover { color: #ff5555; }
.tag {
  display: inline-block;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 20px;
  margin-top: 4px;
  font-weight: 500;
}
.tag-income { background: #064e3b; color: #34d399; }
.tag-expense { background: #450a0a; color: #f87171; }
.empty { color: #555; font-size: 13px; text-align: center; padding: 30px 0; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #3a3a5a; border-radius: 4px; }
</style>
</head>
<body>
<header>
  <h1>&#x1F4B0; Finance Tracker</h1>
  <div class="header-right">
    <select class="month-select" id="month-filter" onchange="applyMonthFilter()">
      <option value="">All Time</option>
    </select>
    <button class="export-btn" onclick="exportCSV()">&#x2B07; Export CSV</button>
    <span id="date-display"></span>
  </div>
</header>
<div class="container">
  <div class="filter-bar">
    <span>Filter:</span>
    <button class="filter-pill active" onclick="setFilter('all', this)">All</button>
    <button class="filter-pill" onclick="setFilter('income', this)">Income only</button>
    <button class="filter-pill" onclick="setFilter('expense', this)">Expenses only</button>
  </div>
  <div class="cards">
    <div class="card income">
      <div class="label">Total Income</div>
      <span class="icon">&#x1F4C8;</span>
      <div class="value" id="total-income">&#x20B9;0</div>
      <div class="sub" id="income-count">0 transactions</div>
    </div>
    <div class="card expense">
      <div class="label">Total Expenses</div>
      <span class="icon">&#x1F4C9;</span>
      <div class="value" id="total-expense">&#x20B9;0</div>
      <div class="sub" id="expense-count">0 transactions</div>
    </div>
    <div class="card balance">
      <div class="label">Net Balance</div>
      <span class="icon">&#x1F48E;</span>
      <div class="value" id="net-balance">&#x20B9;0</div>
      <div class="sub" id="balance-label">&#x2014;</div>
    </div>
  </div>
  <div class="grid2">
    <div class="panel">
      <h2>Add Transaction</h2>
      <div class="form-group">
        <label>Title</label>
        <input type="text" id="title" placeholder="e.g. Salary, Rent...">
      </div>
      <div class="form-group">
        <label>Amount (&#x20B9;)</label>
        <input type="number" id="amount" placeholder="0.00">
      </div>
      <div class="form-group">
        <label>Category</label>
        <select id="category">
          <option>Salary</option>
          <option>Food</option>
          <option>Transport</option>
          <option>Shopping</option>
          <option>Bills</option>
          <option>Entertainment</option>
          <option>Health</option>
          <option>Other</option>
        </select>
      </div>
      <div class="form-group">
        <label>Type</label>
        <select id="type">
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
      </div>
      <div class="form-group">
        <label>Date</label>
        <input type="date" id="date">
      </div>
      <button class="btn" onclick="addTransaction()">+ Add Transaction</button>
    </div>
    <div class="panel">
      <h2>Spending Chart</h2>
      <canvas id="chart" height="260"></canvas>
    </div>
  </div>
  <div class="panel">
    <h2>Transactions <span id="tx-count" style="color:#555;font-size:12px;font-weight:400;"></span></h2>
    <div class="tx-list" id="tx-list">
      <p class="empty">No transactions yet.</p>
    </div>
  </div>
</div>
<script>
const today = new Date();
document.getElementById("date").valueAsDate = today;
document.getElementById("date-display").textContent = today.toDateString();

let chart;
let currentMonth = "";
let currentFilter = "all";
let allTransactions = [];

// ── helper: format with Indian Rupee symbol + en-IN locale ──
function inr(amount) {
  return "\u20B9" + amount.toLocaleString('en-IN');
}

async function loadMonths() {
  const months = await fetch("/months").then(r => r.json());
  const sel = document.getElementById("month-filter");
  months.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    const [y, mo] = m.split("-");
    const d = new Date(y, mo - 1);
    opt.textContent = d.toLocaleString("default", { month: "long", year: "numeric" });
    sel.appendChild(opt);
  });
}

async function loadData() {
  const url = currentMonth ? `?month=${currentMonth}` : "";
  const [summary, transactions] = await Promise.all([
    fetch("/summary" + url).then(r => r.json()),
    fetch("/transactions" + url).then(r => r.json())
  ]);
  allTransactions = transactions;

  // ── FIXED: use inr() for all currency values ──
  document.getElementById("total-income").textContent = inr(summary.income);
  document.getElementById("total-expense").textContent = inr(summary.expense);
  document.getElementById("net-balance").textContent = inr(summary.balance);

  const incomeCount = transactions.filter(t => t.type === "income").length;
  const expenseCount = transactions.filter(t => t.type === "expense").length;
  document.getElementById("income-count").textContent = incomeCount + " transactions";
  document.getElementById("expense-count").textContent = expenseCount + " transactions";
  document.getElementById("balance-label").textContent = summary.balance >= 0 ? "Positive \u2713" : "Negative \u2717";

  applyFilterRender();
  renderChart(transactions);
}

function applyFilterRender() {
  let filtered = allTransactions;
  if (currentFilter === "income") filtered = allTransactions.filter(t => t.type === "income");
  if (currentFilter === "expense") filtered = allTransactions.filter(t => t.type === "expense");
  renderTransactions(filtered);
  document.getElementById("tx-count").textContent = "\u2014 " + filtered.length + " shown";
}

function setFilter(type, el) {
  currentFilter = type;
  document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
  el.classList.add("active");
  applyFilterRender();
}

function applyMonthFilter() {
  currentMonth = document.getElementById("month-filter").value;
  loadData();
}

function exportCSV() {
  const url = currentMonth ? `/export?month=${currentMonth}` : "/export";
  window.location.href = url;
}

function renderTransactions(list) {
  const el = document.getElementById("tx-list");
  if (!list.length) {
    el.innerHTML = '<p class="empty">No transactions found.</p>';
    return;
  }
  el.innerHTML = list.map(t => `
    <div class="tx-item">
      <div class="tx-left">
        <div class="tx-title">${t.title}</div>
        <div class="tx-meta">${t.date} &nbsp;&bull;&nbsp; ${t.category}</div>
        <span class="tag tag-${t.type}">${t.type}</span>
      </div>
      <div class="tx-right">
        <div class="tx-amount ${t.type}">${t.type === "income" ? "+" : "-"}${inr(t.amount)}</div>
        <button class="tx-delete" onclick="deleteTransaction(${t.id})">&#x2715; remove</button>
      </div>
    </div>
  `).join("");
}

function renderChart(transactions) {
  const cats = {};
  transactions.filter(t => t.type === "expense").forEach(t => {
    cats[t.category] = (cats[t.category] || 0) + t.amount;
  });
  const labels = Object.keys(cats);
  const data = Object.values(cats);
  const colors = ["#a78bfa","#f87171","#34d399","#60a5fa","#fbbf24","#f472b6","#818cf8","#a3e635"];

  if (chart) chart.destroy();
  chart = new Chart(document.getElementById("chart"), {
    type: "doughnut",
    data: {
      labels: labels.length ? labels : ["No expenses"],
      datasets: [{ data: data.length ? data : [1], backgroundColor: colors, borderWidth: 0 }]
    },
    options: {
      plugins: {
        legend: { labels: { color: "#aaa", font: { size: 11 }, boxWidth: 12 } },
        tooltip: {
          callbacks: {
            // ── FIXED: tooltip also uses en-IN ──
            label: ctx => " " + inr(ctx.parsed)
          }
        }
      },
      cutout: "65%"
    }
  });
}

async function addTransaction() {
  const title = document.getElementById("title").value.trim();
  const amount = parseFloat(document.getElementById("amount").value);
  const category = document.getElementById("category").value;
  const type = document.getElementById("type").value;
  const date = document.getElementById("date").value;

  if (!title || !amount || !date) { alert("Please fill all fields!"); return; }

  await fetch("/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, amount, category, type, date })
  });

  document.getElementById("title").value = "";
  document.getElementById("amount").value = "";
  await loadMonths();
  loadData();
}

async function deleteTransaction(id) {
  await fetch("/transactions/" + id, { method: "DELETE" });
  loadData();
}

loadMonths().then(() => loadData());
</script>
</body>
</html>
"""

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
