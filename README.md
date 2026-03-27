# 🚀 Job Scraper & Alert System

An automated **job aggregation and alert system** that scrapes multiple job platforms, filters relevant opportunities, removes duplicates, and sends a **digest email with Excel attachment**.

---

## 🔥 Features

* 🔍 Multi-keyword job search (Python, Backend, AI, etc.)
* 🌐 Multi-platform scraping (Internshala, Indeed, Wellfound)
* 🧠 Smart filtering (removes irrelevant roles like marketing, HR, etc.)
* 🗂️ SQLite database for deduplication
* ⏱️ Scheduler for periodic execution
* 📧 Email alerts (digest format, not spam)
* 📊 Excel report attachment

---

## 🧩 Tech Stack

* **Python**
* **Requests + BeautifulSoup**
* **Playwright (for JS-heavy sites)**
* **SQLite**
* **smtplib (Email automation)**
* **Schedule (cron-like automation)**

---

## ⚙️ Project Structure

```
job-scraper/
├── core/
│   ├── storage.py        # DB + deduplication
│   └── notifier.py       # Email alerts
├── scrapers/
│   ├── internshala.py
│   ├── indeed.py
│   └── wellfound.py
├── main.py               # Main pipeline
├── scheduler.py          # Runs periodically
├── requirements.txt
└── jobs.db               # Local database (ignored)
```

---

## 🚀 How It Works

1. Scrapes jobs from multiple platforms
2. Filters irrelevant and duplicate jobs
3. Stores new jobs in SQLite DB
4. Sends a **single digest email** with all new jobs

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python main.py
```

---

## ⏱️ Run Automatically

```bash
python scheduler.py
```

---

## 🔐 Setup Email Alerts

* Enable **2-Step Verification** in Gmail
* Generate **App Password**
* Add credentials in `notifier.py`

---

## 🎯 Use Case

* Job seekers looking for automated alerts
* Developers learning web scraping + automation
* Building real-world data pipelines

---
