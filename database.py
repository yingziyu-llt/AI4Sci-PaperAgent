import sqlite3
import os
import json
import numpy as np
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
        # Store full paper info for feedback lookup
        conn.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                paper_id TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                journal TEXT,
                link TEXT,
                embedding BLOB,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # label: 1 for like, -1 for dislike
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                paper_id TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                label INTEGER, 
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_paper(paper_id: str, title: str, abstract: str, journal: str, link: str, score: float, embedding: np.ndarray = None):
    """Save paper details for later retrieval."""
    embedding_blob = embedding.tobytes() if embedding is not None else None
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO papers (paper_id, title, abstract, journal, link, score, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (paper_id, title, abstract, journal, link, score, embedding_blob))
        conn.commit()

def get_paper(paper_id: str):
    """Retrieve paper details by ID."""
    with get_db_connection() as conn:
        cur = conn.execute('SELECT * FROM papers WHERE paper_id = ?', (paper_id,))
        return cur.fetchone()

def get_papers_by_ids(paper_ids: list[str]):
    """Retrieve multiple papers by IDs."""
    if not paper_ids:
        return []
    placeholders = ', '.join(['?'] * len(paper_ids))
    with get_db_connection() as conn:
        cur = conn.execute(f'SELECT * FROM papers WHERE paper_id IN ({placeholders})', paper_ids)
        return cur.fetchall()

def save_feedback(paper_id: str, title: str, abstract: str, label: int, embedding: np.ndarray = None):
    """Save or update user feedback for a paper."""
    embedding_blob = embedding.tobytes() if embedding is not None else None
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO user_feedback (paper_id, title, abstract, label, embedding)
            VALUES (?, ?, ?, ?, ?)
        ''', (paper_id, title, abstract, label, embedding_blob))
        conn.commit()

def get_all_feedback():
    """Retrieve all user feedback with embeddings."""
    with get_db_connection() as conn:
        cur = conn.execute('SELECT paper_id, title, abstract, label, embedding FROM user_feedback')
        rows = cur.fetchall()
        results = []
        for row in rows:
            embedding = np.frombuffer(row['embedding'], dtype=np.float32) if row['embedding'] else None
            results.append({
                "paper_id": row['paper_id'],
                "title": row['title'],
                "abstract": row['abstract'],
                "label": row['label'],
                "embedding": embedding
            })
        return results

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
