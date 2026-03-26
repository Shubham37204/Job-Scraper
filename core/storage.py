import sqlite3

def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            link TEXT UNIQUE,   -- UNIQUE prevents duplicate URLs
            posted TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_new_job(link):
    """Returns True if this job URL hasn't been seen before"""
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM jobs WHERE link = ?", (link,))
    result = cursor.fetchone() is None
    conn.close()
    return result

def save_job(job):
    """Saves a job dict to the DB"""
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO jobs (title, company, link, posted, source)
        VALUES (?, ?, ?, ?, ?)
    """, (job['title'], job['company'], job['link'], job['posted'], job['source']))
    
    conn.commit()
    conn.close()