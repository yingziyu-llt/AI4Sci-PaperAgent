import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseFetcher

class BiorxivFetcher(BaseFetcher):
    def _fetch_server(self, server: str, days: int) -> List[Dict[str, Any]]:
        """Fetch papers from a specific server (biorxiv or medrxiv)."""
        all_papers = []
        
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=days)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")
        
        cursor = 0
        # Format: https://api.biorxiv.org/details/[server]/[start_date]/[end_date]/[cursor]/json
        while True:
            url = f"https://api.biorxiv.org/details/{server}/{start_date}/{end_date}/{cursor}/json"
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    resp = requests.get(url, timeout=20)
                    if resp.status_code == 200:
                        data = resp.json()
                        break
                    elif resp.status_code == 429:
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        print(f"Error fetching {server} (status {resp.status_code}): {url}")
                        return all_papers
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Final error fetching {server}: {e}")
                        return all_papers
                    time.sleep(1)

            messages = data.get("messages", [])
            if not messages or messages[0].get("status") != "ok":
                break

            collection = data.get("collection", [])
            if not collection:
                break
            
            total_expected = int(messages[0].get("total", 0))
            
            for item in collection:
                title = item.get("title", "").strip()
                abstract = item.get("abstract", "").strip()
                content_to_search = f"{title} {abstract}"
                matches = self.get_matches(content_to_search)
                
                if matches:
                    version = item.get("version", "1")
                    doi = item.get("doi")
                    journal_name = "bioRxiv" if server == "biorxiv" else "medRxiv"
                    
                    authors = item.get("authors", "")
                    author_corresponding = item.get("author_corresponding", "")
                    institution = item.get("author_corresponding_institution", "")
                    
                    author_info = authors
                    if author_corresponding:
                        author_info += f" (Corresponding: {author_corresponding}"
                        if institution:
                            author_info += f", {institution}"
                        author_info += ")"
                    
                    all_papers.append({
                        "journal": journal_name,
                        "title": title,
                        "authors": author_info,
                        "link": f"https://www.{server}.org/content/{doi}v{version}",
                        "published": item.get("date"),
                        "doi": doi,
                        "category": item.get("category"),
                        "summary": abstract,
                        "matches": matches
                    })
            
            cursor += len(collection)
            if cursor >= total_expected or len(collection) == 0:
                break
            
            # Rate limiting compliance
            time.sleep(0.5)
            
        return all_papers

    def fetch(self, days: int = 3) -> List[Dict[str, Any]]:
        all_papers = []
        # Parallelize fetching from biorxiv and medrxiv
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_server = {
                executor.submit(self._fetch_server, server, days): server 
                for server in ["biorxiv", "medrxiv"]
            }
            for future in as_completed(future_to_server):
                try:
                    all_papers.extend(future.result())
                except Exception as e:
                    server = future_to_server[future]
                    print(f"Parallel fetch error for {server}: {e}")
        return all_papers
