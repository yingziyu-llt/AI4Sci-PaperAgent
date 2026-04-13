import requests
import feedparser
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseFetcher

class ArxivFetcher(BaseFetcher):
    ARXIV_CATEGORIES = [
        "cs.LG", "cs.AI", "cs.CV", "q-bio.BM", "q-bio.GN", "q-bio.QM", "q-bio.MN", "physics.chem-ph", "stat.ML"
    ]

    def _fetch_category_api(self, cat: str, seen_ids: set, lock: threading.Lock, max_results: int = 50) -> List[Dict[str, Any]]:
        papers = []
        # Use Arxiv API instead of RSS for better reliability and more results
        url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"Error fetching Arxiv API {cat}: status {resp.status_code}")
                return papers
            
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                paper_id = entry.id.split('/abs/')[-1] # Extract ID
                
                with lock:
                    if paper_id in seen_ids:
                        continue
                    seen_ids.add(paper_id)
                
                summary = entry.get('summary', '') or entry.get('description', '')
                search_text = f"{entry.title} {summary}"
                matches = self.get_matches(search_text)
                
                if not matches:
                    continue
                
                # Arxiv API date format: 2024-03-21T18:00:00Z
                date_str = entry.get('published', '')[:10]
                
                authors = [a.get('name', '') for a in entry.get('authors', [])]
                authors_str = ", ".join(authors) if authors else entry.get('author', 'Unknown')
                
                papers.append({
                    "journal": f"arXiv ({cat})",
                    "title": entry.title,
                    "authors": authors_str,
                    "link": entry.link,
                    "published": date_str,
                    "summary": summary,
                    "id": paper_id,
                    "matches": matches
                })
        except Exception as e:
            print(f"Error fetching Arxiv API {cat}: {e}")
        return papers

    def fetch(self, max_results_per_cat: int = 50) -> List[Dict[str, Any]]:
        seen_ids = set()
        lock = threading.Lock()
        all_papers = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_cat = {
                executor.submit(self._fetch_category_api, cat, seen_ids, lock, max_results_per_cat): cat 
                for cat in self.ARXIV_CATEGORIES
            }
            for future in as_completed(future_to_cat):
                all_papers.extend(future.result())
                
        return all_papers
