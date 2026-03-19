from typing import List, Dict, Any, Annotated, TypedDict
import operator

class PaperState(TypedDict):
    all_papers: List[Dict[str, Any]]  # Raw papers fetched
    new_papers: List[Dict[str, Any]]  # Papers not in cache
    scored_papers: List[Dict[str, Any]] # Papers with relevance scores
    top_papers: List[Dict[str, Any]]    # Top-tier papers for detailed summary
    ai_papers: List[Dict[str, Any]]     # AI general progress papers (top 10)
    bio_papers: List[Dict[str, Any]]    # AI4S bio-related papers (relevance >= 7)
    report_path: str                  # Final MD report path

