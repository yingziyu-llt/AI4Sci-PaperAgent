import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import BaseFetcher

class BiorxivFetcher(BaseFetcher):
    def fetch(self, days: int = 3) -> List[Dict[str, Any]]:
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=days)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")

        all_papers = []
        cursor = 0
        while True:
            url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{cursor}"
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code != 200:
                    break
                data = resp.json()
                if "collection" not in data or not data["collection"]:
                    break
                
                papers_batch = data["collection"]
                total_expected = int(data["messages"][0]["total"])
                
                for item in papers_batch:
                    title = item.get("title", "").strip()
                    abstract = item.get("abstract", "").strip()
                    content_to_search = f"{title} {abstract}"
                    matches = self.get_matches(content_to_search)
                    
                    if matches:
                        all_papers.append({
                            "journal": "bioRxiv",
                            "title": title,
                            "link": f"https://www.biorxiv.org/content/{item.get('doi')}v1",
                            "published": item.get("date"),
                            "doi": item.get("doi"),
                            "category": item.get("category"),
                            "summary": abstract,
                            "matches": matches
                        })
                
                cursor += len(papers_batch)
                if cursor >= total_expected:
                    break
                time.sleep(2)
            except Exception as e:
                print(f"Error fetching bioRxiv: {e}")
                break
        return all_papers
