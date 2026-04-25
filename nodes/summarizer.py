import asyncio
from typing import Dict, Any, List
from daily_paper_agent.state import PaperState
from daily_paper_agent.llm import get_llm
from daily_paper_agent.schemas import PaperSummary
from daily_paper_agent.config import MIN_RELEVANCE_SCORE
from daily_paper_agent.tools.pdf_downloader import download_and_extract_pdf

# Bio-relevance threshold for classifying into AI4S bio section
BIO_RELEVANCE_THRESHOLD = 7


async def summarize_node(state: PaperState) -> Dict[str, Any]:
    scored_papers = state["scored_papers"]
    qualified_papers = [sp for sp in scored_papers if sp["score"] >= MIN_RELEVANCE_SCORE]
    qualified_papers.sort(key=lambda x: x["score"], reverse=True)
    
    if not qualified_papers:
        return {"top_papers": [], "ai_papers": [], "bio_papers": []}

    # --- Classify papers into two sections ---
    bio_papers = []
    ai_papers = []
    
    for sp in qualified_papers:
        dims = sp.get("dimension_scores", {})
        rel_bio = dims.get("relevance_bio", 0)
        rel_ai = dims.get("relevance_ai", 0)
        
        if rel_bio >= BIO_RELEVANCE_THRESHOLD:
            bio_papers.append(sp)
        elif rel_ai >= BIO_RELEVANCE_THRESHOLD:
            ai_papers.append(sp)
    
    # AI and Bio papers: max 10 each
    ai_papers = ai_papers[:10]
    bio_papers = bio_papers[:10]
    
    # Combine for summarization
    all_to_summarize = bio_papers + ai_papers
    
    print(f"--- SUMMARIZING {len(all_to_summarize)} PAPERS ---")
    print(f"  🤖 AI General: {len(ai_papers)} papers")
    print(f"  🧬 AI4S Bio:   {len(bio_papers)} papers")
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(PaperSummary, include_raw=False)
    
    semaphore = asyncio.Semaphore(5)  # Limit concurrent PDF downloads & LLM calls
    
    async def summarize_paper(sp):
        async with semaphore:
            p = sp["paper"]
            print(f"Summarizing: {p['title'][:60]}...")
            
            # Try to download and extract PDF for deeper summarization
            pdf_text = None
            try:
                pdf_text = await asyncio.to_thread(
                    download_and_extract_pdf, 
                    p.get("link", ""), 
                    p.get("journal", "")
                )
            except Exception as e:
                print(f"  PDF extraction failed for {p['title'][:40]}: {e}")
            
            # Build prompt with full text or fallback to abstract
            if pdf_text:
                content_source = "论文全文（截取）"
                paper_content = pdf_text
            else:
                content_source = "摘要"
                paper_content = p.get('summary', '')
            
            system_prompt = (
                "你是一位专业的AI for Science领域论文分析专家。请根据以下论文内容，"
                "从三个维度进行深度总结：核心创新（innovation）、技术方法（methodology）、关键结果（key_result）。"
                "所有内容必须使用中文输出，但JSON键名保持英文。"
                "总结应当深入具体，包含关键技术细节、数据规模、性能指标等。"
            )
            prompt = f"""论文标题: {p['title']}
信息来源: {content_source}

{paper_content}"""
            
            try:
                summary = await structured_llm.ainvoke([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ])
                sp["detailed_summary"] = summary
                sp["used_pdf"] = bool(pdf_text)
            except Exception as e:
                print(f"Error summarizing paper {p['title'][:50]}: {e}")
                sp["used_pdf"] = False
                
    tasks = [summarize_paper(sp) for sp in all_to_summarize]
    await asyncio.gather(*tasks)

    # top_papers is kept for backward compatibility
    return {
        "top_papers": all_to_summarize,
        "ai_papers": ai_papers,
        "bio_papers": bio_papers
    }
