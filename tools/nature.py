import feedparser
import re
from typing import List, Dict, Any
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

    def fetch(self) -> List[Dict[str, Any]]:
        results = []
        seen_links = set()
        for journal, url in self.NATURE_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if entry.link in seen_links or not self.is_research_article(entry):
                        continue
                    
                    summary = entry.get('summary', '') or entry.get('description', '')
                    clean_summary = re.sub(r'<[^>]+>', '', summary)
                    search_text = f"{entry.title} {clean_summary}"
                    # For Nature, we bypass the strict keyword matching requirement
                    # because Nature abstracts are often too short to hit multiple keywords.
                    # We add a fake keyword 'Nature_Bypass' so it survives the config.py pre-filter if enabled.
                    results.append({
                        "journal": journal,
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get('published', 'N/A'),
                        "matches": ["Nature_Bypass"] * 5,  # Give it enough matches to pass any threshold
                        "summary": clean_summary[:1000]
                    })
                    seen_links.add(entry.link)
            except Exception as e:
                print(f"Error fetching {journal}: {e}")
        return results
