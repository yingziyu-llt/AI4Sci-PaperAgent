import asyncio
import re
from typing import Dict, Any, List
from daily_paper_agent.state import PaperState
from daily_paper_agent.llm import get_llm
from daily_paper_agent.schemas import BatchEvaluation
from daily_paper_agent.config import MAX_PAPERS_PER_BATCH, ENABLE_PRE_FILTER, PRE_FILTER_KEYWORD_THRESHOLD
from daily_paper_agent.keywords import get_all_keywords

async def score_batch_async(structured_llm, batch, batch_idx, system_prompt):
    """异步处理单个批次的评分"""
    print(f"Scoring batch {batch_idx + 1}...")
    
    batch_text = ""
    for idx, p in enumerate(batch):
        journal = f"\nJournal: {p.get('journal', 'Unknown')}" if p.get('journal') else ""
        batch_text += f"ID: {idx}\nTitle: {p['title']}{journal}\nAbstract: {p.get('summary', '')[:500]}\n---\n"

    prompt = f"Evaluate these papers:\n{batch_text}"
    
    try:
        # 使用 ainvoke 进行异步调用
        # 显式使用 system/user 消息结构以适配 DeepSeek
        result = await structured_llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        batch_results = []
        for res in result.evaluations:
            if res.id < len(batch):
                p = batch[res.id]
                
                # Heuristic scoring (Dual Track)
                ai_score = (res.innovation_score * 0.3 + 
                            res.idea_quality_score * 0.3 + 
                            res.ai_relevance_score * 0.4)
                            
                bio_score = (res.innovation_score * 0.3 + 
                             res.idea_quality_score * 0.3 + 
                             res.bio_relevance_score * 0.4)
                                    
                final_score = min(10.0, max(ai_score, bio_score))

                batch_results.append({
                    "paper": p,
                    "score": final_score,
                    "dimension_scores": {
                        "innovation": res.innovation_score,
                        "paper_quality": res.paper_quality_score,
                        "idea_quality": res.idea_quality_score,
                        "relevance_ai": res.ai_relevance_score,
                        "relevance_bio": res.bio_relevance_score
                    }
                })
        return batch_results
    except Exception as e:
        print(f"Error scoring batch {batch_idx + 1}: {e}")
        return []

async def filter_node(state: PaperState) -> Dict[str, Any]:
    new_papers = state.get("new_papers", [])
    if not new_papers:
        return {"scored_papers": []}

    papers_to_score = new_papers
    
    # 1. 预过滤逻辑 (保持原样)
    if ENABLE_PRE_FILTER:
        keywords_lower = [k.lower() for k in get_all_keywords()]
        filtered_papers = []
        for p in new_papers:
            text = (p.get('title', '') + " " + p.get('summary', '')).lower()
            match_count = sum(1 for k in keywords_lower if re.search(rf'\b{re.escape(k)}\b', text))
            if match_count >= PRE_FILTER_KEYWORD_THRESHOLD:
                filtered_papers.append(p)
        print(f"Pre-filtered: {len(filtered_papers)}/{len(new_papers)} papers remaining.")
        papers_to_score = filtered_papers

    if not papers_to_score:
        return {"scored_papers": []}

    # 2. 准备 LLM (建议在外部 config 切换为 DeepSeek-V3.2)
    llm = get_llm()
    # 消除警告的关键：对于 DeepSeek，确保 include_raw=False 或指定特定的解析模式
    structured_llm = llm.with_structured_output(BatchEvaluation, include_raw=False)
    
    system_prompt = """You are a strict, top-tier AI/ML Research Evaluator focusing on AI Methodologies and AI for Science.
    
    Evaluate papers across 5 dimensions: Innovation, Paper Quality, Idea Quality, AI Relevance, and Bio Relevance.
    
    CRITICAL INSTRUCTIONS & RED LINES:
    1. ZERO TOLERANCE for Data Analysis / Wet Lab: If a paper is purely data analysis (e.g. single-cell atlas mapping, differential expression analysis without novel models) OR purely wet-lab experimental, BOTH relevance scores MUST BE 0. We ONLY want papers about AI/ML models and methodologies.
    2. PENALIZE INCREMENTAL WORK: Strongly penalize papers that just "pile up engineering work" without algorithmic innovation. Innovation score should be low.
    3. BE OPEN-MINDED TO NEW PARADIGMS: Strongly REWARD novel architectures, generative models (Diffusion, Flow Matching), geometric deep learning, and large pre-trained models. Do not limit to existing Bio Foundation Models (like scGPT/Geneformer)—be open to new methodologies.
    4. Provide scores (1-10) for each dimension independently based on the above criteria.
    5. Output ONLY valid JSON according to the schema."""

    # 3. 分组并创建异步任务
    batches = [papers_to_score[i : i + MAX_PAPERS_PER_BATCH] for i in range(0, len(papers_to_score), MAX_PAPERS_PER_BATCH)]
    
    # 限制并发数以防触发 API Rate Limit (RPM)
    # 建议设置与你的 API 级别匹配的信号量
    semaphore = asyncio.Semaphore(100) 

    async def sem_task(batch, idx):
        async with semaphore:
            return await score_batch_async(structured_llm, batch, idx, system_prompt)

    tasks = [sem_task(batch, i) for i, batch in enumerate(batches)]
    
    print(f"--- STARTING ASYNC SCORING FOR {len(papers_to_score)} PAPERS ---")
    results_lists = await asyncio.gather(*tasks)
    
    # 合并结果
    scored_papers = [item for sublist in results_lists for item in sublist]
    print(f"--- SCORING COMPLETE: {len(scored_papers)} papers scored ---")

    return {"scored_papers": scored_papers}