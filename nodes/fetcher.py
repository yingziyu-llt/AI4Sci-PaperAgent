from typing import List, Dict, Any
from daily_paper_agent.state import PaperState
from daily_paper_agent.tools.arxiv import ArxivFetcher
from daily_paper_agent.tools.nature import NatureFetcher
from daily_paper_agent.tools.biorxiv import BiorxivFetcher
from daily_paper_agent.utils import load_cache, is_new
from daily_paper_agent.keywords import KEYWORDS

def fetch_node(state: PaperState) -> Dict[str, Any]:
    print("--- FETCHING PAPERS ---")
    
    arxiv = ArxivFetcher(KEYWORDS)
    nature = NatureFetcher(KEYWORDS)
    biorxiv = BiorxivFetcher(KEYWORDS)
    
    all_papers = []
    all_papers.extend(arxiv.fetch())
    all_papers.extend(nature.fetch())
    all_papers.extend(biorxiv.fetch())
    
    cache = load_cache()
    new_papers = [p for p in all_papers if is_new(p, cache)]
    
    print(f"Fetched {len(all_papers)} total candidate papers.")
    print(f"Found {len(new_papers)} new papers.")
    
    return {"all_papers": all_papers, "new_papers": new_papers}
