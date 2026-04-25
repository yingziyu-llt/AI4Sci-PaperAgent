import asyncio
import re
import numpy as np
from typing import Dict, Any, List
from daily_paper_agent.state import PaperState
from daily_paper_agent.llm import get_llm
from daily_paper_agent.schemas import BatchEvaluation
from daily_paper_agent.config import MAX_PAPERS_PER_BATCH, ENABLE_PRE_FILTER, PRE_FILTER_KEYWORD_THRESHOLD
from daily_paper_agent.keywords import get_all_keywords
from daily_paper_agent.embeddings import EmbeddingTool, calculate_similarity
from daily_paper_agent.database import get_all_feedback

async def score_batch_async(structured_llm, batch, batch_idx, system_prompt):
    """异步处理单个批次的评分"""
    print(f"Scoring batch {batch_idx + 1}...")

    batch_text = ""
    for idx, p in enumerate(batch):
        journal = f"\nJournal: {p.get('journal', 'Unknown')}" if p.get('journal') else ""
        authors = f"\nAuthors: {p.get('authors', 'Unknown')}"
        batch_text += f"ID: {idx}\nTitle: {p['title']}{journal}{authors}\nAbstract: {p.get('summary', '')[:600]}\n---\n"

    prompt = f"Evaluate these papers:\n{batch_text}"

    try:
        # 使用 ainvoke 进行异步调用
        result = await structured_llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])

        batch_results = []
        for res in result.evaluations:
            if res.id < len(batch):
                p = batch[res.id]

                # Dual-Track Scoring (CS Engineering vs AI4Science)
                # Track 1: CS Engineering (Focus on Innovation & AI Relevance)
                cs_score = (res.innovation_score * 0.6 + 
                            res.ai_relevance_score * 0.4)
                
                # Track 2: AI4Science (Focus on Bio Relevance & Practical Utility)
                bio_score = (res.bio_relevance_score * 0.7 + 
                             res.idea_quality_score * 0.3)

                # Final score is the maximum of the two tracks, ensuring no cross-interference
                # We also factor in Paper Quality slightly
                base_score = max(cs_score, bio_score) * 0.9 + res.paper_quality_score * 0.1
                final_score = min(10.0, base_score)

                # Combine with recommendation score (Evolutionary Feedback)
                rec_score = p.get('recommendation_score', 0.5)
                adjusted_score = final_score * (0.8 + 0.4 * rec_score)
                adjusted_score = min(10.0, adjusted_score)

                batch_results.append({
                    "paper": p,
                    "score": adjusted_score,
                    "dimension_scores": {
                        "innovation": res.innovation_score,
                        "paper_quality": res.paper_quality_score,
                        "idea_quality": res.idea_quality_score,
                        "relevance_ai": res.ai_relevance_score,
                        "relevance_bio": res.bio_relevance_score,
                        "recommendation": rec_score
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

    # 1. 预过滤逻辑 (Keyword based)
    papers_to_score = new_papers
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

    # 2. 演化评分 (Evolutionary Ranker using Embeddings)
    feedbacks = get_all_feedback()
    embedding_tool = EmbeddingTool()

    if feedbacks:
        print(f"--- EVOLUTIONARY RANKING WITH {len(feedbacks)} FEEDBACKS ---")
        # Compute Preference Vector: Average(Likes) - 0.5 * Average(Dislikes)
        pos_vecs = [f['embedding'] for f in feedbacks if f['label'] > 0 and f['embedding'] is not None]
        neg_vecs = [f['embedding'] for f in feedbacks if f['label'] < 0 and f['embedding'] is not None]

        pref_vec = None
        if pos_vecs:
            pref_vec = np.mean(pos_vecs, axis=0)
            if neg_vecs:
                pref_vec -= 0.5 * np.mean(neg_vecs, axis=0)

        if pref_vec is not None:
            # Get embeddings for candidate papers
            texts = [f"{p['title']}. {p.get('summary', '')[:500]}" for p in papers_to_score]
            paper_vecs = embedding_tool.get_embeddings_batch(texts)

            scored_candidates = []
            for p, vec in zip(papers_to_score, paper_vecs):
                sim = calculate_similarity(pref_vec, vec) if vec is not None else 0.5
                p['recommendation_score'] = float(sim)
                p['embedding'] = vec # Store for later feedback
                scored_candidates.append((sim, p))

            # Sort by similarity and keep top N to reduce LLM load
            scored_candidates.sort(key=lambda x: x[0], reverse=True)

            # 如果论文超过一定数量，利用推荐系统结果截断 LLM 输入，实现“进化性”地节省 Token
            TOP_K_FOR_LLM = 50
            if len(scored_candidates) > TOP_K_FOR_LLM:
                print(f"Truncating candidates for LLM: {len(scored_candidates)} -> {TOP_K_FOR_LLM}")
                papers_to_score = [item[1] for item in scored_candidates[:TOP_K_FOR_LLM]]
            else:
                papers_to_score = [item[1] for item in scored_candidates]
        else:
            for p in papers_to_score: p['recommendation_score'] = 0.5
    else:
        for p in papers_to_score: p['recommendation_score'] = 0.5

    # 3. LLM 深度评分
    llm = get_llm()
    structured_llm = llm.with_structured_output(BatchEvaluation, include_raw=False)

    system_prompt = """You are a top-tier AI Researcher & Evaluator specializing in AI for Science. Your mission is to curate a high-impact list of papers, distinguishing between "Architectural Breakthroughs" and "Practical Scientific Utility", while filtering out "Math-heavy theoretical fluff".

    ### TRACK 1: ARCHITECTURAL & ENGINEERING INNOVATION (The "Mamba" Standard)
    We want papers that change HOW we build AI. 
    - NOVELTY: New architectures (e.g., Mamba, State Space Models, Linear Transformers, Efficient Attention).
    - EFFICIENCY: Significant scaling or speed breakthroughs (e.g., training LLMs on long sequences).
    - DOMAINS: Advanced NLP, CV, and General ML that are high-impact and scalable.
    - RED LINE: If a paper is purely theoretical (measure theory, abstract convergence proofs) with zero large-scale experimental results, give it 0 for Innovation and AI Relevance.

    ### TRACK 2: AI FOR SCIENCE (Bio + Chem Utility)
    We want papers that solve real scientific problems.
    - CORE INTERESTS: Single-cell & Spatial Omics, AIDD (PROTAC, Molecular Glue, 3D Geometry), Protein Folding (AlphaFold-level), Automated Labs.
    - UTILITY: Does it help design a drug, find a target, or model a biological system more accurately?
    - RED LINE: Penalize papers that are purely wet-lab OR purely incremental data analysis (e.g., "we ran Seurat on a new dataset") without novel AI methodology.

    ### EVALUATION SIGNALS (Using Metadata)
    - AUTHORS/LABS: Give high weight to top AI labs (OpenAI, DeepMind, Meta, Mila, etc.) or renowned Bio labs (Baker, Church, etc.). 
    - DEPARTMENTS: Be skeptical of pure Math/Stat departments if the paper lacks empirical benchmarking.
    - RELEVANCE: 
        - Track 1 papers should have high 'ai_relevance_score' but can have low 'bio_relevance_score'.
        - Track 2 papers should have high 'bio_relevance_score' but can have medium 'ai_relevance_score'.

    Output ONLY valid JSON."""

    # 4. 分组并创建异步任务
    batches = [papers_to_score[i : i + MAX_PAPERS_PER_BATCH] for i in range(0, len(papers_to_score), MAX_PAPERS_PER_BATCH)]

    # 限制并发数以防触发 API Rate Limit (RPM) 且避免连接池耗尽
    semaphore = asyncio.Semaphore(20) 

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