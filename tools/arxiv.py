import feedparser
from typing import List, Dict, Any
from .base import BaseFetcher

class ArxivFetcher(BaseFetcher):
    ARXIV_CATEGORIES = [
        "cs.LG", "cs.AI", "cs.CV", "q-bio.BM", "q-bio.GN", "q-bio.QM", "q-bio.MN", "physics.chem-ph", "stat.ML"
    ]

    def fetch(self) -> List[Dict[str, Any]]:
        seen_ids = set()
        all_papers = []
        for cat in self.ARXIV_CATEGORIES:
            url = f"https://rss.arxiv.org/rss/{cat}"
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    paper_id = entry.id
                    if paper_id in seen_ids:
                        continue
                    
                    summary = entry.get('summary', '') or entry.get('description', '')
                    search_text = f"{entry.title} {summary}"
                    matches = self.get_matches(search_text)
                    
                    if not matches:
                        continue
                    
                    date_str = entry.get('updated', entry.get('published', ''))[:10]
                    all_papers.append({
                        "journal": f"arXiv ({cat})",
                        "title": entry.title,
                        "link": entry.link,
                        "published": date_str,
                        "summary": summary,
                        "id": paper_id,
                        "matches": matches
                    })
                    seen_ids.add(paper_id)
            except Exception as e:
                print(f"Error fetching {cat}: {e}")
        return all_papers
