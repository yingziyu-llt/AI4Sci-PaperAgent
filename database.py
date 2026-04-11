import sqlite3
import os
from .config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS processed_papers (
                paper_id TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def is_paper_seen(paper_id: str) -> bool:
    """Check if a paper ID has already been processed."""
    if not paper_id:
        return False
    with get_db_connection() as conn:
        cur = conn.execute('SELECT 1 FROM processed_papers WHERE paper_id = ?', (paper_id,))
        return cur.fetchone() is not None

def mark_papers_seen(paper_ids: list[str]):
    """Mark multiple paper IDs as processed."""
    if not paper_ids:
        return
    with get_db_connection() as conn:
        conn.executemany(
            'INSERT OR IGNORE INTO processed_papers (paper_id) VALUES (?)',
            [(pid,) for pid in paper_ids]
        )
        conn.commit()

def get_all_seen_ids() -> list[str]:
    """Retrieve all seen paper IDs."""
    with get_db_connection() as conn:
        cur = conn.execute('SELECT paper_id FROM processed_papers')
        return [row['paper_id'] for row in cur.fetchall()]
