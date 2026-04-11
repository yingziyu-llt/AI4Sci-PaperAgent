from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from daily_paper_agent.state import PaperState
from daily_paper_agent.tools.arxiv import ArxivFetcher
from daily_paper_agent.tools.nature import NatureFetcher
from daily_paper_agent.tools.biorxiv import BiorxivFetcher
from daily_paper_agent.utils import load_cache, is_new
from daily_paper_agent.keywords import KEYWORDS

def fetch_node(state: PaperState) -> Dict[str, Any]:
    print("--- FETCHING PAPERS (PARALLEL) ---")
    
    arxiv = ArxivFetcher(KEYWORDS)
    nature = NatureFetcher(KEYWORDS)
    biorxiv = BiorxivFetcher(KEYWORDS)
    
    all_papers = []
    
    # Run all fetchers in parallel
    fetchers = [arxiv, nature, biorxiv]
    with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
        futures = [executor.submit(f.fetch) for f in fetchers]
        for future in as_completed(futures):
            try:
                all_papers.extend(future.result())
            except Exception as e:
                print(f"Fetcher node parallel error: {e}")
    
    cache = load_cache()
    new_papers = [p for p in all_papers if is_new(p, cache)]
    
    print(f"Fetched {len(all_papers)} total candidate papers.")
    print(f"Found {len(new_papers)} new papers.")
    
    return {"all_papers": all_papers, "new_papers": new_papers}
