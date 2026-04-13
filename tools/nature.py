import feedparser
import re
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseFetcher

class NatureFetcher(BaseFetcher):
    NATURE_FEEDS = {
        "Nature": "https://www.nature.com/nature.rss",
        "Nature Methods": "https://www.nature.com/nmeth.rss",
        "Nature Biotechnology": "https://www.nature.com/nbt.rss",
        "Nature Machine Intelligence": "https://www.nature.com/natmachintell.rss",
        "Nature Communications": "https://www.nature.com/ncomms.rss",
        "Nature Biomedical Engineering": "https://www.nature.com/natbiomedeng.rss",
        "Nature Genetics": "https://www.nature.com/ng.rss",
        "Nature Chemical Biology": "https://www.nature.com/nchembio.rss",
        "Nature Chemistry": "https://www.nature.com/nchem.rss",
    }

    def is_research_article(self, entry) -> bool:
        link = entry.link
        if "/articles/d" in link:
            return False
        title = entry.title.lower()
        noise_prefixes = [
            "editorial:", "news:", "q&a:", "correspondence:", "obituary:", 
            "comment:", "author correction:", "publisher correction:",
            "news & views:", "books & arts:", "career:", "briefing chat:"
        ]
        if any(title.startswith(prefix) for prefix in noise_prefixes):
            return False
        return True

    def _fetch_feed(self, journal: str, url: str, seen_links: set, lock: threading.Lock) -> List[Dict[str, Any]]:
        papers = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                with lock:
                    if entry.link in seen_links or not self.is_research_article(entry):
                        continue
                    seen_links.add(entry.link)
                
                summary = entry.get('summary', '') or entry.get('description', '')
                clean_summary = re.sub(r'<[^>]+>', '', summary)

                authors = [a.get('name', '') for a in entry.get('authors', [])]
                authors_str = ", ".join(authors) if authors else entry.get('author', 'Unknown')

                papers.append({
                    "journal": journal,
                    "title": entry.title,
                    "authors": authors_str,
                    "link": entry.link,
                    "published": entry.get('published', 'N/A'),
                    "matches": ["Nature_Bypass"] * 5,
                    "summary": clean_summary[:1000]
                })
        except Exception as e:
            print(f"Error fetching Nature {journal}: {e}")
        return papers

    def fetch(self) -> List[Dict[str, Any]]:
        seen_links = set()
        lock = threading.Lock()
        all_papers = []
        
        with ThreadPoolExecutor(max_workers=len(self.NATURE_FEEDS)) as executor:
            future_to_feed = {
                executor.submit(self._fetch_feed, journal, url, seen_links, lock): journal 
                for journal, url in self.NATURE_FEEDS.items()
            }
            for future in as_completed(future_to_feed):
                all_papers.extend(future.result())
                
        return all_papers
