# Personal Finance Tracker

A fully client-side personal finance tracker — no backend, no server required.  
Built with HTML, CSS, JavaScript, and Chart.js.

## ✅ What was fixed

| Problem | Fix |
|---|---|
| FastAPI + SQLite can't run on Vercel (serverless, no filesystem) | Removed backend entirely |
| Vercel deployment was broken | Now pure static HTML — deploys anywhere |
| Data lost on refresh (serverless has no DB) | `localStorage` persistence |
| No responsive layout | Fully mobile-responsive |
| XSS vulnerability in innerHTML | `escHtml()` sanitization added |
| Negative balance showed wrong sign | Fixed with `Math.abs()` + label |
| Month filter not reset after delete | `rebuildMonthSelect()` called on every change |

## Features

- Add income & expense transactions
- Summary cards: Total Income, Expenses, Net Balance
- Interactive doughnut chart by spending category
- Monthly filter
- Export to CSV
- Filter by income / expense / all
- Data persists in `localStorage` (survives page refresh)
- Demo data pre-loaded on first visit
- Fully responsive (mobile + desktop)

## Tech Stack

- **Frontend:** HTML5, CSS3 (CSS Variables), Vanilla JavaScript
- **Chart:** Chart.js (CDN)
- **Storage:** Browser localStorage
- **Fonts:** Inter (Google Fonts)

## Deploy to Vercel (Free)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy (from this folder)
vercel

# Done — live URL in seconds!
```

Or drag-and-drop the folder at **vercel.com/new**.

## Deploy to GitHub Pages

1. Push this folder to a GitHub repo
2. Go to Settings → Pages
3. Set Source to `main` branch, `/ (root)`
4. Your site is live at `https://<username>.github.io/<repo>/`

## Author

Piyush Jha — [LinkedIn](https://linkedin.com/in/piyushjha2003) | [Portfolio](https://piyush-jha-portfolio-html.vercel.app)
