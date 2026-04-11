import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from .config import SENDER_EMAIL, AUTH_CODE, RECEIVER_EMAIL
from .database import init_db, is_paper_seen, mark_papers_seen, get_all_seen_ids
import os
from typing import List, Dict, Any
import httpx  # 确保在文件顶部导入


CACHE_FILE = "paper_cache.json"

# Initialize database
init_db()

def load_cache() -> List[str]:
    # Migration step: Check if old JSON cache exists
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                old_ids = data.get("processed_ids", [])
                if old_ids:
                    mark_papers_seen(old_ids)
                    print(f"Migrated {len(old_ids)} IDs from {CACHE_FILE} to database.")
            # Rename or remove old cache file to prevent repeated migration
            os.rename(CACHE_FILE, CACHE_FILE + ".bak")
        except Exception as e:
            print(f"Migration error: {e}")
    
    return get_all_seen_ids()

def update_cache(new_ids: List[str]):
    mark_papers_seen(new_ids)

def is_new(paper: Dict[str, Any], cache: List[str] = None) -> bool:
    paper_id = paper.get("doi") or paper.get("id") or paper.get("link")
    if cache is not None:
        # If cache is provided (from load_cache), use it for efficiency in batch processing
        return paper_id not in cache
    # Otherwise, check the database directly
    return not is_paper_seen(paper_id)
