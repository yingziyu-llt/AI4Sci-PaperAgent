import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from .config import SENDER_EMAIL, AUTH_CODE, RECEIVER_EMAIL
import os
from typing import List, Dict, Any
import httpx  # 确保在文件顶部导入


CACHE_FILE = "paper_cache.json"

def load_cache() -> List[str]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f).get("processed_ids", [])
            except:
                return []
    return []

def update_cache(new_ids: List[str]):
    cache = load_cache()
    updated_cache = list(set(cache + new_ids))
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({"processed_ids": updated_cache}, f, indent=2)

def is_new(paper: Dict[str, Any], cache: List[str]) -> bool:
    paper_id = paper.get("doi") or paper.get("id") or paper.get("link")
    return paper_id not in cache
