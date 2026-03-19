import os
from datetime import datetime
from typing import Dict, Any
from daily_paper_agent.state import PaperState
from daily_paper_agent.utils import update_cache
from daily_paper_agent.config import REPORT_OUTPUT_DIR, REPORT_FILENAME_FORMAT, MIN_RELEVANCE_SCORE


def _write_paper_entry(f, sp, index: int = 0):
    """Write a single paper entry in markdown format."""
    p = sp["paper"]
    f.write(f"""### {p['title']}
""")
    f.write(f"""- **来源**: {p['journal']} | **综合评分**: {sp['score']:.1f}/10
""")
    dim = sp.get("dimension_scores", {})
    if dim:
        f.write(f"""- **维度评分**: 创新性 ({dim.get('innovation', 0)}/10), 启发度 ({dim.get('idea_quality', 0)}/10), 通用AI ({dim.get('relevance_ai', 0)}/10), 生科AI ({dim.get('relevance_bio', 0)}/10)
""")
    f.write(f"""- **链接**: [{p['link']}]({p['link']})
""")
    
    # Indicate if PDF full text was used for summarization
    if sp.get("used_pdf"):
        f.write("""- 📄 *本文总结基于PDF全文*
""")
    
    ds = sp.get("detailed_summary")
    if ds:
        f.write(f"""#### 深度总结
""")
        f.write(f"""- **核心创新**: {ds.innovation}
""")
        f.write(f"""- **技术方法**: {ds.methodology}
""")
        f.write(f"""- **关键结果**: {ds.key_result}
""")
    f.write("""---
""")


def report_node(state: PaperState) -> Dict[str, Any]:
    print("--- GENERATING REPORT ---")
    
    ai_papers = state.get("ai_papers", [])
    bio_papers = state.get("bio_papers", [])
    all_scored = state["scored_papers"]
    top_papers = state.get("top_papers", [])
    
    if not os.path.exists(REPORT_OUTPUT_DIR):
        os.makedirs(REPORT_OUTPUT_DIR)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = datetime.now().strftime(REPORT_FILENAME_FORMAT)
    filepath = os.path.join(REPORT_OUTPUT_DIR, filename)

    # Collect IDs of papers that appear in the two main sections
    featured_links = set()
    for sp in ai_papers + bio_papers:
        featured_links.add(sp["paper"].get("link"))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"""# 每日论文智能报告 - {date_str}

""")
        f.write(f"""今日共处理 {len(all_scored)} 篇论文，其中 AI 最新进展 {len(ai_papers)} 篇，AI4S 生物相关进展 {len(bio_papers)} 篇。

""")

        # --- Section 1: AI Latest Progress ---
        f.write("""## 🤖 AI 最新进展

> 涵盖深度学习、生成模型、基础模型等 AI/ML 前沿方向的最新工作，不限于生物领域。

""")
        if ai_papers:
            for sp in ai_papers:
                _write_paper_entry(f, sp)
        else:
            f.write("""暂无 AI 通用进展论文。

""")

        # --- Section 2: AI4S Bio Related Progress ---
        f.write("""## 🧬 AI for Science 生物相关进展

> 聚焦单细胞组学、AI 药物设计、蛋白质结构预测、分子模拟等 AI4S 核心领域。

""")
        if bio_papers:
            for sp in bio_papers:
                _write_paper_entry(f, sp)
        else:
            f.write("""暂无 AI4S 生物相关进展论文。

""")

        # --- Section 3: Other scanned papers ---
        f.write("""## 📚 其他扫描论文
""")
        others = [sp for sp in all_scored 
                  if sp["score"] < MIN_RELEVANCE_SCORE 
                  and sp["paper"].get("link") not in featured_links]
        others.sort(key=lambda x: x["score"], reverse=True)
        for sp in others[:20]:
            p = sp["paper"]
            f.write(f"- [{p['journal']}] **{p['title']}** (评分: {sp['score']:.1f})\n")

    # Update cache
    new_ids = []
    for sp in all_scored:
        p = sp["paper"]
        p_id = p.get("doi") or p.get("id") or p.get("link")
        new_ids.append(p_id)
    
    if new_ids:
        update_cache(new_ids)
        print(f"Updated cache with {len(new_ids)} new papers.")

    print(f"Report generated: {filepath}")
    return {"report_path": filepath}
